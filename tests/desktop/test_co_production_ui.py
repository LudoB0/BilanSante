"""Tests for co_production_ui adapter (IdentifyVigilancePoints)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_VIGILANCE_RESULT = {
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "short_id": "a1b2c3d4",
    "vigilance_text": "Point 1: Tension arterielle elevee\nPoint 2: IMC surpoids",
    "vigilance_md_path": "/tmp/data/sessions/Vigilance_a1b2c3d4.md",
}


# ---------------------------------------------------------------------------
# Tests: create_co_production_state
# ---------------------------------------------------------------------------


class TestCreateCoProductionState:
    def test_initial_status(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        assert state["status"] == "initial"

    def test_initial_session_id(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        assert state["session_id"] is None

    def test_initial_short_id(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        assert state["short_id"] is None

    def test_initial_md_path(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        assert state["md_path"] is None

    def test_initial_vigilance_text(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        assert state["vigilance_text"] is None

    def test_initial_vigilance_md_path(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        assert state["vigilance_md_path"] is None

    def test_initial_action_points(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        assert state["action_points"] == ["", "", ""]

    def test_initial_errors(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        assert state["errors"] == []


# ---------------------------------------------------------------------------
# Tests: mark_loading
# ---------------------------------------------------------------------------


class TestMarkLoading:
    def test_status_changes(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.mark_loading(state)
        assert new["status"] == "loading"

    def test_immutability(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.mark_loading(state)
        assert state["status"] == "initial"
        assert new is not state


# ---------------------------------------------------------------------------
# Tests: load_vigilance_result
# ---------------------------------------------------------------------------


class TestLoadVigilanceResult:
    def test_status_vigilance_ready(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.load_vigilance_result(
            state, SAMPLE_VIGILANCE_RESULT
        )
        assert new["status"] == "vigilance_ready"

    def test_session_id(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.load_vigilance_result(
            state, SAMPLE_VIGILANCE_RESULT
        )
        assert new["session_id"] == SAMPLE_VIGILANCE_RESULT["session_id"]

    def test_short_id(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.load_vigilance_result(
            state, SAMPLE_VIGILANCE_RESULT
        )
        assert new["short_id"] == "a1b2c3d4"

    def test_vigilance_text(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.load_vigilance_result(
            state, SAMPLE_VIGILANCE_RESULT
        )
        assert "Tension arterielle" in new["vigilance_text"]

    def test_vigilance_md_path(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.load_vigilance_result(
            state, SAMPLE_VIGILANCE_RESULT
        )
        assert new["vigilance_md_path"] == SAMPLE_VIGILANCE_RESULT["vigilance_md_path"]

    def test_errors_cleared(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        err = co_production_ui_adapter.mark_vigilance_error(state, ["prev error"])
        new = co_production_ui_adapter.load_vigilance_result(
            err, SAMPLE_VIGILANCE_RESULT
        )
        assert new["errors"] == []

    def test_immutability(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.load_vigilance_result(
            state, SAMPLE_VIGILANCE_RESULT
        )
        assert state["status"] == "initial"
        assert state["session_id"] is None
        assert new is not state


# ---------------------------------------------------------------------------
# Tests: mark_vigilance_error
# ---------------------------------------------------------------------------


class TestMarkVigilanceError:
    def test_status_erreur(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.mark_vigilance_error(state, ["err1", "err2"])
        assert new["status"] == "erreur"

    def test_errors_stored(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.mark_vigilance_error(state, ["network error"])
        assert new["errors"] == ["network error"]

    def test_immutability(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.mark_vigilance_error(state, ["err"])
        assert state["status"] == "initial"
        assert state["errors"] == []
        assert new is not state


# ---------------------------------------------------------------------------
# Tests: update_action_point
# ---------------------------------------------------------------------------


class TestUpdateActionPoint:
    def test_set_point_0(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.update_action_point(state, 0, "Action 1")
        assert new["action_points"][0] == "Action 1"

    def test_set_point_1(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.update_action_point(state, 1, "Action 2")
        assert new["action_points"][1] == "Action 2"

    def test_set_point_2(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.update_action_point(state, 2, "Action 3")
        assert new["action_points"][2] == "Action 3"

    def test_invalid_index_raises(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        with pytest.raises(ValueError, match="Index invalide"):
            co_production_ui_adapter.update_action_point(state, 3, "Nope")

    def test_negative_index_raises(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        with pytest.raises(ValueError, match="Index invalide"):
            co_production_ui_adapter.update_action_point(state, -1, "Nope")

    def test_overwrite_point(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        s1 = co_production_ui_adapter.update_action_point(state, 0, "Old")
        s2 = co_production_ui_adapter.update_action_point(s1, 0, "New")
        assert s2["action_points"][0] == "New"

    def test_immutability(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.update_action_point(state, 0, "Action")
        assert state["action_points"] == ["", "", ""]
        assert new is not state


# ---------------------------------------------------------------------------
# Tests: mark_saving
# ---------------------------------------------------------------------------


class TestMarkSaving:
    def test_status_saving(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.mark_saving(state)
        assert new["status"] == "saving"

    def test_immutability(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.mark_saving(state)
        assert state["status"] == "initial"
        assert new is not state


# ---------------------------------------------------------------------------
# Tests: mark_saved
# ---------------------------------------------------------------------------


class TestMarkSaved:
    def test_status_saved(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.mark_saved(state)
        assert new["status"] == "saved"

    def test_errors_cleared(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        err = co_production_ui_adapter.mark_save_error(state, ["save err"])
        new = co_production_ui_adapter.mark_saved(err)
        assert new["errors"] == []

    def test_immutability(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.mark_saved(state)
        assert state["status"] == "initial"
        assert new is not state


# ---------------------------------------------------------------------------
# Tests: mark_save_error
# ---------------------------------------------------------------------------


class TestMarkSaveError:
    def test_status_erreur(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.mark_save_error(state, ["disk full"])
        assert new["status"] == "erreur"

    def test_errors_stored(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.mark_save_error(state, ["err1", "err2"])
        assert new["errors"] == ["err1", "err2"]

    def test_immutability(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        new = co_production_ui_adapter.mark_save_error(state, ["err"])
        assert state["status"] == "initial"
        assert state["errors"] == []
        assert new is not state


# ---------------------------------------------------------------------------
# Tests: get_action_points
# ---------------------------------------------------------------------------


class TestGetActionPoints:
    def test_returns_three_empty_initially(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        points = co_production_ui_adapter.get_action_points(state)
        assert points == ["", "", ""]

    def test_returns_updated_points(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        s1 = co_production_ui_adapter.update_action_point(state, 0, "A")
        s2 = co_production_ui_adapter.update_action_point(s1, 1, "B")
        s3 = co_production_ui_adapter.update_action_point(s2, 2, "C")
        points = co_production_ui_adapter.get_action_points(s3)
        assert points == ["A", "B", "C"]

    def test_returns_copy(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        points = co_production_ui_adapter.get_action_points(state)
        assert points is not state["action_points"]


# ---------------------------------------------------------------------------
# Tests: is_vigilance_ready
# ---------------------------------------------------------------------------


class TestIsVigilanceReady:
    def test_initial_not_ready(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        assert co_production_ui_adapter.is_vigilance_ready(state) is False

    def test_loading_not_ready(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        loading = co_production_ui_adapter.mark_loading(state)
        assert co_production_ui_adapter.is_vigilance_ready(loading) is False

    def test_ready_after_load(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        loaded = co_production_ui_adapter.load_vigilance_result(
            state, SAMPLE_VIGILANCE_RESULT
        )
        assert co_production_ui_adapter.is_vigilance_ready(loaded) is True

    def test_erreur_not_ready(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        err = co_production_ui_adapter.mark_vigilance_error(state, ["err"])
        assert co_production_ui_adapter.is_vigilance_ready(err) is False

    def test_saved_not_ready(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        saved = co_production_ui_adapter.mark_saved(state)
        assert co_production_ui_adapter.is_vigilance_ready(saved) is False


# ---------------------------------------------------------------------------
# Tests: can_validate
# ---------------------------------------------------------------------------


class TestCanValidate:
    def test_initial_cannot_validate(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        assert co_production_ui_adapter.can_validate(state) is False

    def test_loading_cannot_validate(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        loading = co_production_ui_adapter.mark_loading(state)
        assert co_production_ui_adapter.can_validate(loading) is False

    def test_vigilance_ready_empty_points_cannot_validate(
        self, co_production_ui_adapter
    ):
        state = co_production_ui_adapter.create_co_production_state()
        loaded = co_production_ui_adapter.load_vigilance_result(
            state, SAMPLE_VIGILANCE_RESULT
        )
        assert co_production_ui_adapter.can_validate(loaded) is False

    def test_vigilance_ready_partial_points_cannot_validate(
        self, co_production_ui_adapter
    ):
        state = co_production_ui_adapter.create_co_production_state()
        loaded = co_production_ui_adapter.load_vigilance_result(
            state, SAMPLE_VIGILANCE_RESULT
        )
        s1 = co_production_ui_adapter.update_action_point(loaded, 0, "A")
        s2 = co_production_ui_adapter.update_action_point(s1, 1, "B")
        assert co_production_ui_adapter.can_validate(s2) is False

    def test_vigilance_ready_all_points_can_validate(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        loaded = co_production_ui_adapter.load_vigilance_result(
            state, SAMPLE_VIGILANCE_RESULT
        )
        s1 = co_production_ui_adapter.update_action_point(loaded, 0, "A")
        s2 = co_production_ui_adapter.update_action_point(s1, 1, "B")
        s3 = co_production_ui_adapter.update_action_point(s2, 2, "C")
        assert co_production_ui_adapter.can_validate(s3) is True

    def test_whitespace_only_point_cannot_validate(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        loaded = co_production_ui_adapter.load_vigilance_result(
            state, SAMPLE_VIGILANCE_RESULT
        )
        s1 = co_production_ui_adapter.update_action_point(loaded, 0, "A")
        s2 = co_production_ui_adapter.update_action_point(s1, 1, "B")
        s3 = co_production_ui_adapter.update_action_point(s2, 2, "   ")
        assert co_production_ui_adapter.can_validate(s3) is False

    def test_saved_status_cannot_validate(self, co_production_ui_adapter):
        state = co_production_ui_adapter.create_co_production_state()
        saved = co_production_ui_adapter.mark_saved(state)
        assert co_production_ui_adapter.can_validate(saved) is False


# ---------------------------------------------------------------------------
# Tests: full workflow
# ---------------------------------------------------------------------------


class TestFullWorkflow:
    def test_happy_path(self, co_production_ui_adapter):
        """Test the complete state flow: initial → loading → ready → saving → saved."""
        ui = co_production_ui_adapter

        state = ui.create_co_production_state()
        assert state["status"] == "initial"

        state = ui.mark_loading(state)
        assert state["status"] == "loading"

        state = ui.load_vigilance_result(state, SAMPLE_VIGILANCE_RESULT)
        assert state["status"] == "vigilance_ready"
        assert ui.is_vigilance_ready(state) is True
        assert ui.can_validate(state) is False

        state = ui.update_action_point(state, 0, "Surveiller tension")
        state = ui.update_action_point(state, 1, "Adapter alimentation")
        state = ui.update_action_point(state, 2, "Activite physique")
        assert ui.can_validate(state) is True

        points = ui.get_action_points(state)
        assert points == [
            "Surveiller tension",
            "Adapter alimentation",
            "Activite physique",
        ]

        state = ui.mark_saving(state)
        assert state["status"] == "saving"

        state = ui.mark_saved(state)
        assert state["status"] == "saved"
        assert state["errors"] == []

    def test_error_recovery(self, co_production_ui_adapter):
        """Test error state and transition to success."""
        ui = co_production_ui_adapter

        state = ui.create_co_production_state()
        state = ui.mark_loading(state)
        state = ui.mark_vigilance_error(state, ["API timeout"])
        assert state["status"] == "erreur"
        assert state["errors"] == ["API timeout"]
        assert ui.is_vigilance_ready(state) is False
