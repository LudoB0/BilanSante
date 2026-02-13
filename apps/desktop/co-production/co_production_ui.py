"""Co-production UI adapter.

Pure state management for the co-production screen
(IdentifyVigilancePoints).  No framework dependencies,
no file I/O.  Every public function returns a new state dict
(immutable via deepcopy).
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_co_production_state() -> Dict[str, Any]:
    """Create a fresh initial state."""
    return {
        "status": "initial",
        "session_id": None,
        "short_id": None,
        "md_path": None,
        "vigilance_text": None,
        "vigilance_md_path": None,
        "action_points": ["", "", ""],
        "errors": [],
    }


def mark_loading(state: Dict[str, Any]) -> Dict[str, Any]:
    """Transition to ``"loading"`` status (AI call in progress)."""
    new = deepcopy(state)
    new["status"] = "loading"
    return new


def load_vigilance_result(
    state: Dict[str, Any], result_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Load the AI vigilance result.

    Transitions to ``"vigilance_ready"`` status.
    """
    new = deepcopy(state)
    new["status"] = "vigilance_ready"
    new["session_id"] = result_data["session_id"]
    new["short_id"] = result_data["short_id"]
    new["vigilance_text"] = result_data["vigilance_text"]
    new["vigilance_md_path"] = result_data["vigilance_md_path"]
    new["errors"] = []
    return new


def mark_vigilance_error(
    state: Dict[str, Any], errors: List[str]
) -> Dict[str, Any]:
    """Transition to ``"erreur"`` status (AI call failed)."""
    new = deepcopy(state)
    new["status"] = "erreur"
    new["errors"] = list(errors)
    return new


def update_action_point(
    state: Dict[str, Any], index: int, text: str
) -> Dict[str, Any]:
    """Update the action point at *index* (0, 1 or 2)."""
    if index not in (0, 1, 2):
        raise ValueError(f"Index invalide: {index}")
    new = deepcopy(state)
    new["action_points"][index] = text
    return new


def mark_saving(state: Dict[str, Any]) -> Dict[str, Any]:
    """Transition to ``"saving"`` status."""
    new = deepcopy(state)
    new["status"] = "saving"
    return new


def mark_saved(state: Dict[str, Any]) -> Dict[str, Any]:
    """Transition to ``"saved"`` status."""
    new = deepcopy(state)
    new["status"] = "saved"
    new["errors"] = []
    return new


def mark_save_error(
    state: Dict[str, Any], errors: List[str]
) -> Dict[str, Any]:
    """Transition to ``"erreur"`` status (save failed)."""
    new = deepcopy(state)
    new["status"] = "erreur"
    new["errors"] = list(errors)
    return new


def get_action_points(state: Dict[str, Any]) -> List[str]:
    """Return a copy of the 3 action points."""
    return list(state.get("action_points", ["", "", ""]))


def is_vigilance_ready(state: Dict[str, Any]) -> bool:
    """Return True if the AI result has been received."""
    return state.get("status") == "vigilance_ready"


def can_validate(state: Dict[str, Any]) -> bool:
    """Return True if all 3 action points are non-empty and status allows."""
    if state.get("status") != "vigilance_ready":
        return False
    points = state.get("action_points", ["", "", ""])
    return all(isinstance(p, str) and p.strip() for p in points)
