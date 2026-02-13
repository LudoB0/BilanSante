"""Questionnaire summary UI adapter.

Pure state management for the questionnaire summary display
(BuildQuestionnaireSummarySection).  No framework dependencies,
no file I/O.  Every public function returns a new state dict
(immutable via deepcopy).
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_summary_state() -> Dict[str, Any]:
    """Create a fresh initial state."""
    return {
        "status": "initial",
        "session_id": None,
        "short_id": None,
        "age_range": None,
        "items": [],
        "metrics": None,
        "pharmacist_notes": {},
        "pharmacist_blood_pressure": "",
        "pharmacist_report": "",
        "md_path": None,
        "errors": [],
    }


def mark_loading(state: Dict[str, Any]) -> Dict[str, Any]:
    """Transition to ``"loading"`` status."""
    new = deepcopy(state)
    new["status"] = "loading"
    return new


def load_summary(
    state: Dict[str, Any], summary_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Load summary data returned by the service.

    Transitions to ``"ready"`` status.
    """
    new = deepcopy(state)
    new["status"] = "ready"
    new["session_id"] = summary_data["session_id"]
    new["short_id"] = summary_data["short_id"]
    new["age_range"] = summary_data["age_range"]
    new["items"] = list(summary_data["items"])
    new["metrics"] = summary_data.get("metrics")
    new["md_path"] = summary_data["md_path"]
    new["errors"] = []
    return new


def mark_summary_error(
    state: Dict[str, Any], errors: List[str]
) -> Dict[str, Any]:
    """Transition to ``"erreur"`` status."""
    new = deepcopy(state)
    new["status"] = "erreur"
    new["errors"] = list(errors)
    return new


def update_pharmacist_note(
    state: Dict[str, Any], question_id: str, note: str
) -> Dict[str, Any]:
    """Update the pharmacist note for a specific question."""
    new = deepcopy(state)
    new["pharmacist_notes"][question_id] = note
    return new


def update_pharmacist_blood_pressure(
    state: Dict[str, Any], blood_pressure: str
) -> Dict[str, Any]:
    """Update the pharmacist blood-pressure value."""
    new = deepcopy(state)
    new["pharmacist_blood_pressure"] = blood_pressure
    return new


def update_pharmacist_report(
    state: Dict[str, Any], report: str
) -> Dict[str, Any]:
    """Update the final pharmacist report text."""
    new = deepcopy(state)
    new["pharmacist_report"] = report
    return new


def mark_capturing(state: Dict[str, Any]) -> Dict[str, Any]:
    """Transition to ``"capturing"`` status (saving notes in progress)."""
    new = deepcopy(state)
    new["status"] = "capturing"
    return new


def mark_captured(state: Dict[str, Any]) -> Dict[str, Any]:
    """Transition to ``"captured"`` status (notes saved successfully)."""
    new = deepcopy(state)
    new["status"] = "captured"
    new["errors"] = []
    return new


def mark_capture_error(
    state: Dict[str, Any], errors: List[str]
) -> Dict[str, Any]:
    """Transition to ``"capture_error"`` status."""
    new = deepcopy(state)
    new["status"] = "capture_error"
    new["errors"] = list(errors)
    return new


def get_pharmacist_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract all pharmacist inputs from state for persistence."""
    return {
        "pharmacist_notes": dict(state.get("pharmacist_notes", {})),
        "pharmacist_blood_pressure": state.get("pharmacist_blood_pressure", ""),
        "pharmacist_report": state.get("pharmacist_report", ""),
    }


def get_summary_items(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return the list of question/response items for display."""
    return list(state.get("items", []))


def is_ready(state: Dict[str, Any]) -> bool:
    """Return True if the summary is loaded and ready for display."""
    return state.get("status") == "ready"
