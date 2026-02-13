"""Tests for the application_context_ui adapter (pytest migration)."""

from __future__ import annotations

import pytest


# ===================================================================
# create_ui_state
# ===================================================================


class TestCreateUiState:
    def test_initial_state(self, ui_adapter):
        state = ui_adapter.create_ui_state()
        assert state["status"] == "initial"
        assert state["nom_pharmacie"] == ""
        assert state["cle_api"] == ""

    def test_existing_data_sets_edition(self, ui_adapter):
        state = ui_adapter.create_ui_state(existing={"nom_pharmacie": "Test"})
        assert state["status"] == "edition"
        assert state["nom_pharmacie"] == "Test"

    def test_unknown_key_in_existing_is_ignored(self, ui_adapter):
        state = ui_adapter.create_ui_state(existing={"unknown_field": "val"})
        assert "unknown_field" not in state


# ===================================================================
# update_ui_state
# ===================================================================


class TestUpdateUiState:
    def test_updates_field_and_status(self, ui_adapter):
        state = ui_adapter.create_ui_state()
        updated = ui_adapter.update_ui_state(state, "ville", "Lyon")
        assert updated["ville"] == "Lyon"
        assert updated["status"] == "edition"

    def test_does_not_mutate_original(self, ui_adapter):
        state = ui_adapter.create_ui_state()
        ui_adapter.update_ui_state(state, "ville", "Lyon")
        assert state["ville"] == ""

    def test_unknown_field_raises(self, ui_adapter):
        state = ui_adapter.create_ui_state()
        with pytest.raises(ValueError, match="Unknown field"):
            ui_adapter.update_ui_state(state, "nonexistent", "x")


# ===================================================================
# validate_ui_state
# ===================================================================


class TestValidateUiState:
    def test_empty_state_reports_required_missing(self, ui_adapter):
        state = ui_adapter.create_ui_state()
        errors = ui_adapter.validate_ui_state(state)
        assert any("nom_pharmacie" in e for e in errors)
        assert any("cle_api" in e for e in errors)

    def test_valid_state_returns_no_errors(self, ui_adapter, valid_ui_state):
        errors = ui_adapter.validate_ui_state(valid_ui_state)
        assert errors == []


# ===================================================================
# build_submission_payload
# ===================================================================


class TestBuildSubmissionPayload:
    def test_builds_from_valid_state(self, ui_adapter, valid_ui_state):
        payload = ui_adapter.build_submission_payload(valid_ui_state)
        assert payload["nom_pharmacie"] == "Pharmacie Test"
        assert payload["fournisseur_ia"] == "openai"

    def test_raises_on_invalid_state(self, ui_adapter):
        state = ui_adapter.create_ui_state()
        with pytest.raises(ValueError, match="Validation"):
            ui_adapter.build_submission_payload(state)

    def test_payload_contains_optional_fields(self, ui_adapter, valid_ui_state):
        payload = ui_adapter.build_submission_payload(valid_ui_state)
        assert "site_web" in payload
        assert "instagram" in payload

    def test_payload_contains_modele_ia(self, ui_adapter, valid_ui_state):
        valid_ui_state["modele_ia"] = "eco"
        payload = ui_adapter.build_submission_payload(valid_ui_state)
        assert payload["modele_ia"] == "eco"
