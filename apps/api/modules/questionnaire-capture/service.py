"""Questionnaire-capture service.

Business logic for capturing and persisting questionnaire responses
submitted from the tablet web page.  Responses are stored in
data/sessions/<session_id>_responses.json.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[4]

DATA_DIR = "data"
SESSIONS_SUBDIR = "sessions"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_base(base: Path | None) -> Path:
    return base if base is not None else PROJECT_ROOT


def _sessions_dir(base: Path) -> Path:
    return base / DATA_DIR / SESSIONS_SUBDIR


def _responses_path(session_id: str, base: Path) -> Path:
    return _sessions_dir(base) / f"{session_id}_responses.json"


def _session_path(session_id: str, base: Path) -> Path:
    return _sessions_dir(base) / f"{session_id}.json"


def _load_session(session_id: str, base: Path) -> Dict[str, Any] | None:
    path = _session_path(session_id, base)
    if not path.is_file():
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate_responses(responses: List[Dict[str, Any]]) -> List[str]:
    """Validate the structure of a list of responses.

    Each response must have at least ``question_id`` and ``value``.
    Returns a list of error messages (empty = valid).
    """
    errors: List[str] = []
    if not isinstance(responses, list):
        errors.append("Les reponses doivent etre une liste")
        return errors

    for i, resp in enumerate(responses):
        prefix = f"Reponse {i + 1}"
        if not isinstance(resp, dict):
            errors.append(f"{prefix}: format invalide")
            continue
        if not resp.get("question_id"):
            errors.append(f"{prefix}: question_id manquant")
        if "value" not in resp:
            errors.append(f"{prefix}: value manquant")
    return errors


def save_responses(
    session_id: str,
    responses: List[Dict[str, Any]],
    submitted_at: str | None = None,
    base: Path | None = None,
) -> Dict[str, Any]:
    """Save questionnaire responses for a session.

    Validates the session is active and responses are well-formed,
    then persists to ``data/sessions/<session_id>_responses.json``.

    Returns the persisted record dict.

    Raises ``ValueError`` on validation failure.
    """
    base = _resolve_base(base)

    # Check session
    session = _load_session(session_id, base)
    if session is None:
        raise ValueError(f"Session inconnue: {session_id}")
    if session.get("status") != "active":
        raise ValueError(f"Session inactive: {session_id}")

    # Validate responses
    errors = validate_responses(responses)
    if errors:
        raise ValueError(
            "Reponses invalides: " + "; ".join(errors)
        )

    if submitted_at is None:
        submitted_at = datetime.now().isoformat(timespec="seconds")

    record: Dict[str, Any] = {
        "session_id": session_id,
        "submitted_at": submitted_at,
        "responses_count": len(responses),
        "responses": list(responses),
    }

    # Persist
    sessions_dir = _sessions_dir(base)
    sessions_dir.mkdir(parents=True, exist_ok=True)
    path = _responses_path(session_id, base)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, ensure_ascii=False, indent=2)

    return record


def load_responses(
    session_id: str, base: Path | None = None
) -> Dict[str, Any] | None:
    """Load saved responses for a session.

    Returns the record dict or ``None`` if no responses exist.
    """
    base = _resolve_base(base)
    path = _responses_path(session_id, base)
    if not path.is_file():
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None
