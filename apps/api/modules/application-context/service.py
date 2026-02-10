"""Application-context service.

Business logic for loading, saving and validating the pharmacy
configuration.  Persists data to config/settings.json and
config/img/logo.png.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[4]

CONFIG_DIR = "config"
SETTINGS_FILE = "settings.json"
LOGO_SUBDIR = "img"
LOGO_FILE = "logo.png"

REQUIRED_TEXT_FIELDS: tuple[str, ...] = (
    "nom_pharmacie",
    "adresse",
    "code_postal",
    "ville",
    "telephone",
    "fournisseur_ia",
    "cle_api",
)

OPTIONAL_TEXT_FIELDS: tuple[str, ...] = (
    "site_web",
    "instagram",
    "facebook",
    "x",
    "linkedin",
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_base(base: Path | None) -> Path:
    return base if base is not None else PROJECT_ROOT


def _settings_path(base: Path) -> Path:
    return base / CONFIG_DIR / SETTINGS_FILE


def _logo_path(base: Path) -> Path:
    return base / CONFIG_DIR / LOGO_SUBDIR / LOGO_FILE


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_config(base: Path | None = None) -> Dict[str, Any]:
    """Load configuration from disk.

    Returns a dict with all text fields plus ``logo_image`` (absolute
    path string if the logo file exists, empty string otherwise).
    When no settings.json exists, all fields default to ``""``.
    """
    base = _resolve_base(base)
    settings = _settings_path(base)

    result: Dict[str, Any] = {}
    for field in REQUIRED_TEXT_FIELDS:
        result[field] = ""
    for field in OPTIONAL_TEXT_FIELDS:
        result[field] = ""
    result["logo_image"] = ""

    if settings.is_file():
        with open(settings, encoding="utf-8") as fh:
            data = json.load(fh)
        for key in (*REQUIRED_TEXT_FIELDS, *OPTIONAL_TEXT_FIELDS):
            if key in data:
                result[key] = data[key]

    logo = _logo_path(base)
    if logo.is_file():
        result["logo_image"] = str(logo.resolve())

    return result


def validate_config(payload: Dict[str, Any]) -> List[str]:
    """Validate a configuration payload (pure, no disk I/O).

    Returns a list of error messages.  An empty list means the payload
    is valid.
    """
    errors: List[str] = []

    for field in REQUIRED_TEXT_FIELDS:
        value = payload.get(field)
        if not isinstance(value, str) or value.strip() == "":
            errors.append(f"Champ obligatoire manquant: {field}")

    # Specific signalling for API key (INTERFACE.md §7)
    cle = payload.get("cle_api")
    if not isinstance(cle, str) or cle.strip() == "":
        if not any("cle_api" in e for e in errors):
            errors.append("Cle API manquante ou invalide")

    logo = payload.get("logo_image")
    if logo is None or logo == "" or logo == b"":
        errors.append("Champ obligatoire manquant: logo_image")

    return errors


def save_config(payload: Dict[str, Any], base: Path | None = None) -> None:
    """Validate and persist configuration to disk.

    ``payload["logo_image"]`` may be a file-path string (copied to
    config/img/logo.png) or raw ``bytes`` (written directly).

    Raises ``ValueError`` when validation fails.
    """
    errors = validate_config(payload)
    if errors:
        raise ValueError("Validation echouee: " + "; ".join(errors))

    base = _resolve_base(base)

    # Ensure directories exist
    config_dir = base / CONFIG_DIR
    logo_dir = config_dir / LOGO_SUBDIR
    logo_dir.mkdir(parents=True, exist_ok=True)

    # --- Write text fields to settings.json ---------------------------------
    text_data: Dict[str, str] = {}
    for field in (*REQUIRED_TEXT_FIELDS, *OPTIONAL_TEXT_FIELDS):
        text_data[field] = payload.get(field, "")

    with open(_settings_path(base), "w", encoding="utf-8") as fh:
        json.dump(text_data, fh, ensure_ascii=False, indent=2)

    # --- Write logo ----------------------------------------------------------
    logo_value = payload["logo_image"]
    dest = _logo_path(base)

    if isinstance(logo_value, bytes):
        dest.write_bytes(logo_value)
    elif isinstance(logo_value, str):
        source = Path(logo_value)
        if not source.is_file():
            raise ValueError(f"Fichier logo introuvable: {logo_value}")
        if source.suffix.lower() in (".jpg", ".jpeg"):
            img = Image.open(source)
            img.save(dest, "PNG")
        else:
            shutil.copy2(source, dest)


def is_configured(base: Path | None = None) -> bool:
    """Return True if a complete, valid configuration exists on disk."""
    base = _resolve_base(base)

    settings = _settings_path(base)
    if not settings.is_file():
        return False

    try:
        with open(settings, encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError):
        return False

    for field in REQUIRED_TEXT_FIELDS:
        value = data.get(field)
        if not isinstance(value, str) or value.strip() == "":
            return False

    if not _logo_path(base).is_file():
        return False

    return True
