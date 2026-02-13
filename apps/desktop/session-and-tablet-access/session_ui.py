"""Session UI adapter.

Pure state management for the session initialisation screen.
No framework dependencies, no file I/O.  Every public function
returns a new state dict (immutable via deepcopy).
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


_EMPTY_PHARMACY_CONTEXT: Dict[str, str] = {
    "nom_pharmacie": "",
    "adresse": "",
    "code_postal": "",
    "ville": "",
    "site_web": "",
    "instagram": "",
    "facebook": "",
    "x": "",
    "linkedin": "",
    "logo_path": "",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_ui_state() -> Dict[str, Any]:
    """Create a fresh initial state."""
    return {
        "status": "initial",
        "pharmacy_context": dict(_EMPTY_PHARMACY_CONTEXT),
        "available_age_ranges": [],
        "selected_age_range": None,
        "selected_sex": None,
        "session": None,
        "qr_data": None,
        "questionnaire_status": None,
        "errors": [],
        "precondition_errors": [],
    }


def load_context(
    state: Dict[str, Any],
    pharmacy_context: Dict[str, Any],
    available_age_ranges: List[str],
    precondition_errors: List[str],
) -> Dict[str, Any]:
    """Load pharmacy context and available age ranges into state.

    Transitions to ``"ready"`` if preconditions are met, or to
    ``"erreur"`` if there are precondition errors.
    """
    new = deepcopy(state)
    new["pharmacy_context"] = dict(pharmacy_context)
    new["available_age_ranges"] = list(available_age_ranges)
    new["precondition_errors"] = list(precondition_errors)
    if precondition_errors:
        new["status"] = "erreur"
        new["errors"] = list(precondition_errors)
    else:
        new["status"] = "ready"
        new["errors"] = []
    return new


def select_age_range(
    state: Dict[str, Any], age_range: str
) -> Dict[str, Any]:
    """Set the selected age range."""
    new = deepcopy(state)
    new["selected_age_range"] = age_range
    new["errors"] = []
    return new


def deselect_age_range(state: Dict[str, Any]) -> Dict[str, Any]:
    """Clear the selected age range."""
    new = deepcopy(state)
    new["selected_age_range"] = None
    return new


def select_sex(state: Dict[str, Any], sex: str) -> Dict[str, Any]:
    """Set the selected sex (``H`` or ``F``)."""
    new = deepcopy(state)
    new["selected_sex"] = sex
    new["errors"] = []
    return new


def deselect_sex(state: Dict[str, Any]) -> Dict[str, Any]:
    """Clear the selected sex."""
    new = deepcopy(state)
    new["selected_sex"] = None
    return new


def validate_ui_state(state: Dict[str, Any]) -> List[str]:
    """Validate the state for session creation readiness.

    Returns a list of error messages.  Empty means valid.
    """
    errors: List[str] = []
    if state.get("precondition_errors"):
        return list(state["precondition_errors"])
    if state.get("selected_age_range") is None:
        errors.append("Aucune tranche d'age selectionnee")
    elif state["selected_age_range"] not in state.get(
        "available_age_ranges", []
    ):
        errors.append("Tranche d'age non disponible")
    if state.get("selected_sex") is None:
        errors.append("Aucun sexe selectionne")
    elif state["selected_sex"] not in ("H", "F"):
        errors.append("Sexe invalide")
    return errors


def can_start(state: Dict[str, Any]) -> bool:
    """Return True if the session can be started."""
    if state.get("status") != "ready":
        return False
    return len(validate_ui_state(state)) == 0


def mark_starting(state: Dict[str, Any]) -> Dict[str, Any]:
    """Transition to ``"starting"`` status."""
    new = deepcopy(state)
    new["status"] = "starting"
    return new


def mark_created(
    state: Dict[str, Any], session: Dict[str, Any]
) -> Dict[str, Any]:
    """Transition to ``"created"`` and store the session data."""
    new = deepcopy(state)
    new["status"] = "created"
    new["session"] = dict(session)
    new["errors"] = []
    return new


def mark_error(
    state: Dict[str, Any], errors: List[str]
) -> Dict[str, Any]:
    """Transition to ``"erreur"`` and store errors."""
    new = deepcopy(state)
    new["status"] = "erreur"
    new["errors"] = list(errors)
    return new


def build_submission_payload(state: Dict[str, Any]) -> Dict[str, str]:
    """Return age range and sex for session creation.

    Raises ``ValueError`` if the state is not valid.
    """
    errors = validate_ui_state(state)
    if errors:
        raise ValueError("Validation echouee: " + "; ".join(errors))
    return {
        "age_range": state["selected_age_range"],
        "sex": state["selected_sex"],
    }


# ---------------------------------------------------------------------------
# QR Code state transitions (GenerateSessionQRCode)
# ---------------------------------------------------------------------------


def mark_qr_generating(state: Dict[str, Any]) -> Dict[str, Any]:
    """Transition to ``"qr_generating"`` status."""
    new = deepcopy(state)
    new["status"] = "qr_generating"
    return new


def mark_qr_ready(
    state: Dict[str, Any], qr_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Transition to ``"qr_ready"`` and store QR data."""
    new = deepcopy(state)
    new["status"] = "qr_ready"
    new["qr_data"] = dict(qr_data)
    new["errors"] = []
    return new


def mark_qr_error(
    state: Dict[str, Any], errors: List[str]
) -> Dict[str, Any]:
    """Transition to ``"erreur"`` due to QR generation failure."""
    new = deepcopy(state)
    new["status"] = "erreur"
    new["errors"] = list(errors)
    return new


# ---------------------------------------------------------------------------
# Questionnaire status transitions
# ---------------------------------------------------------------------------


def mark_questionnaire_disponible(state: Dict[str, Any]) -> Dict[str, Any]:
    """Set questionnaire status to ``"disponible"``."""
    new = deepcopy(state)
    new["questionnaire_status"] = "disponible"
    return new


def mark_questionnaire_en_cours(state: Dict[str, Any]) -> Dict[str, Any]:
    """Set questionnaire status to ``"en_cours"``."""
    new = deepcopy(state)
    new["questionnaire_status"] = "en_cours"
    return new


def mark_questionnaire_termine(state: Dict[str, Any]) -> Dict[str, Any]:
    """Set questionnaire status to ``"termine"``."""
    new = deepcopy(state)
    new["questionnaire_status"] = "termine"
    return new
