"""Tests for the questionnaire-catalog service."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_questionnaire(base: Path, age_range: str, data: dict) -> None:
    """Write a questionnaire JSON inside base/config/questionnaires/."""
    qdir = base / "config" / "questionnaires"
    qdir.mkdir(parents=True, exist_ok=True)
    (qdir / f"{age_range}.json").write_text(
        json.dumps(data, ensure_ascii=False), encoding="utf-8"
    )


def _minimal_questionnaire(age_range: str = "18-25", **overrides) -> dict:
    """Return a minimal valid questionnaire."""
    data = {
        "age_range": age_range,
        "version": 1,
        "created_at": "",
        "updated_at": "",
        "questions": [
            {
                "id": "q1",
                "order": 0,
                "type": "boolean",
                "label": "Avez-vous des allergies ?",
                "required": True,
                "options": [],
                "scale_config": None,
            }
        ],
    }
    data.update(overrides)
    return data


def _choice_question(qid: str = "q2", qtype: str = "single_choice") -> dict:
    return {
        "id": qid,
        "order": 1,
        "type": qtype,
        "label": "Niveau activite physique ?",
        "required": True,
        "options": ["Sedentaire", "Modere", "Actif"],
        "scale_config": None,
    }


def _scale_question(qid: str = "q3") -> dict:
    return {
        "id": qid,
        "order": 2,
        "type": "scale",
        "label": "Evaluez votre forme",
        "required": True,
        "options": [],
        "scale_config": {"min": 1, "max": 10, "step": 1},
    }


# ===================================================================
# list_questionnaires
# ===================================================================


class TestListQuestionnaires:
    def test_empty_when_no_directory(self, catalog_service, tmp_path):
        result = catalog_service.list_questionnaires(base=tmp_path)
        assert result == []

    def test_returns_configured_ranges(self, catalog_service, tmp_path):
        _write_questionnaire(tmp_path, "18-25", _minimal_questionnaire("18-25"))
        _write_questionnaire(tmp_path, "70-75", _minimal_questionnaire("70-75"))
        result = catalog_service.list_questionnaires(base=tmp_path)
        assert "18-25" in result
        assert "70-75" in result
        assert len(result) == 2

    def test_preserves_valid_age_range_order(self, catalog_service, tmp_path):
        for ar in ("70-75", "18-25"):
            _write_questionnaire(tmp_path, ar, _minimal_questionnaire(ar))
        result = catalog_service.list_questionnaires(base=tmp_path)
        assert result == ["18-25", "70-75"]

    def test_ignores_invalid_filenames(self, catalog_service, tmp_path):
        _write_questionnaire(tmp_path, "18-25", _minimal_questionnaire("18-25"))
        # Write an extra file with an invalid age range name
        qdir = tmp_path / "config" / "questionnaires"
        (qdir / "99-100.json").write_text("{}", encoding="utf-8")
        result = catalog_service.list_questionnaires(base=tmp_path)
        assert result == ["18-25"]


# ===================================================================
# load_questionnaire
# ===================================================================


class TestLoadQuestionnaire:
    def test_returns_empty_structure_when_missing(self, catalog_service, tmp_path):
        result = catalog_service.load_questionnaire("18-25", base=tmp_path)
        assert result["age_range"] == "18-25"
        assert result["questions"] == []
        assert result["version"] == 1

    def test_loads_existing(self, catalog_service, tmp_path):
        data = _minimal_questionnaire("45-50")
        _write_questionnaire(tmp_path, "45-50", data)
        result = catalog_service.load_questionnaire("45-50", base=tmp_path)
        assert result["age_range"] == "45-50"
        assert len(result["questions"]) == 1
        assert result["questions"][0]["label"] == "Avez-vous des allergies ?"

    def test_invalid_age_range_raises(self, catalog_service, tmp_path):
        with pytest.raises(ValueError, match="invalide"):
            catalog_service.load_questionnaire("99-100", base=tmp_path)


# ===================================================================
# validate_questionnaire
# ===================================================================


class TestValidateQuestionnaire:
    def test_valid_questionnaire_no_errors(self, catalog_service):
        errors = catalog_service.validate_questionnaire(_minimal_questionnaire())
        assert errors == []

    def test_invalid_age_range(self, catalog_service):
        q = _minimal_questionnaire(age_range="99-100")
        errors = catalog_service.validate_questionnaire(q)
        assert any("invalide" in e for e in errors)

    def test_no_questions(self, catalog_service):
        q = _minimal_questionnaire(questions=[])
        errors = catalog_service.validate_questionnaire(q)
        assert any("au moins une question" in e for e in errors)

    def test_question_missing_label(self, catalog_service):
        q = _minimal_questionnaire()
        q["questions"][0]["label"] = ""
        errors = catalog_service.validate_questionnaire(q)
        assert any("libelle manquant" in e for e in errors)

    def test_question_invalid_type(self, catalog_service):
        q = _minimal_questionnaire()
        q["questions"][0]["type"] = "unknown_type"
        errors = catalog_service.validate_questionnaire(q)
        assert any("type invalide" in e for e in errors)

    def test_choice_question_needs_at_least_2_options(self, catalog_service):
        q = _minimal_questionnaire()
        q["questions"] = [_choice_question()]
        q["questions"][0]["options"] = ["Seule option"]
        errors = catalog_service.validate_questionnaire(q)
        assert any("au moins 2 options" in e for e in errors)

    def test_choice_question_empty_option_label(self, catalog_service):
        q = _minimal_questionnaire()
        q["questions"] = [_choice_question()]
        q["questions"][0]["options"] = ["Valide", ""]
        errors = catalog_service.validate_questionnaire(q)
        assert any("libelle vide" in e for e in errors)

    def test_multiple_choice_same_rules(self, catalog_service):
        q = _minimal_questionnaire()
        q["questions"] = [_choice_question(qtype="multiple_choice")]
        q["questions"][0]["options"] = ["Seul"]
        errors = catalog_service.validate_questionnaire(q)
        assert any("au moins 2 options" in e for e in errors)

    def test_scale_question_needs_config(self, catalog_service):
        q = _minimal_questionnaire()
        q["questions"] = [_scale_question()]
        q["questions"][0]["scale_config"] = None
        errors = catalog_service.validate_questionnaire(q)
        assert any("scale_config" in e for e in errors)

    def test_scale_min_gte_max(self, catalog_service):
        q = _minimal_questionnaire()
        sq = _scale_question()
        sq["scale_config"] = {"min": 10, "max": 1, "step": 1}
        q["questions"] = [sq]
        errors = catalog_service.validate_questionnaire(q)
        assert any("inferieur" in e for e in errors)

    def test_scale_step_zero(self, catalog_service):
        q = _minimal_questionnaire()
        sq = _scale_question()
        sq["scale_config"] = {"min": 1, "max": 10, "step": 0}
        q["questions"] = [sq]
        errors = catalog_service.validate_questionnaire(q)
        assert any("step invalide" in e for e in errors)

    def test_scale_step_negative(self, catalog_service):
        q = _minimal_questionnaire()
        sq = _scale_question()
        sq["scale_config"] = {"min": 1, "max": 10, "step": -1}
        q["questions"] = [sq]
        errors = catalog_service.validate_questionnaire(q)
        assert any("step invalide" in e for e in errors)

    def test_valid_with_all_question_types(self, catalog_service):
        q = _minimal_questionnaire()
        q["questions"] = [
            {
                "id": "q1", "order": 0, "type": "boolean",
                "label": "Q1", "required": True,
                "options": [], "scale_config": None,
            },
            {
                "id": "q2", "order": 1, "type": "single_choice",
                "label": "Q2", "required": True,
                "options": ["A", "B"], "scale_config": None,
            },
            {
                "id": "q3", "order": 2, "type": "multiple_choice",
                "label": "Q3", "required": True,
                "options": ["X", "Y", "Z"], "scale_config": None,
            },
            {
                "id": "q4", "order": 3, "type": "short_text",
                "label": "Q4", "required": True,
                "options": [], "scale_config": None,
            },
            {
                "id": "q5", "order": 4, "type": "scale",
                "label": "Q5", "required": True,
                "options": [], "scale_config": {"min": 1, "max": 10, "step": 1},
            },
        ]
        errors = catalog_service.validate_questionnaire(q)
        assert errors == []


# ===================================================================
# save_questionnaire
# ===================================================================


class TestSaveQuestionnaire:
    def test_saves_valid_questionnaire(self, catalog_service, tmp_path):
        catalog_service.save_questionnaire(
            _minimal_questionnaire("18-25"), base=tmp_path
        )
        path = tmp_path / "config" / "questionnaires" / "18-25.json"
        assert path.is_file()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["age_range"] == "18-25"
        assert len(data["questions"]) == 1
        assert data["created_at"] != ""
        assert data["updated_at"] != ""

    def test_creates_directories(self, catalog_service, tmp_path):
        catalog_service.save_questionnaire(
            _minimal_questionnaire(), base=tmp_path
        )
        assert (tmp_path / "config" / "questionnaires").is_dir()

    def test_rejects_invalid_questionnaire(self, catalog_service, tmp_path):
        with pytest.raises(ValueError, match="Validation"):
            catalog_service.save_questionnaire(
                _minimal_questionnaire(questions=[]), base=tmp_path
            )

    def test_preserves_created_at_on_update(self, catalog_service, tmp_path):
        q = _minimal_questionnaire()
        catalog_service.save_questionnaire(q, base=tmp_path)
        path = tmp_path / "config" / "questionnaires" / "18-25.json"
        first = json.loads(path.read_text(encoding="utf-8"))
        original_created = first["created_at"]

        q["questions"][0]["label"] = "Modifie"
        catalog_service.save_questionnaire(q, base=tmp_path)
        second = json.loads(path.read_text(encoding="utf-8"))
        assert second["created_at"] == original_created
        assert second["questions"][0]["label"] == "Modifie"

    def test_overwrites_existing(self, catalog_service, tmp_path):
        catalog_service.save_questionnaire(
            _minimal_questionnaire(), base=tmp_path
        )
        q = _minimal_questionnaire()
        q["questions"].append(_choice_question())
        catalog_service.save_questionnaire(q, base=tmp_path)
        data = json.loads(
            (tmp_path / "config" / "questionnaires" / "18-25.json")
            .read_text(encoding="utf-8")
        )
        assert len(data["questions"]) == 2


# ===================================================================
# delete_questionnaire
# ===================================================================


class TestDeleteQuestionnaire:
    def test_deletes_existing(self, catalog_service, tmp_path):
        _write_questionnaire(tmp_path, "18-25", _minimal_questionnaire())
        result = catalog_service.delete_questionnaire("18-25", base=tmp_path)
        assert result is True
        assert not (tmp_path / "config" / "questionnaires" / "18-25.json").exists()

    def test_returns_false_when_missing(self, catalog_service, tmp_path):
        result = catalog_service.delete_questionnaire("18-25", base=tmp_path)
        assert result is False

    def test_invalid_age_range_raises(self, catalog_service, tmp_path):
        with pytest.raises(ValueError, match="invalide"):
            catalog_service.delete_questionnaire("99-100", base=tmp_path)


# ===================================================================
# new_question
# ===================================================================


class TestNewQuestion:
    def test_generates_unique_id(self, catalog_service):
        existing = [{"id": "q1"}, {"id": "q2"}]
        q = catalog_service.new_question(existing)
        assert q["id"] == "q3"

    def test_first_question_is_q1(self, catalog_service):
        q = catalog_service.new_question([])
        assert q["id"] == "q1"

    def test_default_type_is_boolean(self, catalog_service):
        q = catalog_service.new_question([])
        assert q["type"] == "boolean"
        assert q["options"] == []
        assert q["scale_config"] is None

    def test_scale_type_has_config(self, catalog_service):
        q = catalog_service.new_question([], qtype="scale")
        assert q["scale_config"] == {"min": 1, "max": 10, "step": 1}

    def test_choice_type_has_empty_options(self, catalog_service):
        q = catalog_service.new_question([], qtype="single_choice")
        assert len(q["options"]) == 2

    def test_multiple_choice_has_empty_options(self, catalog_service):
        q = catalog_service.new_question([], qtype="multiple_choice")
        assert len(q["options"]) == 2

    def test_order_matches_list_length(self, catalog_service):
        existing = [{"id": "q1"}]
        q = catalog_service.new_question(existing)
        assert q["order"] == 1

    def test_required_defaults_to_true(self, catalog_service):
        q = catalog_service.new_question([])
        assert q["required"] is True
