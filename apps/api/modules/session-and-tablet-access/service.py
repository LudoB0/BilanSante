"""Session-and-tablet-access service.

Business logic for initialising interview sessions.  Reads pharmacy
context from config/settings.json, filters available age ranges from
config/questionnaires/, and creates session files in data/sessions/.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import socket
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
VALID_SEX_VALUES: tuple[str, ...] = ("H", "F")

QR_SECRET_FILE = "qr_secret.key"
QR_PAYLOAD_VERSION = 1
TABLET_SERVER_PORT = 5000

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


def _qr_secret_path(base: Path) -> Path:
    return base / CONFIG_DIR / QR_SECRET_FILE


def get_local_ip() -> str:
    """Detect the local IP address reachable from the LAN.

    Opens a UDP socket to a public address (no data sent) to let
    the OS select the correct network interface.  Falls back to
    ``127.0.0.1`` if detection fails.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.254.254.254", 1))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def get_questionnaire_base_url(port: int = TABLET_SERVER_PORT) -> str:
    """Build the questionnaire base URL using the local IP."""
    ip = get_local_ip()
    return f"http://{ip}:{port}/questionnaire"


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


def create_session(age_range: str, sex: str, base: Path | None = None) -> Dict[str, Any]:
    """Create a new interview session.

    Validates preconditions, generates a UUID v4, writes the session
    file to data/sessions/<session_id>.json, and returns the session
    dict.

    Raises ValueError if age_range is invalid, sex is not H/F,
    preconditions are not met, or the selected age range has no
    questionnaire.
    """
    if age_range not in VALID_AGE_RANGES:
        raise ValueError(f"Tranche d'age invalide: {age_range}")
    if sex not in VALID_SEX_VALUES:
        raise ValueError(f"Sexe invalide: {sex}")

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
        "sex": sex,
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


# ---------------------------------------------------------------------------
# QR Code generation (GenerateSessionQRCode)
# ---------------------------------------------------------------------------


def load_or_create_qr_secret(base: Path | None = None) -> str:
    """Load or generate the HMAC secret for QR code signing.

    Creates ``config/qr_secret.key`` on first call.
    """
    base = _resolve_base(base)
    path = _qr_secret_path(base)
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    secret = secrets.token_hex(32)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(secret, encoding="utf-8")
    return secret


def load_session(session_id: str, base: Path | None = None) -> Dict[str, Any]:
    """Load an existing session from disk.

    Raises ``ValueError`` if the session file does not exist or is
    not valid JSON.
    """
    base = _resolve_base(base)
    session_path = _sessions_dir(base) / f"{session_id}.json"
    if not session_path.is_file():
        raise ValueError(f"Session inconnue: {session_id}")
    try:
        with open(session_path, encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"Session invalide: {session_id}") from exc


def generate_session_token() -> str:
    """Generate an opaque, non-guessable token for QR payload."""
    return secrets.token_urlsafe(32)


def compute_signature(session_id: str, token: str, secret_key: str) -> str:
    """Compute HMAC-SHA256 signature for the QR payload fields."""
    message = f"v={QR_PAYLOAD_VERSION}&sid={session_id}&t={token}"
    return hmac.new(
        secret_key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def build_qr_payload(
    base_url: str, session_id: str, token: str, signature: str
) -> str:
    """Build the complete QR code payload URL.

    Format: ``<base_url>?v=1&sid=<session_id>&t=<token>&sig=<signature>``
    """
    return (
        f"{base_url}?v={QR_PAYLOAD_VERSION}"
        f"&sid={session_id}&t={token}&sig={signature}"
    )


def generate_qr_data(
    session_id: str,
    base: Path | None = None,
    base_url: str | None = None,
) -> Dict[str, Any]:
    """Generate QR code data for an active session.

    Validates session status, generates token and signature,
    builds the payload URL.

    Returns a dict with ``payload``, ``session_id``, ``version``,
    ``token``, ``signature``.

    Raises ``ValueError`` if the session does not exist or is not
    active, or if mandatory inputs are missing.
    """
    base = _resolve_base(base)

    session = load_session(session_id, base)
    if session.get("status") != "active":
        raise ValueError(f"Session inactive: {session_id}")

    if base_url is None:
        base_url = get_questionnaire_base_url()

    if not base_url:
        raise ValueError("URL de base questionnaire absente")

    secret = load_or_create_qr_secret(base)
    token = generate_session_token()
    signature = compute_signature(session_id, token, secret)
    payload = build_qr_payload(base_url, session_id, token, signature)

    return {
        "payload": payload,
        "session_id": session_id,
        "version": QR_PAYLOAD_VERSION,
        "token": token,
        "signature": signature,
    }


def verify_qr_signature(
    session_id: str,
    token: str,
    signature: str,
    base: Path | None = None,
) -> bool:
    """Verify a QR payload signature against the stored secret."""
    base = _resolve_base(base)
    secret = load_or_create_qr_secret(base)
    expected = compute_signature(session_id, token, secret)
    return hmac.compare_digest(signature, expected)


# ---------------------------------------------------------------------------
# Tablet access helpers (ServeQuestionnaireOnTablet)
# ---------------------------------------------------------------------------


def validate_qr_params(
    v: str | int | None,
    sid: str | None,
    t: str | None,
    sig: str | None,
    base: Path | None = None,
) -> Dict[str, Any]:
    """Validate the QR code URL parameters.

    Returns ``{"valid": True, "session": <session_dict>}`` on success,
    or ``{"valid": False, "error": "<message>"}`` on failure.
    """
    # Check all params present
    if not sid:
        return {"valid": False, "error": "Parametre sid manquant"}
    if not t:
        return {"valid": False, "error": "Parametre t manquant"}
    if not sig:
        return {"valid": False, "error": "Parametre sig manquant"}

    # Check version
    try:
        version = int(v) if v is not None else None
    except (ValueError, TypeError):
        version = None
    if version != QR_PAYLOAD_VERSION:
        return {"valid": False, "error": "Version du payload invalide"}

    # Verify signature
    base = _resolve_base(base)
    if not verify_qr_signature(sid, t, sig, base):
        return {"valid": False, "error": "Signature invalide"}

    # Load and check session
    try:
        session = load_session(sid, base)
    except ValueError:
        return {"valid": False, "error": "Session inconnue"}

    if session.get("status") != "active":
        return {"valid": False, "error": "Session inactive"}

    return {"valid": True, "session": session}


def load_questionnaire_for_session(
    session_id: str, base: Path | None = None
) -> Dict[str, Any]:
    """Load the questionnaire for a session's age range.

    Raises ``ValueError`` if the session is unknown or no
    questionnaire is available for its age range.
    """
    base = _resolve_base(base)
    session = load_session(session_id, base)
    age_range = session.get("age_range")
    if not age_range:
        raise ValueError("Session sans tranche d'age")

    qpath = _questionnaires_dir(base) / f"{age_range}.json"
    if not qpath.is_file():
        raise ValueError(
            f"Questionnaire non disponible pour la tranche d'age: {age_range}"
        )
    try:
        with open(qpath, encoding="utf-8") as fh:
            questionnaire = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(
            f"Questionnaire invalide pour la tranche d'age: {age_range}"
        ) from exc

    questions = questionnaire.get("questions")
    if not isinstance(questions, list) or len(questions) == 0:
        raise ValueError(
            f"Questionnaire vide pour la tranche d'age: {age_range}"
        )
    return questionnaire
