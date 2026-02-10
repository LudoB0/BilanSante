"""UI contract adapter for questionnaire-catalog module.

Pure state management without framework-specific behavior.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

VALID_AGE_RANGES: tuple[str, ...] = ("18-25", "45-50", "60-65", "70-75")

VALID_QUESTION_TYPES: tuple[str, ...] = (
    "boolean",
    "single_choice",
    "multiple_choice",
    "short_text",
    "scale",
)


def create_ui_state(
    configured_ranges: List[str] | None = None,
) -> Dict[str, Any]:
    """Create the initial UI state.

    configured_ranges: list of age ranges that already have a saved
    questionnaire.
    """
    status_map: Dict[str, bool] = {ar: False for ar in VALID_AGE_RANGES}
    if configured_ranges:
        for ar in configured_ranges:
            if ar in status_map:
                status_map[ar] = True

    return {
        "status": "initial",
        "selected_age_range": None,
        "age_ranges_status": status_map,
        "questionnaire": None,
        "errors": [],
    }


def select_age_range(
    state: Dict[str, Any],
    age_range: str,
    questionnaire: Dict[str, Any] | None,
) -> Dict[str, Any]:
    """Select an age range and load its questionnaire.

    If questionnaire is None or has no questions, enters 'creation' status.
    If questionnaire has questions, enters 'edition' status.
    """
    updated = deepcopy(state)
    updated["selected_age_range"] = age_range
    updated["questionnaire"] = questionnaire
    updated["errors"] = []

    if questionnaire and questionnaire.get("questions"):
        updated["status"] = "edition"
    else:
        updated["status"] = "creation"
    return updated


def add_question(
    state: Dict[str, Any],
    question: Dict[str, Any],
) -> Dict[str, Any]:
    """Add a question to the current questionnaire."""
    updated = deepcopy(state)
    if updated["questionnaire"] is None:
        updated["questionnaire"] = {
            "age_range": updated["selected_age_range"],
            "version": 1,
            "created_at": "",
            "updated_at": "",
            "questions": [],
        }
    updated["questionnaire"]["questions"].append(question)
    updated["status"] = "edition"
    updated["errors"] = []
    return updated


def remove_question(
    state: Dict[str, Any],
    index: int,
) -> Dict[str, Any]:
    """Remove a question by index. Reorder remaining questions."""
    updated = deepcopy(state)
    questions = updated["questionnaire"]["questions"]
    if 0 <= index < len(questions):
        questions.pop(index)
        for i, q in enumerate(questions):
            q["order"] = i
    updated["status"] = "edition"
    updated["errors"] = []
    return updated


def update_question(
    state: Dict[str, Any],
    index: int,
    field: str,
    value: Any,
) -> Dict[str, Any]:
    """Update a field on a specific question."""
    updated = deepcopy(state)
    questions = updated["questionnaire"]["questions"]
    if 0 <= index < len(questions):
        questions[index][field] = value

        if field == "type":
            if value == "scale":
                questions[index]["scale_config"] = {
                    "min": 1, "max": 10, "step": 1
                }
                questions[index]["options"] = []
            elif value in ("single_choice", "multiple_choice"):
                questions[index]["scale_config"] = None
                if len(questions[index].get("options", [])) < 2:
                    questions[index]["options"] = ["", ""]
            else:
                questions[index]["scale_config"] = None
                questions[index]["options"] = []

    updated["status"] = "edition"
    updated["errors"] = []
    return updated


def add_option(
    state: Dict[str, Any],
    question_index: int,
) -> Dict[str, Any]:
    """Add an empty option to a choice question."""
    updated = deepcopy(state)
    questions = updated["questionnaire"]["questions"]
    if 0 <= question_index < len(questions):
        questions[question_index]["options"].append("")
    updated["status"] = "edition"
    return updated


def remove_option(
    state: Dict[str, Any],
    question_index: int,
    option_index: int,
) -> Dict[str, Any]:
    """Remove an option from a choice question."""
    updated = deepcopy(state)
    questions = updated["questionnaire"]["questions"]
    if 0 <= question_index < len(questions):
        options = questions[question_index]["options"]
        if 0 <= option_index < len(options):
            options.pop(option_index)
    updated["status"] = "edition"
    return updated


def update_option(
    state: Dict[str, Any],
    question_index: int,
    option_index: int,
    value: str,
) -> Dict[str, Any]:
    """Update an option label."""
    updated = deepcopy(state)
    questions = updated["questionnaire"]["questions"]
    if 0 <= question_index < len(questions):
        options = questions[question_index]["options"]
        if 0 <= option_index < len(options):
            options[option_index] = value
    updated["status"] = "edition"
    return updated


def move_question(
    state: Dict[str, Any],
    from_index: int,
    to_index: int,
) -> Dict[str, Any]:
    """Reorder a question from one position to another."""
    updated = deepcopy(state)
    questions = updated["questionnaire"]["questions"]
    if (
        0 <= from_index < len(questions)
        and 0 <= to_index < len(questions)
        and from_index != to_index
    ):
        q = questions.pop(from_index)
        questions.insert(to_index, q)
        for i, question in enumerate(questions):
            question["order"] = i
    updated["status"] = "edition"
    return updated


def validate_ui_state(state: Dict[str, Any]) -> List[str]:
    """Validate the current UI state for submission readiness.

    Returns a list of error messages.  Empty means valid.
    """
    errors: List[str] = []

    if not state.get("selected_age_range"):
        errors.append("Aucune tranche d'age selectionnee")
        return errors

    questionnaire = state.get("questionnaire")
    if not questionnaire:
        errors.append("Aucun questionnaire en cours")
        return errors

    questions = questionnaire.get("questions", [])
    if len(questions) == 0:
        errors.append("Le questionnaire doit contenir au moins une question")
        return errors

    for i, q in enumerate(questions):
        prefix = f"Question {i + 1}"
        if not q.get("label", "").strip():
            errors.append(f"{prefix}: libelle manquant")

        qtype = q.get("type")
        if qtype not in VALID_QUESTION_TYPES:
            errors.append(f"{prefix}: type invalide")
        elif qtype in ("single_choice", "multiple_choice"):
            opts = q.get("options", [])
            if len(opts) < 2:
                errors.append(f"{prefix}: au moins 2 options requises")
            for j, opt in enumerate(opts):
                if not isinstance(opt, str) or not opt.strip():
                    errors.append(f"{prefix}, option {j + 1}: libelle vide")
        elif qtype == "scale":
            sc = q.get("scale_config")
            if not isinstance(sc, dict):
                errors.append(f"{prefix}: configuration echelle manquante")

    return errors


def build_submission_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    """Build the questionnaire payload for the service layer.

    Raises ValueError if validation fails.
    """
    errors = validate_ui_state(state)
    if errors:
        raise ValueError("Validation UI bloquante: " + "; ".join(errors))

    return deepcopy(state["questionnaire"])


def mark_saved(state: Dict[str, Any]) -> Dict[str, Any]:
    """Transition state to 'valide' after successful save."""
    updated = deepcopy(state)
    updated["status"] = "valide"
    updated["errors"] = []
    ar = updated["selected_age_range"]
    if ar:
        updated["age_ranges_status"][ar] = True
    return updated


def mark_error(state: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
    """Transition state to 'erreur' with error messages."""
    updated = deepcopy(state)
    updated["status"] = "erreur"
    updated["errors"] = errors
    return updated
