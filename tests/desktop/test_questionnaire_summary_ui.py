"""Tests for questionnaire_summary_ui adapter (BuildQuestionnaireSummarySection)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_SUMMARY_DATA = {
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "short_id": "a1b2c3d4",
    "age_range": "45-50",
    "md_path": "/tmp/data/sessions/QuestionnaireComplet_a1b2c3d4.md",
    "items": [
        {
            "question_id": "q1",
            "label": "Genre",
            "type": "single_choice",
            "options": ["Un homme", "Une femme"],
            "response_value": "Un homme",
            "response_display": "Un homme",
        },
        {
            "question_id": "q2",
            "label": "Enfants",
            "type": "boolean",
            "options": [],
            "response_value": True,
            "response_display": "Oui",
        },
    ],
    "metrics": {
        "poids_kg": 80.0,
        "taille_m": 1.75,
        "imc": 26.1,
        "imc_display": "26.1",
    },
}


# ---------------------------------------------------------------------------
# Tests: create_summary_state
# ---------------------------------------------------------------------------


class TestCreateSummaryState:
    def test_initial_status(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        assert state["status"] == "initial"

    def test_initial_session_id(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        assert state["session_id"] is None

    def test_initial_short_id(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        assert state["short_id"] is None

    def test_initial_age_range(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        assert state["age_range"] is None

    def test_initial_items(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        assert state["items"] == []

    def test_initial_pharmacist_notes(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        assert state["pharmacist_notes"] == {}

    def test_initial_metrics(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        assert state["metrics"] is None

    def test_initial_pharmacist_blood_pressure(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        assert state["pharmacist_blood_pressure"] == ""

    def test_initial_pharmacist_report(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        assert state["pharmacist_report"] == ""

    def test_initial_md_path(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        assert state["md_path"] is None

    def test_initial_errors(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        assert state["errors"] == []


# ---------------------------------------------------------------------------
# Tests: mark_loading
# ---------------------------------------------------------------------------


class TestMarkLoading:
    def test_status_changes(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.mark_loading(state)
        assert new["status"] == "loading"

    def test_immutability(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.mark_loading(state)
        assert state["status"] == "initial"
        assert new is not state


# ---------------------------------------------------------------------------
# Tests: load_summary
# ---------------------------------------------------------------------------


class TestLoadSummary:
    def test_status_ready(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.load_summary(state, SAMPLE_SUMMARY_DATA)
        assert new["status"] == "ready"

    def test_session_id(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.load_summary(state, SAMPLE_SUMMARY_DATA)
        assert new["session_id"] == SAMPLE_SUMMARY_DATA["session_id"]

    def test_short_id(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.load_summary(state, SAMPLE_SUMMARY_DATA)
        assert new["short_id"] == "a1b2c3d4"

    def test_age_range(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.load_summary(state, SAMPLE_SUMMARY_DATA)
        assert new["age_range"] == "45-50"

    def test_items_loaded(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.load_summary(state, SAMPLE_SUMMARY_DATA)
        assert len(new["items"]) == 2

    def test_metrics_loaded(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.load_summary(state, SAMPLE_SUMMARY_DATA)
        assert new["metrics"]["poids_kg"] == 80.0
        assert new["metrics"]["taille_m"] == 1.75
        assert new["metrics"]["imc_display"] == "26.1"

    def test_md_path(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.load_summary(state, SAMPLE_SUMMARY_DATA)
        assert new["md_path"] == SAMPLE_SUMMARY_DATA["md_path"]

    def test_errors_cleared(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        state_err = summary_ui_adapter.mark_summary_error(state, ["err"])
        new = summary_ui_adapter.load_summary(state_err, SAMPLE_SUMMARY_DATA)
        assert new["errors"] == []

    def test_immutability(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.load_summary(state, SAMPLE_SUMMARY_DATA)
        assert state["status"] == "initial"
        assert state["items"] == []
        assert new is not state


# ---------------------------------------------------------------------------
# Tests: mark_summary_error
# ---------------------------------------------------------------------------


class TestMarkSummaryError:
    def test_status_erreur(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.mark_summary_error(state, ["err1", "err2"])
        assert new["status"] == "erreur"

    def test_errors_stored(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.mark_summary_error(state, ["err1"])
        assert new["errors"] == ["err1"]

    def test_immutability(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.mark_summary_error(state, ["err"])
        assert state["status"] == "initial"
        assert state["errors"] == []
        assert new is not state


# ---------------------------------------------------------------------------
# Tests: update_pharmacist_note
# ---------------------------------------------------------------------------


class TestUpdatePharmacistNote:
    def test_note_set(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.update_pharmacist_note(state, "q1", "Note for q1")
        assert new["pharmacist_notes"]["q1"] == "Note for q1"

    def test_multiple_notes(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        s1 = summary_ui_adapter.update_pharmacist_note(state, "q1", "Note 1")
        s2 = summary_ui_adapter.update_pharmacist_note(s1, "q2", "Note 2")
        assert s2["pharmacist_notes"]["q1"] == "Note 1"
        assert s2["pharmacist_notes"]["q2"] == "Note 2"

    def test_overwrite_note(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        s1 = summary_ui_adapter.update_pharmacist_note(state, "q1", "Old")
        s2 = summary_ui_adapter.update_pharmacist_note(s1, "q1", "New")
        assert s2["pharmacist_notes"]["q1"] == "New"

    def test_immutability(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.update_pharmacist_note(state, "q1", "Note")
        assert state["pharmacist_notes"] == {}
        assert new is not state


# ---------------------------------------------------------------------------
# Tests: update_pharmacist_report
# ---------------------------------------------------------------------------


class TestUpdatePharmacistBloodPressure:
    def test_blood_pressure_set(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.update_pharmacist_blood_pressure(state, "120/80")
        assert new["pharmacist_blood_pressure"] == "120/80"

    def test_overwrite_blood_pressure(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        s1 = summary_ui_adapter.update_pharmacist_blood_pressure(state, "130/90")
        s2 = summary_ui_adapter.update_pharmacist_blood_pressure(s1, "120/80")
        assert s2["pharmacist_blood_pressure"] == "120/80"

    def test_immutability(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.update_pharmacist_blood_pressure(state, "120/80")
        assert state["pharmacist_blood_pressure"] == ""
        assert new is not state


# ---------------------------------------------------------------------------
# Tests: update_pharmacist_report
# ---------------------------------------------------------------------------


class TestUpdatePharmacistReport:
    def test_report_set(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.update_pharmacist_report(state, "Mon rapport")
        assert new["pharmacist_report"] == "Mon rapport"

    def test_overwrite_report(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        s1 = summary_ui_adapter.update_pharmacist_report(state, "Old")
        s2 = summary_ui_adapter.update_pharmacist_report(s1, "New")
        assert s2["pharmacist_report"] == "New"

    def test_immutability(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        new = summary_ui_adapter.update_pharmacist_report(state, "Report")
        assert state["pharmacist_report"] == ""
        assert new is not state


# ---------------------------------------------------------------------------
# Tests: get_summary_items
# ---------------------------------------------------------------------------


class TestGetSummaryItems:
    def test_returns_items(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        loaded = summary_ui_adapter.load_summary(state, SAMPLE_SUMMARY_DATA)
        items = summary_ui_adapter.get_summary_items(loaded)
        assert len(items) == 2

    def test_returns_copy(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        loaded = summary_ui_adapter.load_summary(state, SAMPLE_SUMMARY_DATA)
        items = summary_ui_adapter.get_summary_items(loaded)
        assert items is not loaded["items"]

    def test_empty_when_initial(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        items = summary_ui_adapter.get_summary_items(state)
        assert items == []


# ---------------------------------------------------------------------------
# Tests: is_ready
# ---------------------------------------------------------------------------


class TestIsReady:
    def test_initial_not_ready(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        assert summary_ui_adapter.is_ready(state) is False

    def test_loading_not_ready(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        loading = summary_ui_adapter.mark_loading(state)
        assert summary_ui_adapter.is_ready(loading) is False

    def test_ready_after_load(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        loaded = summary_ui_adapter.load_summary(state, SAMPLE_SUMMARY_DATA)
        assert summary_ui_adapter.is_ready(loaded) is True

    def test_erreur_not_ready(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        err = summary_ui_adapter.mark_summary_error(state, ["err"])
        assert summary_ui_adapter.is_ready(err) is False


# ---------------------------------------------------------------------------
# Tests: mark_capturing / mark_captured / mark_capture_error
# ---------------------------------------------------------------------------


class TestCaptureTransitions:
    def test_mark_capturing(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        loaded = summary_ui_adapter.load_summary(state, SAMPLE_SUMMARY_DATA)
        capturing = summary_ui_adapter.mark_capturing(loaded)
        assert capturing["status"] == "capturing"

    def test_mark_captured(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        loaded = summary_ui_adapter.load_summary(state, SAMPLE_SUMMARY_DATA)
        capturing = summary_ui_adapter.mark_capturing(loaded)
        captured = summary_ui_adapter.mark_captured(capturing)
        assert captured["status"] == "captured"
        assert captured["errors"] == []

    def test_mark_capture_error(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        loaded = summary_ui_adapter.load_summary(state, SAMPLE_SUMMARY_DATA)
        capturing = summary_ui_adapter.mark_capturing(loaded)
        err = summary_ui_adapter.mark_capture_error(capturing, ["Erreur ecriture"])
        assert err["status"] == "capture_error"
        assert err["errors"] == ["Erreur ecriture"]

    def test_immutability_capturing(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        loaded = summary_ui_adapter.load_summary(state, SAMPLE_SUMMARY_DATA)
        capturing = summary_ui_adapter.mark_capturing(loaded)
        assert loaded["status"] == "ready"
        assert capturing is not loaded

    def test_immutability_captured(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        capturing = summary_ui_adapter.mark_capturing(state)
        captured = summary_ui_adapter.mark_captured(capturing)
        assert capturing["status"] == "capturing"
        assert captured is not capturing


# ---------------------------------------------------------------------------
# Tests: get_pharmacist_data
# ---------------------------------------------------------------------------


class TestGetPharmacistData:
    def test_returns_all_fields(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        s1 = summary_ui_adapter.update_pharmacist_note(state, "q1", "Note 1")
        s2 = summary_ui_adapter.update_pharmacist_blood_pressure(s1, "120/80")
        s3 = summary_ui_adapter.update_pharmacist_report(s2, "Rapport")

        data = summary_ui_adapter.get_pharmacist_data(s3)

        assert data["pharmacist_notes"] == {"q1": "Note 1"}
        assert data["pharmacist_blood_pressure"] == "120/80"
        assert data["pharmacist_report"] == "Rapport"

    def test_empty_state(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        data = summary_ui_adapter.get_pharmacist_data(state)

        assert data["pharmacist_notes"] == {}
        assert data["pharmacist_blood_pressure"] == ""
        assert data["pharmacist_report"] == ""

    def test_returns_copy_of_notes(self, summary_ui_adapter):
        state = summary_ui_adapter.create_summary_state()
        s1 = summary_ui_adapter.update_pharmacist_note(state, "q1", "Note")
        data = summary_ui_adapter.get_pharmacist_data(s1)
        assert data["pharmacist_notes"] is not s1["pharmacist_notes"]
