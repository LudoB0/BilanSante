"""Tests for the questionnaire_catalog_ui adapter."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _question(qid="q1", order=0, qtype="boolean", label="Test ?"):
    """Return a minimal question dict."""
    q = {
        "id": qid,
        "order": order,
        "type": qtype,
        "label": label,
        "required": True,
        "options": [],
        "scale_config": None,
    }
    if qtype in ("single_choice", "multiple_choice"):
        q["options"] = ["A", "B"]
    if qtype == "scale":
        q["scale_config"] = {"min": 1, "max": 10, "step": 1}
    return q


def _questionnaire(age_range="18-25", questions=None):
    """Return a minimal questionnaire dict."""
    return {
        "age_range": age_range,
        "version": 1,
        "created_at": "",
        "updated_at": "",
        "questions": questions if questions is not None else [_question()],
    }


# ===================================================================
# create_ui_state
# ===================================================================


class TestCreateUiState:
    def test_initial_state(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        assert state["status"] == "initial"
        assert state["selected_age_range"] is None
        assert state["questionnaire"] is None
        assert state["errors"] == []
        assert all(v is False for v in state["age_ranges_status"].values())

    def test_with_configured_ranges(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state(
            configured_ranges=["18-25", "70-75"]
        )
        assert state["age_ranges_status"]["18-25"] is True
        assert state["age_ranges_status"]["70-75"] is True
        assert state["age_ranges_status"]["45-50"] is False
        assert state["age_ranges_status"]["60-65"] is False

    def test_ignores_invalid_ranges(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state(
            configured_ranges=["99-100", "18-25"]
        )
        assert state["age_ranges_status"]["18-25"] is True
        assert "99-100" not in state["age_ranges_status"]

    def test_all_four_age_ranges_present(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        assert set(state["age_ranges_status"].keys()) == {
            "18-25", "45-50", "60-65", "70-75"
        }


# ===================================================================
# select_age_range
# ===================================================================


class TestSelectAgeRange:
    def test_select_with_no_questionnaire(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        updated = catalog_ui_adapter.select_age_range(state, "18-25", None)
        assert updated["selected_age_range"] == "18-25"
        assert updated["status"] == "creation"
        assert updated["questionnaire"] is None

    def test_select_with_existing_questionnaire(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q = _questionnaire()
        updated = catalog_ui_adapter.select_age_range(state, "18-25", q)
        assert updated["status"] == "edition"
        assert updated["questionnaire"] is not None
        assert len(updated["questionnaire"]["questions"]) == 1

    def test_select_with_empty_questionnaire(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q = _questionnaire(questions=[])
        updated = catalog_ui_adapter.select_age_range(state, "18-25", q)
        assert updated["status"] == "creation"

    def test_does_not_mutate_original(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        catalog_ui_adapter.select_age_range(state, "18-25", None)
        assert state["selected_age_range"] is None
        assert state["status"] == "initial"

    def test_clears_errors(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        state = catalog_ui_adapter.mark_error(state, ["Erreur precedente"])
        updated = catalog_ui_adapter.select_age_range(state, "18-25", None)
        assert updated["errors"] == []


# ===================================================================
# add_question
# ===================================================================


class TestAddQuestion:
    def test_adds_question_to_existing(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire()
        )
        new_q = _question("q2", order=1)
        updated = catalog_ui_adapter.add_question(state, new_q)
        assert len(updated["questionnaire"]["questions"]) == 2
        assert updated["status"] == "edition"

    def test_creates_questionnaire_if_none(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        state = catalog_ui_adapter.select_age_range(state, "18-25", None)
        q = _question()
        updated = catalog_ui_adapter.add_question(state, q)
        assert updated["questionnaire"] is not None
        assert updated["questionnaire"]["age_range"] == "18-25"
        assert len(updated["questionnaire"]["questions"]) == 1

    def test_does_not_mutate_original(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire()
        )
        original_count = len(state["questionnaire"]["questions"])
        catalog_ui_adapter.add_question(state, _question("q2"))
        assert len(state["questionnaire"]["questions"]) == original_count


# ===================================================================
# remove_question
# ===================================================================


class TestRemoveQuestion:
    def test_removes_by_index(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q_data = _questionnaire(
            questions=[_question("q1", 0), _question("q2", 1)]
        )
        state = catalog_ui_adapter.select_age_range(state, "18-25", q_data)
        updated = catalog_ui_adapter.remove_question(state, 0)
        assert len(updated["questionnaire"]["questions"]) == 1
        assert updated["questionnaire"]["questions"][0]["id"] == "q2"

    def test_reorders_after_removal(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q_data = _questionnaire(
            questions=[
                _question("q1", 0),
                _question("q2", 1),
                _question("q3", 2),
            ]
        )
        state = catalog_ui_adapter.select_age_range(state, "18-25", q_data)
        updated = catalog_ui_adapter.remove_question(state, 1)
        assert updated["questionnaire"]["questions"][0]["order"] == 0
        assert updated["questionnaire"]["questions"][1]["order"] == 1
        assert updated["questionnaire"]["questions"][1]["id"] == "q3"

    def test_out_of_bounds_does_nothing(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q_data = _questionnaire(questions=[_question()])
        state = catalog_ui_adapter.select_age_range(state, "18-25", q_data)
        updated = catalog_ui_adapter.remove_question(state, 5)
        assert len(updated["questionnaire"]["questions"]) == 1


# ===================================================================
# update_question
# ===================================================================


class TestUpdateQuestion:
    def test_updates_label(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire()
        )
        updated = catalog_ui_adapter.update_question(
            state, 0, "label", "Nouveau libelle"
        )
        assert updated["questionnaire"]["questions"][0]["label"] == "Nouveau libelle"

    def test_type_change_to_choice_initializes_options(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire()
        )
        updated = catalog_ui_adapter.update_question(
            state, 0, "type", "single_choice"
        )
        q = updated["questionnaire"]["questions"][0]
        assert q["type"] == "single_choice"
        assert len(q["options"]) == 2
        assert q["scale_config"] is None

    def test_type_change_to_scale_initializes_config(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire()
        )
        updated = catalog_ui_adapter.update_question(
            state, 0, "type", "scale"
        )
        q = updated["questionnaire"]["questions"][0]
        assert q["scale_config"] == {"min": 1, "max": 10, "step": 1}
        assert q["options"] == []

    def test_type_change_to_boolean_clears_options_and_scale(
        self, catalog_ui_adapter
    ):
        state = catalog_ui_adapter.create_ui_state()
        q_data = _questionnaire(
            questions=[_question("q1", 0, "single_choice", "Q")]
        )
        state = catalog_ui_adapter.select_age_range(state, "18-25", q_data)
        updated = catalog_ui_adapter.update_question(
            state, 0, "type", "boolean"
        )
        q = updated["questionnaire"]["questions"][0]
        assert q["options"] == []
        assert q["scale_config"] is None

    def test_type_change_to_short_text_clears(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q_data = _questionnaire(
            questions=[_question("q1", 0, "scale", "Q")]
        )
        state = catalog_ui_adapter.select_age_range(state, "18-25", q_data)
        updated = catalog_ui_adapter.update_question(
            state, 0, "type", "short_text"
        )
        q = updated["questionnaire"]["questions"][0]
        assert q["options"] == []
        assert q["scale_config"] is None

    def test_does_not_mutate_original(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire()
        )
        original_label = state["questionnaire"]["questions"][0]["label"]
        catalog_ui_adapter.update_question(state, 0, "label", "Changed")
        assert state["questionnaire"]["questions"][0]["label"] == original_label

    def test_out_of_bounds_does_nothing(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire()
        )
        updated = catalog_ui_adapter.update_question(
            state, 99, "label", "Nothing"
        )
        assert updated["questionnaire"]["questions"][0]["label"] == "Test ?"


# ===================================================================
# add_option / remove_option / update_option
# ===================================================================


class TestOptionManagement:
    def test_add_option(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q_data = _questionnaire(
            questions=[_question("q1", 0, "single_choice", "Q")]
        )
        state = catalog_ui_adapter.select_age_range(state, "18-25", q_data)
        updated = catalog_ui_adapter.add_option(state, 0)
        assert len(updated["questionnaire"]["questions"][0]["options"]) == 3
        assert updated["questionnaire"]["questions"][0]["options"][-1] == ""

    def test_remove_option(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q_data = _questionnaire(
            questions=[_question("q1", 0, "single_choice", "Q")]
        )
        # Options are ["A", "B"] from helper
        state = catalog_ui_adapter.select_age_range(state, "18-25", q_data)
        state = catalog_ui_adapter.add_option(state, 0)
        # Now ["A", "B", ""]
        updated = catalog_ui_adapter.remove_option(state, 0, 1)
        assert updated["questionnaire"]["questions"][0]["options"] == ["A", ""]

    def test_update_option(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q_data = _questionnaire(
            questions=[_question("q1", 0, "single_choice", "Q")]
        )
        state = catalog_ui_adapter.select_age_range(state, "18-25", q_data)
        updated = catalog_ui_adapter.update_option(state, 0, 1, "Modifie")
        assert (
            updated["questionnaire"]["questions"][0]["options"][1] == "Modifie"
        )

    def test_remove_option_out_of_bounds(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q_data = _questionnaire(
            questions=[_question("q1", 0, "single_choice", "Q")]
        )
        state = catalog_ui_adapter.select_age_range(state, "18-25", q_data)
        updated = catalog_ui_adapter.remove_option(state, 0, 99)
        assert len(updated["questionnaire"]["questions"][0]["options"]) == 2


# ===================================================================
# move_question
# ===================================================================


class TestMoveQuestion:
    def test_move_down(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q_data = _questionnaire(
            questions=[
                _question("q1", 0, label="First"),
                _question("q2", 1, label="Second"),
            ]
        )
        state = catalog_ui_adapter.select_age_range(state, "18-25", q_data)
        updated = catalog_ui_adapter.move_question(state, 0, 1)
        qs = updated["questionnaire"]["questions"]
        assert qs[0]["id"] == "q2"
        assert qs[1]["id"] == "q1"
        assert qs[0]["order"] == 0
        assert qs[1]["order"] == 1

    def test_move_up(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q_data = _questionnaire(
            questions=[
                _question("q1", 0),
                _question("q2", 1),
                _question("q3", 2),
            ]
        )
        state = catalog_ui_adapter.select_age_range(state, "18-25", q_data)
        updated = catalog_ui_adapter.move_question(state, 2, 0)
        qs = updated["questionnaire"]["questions"]
        assert qs[0]["id"] == "q3"
        assert qs[1]["id"] == "q1"
        assert qs[2]["id"] == "q2"

    def test_same_index_does_nothing(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q_data = _questionnaire(
            questions=[_question("q1", 0), _question("q2", 1)]
        )
        state = catalog_ui_adapter.select_age_range(state, "18-25", q_data)
        updated = catalog_ui_adapter.move_question(state, 0, 0)
        assert updated["questionnaire"]["questions"][0]["id"] == "q1"

    def test_out_of_bounds_does_nothing(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q_data = _questionnaire(questions=[_question()])
        state = catalog_ui_adapter.select_age_range(state, "18-25", q_data)
        updated = catalog_ui_adapter.move_question(state, 0, 5)
        assert len(updated["questionnaire"]["questions"]) == 1


# ===================================================================
# validate_ui_state
# ===================================================================


class TestValidateUiState:
    def test_no_age_range_selected(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        errors = catalog_ui_adapter.validate_ui_state(state)
        assert any("tranche" in e.lower() for e in errors)

    def test_no_questionnaire(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        state = catalog_ui_adapter.select_age_range(state, "18-25", None)
        errors = catalog_ui_adapter.validate_ui_state(state)
        assert any("questionnaire" in e.lower() for e in errors)

    def test_no_questions(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire(questions=[])
        )
        errors = catalog_ui_adapter.validate_ui_state(state)
        assert any("au moins une question" in e for e in errors)

    def test_question_missing_label(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q = _question(label="")
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire(questions=[q])
        )
        errors = catalog_ui_adapter.validate_ui_state(state)
        assert any("libelle manquant" in e for e in errors)

    def test_question_invalid_type(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q = _question()
        q["type"] = "invalid"
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire(questions=[q])
        )
        errors = catalog_ui_adapter.validate_ui_state(state)
        assert any("type invalide" in e for e in errors)

    def test_choice_too_few_options(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q = _question(qtype="single_choice")
        q["options"] = ["Seul"]
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire(questions=[q])
        )
        errors = catalog_ui_adapter.validate_ui_state(state)
        assert any("au moins 2 options" in e for e in errors)

    def test_choice_empty_option(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q = _question(qtype="single_choice")
        q["options"] = ["Valide", ""]
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire(questions=[q])
        )
        errors = catalog_ui_adapter.validate_ui_state(state)
        assert any("libelle vide" in e for e in errors)

    def test_scale_missing_config(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q = _question(qtype="scale")
        q["scale_config"] = None
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire(questions=[q])
        )
        errors = catalog_ui_adapter.validate_ui_state(state)
        assert any("echelle" in e.lower() for e in errors)

    def test_valid_state_no_errors(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire()
        )
        errors = catalog_ui_adapter.validate_ui_state(state)
        assert errors == []

    def test_valid_all_types(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        questions = [
            _question("q1", 0, "boolean", "Q1"),
            _question("q2", 1, "single_choice", "Q2"),
            _question("q3", 2, "multiple_choice", "Q3"),
            _question("q4", 3, "short_text", "Q4"),
            _question("q5", 4, "scale", "Q5"),
        ]
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire(questions=questions)
        )
        errors = catalog_ui_adapter.validate_ui_state(state)
        assert errors == []

    def test_invalid_sex_target(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q = _question()
        q["sex_target"] = "X"
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire(questions=[q])
        )
        errors = catalog_ui_adapter.validate_ui_state(state)
        assert any("sex_target invalide" in e for e in errors)

    def test_valid_sex_target(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q = _question()
        q["sex_target"] = "F"
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire(questions=[q])
        )
        errors = catalog_ui_adapter.validate_ui_state(state)
        assert errors == []

    def test_missing_sex_target_is_ok(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        q = _question()
        q.pop("sex_target", None)
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire(questions=[q])
        )
        errors = catalog_ui_adapter.validate_ui_state(state)
        assert errors == []


# ===================================================================
# build_submission_payload
# ===================================================================


class TestBuildSubmissionPayload:
    def test_builds_from_valid_state(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire()
        )
        payload = catalog_ui_adapter.build_submission_payload(state)
        assert payload["age_range"] == "18-25"
        assert len(payload["questions"]) == 1

    def test_raises_on_invalid_state(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        with pytest.raises(ValueError, match="Validation"):
            catalog_ui_adapter.build_submission_payload(state)

    def test_payload_is_deep_copy(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        state = catalog_ui_adapter.select_age_range(
            state, "18-25", _questionnaire()
        )
        payload = catalog_ui_adapter.build_submission_payload(state)
        payload["questions"][0]["label"] = "Modified"
        assert (
            state["questionnaire"]["questions"][0]["label"] != "Modified"
        )


# ===================================================================
# mark_saved / mark_error
# ===================================================================


class TestMarkSaved:
    def test_transitions_to_valide(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        state["selected_age_range"] = "18-25"
        state["status"] = "edition"
        updated = catalog_ui_adapter.mark_saved(state)
        assert updated["status"] == "valide"
        assert updated["errors"] == []
        assert updated["age_ranges_status"]["18-25"] is True

    def test_does_not_mutate_original(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        state["selected_age_range"] = "18-25"
        catalog_ui_adapter.mark_saved(state)
        assert state["age_ranges_status"]["18-25"] is False


class TestMarkError:
    def test_transitions_to_erreur(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        updated = catalog_ui_adapter.mark_error(state, ["Erreur 1", "Erreur 2"])
        assert updated["status"] == "erreur"
        assert "Erreur 1" in updated["errors"]
        assert "Erreur 2" in updated["errors"]

    def test_does_not_mutate_original(self, catalog_ui_adapter):
        state = catalog_ui_adapter.create_ui_state()
        catalog_ui_adapter.mark_error(state, ["Erreur"])
        assert state["status"] == "initial"
        assert state["errors"] == []
