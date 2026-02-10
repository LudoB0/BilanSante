"""Session-and-tablet-access service.

Business logic for initialising interview sessions.  Reads pharmacy
context from config/settings.json, filters available age ranges from
config/questionnaires/, and creates session files in data/sessions/.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[4]

CONFIG_DIR = "config"
SETTINGS_FILE = "settings.json"
LOGO_SUBDIR = "img"
LOGO_FILE = "logo.png"
QUESTIONNAIRES_SUBDIR = "questionnaires"
DATA_DIR = "data"
SESSIONS_SUBDIR = "sessions"

VALID_AGE_RANGES: tuple[str, ...] = ("18-25", "45-50", "60-65", "70-75")

REQUIRED_SETTINGS_FIELDS: tuple[str, ...] = (
    "nom_pharmacie",
    "adresse",
    "code_postal",
    "ville",
    "telephone",
    "fournisseur_ia",
    "cle_api",
)

PHARMACY_DISPLAY_FIELDS: tuple[str, ...] = (
    "nom_pharmacie",
    "adresse",
    "code_postal",
    "ville",
)

OPTIONAL_DISPLAY_FIELDS: tuple[str, ...] = (
    "site_web",
    "instagram",
    "facebook",
    "x",
    "linkedin",
)

_MAX_UUID_RETRIES = 5


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_base(base: Path | None) -> Path:
    return base if base is not None else PROJECT_ROOT


def _settings_path(base: Path) -> Path:
    return base / CONFIG_DIR / SETTINGS_FILE


def _logo_path(base: Path) -> Path:
    return base / CONFIG_DIR / LOGO_SUBDIR / LOGO_FILE


def _questionnaires_dir(base: Path) -> Path:
    return base / CONFIG_DIR / QUESTIONNAIRES_SUBDIR


def _sessions_dir(base: Path) -> Path:
    return base / DATA_DIR / SESSIONS_SUBDIR


def _load_settings(base: Path) -> Dict[str, Any] | None:
    """Load and parse settings.json.  Returns None on failure."""
    path = _settings_path(base)
    if not path.is_file():
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None


def _questionnaire_has_questions(path: Path) -> bool:
    """Return True if the questionnaire file has >= 1 question."""
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        questions = data.get("questions")
        return isinstance(questions, list) and len(questions) >= 1
    except (json.JSONDecodeError, OSError, KeyError):
        return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def check_preconditions(base: Path | None = None) -> List[str]:
    """Check all preconditions for session initialisation.

    Returns a list of error messages.  An empty list means all
    preconditions are met.
    """
    base = _resolve_base(base)
    errors: List[str] = []

    # Settings file
    data = _load_settings(base)
    if data is None:
        errors.append("Parametrage applicatif manquant ou invalide")
    else:
        for field in REQUIRED_SETTINGS_FIELDS:
            value = data.get(field)
            if not isinstance(value, str) or value.strip() == "":
                errors.append(f"Champ obligatoire manquant: {field}")

    # Logo
    if not _logo_path(base).is_file():
        errors.append("Logo de la pharmacie manquant")

    # At least one questionnaire with questions
    qdir = _questionnaires_dir(base)
    has_questionnaire = False
    if qdir.is_dir():
        for age_range in VALID_AGE_RANGES:
            path = qdir / f"{age_range}.json"
            if path.is_file() and _questionnaire_has_questions(path):
                has_questionnaire = True
                break
    if not has_questionnaire:
        errors.append("Aucun questionnaire disponible")

    return errors


def load_pharmacy_context(base: Path | None = None) -> Dict[str, Any]:
    """Load pharmacy display information from config/settings.json.

    Returns a dict with pharmacy display fields, optional web links,
    and logo_path.  Missing values default to empty strings.
    """
    base = _resolve_base(base)
    result: Dict[str, Any] = {}

    for field in PHARMACY_DISPLAY_FIELDS:
        result[field] = ""
    for field in OPTIONAL_DISPLAY_FIELDS:
        result[field] = ""
    result["logo_path"] = ""

    data = _load_settings(base)
    if data is not None:
        for field in (*PHARMACY_DISPLAY_FIELDS, *OPTIONAL_DISPLAY_FIELDS):
            if field in data and isinstance(data[field], str):
                result[field] = data[field]

    logo = _logo_path(base)
    if logo.is_file():
        result["logo_path"] = str(logo.resolve())

    return result


def list_available_age_ranges(base: Path | None = None) -> List[str]:
    """Return age ranges that have a questionnaire with >= 1 question.

    Preserves the canonical order defined in VALID_AGE_RANGES.
    """
    base = _resolve_base(base)
    qdir = _questionnaires_dir(base)
    if not qdir.is_dir():
        return []
    result: List[str] = []
    for age_range in VALID_AGE_RANGES:
        path = qdir / f"{age_range}.json"
        if path.is_file() and _questionnaire_has_questions(path):
            result.append(age_range)
    return result


def create_session(age_range: str, base: Path | None = None) -> Dict[str, Any]:
    """Create a new interview session.

    Validates preconditions, generates a UUID v4, writes the session
    file to data/sessions/<session_id>.json, and returns the session
    dict.

    Raises ValueError if age_range is invalid, preconditions are not
    met, or the selected age range has no questionnaire.
    """
    if age_range not in VALID_AGE_RANGES:
        raise ValueError(f"Tranche d'age invalide: {age_range}")

    base = _resolve_base(base)

    errors = check_preconditions(base)
    if errors:
        raise ValueError(
            "Preconditions non remplies: " + "; ".join(errors)
        )

    available = list_available_age_ranges(base)
    if age_range not in available:
        raise ValueError(
            f"Aucun questionnaire disponible pour la tranche d'age: {age_range}"
        )

    # Load pharmacy metadata
    data = _load_settings(base)
    pharmacy_meta: Dict[str, str] = {}
    if data is not None:
        for field in PHARMACY_DISPLAY_FIELDS:
            pharmacy_meta[field] = data.get(field, "")

    # Generate unique session ID
    sessions_dir = _sessions_dir(base)
    sessions_dir.mkdir(parents=True, exist_ok=True)

    session_id = ""
    for _ in range(_MAX_UUID_RETRIES):
        candidate = str(uuid.uuid4())
        if not (sessions_dir / f"{candidate}.json").exists():
            session_id = candidate
            break
    if not session_id:
        raise RuntimeError("Impossible de generer un identifiant de session unique")

    session: Dict[str, Any] = {
        "session_id": session_id,
        "age_range": age_range,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "status": "active",
        "metadata": {
            "pharmacie": pharmacy_meta,
        },
    }

    session_path = sessions_dir / f"{session_id}.json"
    with open(session_path, "w", encoding="utf-8") as fh:
        json.dump(session, fh, ensure_ascii=False, indent=2)

    return session
