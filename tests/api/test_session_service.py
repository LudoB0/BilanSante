"""Tests for the session-and-tablet-access service module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _full_settings(**overrides) -> dict:
    """Return a valid settings dict with all required fields."""
    data = {
        "nom_pharmacie": "Pharmacie Test",
        "adresse": "1 rue de Test",
        "code_postal": "75001",
        "ville": "Paris",
        "telephone": "0102030405",
        "fournisseur_ia": "openai",
        "cle_api": "sk-test-key-123",
        "site_web": "",
        "instagram": "",
        "facebook": "",
        "x": "",
        "linkedin": "",
    }
    data.update(overrides)
    return data


def _write_settings(base: Path, data: dict | None = None) -> None:
    cfg = base / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    payload = data if data is not None else _full_settings()
    (cfg / "settings.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _write_logo(base: Path, content: bytes = b"png-bytes") -> None:
    img_dir = base / "config" / "img"
    img_dir.mkdir(parents=True, exist_ok=True)
    (img_dir / "logo.png").write_bytes(content)


def _write_questionnaire(
    base: Path, age_range: str, questions: list | None = None
) -> None:
    qdir = base / "config" / "questionnaires"
    qdir.mkdir(parents=True, exist_ok=True)
    data = {
        "age_range": age_range,
        "version": 1,
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00",
        "questions": questions if questions is not None else [
            {"id": "q1", "order": 0, "type": "boolean", "label": "Test ?",
             "required": True, "options": [], "scale_config": None}
        ],
    }
    (qdir / f"{age_range}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _setup_valid_env(base: Path) -> None:
    """Set up a fully valid environment (settings, logo, questionnaire)."""
    _write_settings(base)
    _write_logo(base)
    _write_questionnaire(base, "45-50")


# ---------------------------------------------------------------------------
# TestCheckPreconditions
# ---------------------------------------------------------------------------


class TestCheckPreconditions:
    def test_no_errors_when_fully_configured(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        errors = session_service.check_preconditions(base=tmp_path)
        assert errors == []

    def test_error_when_no_settings_file(self, session_service, tmp_path):
        _write_logo(tmp_path)
        _write_questionnaire(tmp_path, "18-25")
        errors = session_service.check_preconditions(base=tmp_path)
        assert any("Parametrage" in e for e in errors)

    def test_error_when_settings_missing_required_field(
        self, session_service, tmp_path
    ):
        _write_settings(tmp_path, _full_settings(nom_pharmacie=""))
        _write_logo(tmp_path)
        _write_questionnaire(tmp_path, "18-25")
        errors = session_service.check_preconditions(base=tmp_path)
        assert any("nom_pharmacie" in e for e in errors)

    def test_error_when_no_logo(self, session_service, tmp_path):
        _write_settings(tmp_path)
        _write_questionnaire(tmp_path, "18-25")
        errors = session_service.check_preconditions(base=tmp_path)
        assert any("Logo" in e for e in errors)

    def test_error_when_no_questionnaires(self, session_service, tmp_path):
        _write_settings(tmp_path)
        _write_logo(tmp_path)
        errors = session_service.check_preconditions(base=tmp_path)
        assert any("questionnaire" in e.lower() for e in errors)

    def test_error_when_questionnaire_has_zero_questions(
        self, session_service, tmp_path
    ):
        _write_settings(tmp_path)
        _write_logo(tmp_path)
        _write_questionnaire(tmp_path, "18-25", questions=[])
        errors = session_service.check_preconditions(base=tmp_path)
        assert any("questionnaire" in e.lower() for e in errors)

    def test_error_when_settings_invalid_json(self, session_service, tmp_path):
        cfg = tmp_path / "config"
        cfg.mkdir(parents=True, exist_ok=True)
        (cfg / "settings.json").write_text("{invalid json", encoding="utf-8")
        _write_logo(tmp_path)
        _write_questionnaire(tmp_path, "18-25")
        errors = session_service.check_preconditions(base=tmp_path)
        assert any("Parametrage" in e for e in errors)

    def test_multiple_errors_accumulated(self, session_service, tmp_path):
        # No settings, no logo, no questionnaire
        errors = session_service.check_preconditions(base=tmp_path)
        assert len(errors) >= 3


# ---------------------------------------------------------------------------
# TestLoadPharmacyContext
# ---------------------------------------------------------------------------


class TestLoadPharmacyContext:
    def test_returns_all_fields_when_configured(
        self, session_service, tmp_path
    ):
        _write_settings(
            tmp_path,
            _full_settings(site_web="https://example.com", instagram="@pharma"),
        )
        _write_logo(tmp_path)
        ctx = session_service.load_pharmacy_context(base=tmp_path)
        assert ctx["nom_pharmacie"] == "Pharmacie Test"
        assert ctx["adresse"] == "1 rue de Test"
        assert ctx["code_postal"] == "75001"
        assert ctx["ville"] == "Paris"
        assert ctx["site_web"] == "https://example.com"
        assert ctx["instagram"] == "@pharma"

    def test_returns_empty_strings_when_no_settings(
        self, session_service, tmp_path
    ):
        ctx = session_service.load_pharmacy_context(base=tmp_path)
        assert ctx["nom_pharmacie"] == ""
        assert ctx["ville"] == ""

    def test_logo_path_when_logo_exists(self, session_service, tmp_path):
        _write_settings(tmp_path)
        _write_logo(tmp_path)
        ctx = session_service.load_pharmacy_context(base=tmp_path)
        assert ctx["logo_path"] != ""
        assert Path(ctx["logo_path"]).is_file()

    def test_logo_path_empty_when_no_logo(self, session_service, tmp_path):
        _write_settings(tmp_path)
        ctx = session_service.load_pharmacy_context(base=tmp_path)
        assert ctx["logo_path"] == ""

    def test_optional_fields_included(self, session_service, tmp_path):
        _write_settings(tmp_path)
        ctx = session_service.load_pharmacy_context(base=tmp_path)
        for field in ("site_web", "instagram", "facebook", "x", "linkedin"):
            assert field in ctx


# ---------------------------------------------------------------------------
# TestListAvailableAgeRanges
# ---------------------------------------------------------------------------


class TestListAvailableAgeRanges:
    def test_empty_when_no_questionnaires_dir(
        self, session_service, tmp_path
    ):
        result = session_service.list_available_age_ranges(base=tmp_path)
        assert result == []

    def test_returns_ranges_with_questions(self, session_service, tmp_path):
        _write_questionnaire(tmp_path, "45-50")
        _write_questionnaire(tmp_path, "18-25")
        result = session_service.list_available_age_ranges(base=tmp_path)
        assert "45-50" in result
        assert "18-25" in result

    def test_excludes_empty_questionnaires(self, session_service, tmp_path):
        _write_questionnaire(tmp_path, "45-50")
        _write_questionnaire(tmp_path, "18-25", questions=[])
        result = session_service.list_available_age_ranges(base=tmp_path)
        assert "45-50" in result
        assert "18-25" not in result

    def test_preserves_canonical_order(self, session_service, tmp_path):
        # Write in reverse order
        _write_questionnaire(tmp_path, "70-75")
        _write_questionnaire(tmp_path, "18-25")
        _write_questionnaire(tmp_path, "45-50")
        result = session_service.list_available_age_ranges(base=tmp_path)
        assert result == ["18-25", "45-50", "70-75"]

    def test_ignores_invalid_questionnaire_files(
        self, session_service, tmp_path
    ):
        _write_questionnaire(tmp_path, "45-50")
        qdir = tmp_path / "config" / "questionnaires"
        (qdir / "99-99.json").write_text("{}", encoding="utf-8")
        result = session_service.list_available_age_ranges(base=tmp_path)
        assert result == ["45-50"]

    def test_handles_corrupt_questionnaire_file(
        self, session_service, tmp_path
    ):
        _write_questionnaire(tmp_path, "45-50")
        qdir = tmp_path / "config" / "questionnaires"
        (qdir / "18-25.json").write_text("{bad json", encoding="utf-8")
        result = session_service.list_available_age_ranges(base=tmp_path)
        assert result == ["45-50"]


# ---------------------------------------------------------------------------
# TestCreateSession
# ---------------------------------------------------------------------------


class TestCreateSession:
    def test_creates_session_file(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", base=tmp_path)
        session_path = (
            tmp_path / "data" / "sessions" / f"{session['session_id']}.json"
        )
        assert session_path.is_file()

    def test_session_has_correct_structure(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", base=tmp_path)
        assert "session_id" in session
        assert "age_range" in session
        assert "created_at" in session
        assert "status" in session
        assert "metadata" in session
        assert "pharmacie" in session["metadata"]

    def test_session_id_is_uuid_format(self, session_service, tmp_path):
        import uuid as uuid_mod

        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", base=tmp_path)
        # Should not raise
        uuid_mod.UUID(session["session_id"], version=4)

    def test_session_status_is_active(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", base=tmp_path)
        assert session["status"] == "active"

    def test_session_age_range_matches_input(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", base=tmp_path)
        assert session["age_range"] == "45-50"

    def test_session_has_created_at_iso(self, session_service, tmp_path):
        from datetime import datetime

        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", base=tmp_path)
        # Should parse without error
        datetime.fromisoformat(session["created_at"])

    def test_session_metadata_pharmacie(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", base=tmp_path)
        pharma = session["metadata"]["pharmacie"]
        assert pharma["nom_pharmacie"] == "Pharmacie Test"
        assert pharma["adresse"] == "1 rue de Test"
        assert pharma["code_postal"] == "75001"
        assert pharma["ville"] == "Paris"

    def test_session_file_content_matches_return(
        self, session_service, tmp_path
    ):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", base=tmp_path)
        session_path = (
            tmp_path / "data" / "sessions" / f"{session['session_id']}.json"
        )
        with open(session_path, encoding="utf-8") as fh:
            on_disk = json.load(fh)
        assert on_disk == session

    def test_creates_data_sessions_directory(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session_service.create_session("45-50", base=tmp_path)
        assert (tmp_path / "data" / "sessions").is_dir()

    def test_invalid_age_range_raises(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        with pytest.raises(ValueError, match="invalide"):
            session_service.create_session("99-99", base=tmp_path)

    def test_preconditions_unmet_raises(self, session_service, tmp_path):
        # No setup at all
        with pytest.raises(ValueError, match="Preconditions"):
            session_service.create_session("45-50", base=tmp_path)

    def test_age_range_without_questionnaire_raises(
        self, session_service, tmp_path
    ):
        _write_settings(tmp_path)
        _write_logo(tmp_path)
        _write_questionnaire(tmp_path, "45-50")
        with pytest.raises(ValueError, match="questionnaire"):
            session_service.create_session("18-25", base=tmp_path)

    def test_returns_session_dict(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        result = session_service.create_session("45-50", base=tmp_path)
        assert isinstance(result, dict)
        assert result["session_id"]

    def test_two_sessions_have_different_ids(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        s1 = session_service.create_session("45-50", base=tmp_path)
        s2 = session_service.create_session("45-50", base=tmp_path)
        assert s1["session_id"] != s2["session_id"]
