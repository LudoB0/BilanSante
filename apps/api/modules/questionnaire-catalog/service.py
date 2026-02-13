"""Questionnaire-catalog service.

Business logic for creating, loading, validating and persisting
questionnaires by age range.  Persists data to
config/questionnaires/<age_range>.json.
"""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[4]

CONFIG_DIR = "config"
QUESTIONNAIRES_SUBDIR = "questionnaires"

VALID_AGE_RANGES: tuple[str, ...] = ("18-25", "45-50", "60-65", "70-75")

VALID_QUESTION_TYPES: tuple[str, ...] = (
    "boolean",
    "single_choice",
    "multiple_choice",
    "short_text",
    "scale",
)

VALID_SEX_TARGETS: tuple[str, ...] = ("H", "F", "M")

DEFAULT_SCALE_CONFIG: Dict[str, int] = {"min": 1, "max": 10, "step": 1}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_base(base: Path | None) -> Path:
    return base if base is not None else PROJECT_ROOT


def _questionnaires_dir(base: Path) -> Path:
    return base / CONFIG_DIR / QUESTIONNAIRES_SUBDIR


def _questionnaire_path(age_range: str, base: Path) -> Path:
    return _questionnaires_dir(base) / f"{age_range}.json"


def _generate_question_id(questions: List[Dict[str, Any]]) -> str:
    """Generate the next question id based on existing questions."""
    max_num = 0
    for q in questions:
        qid = q.get("id", "")
        if qid.startswith("q") and qid[1:].isdigit():
            max_num = max(max_num, int(qid[1:]))
    return f"q{max_num + 1}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def list_questionnaires(base: Path | None = None) -> List[str]:
    """Return age ranges that have a saved questionnaire."""
    base = _resolve_base(base)
    qdir = _questionnaires_dir(base)
    if not qdir.is_dir():
        return []
    result = []
    for age_range in VALID_AGE_RANGES:
        path = qdir / f"{age_range}.json"
        if path.is_file():
            result.append(age_range)
    return result


def load_questionnaire(
    age_range: str, base: Path | None = None
) -> Dict[str, Any]:
    """Load a questionnaire for the given age range.

    Returns an empty questionnaire structure if no file exists.
    Raises ValueError if age_range is not in VALID_AGE_RANGES.
    """
    if age_range not in VALID_AGE_RANGES:
        raise ValueError(f"Tranche d'age invalide: {age_range}")

    base = _resolve_base(base)
    path = _questionnaire_path(age_range, base)

    if path.is_file():
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    return {
        "age_range": age_range,
        "version": 1,
        "created_at": "",
        "updated_at": "",
        "questions": [],
    }


def validate_questionnaire(questionnaire: Dict[str, Any]) -> List[str]:
    """Validate a questionnaire payload (pure, no disk I/O).

    Returns a list of error messages.  An empty list means valid.
    """
    errors: List[str] = []

    age_range = questionnaire.get("age_range")
    if age_range not in VALID_AGE_RANGES:
        errors.append(f"Tranche d'age invalide ou manquante: {age_range}")

    questions = questionnaire.get("questions")
    if not isinstance(questions, list) or len(questions) == 0:
        errors.append("Le questionnaire doit contenir au moins une question")
        return errors

    for i, q in enumerate(questions):
        prefix = f"Question {i + 1}"

        label = q.get("label")
        if not isinstance(label, str) or label.strip() == "":
            errors.append(f"{prefix}: libelle manquant")

        sex_target = q.get("sex_target")
        if sex_target is not None and sex_target not in VALID_SEX_TARGETS:
            errors.append(f"{prefix}: sex_target invalide ({sex_target})")

        qtype = q.get("type")
        if qtype not in VALID_QUESTION_TYPES:
            errors.append(f"{prefix}: type invalide ({qtype})")
        else:
            if qtype in ("single_choice", "multiple_choice"):
                options = q.get("options", [])
                if not isinstance(options, list) or len(options) < 2:
                    errors.append(
                        f"{prefix}: les questions de type {qtype} "
                        f"necessitent au moins 2 options"
                    )
                else:
                    for j, opt in enumerate(options):
                        if not isinstance(opt, str) or opt.strip() == "":
                            errors.append(
                                f"{prefix}, option {j + 1}: libelle vide"
                            )

            if qtype == "scale":
                sc = q.get("scale_config")
                if not isinstance(sc, dict):
                    errors.append(f"{prefix}: scale_config manquant")
                else:
                    sc_min = sc.get("min")
                    sc_max = sc.get("max")
                    sc_step = sc.get("step")
                    if not isinstance(sc_min, (int, float)):
                        errors.append(f"{prefix}: scale_config.min invalide")
                    if not isinstance(sc_max, (int, float)):
                        errors.append(f"{prefix}: scale_config.max invalide")
                    if not isinstance(sc_step, (int, float)) or sc_step <= 0:
                        errors.append(f"{prefix}: scale_config.step invalide")
                    if (
                        isinstance(sc_min, (int, float))
                        and isinstance(sc_max, (int, float))
                        and sc_min >= sc_max
                    ):
                        errors.append(
                            f"{prefix}: scale_config.min doit etre inferieur a max"
                        )

    return errors


def save_questionnaire(
    questionnaire: Dict[str, Any], base: Path | None = None
) -> None:
    """Validate and persist a questionnaire to disk.

    Raises ValueError when validation fails.
    """
    errors = validate_questionnaire(questionnaire)
    if errors:
        raise ValueError("Validation echouee: " + "; ".join(errors))

    base = _resolve_base(base)
    age_range = questionnaire["age_range"]

    qdir = _questionnaires_dir(base)
    qdir.mkdir(parents=True, exist_ok=True)

    now = datetime.now().isoformat(timespec="seconds")
    data = deepcopy(questionnaire)
    path = _questionnaire_path(age_range, base)

    if path.is_file():
        existing = json.loads(path.read_text(encoding="utf-8"))
        data["created_at"] = existing.get("created_at", now)
    else:
        data["created_at"] = now
    data["updated_at"] = now

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def delete_questionnaire(
    age_range: str, base: Path | None = None
) -> bool:
    """Remove the questionnaire for a given age range.

    Returns True if deleted, False if no file existed.
    Raises ValueError if age_range is invalid.
    """
    if age_range not in VALID_AGE_RANGES:
        raise ValueError(f"Tranche d'age invalide: {age_range}")

    base = _resolve_base(base)
    path = _questionnaire_path(age_range, base)

    if path.is_file():
        path.unlink()
        return True
    return False


def new_question(
    questions: List[Dict[str, Any]],
    qtype: str = "boolean",
) -> Dict[str, Any]:
    """Create a new empty question dict with a unique id."""
    qid = _generate_question_id(questions)
    order = len(questions)
    question: Dict[str, Any] = {
        "id": qid,
        "order": order,
        "type": qtype,
        "label": "",
        "required": True,
        "sex_target": "M",
        "options": [],
        "scale_config": None,
    }
    if qtype == "scale":
        question["scale_config"] = dict(DEFAULT_SCALE_CONFIG)
    if qtype in ("single_choice", "multiple_choice"):
        question["options"] = ["", ""]
    return question
