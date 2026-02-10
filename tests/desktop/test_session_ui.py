"""Tests for the session_ui adapter module."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _pharmacy_context(**overrides) -> dict:
    """Return a valid pharmacy context dict."""
    ctx = {
        "nom_pharmacie": "Pharmacie Test",
        "adresse": "1 rue de Test",
        "code_postal": "75001",
        "ville": "Paris",
        "site_web": "",
        "instagram": "",
        "facebook": "",
        "x": "",
        "linkedin": "",
        "logo_path": "/fake/logo.png",
    }
    ctx.update(overrides)
    return ctx


def _loaded_state(ui, **overrides):
    """Return a state that has been through load_context (status=ready)."""
    state = ui.create_ui_state()
    ctx = overrides.pop("pharmacy_context", _pharmacy_context())
    ranges = overrides.pop("available_age_ranges", ["18-25", "45-50"])
    errors = overrides.pop("precondition_errors", [])
    return ui.load_context(state, ctx, ranges, errors)


def _ready_with_selection(ui, age_range="45-50"):
    """Return a ready state with an age range selected."""
    state = _loaded_state(ui)
    return ui.select_age_range(state, age_range)


def _session_data():
    """Return a fake session dict."""
    return {
        "session_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "age_range": "45-50",
        "created_at": "2026-02-10T10:00:00",
        "status": "active",
        "metadata": {
            "pharmacie": {
                "nom_pharmacie": "Pharmacie Test",
                "adresse": "1 rue de Test",
                "code_postal": "75001",
                "ville": "Paris",
            }
        },
    }


# ---------------------------------------------------------------------------
# TestCreateUiState
# ---------------------------------------------------------------------------


class TestCreateUiState:
    def test_status_is_initial(self, session_ui_adapter):
        state = session_ui_adapter.create_ui_state()
        assert state["status"] == "initial"

    def test_pharmacy_context_is_empty(self, session_ui_adapter):
        state = session_ui_adapter.create_ui_state()
        assert state["pharmacy_context"]["nom_pharmacie"] == ""
        assert state["pharmacy_context"]["logo_path"] == ""

    def test_available_age_ranges_is_empty(self, session_ui_adapter):
        state = session_ui_adapter.create_ui_state()
        assert state["available_age_ranges"] == []

    def test_selected_age_range_is_none(self, session_ui_adapter):
        state = session_ui_adapter.create_ui_state()
        assert state["selected_age_range"] is None

    def test_session_is_none(self, session_ui_adapter):
        state = session_ui_adapter.create_ui_state()
        assert state["session"] is None

    def test_errors_is_empty(self, session_ui_adapter):
        state = session_ui_adapter.create_ui_state()
        assert state["errors"] == []

    def test_precondition_errors_is_empty(self, session_ui_adapter):
        state = session_ui_adapter.create_ui_state()
        assert state["precondition_errors"] == []


# ---------------------------------------------------------------------------
# TestLoadContext
# ---------------------------------------------------------------------------


class TestLoadContext:
    def test_loads_pharmacy_context(self, session_ui_adapter):
        state = _loaded_state(session_ui_adapter)
        assert state["pharmacy_context"]["nom_pharmacie"] == "Pharmacie Test"

    def test_loads_available_age_ranges(self, session_ui_adapter):
        state = _loaded_state(session_ui_adapter)
        assert state["available_age_ranges"] == ["18-25", "45-50"]

    def test_status_ready_when_no_errors(self, session_ui_adapter):
        state = _loaded_state(session_ui_adapter)
        assert state["status"] == "ready"

    def test_status_erreur_when_precondition_errors(self, session_ui_adapter):
        state = _loaded_state(
            session_ui_adapter,
            precondition_errors=["Logo manquant"],
        )
        assert state["status"] == "erreur"

    def test_stores_precondition_errors(self, session_ui_adapter):
        state = _loaded_state(
            session_ui_adapter,
            precondition_errors=["Logo manquant"],
        )
        assert state["precondition_errors"] == ["Logo manquant"]
        assert state["errors"] == ["Logo manquant"]

    def test_does_not_mutate_original(self, session_ui_adapter):
        original = session_ui_adapter.create_ui_state()
        _loaded_state(session_ui_adapter)
        assert original["status"] == "initial"
        assert original["available_age_ranges"] == []


# ---------------------------------------------------------------------------
# TestSelectAgeRange
# ---------------------------------------------------------------------------


class TestSelectAgeRange:
    def test_sets_selected_age_range(self, session_ui_adapter):
        state = _loaded_state(session_ui_adapter)
        updated = session_ui_adapter.select_age_range(state, "45-50")
        assert updated["selected_age_range"] == "45-50"

    def test_status_remains_ready(self, session_ui_adapter):
        state = _loaded_state(session_ui_adapter)
        updated = session_ui_adapter.select_age_range(state, "45-50")
        assert updated["status"] == "ready"

    def test_clears_errors(self, session_ui_adapter):
        state = _loaded_state(session_ui_adapter)
        state_with_err = session_ui_adapter.mark_error(
            state, ["Some error"]
        )
        # Reset to ready manually for this test
        state_with_err["status"] = "ready"
        updated = session_ui_adapter.select_age_range(
            state_with_err, "45-50"
        )
        assert updated["errors"] == []

    def test_does_not_mutate_original(self, session_ui_adapter):
        state = _loaded_state(session_ui_adapter)
        session_ui_adapter.select_age_range(state, "45-50")
        assert state["selected_age_range"] is None


# ---------------------------------------------------------------------------
# TestDeselectAgeRange
# ---------------------------------------------------------------------------


class TestDeselectAgeRange:
    def test_clears_selection(self, session_ui_adapter):
        state = _ready_with_selection(session_ui_adapter, "45-50")
        updated = session_ui_adapter.deselect_age_range(state)
        assert updated["selected_age_range"] is None

    def test_status_remains_ready(self, session_ui_adapter):
        state = _ready_with_selection(session_ui_adapter, "45-50")
        updated = session_ui_adapter.deselect_age_range(state)
        assert updated["status"] == "ready"


# ---------------------------------------------------------------------------
# TestValidateUiState
# ---------------------------------------------------------------------------


class TestValidateUiState:
    def test_no_errors_when_valid(self, session_ui_adapter):
        state = _ready_with_selection(session_ui_adapter)
        errors = session_ui_adapter.validate_ui_state(state)
        assert errors == []

    def test_error_when_no_age_range_selected(self, session_ui_adapter):
        state = _loaded_state(session_ui_adapter)
        errors = session_ui_adapter.validate_ui_state(state)
        assert any("tranche" in e.lower() for e in errors)

    def test_error_when_preconditions_failed(self, session_ui_adapter):
        state = _loaded_state(
            session_ui_adapter,
            precondition_errors=["Logo manquant"],
        )
        errors = session_ui_adapter.validate_ui_state(state)
        assert "Logo manquant" in errors

    def test_error_when_age_range_not_in_available(self, session_ui_adapter):
        state = _loaded_state(session_ui_adapter)
        state = session_ui_adapter.select_age_range(state, "70-75")
        errors = session_ui_adapter.validate_ui_state(state)
        assert any("disponible" in e.lower() for e in errors)


# ---------------------------------------------------------------------------
# TestCanStart
# ---------------------------------------------------------------------------


class TestCanStart:
    def test_true_when_ready_and_selected(self, session_ui_adapter):
        state = _ready_with_selection(session_ui_adapter)
        assert session_ui_adapter.can_start(state) is True

    def test_false_when_no_selection(self, session_ui_adapter):
        state = _loaded_state(session_ui_adapter)
        assert session_ui_adapter.can_start(state) is False

    def test_false_when_preconditions_failed(self, session_ui_adapter):
        state = _loaded_state(
            session_ui_adapter,
            precondition_errors=["Error"],
        )
        assert session_ui_adapter.can_start(state) is False

    def test_false_when_status_not_ready(self, session_ui_adapter):
        state = session_ui_adapter.create_ui_state()
        assert session_ui_adapter.can_start(state) is False

    def test_false_when_status_created(self, session_ui_adapter):
        state = _ready_with_selection(session_ui_adapter)
        state = session_ui_adapter.mark_created(state, _session_data())
        assert session_ui_adapter.can_start(state) is False


# ---------------------------------------------------------------------------
# TestMarkStarting
# ---------------------------------------------------------------------------


class TestMarkStarting:
    def test_transitions_to_starting(self, session_ui_adapter):
        state = _ready_with_selection(session_ui_adapter)
        updated = session_ui_adapter.mark_starting(state)
        assert updated["status"] == "starting"

    def test_does_not_mutate_original(self, session_ui_adapter):
        state = _ready_with_selection(session_ui_adapter)
        session_ui_adapter.mark_starting(state)
        assert state["status"] == "ready"


# ---------------------------------------------------------------------------
# TestMarkCreated
# ---------------------------------------------------------------------------


class TestMarkCreated:
    def test_transitions_to_created(self, session_ui_adapter):
        state = _ready_with_selection(session_ui_adapter)
        updated = session_ui_adapter.mark_created(state, _session_data())
        assert updated["status"] == "created"

    def test_stores_session_data(self, session_ui_adapter):
        state = _ready_with_selection(session_ui_adapter)
        session = _session_data()
        updated = session_ui_adapter.mark_created(state, session)
        assert updated["session"]["session_id"] == session["session_id"]

    def test_clears_errors(self, session_ui_adapter):
        state = _ready_with_selection(session_ui_adapter)
        state = session_ui_adapter.mark_error(state, ["err"])
        updated = session_ui_adapter.mark_created(state, _session_data())
        assert updated["errors"] == []

    def test_does_not_mutate_original(self, session_ui_adapter):
        state = _ready_with_selection(session_ui_adapter)
        session_ui_adapter.mark_created(state, _session_data())
        assert state["session"] is None


# ---------------------------------------------------------------------------
# TestMarkError
# ---------------------------------------------------------------------------


class TestMarkError:
    def test_transitions_to_erreur(self, session_ui_adapter):
        state = _ready_with_selection(session_ui_adapter)
        updated = session_ui_adapter.mark_error(state, ["erreur test"])
        assert updated["status"] == "erreur"

    def test_stores_errors(self, session_ui_adapter):
        state = _ready_with_selection(session_ui_adapter)
        updated = session_ui_adapter.mark_error(
            state, ["err1", "err2"]
        )
        assert updated["errors"] == ["err1", "err2"]

    def test_does_not_mutate_original(self, session_ui_adapter):
        state = _ready_with_selection(session_ui_adapter)
        session_ui_adapter.mark_error(state, ["err"])
        assert state["errors"] == []


# ---------------------------------------------------------------------------
# TestBuildSubmissionPayload
# ---------------------------------------------------------------------------


class TestBuildSubmissionPayload:
    def test_returns_age_range_when_valid(self, session_ui_adapter):
        state = _ready_with_selection(session_ui_adapter, "45-50")
        result = session_ui_adapter.build_submission_payload(state)
        assert result == "45-50"

    def test_raises_when_no_selection(self, session_ui_adapter):
        state = _loaded_state(session_ui_adapter)
        with pytest.raises(ValueError, match="Validation"):
            session_ui_adapter.build_submission_payload(state)

    def test_raises_when_preconditions_failed(self, session_ui_adapter):
        state = _loaded_state(
            session_ui_adapter,
            precondition_errors=["Error"],
        )
        with pytest.raises(ValueError, match="Validation"):
            session_ui_adapter.build_submission_payload(state)
