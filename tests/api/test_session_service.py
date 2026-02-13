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
        session = session_service.create_session("45-50", "H", base=tmp_path)
        session_path = (
            tmp_path / "data" / "sessions" / f"{session['session_id']}.json"
        )
        assert session_path.is_file()

    def test_session_has_correct_structure(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        assert "session_id" in session
        assert "age_range" in session
        assert "created_at" in session
        assert "status" in session
        assert "metadata" in session
        assert "pharmacie" in session["metadata"]

    def test_session_id_is_uuid_format(self, session_service, tmp_path):
        import uuid as uuid_mod

        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        # Should not raise
        uuid_mod.UUID(session["session_id"], version=4)

    def test_session_status_is_active(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        assert session["status"] == "active"

    def test_session_age_range_matches_input(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        assert session["age_range"] == "45-50"

    def test_session_has_created_at_iso(self, session_service, tmp_path):
        from datetime import datetime

        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        # Should parse without error
        datetime.fromisoformat(session["created_at"])

    def test_session_metadata_pharmacie(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        pharma = session["metadata"]["pharmacie"]
        assert pharma["nom_pharmacie"] == "Pharmacie Test"
        assert pharma["adresse"] == "1 rue de Test"
        assert pharma["code_postal"] == "75001"
        assert pharma["ville"] == "Paris"

    def test_session_file_content_matches_return(
        self, session_service, tmp_path
    ):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        session_path = (
            tmp_path / "data" / "sessions" / f"{session['session_id']}.json"
        )
        with open(session_path, encoding="utf-8") as fh:
            on_disk = json.load(fh)
        assert on_disk == session

    def test_creates_data_sessions_directory(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session_service.create_session("45-50", "H", base=tmp_path)
        assert (tmp_path / "data" / "sessions").is_dir()

    def test_invalid_age_range_raises(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        with pytest.raises(ValueError, match="invalide"):
            session_service.create_session("99-99", "H", base=tmp_path)

    def test_preconditions_unmet_raises(self, session_service, tmp_path):
        # No setup at all
        with pytest.raises(ValueError, match="Preconditions"):
            session_service.create_session("45-50", "H", base=tmp_path)

    def test_age_range_without_questionnaire_raises(
        self, session_service, tmp_path
    ):
        _write_settings(tmp_path)
        _write_logo(tmp_path)
        _write_questionnaire(tmp_path, "45-50")
        with pytest.raises(ValueError, match="questionnaire"):
            session_service.create_session("18-25", "H", base=tmp_path)

    def test_returns_session_dict(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        result = session_service.create_session("45-50", "H", base=tmp_path)
        assert isinstance(result, dict)
        assert result["session_id"]

    def test_two_sessions_have_different_ids(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        s1 = session_service.create_session("45-50", "H", base=tmp_path)
        s2 = session_service.create_session("45-50", "H", base=tmp_path)
        assert s1["session_id"] != s2["session_id"]

    def test_session_has_sex_field(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "F", base=tmp_path)
        assert session["sex"] == "F"

    def test_sex_stored_in_file(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        session_path = (
            tmp_path / "data" / "sessions" / f"{session['session_id']}.json"
        )
        on_disk = json.loads(session_path.read_text(encoding="utf-8"))
        assert on_disk["sex"] == "H"

    def test_invalid_sex_raises(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        with pytest.raises(ValueError, match="Sexe invalide"):
            session_service.create_session("45-50", "X", base=tmp_path)


# ---------------------------------------------------------------------------
# TestLoadOrCreateQrSecret
# ---------------------------------------------------------------------------


class TestLoadOrCreateQrSecret:
    def test_creates_secret_file_when_absent(self, session_service, tmp_path):
        secret = session_service.load_or_create_qr_secret(base=tmp_path)
        assert secret
        assert (tmp_path / "config" / "qr_secret.key").is_file()

    def test_returns_same_secret_on_subsequent_calls(
        self, session_service, tmp_path
    ):
        s1 = session_service.load_or_create_qr_secret(base=tmp_path)
        s2 = session_service.load_or_create_qr_secret(base=tmp_path)
        assert s1 == s2

    def test_secret_is_hex_string(self, session_service, tmp_path):
        secret = session_service.load_or_create_qr_secret(base=tmp_path)
        int(secret, 16)  # Should not raise

    def test_reads_existing_secret(self, session_service, tmp_path):
        cfg = tmp_path / "config"
        cfg.mkdir(parents=True, exist_ok=True)
        (cfg / "qr_secret.key").write_text("my-custom-secret", encoding="utf-8")
        secret = session_service.load_or_create_qr_secret(base=tmp_path)
        assert secret == "my-custom-secret"


# ---------------------------------------------------------------------------
# TestLoadSession
# ---------------------------------------------------------------------------


class TestLoadSession:
    def test_loads_existing_session(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        created = session_service.create_session("45-50", "H", base=tmp_path)
        loaded = session_service.load_session(created["session_id"], base=tmp_path)
        assert loaded == created

    def test_raises_when_session_not_found(self, session_service, tmp_path):
        with pytest.raises(ValueError, match="inconnue"):
            session_service.load_session("nonexistent-id", base=tmp_path)

    def test_raises_when_session_file_invalid(self, session_service, tmp_path):
        sessions_dir = tmp_path / "data" / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        (sessions_dir / "bad-session.json").write_text(
            "{invalid", encoding="utf-8"
        )
        with pytest.raises(ValueError, match="invalide"):
            session_service.load_session("bad-session", base=tmp_path)


# ---------------------------------------------------------------------------
# TestGenerateSessionToken
# ---------------------------------------------------------------------------


class TestGenerateSessionToken:
    def test_returns_non_empty_string(self, session_service):
        token = session_service.generate_session_token()
        assert isinstance(token, str)
        assert len(token) > 0

    def test_tokens_are_unique(self, session_service):
        tokens = {session_service.generate_session_token() for _ in range(100)}
        assert len(tokens) == 100

    def test_token_is_url_safe(self, session_service):
        token = session_service.generate_session_token()
        # url-safe base64 only uses A-Z, a-z, 0-9, -, _
        import re
        assert re.fullmatch(r"[A-Za-z0-9_-]+", token)


# ---------------------------------------------------------------------------
# TestComputeSignature
# ---------------------------------------------------------------------------


class TestComputeSignature:
    def test_returns_hex_string(self, session_service):
        sig = session_service.compute_signature("sid-1", "token-1", "secret")
        int(sig, 16)  # Should not raise

    def test_deterministic(self, session_service):
        sig1 = session_service.compute_signature("sid", "tok", "key")
        sig2 = session_service.compute_signature("sid", "tok", "key")
        assert sig1 == sig2

    def test_different_with_different_session(self, session_service):
        sig1 = session_service.compute_signature("sid-1", "tok", "key")
        sig2 = session_service.compute_signature("sid-2", "tok", "key")
        assert sig1 != sig2

    def test_different_with_different_token(self, session_service):
        sig1 = session_service.compute_signature("sid", "tok-1", "key")
        sig2 = session_service.compute_signature("sid", "tok-2", "key")
        assert sig1 != sig2

    def test_different_with_different_secret(self, session_service):
        sig1 = session_service.compute_signature("sid", "tok", "key-1")
        sig2 = session_service.compute_signature("sid", "tok", "key-2")
        assert sig1 != sig2


# ---------------------------------------------------------------------------
# TestBuildQrPayload
# ---------------------------------------------------------------------------


class TestBuildQrPayload:
    def test_format_matches_spec(self, session_service):
        payload = session_service.build_qr_payload(
            "http://localhost:5000/questionnaire", "my-sid", "my-tok", "my-sig"
        )
        assert payload == (
            "http://localhost:5000/questionnaire"
            "?v=1&sid=my-sid&t=my-tok&sig=my-sig"
        )

    def test_contains_all_required_fields(self, session_service):
        payload = session_service.build_qr_payload(
            "http://example.com", "sid", "tok", "sig"
        )
        assert "v=1" in payload
        assert "sid=sid" in payload
        assert "t=tok" in payload
        assert "sig=sig" in payload

    def test_starts_with_base_url(self, session_service):
        payload = session_service.build_qr_payload(
            "https://custom.url/q", "sid", "tok", "sig"
        )
        assert payload.startswith("https://custom.url/q?")


# ---------------------------------------------------------------------------
# TestGenerateQrData
# ---------------------------------------------------------------------------


class TestGenerateQrData:
    def test_returns_complete_qr_data(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        qr = session_service.generate_qr_data(
            session["session_id"], base=tmp_path
        )
        assert "payload" in qr
        assert "session_id" in qr
        assert "version" in qr
        assert "token" in qr
        assert "signature" in qr

    def test_payload_contains_session_id(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        qr = session_service.generate_qr_data(
            session["session_id"], base=tmp_path
        )
        assert session["session_id"] in qr["payload"]

    def test_payload_contains_all_required_params(
        self, session_service, tmp_path
    ):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        qr = session_service.generate_qr_data(
            session["session_id"], base=tmp_path
        )
        assert "v=1" in qr["payload"]
        assert f"sid={session['session_id']}" in qr["payload"]
        assert f"t={qr['token']}" in qr["payload"]
        assert f"sig={qr['signature']}" in qr["payload"]

    def test_version_is_one(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        qr = session_service.generate_qr_data(
            session["session_id"], base=tmp_path
        )
        assert qr["version"] == 1

    def test_uses_custom_base_url(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        qr = session_service.generate_qr_data(
            session["session_id"],
            base=tmp_path,
            base_url="https://custom.url/q",
        )
        assert qr["payload"].startswith("https://custom.url/q?")

    def test_uses_local_ip_in_default_base_url(
        self, session_service, tmp_path
    ):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        qr = session_service.generate_qr_data(
            session["session_id"], base=tmp_path
        )
        # Should contain the local IP (not localhost) and port 5000
        assert ":5000/questionnaire" in qr["payload"]
        assert "http://" in qr["payload"]
        # Should NOT use localhost
        assert "localhost" not in qr["payload"]

    def test_raises_when_session_not_found(self, session_service, tmp_path):
        with pytest.raises(ValueError, match="inconnue"):
            session_service.generate_qr_data("no-such-id", base=tmp_path)

    def test_raises_when_session_inactive(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        # Manually mark session as inactive
        session_path = (
            tmp_path
            / "data"
            / "sessions"
            / f"{session['session_id']}.json"
        )
        data = json.loads(session_path.read_text(encoding="utf-8"))
        data["status"] = "closed"
        session_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        with pytest.raises(ValueError, match="inactive"):
            session_service.generate_qr_data(
                session["session_id"], base=tmp_path
            )

    def test_raises_when_base_url_empty(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        with pytest.raises(ValueError, match="URL"):
            session_service.generate_qr_data(
                session["session_id"], base=tmp_path, base_url=""
            )

    def test_signature_is_verifiable(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        qr = session_service.generate_qr_data(
            session["session_id"], base=tmp_path
        )
        assert session_service.verify_qr_signature(
            qr["session_id"], qr["token"], qr["signature"], base=tmp_path
        )

    def test_two_calls_produce_different_tokens(
        self, session_service, tmp_path
    ):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        qr1 = session_service.generate_qr_data(
            session["session_id"], base=tmp_path
        )
        qr2 = session_service.generate_qr_data(
            session["session_id"], base=tmp_path
        )
        assert qr1["token"] != qr2["token"]


# ---------------------------------------------------------------------------
# TestVerifyQrSignature
# ---------------------------------------------------------------------------


class TestVerifyQrSignature:
    def test_valid_signature_returns_true(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        qr = session_service.generate_qr_data(
            session["session_id"], base=tmp_path
        )
        assert session_service.verify_qr_signature(
            qr["session_id"], qr["token"], qr["signature"], base=tmp_path
        ) is True

    def test_tampered_session_id_returns_false(
        self, session_service, tmp_path
    ):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        qr = session_service.generate_qr_data(
            session["session_id"], base=tmp_path
        )
        assert session_service.verify_qr_signature(
            "tampered-id", qr["token"], qr["signature"], base=tmp_path
        ) is False

    def test_tampered_token_returns_false(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        qr = session_service.generate_qr_data(
            session["session_id"], base=tmp_path
        )
        assert session_service.verify_qr_signature(
            qr["session_id"], "tampered-token", qr["signature"], base=tmp_path
        ) is False

    def test_tampered_signature_returns_false(
        self, session_service, tmp_path
    ):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        qr = session_service.generate_qr_data(
            session["session_id"], base=tmp_path
        )
        assert session_service.verify_qr_signature(
            qr["session_id"], qr["token"], "tampered-sig", base=tmp_path
        ) is False


# ---------------------------------------------------------------------------
# TestValidateQrParams
# ---------------------------------------------------------------------------


def _create_session_with_qr(svc, tmp_path):
    """Helper: create a session and generate QR data."""
    _setup_valid_env(tmp_path)
    session = svc.create_session("45-50", "H", base=tmp_path)
    qr = svc.generate_qr_data(session["session_id"], base=tmp_path)
    return session, qr


class TestValidateQrParams:
    def test_valid_params(self, session_service, tmp_path):
        session, qr = _create_session_with_qr(session_service, tmp_path)
        result = session_service.validate_qr_params(
            v="1",
            sid=session["session_id"],
            t=qr["token"],
            sig=qr["signature"],
            base=tmp_path,
        )
        assert result["valid"] is True
        assert result["session"]["session_id"] == session["session_id"]

    def test_missing_sid(self, session_service, tmp_path):
        result = session_service.validate_qr_params(
            v="1", sid=None, t="tok", sig="sig", base=tmp_path
        )
        assert result["valid"] is False
        assert "sid" in result["error"].lower()

    def test_missing_token(self, session_service, tmp_path):
        result = session_service.validate_qr_params(
            v="1", sid="sid", t=None, sig="sig", base=tmp_path
        )
        assert result["valid"] is False
        assert "t" in result["error"].lower()

    def test_missing_sig(self, session_service, tmp_path):
        result = session_service.validate_qr_params(
            v="1", sid="sid", t="tok", sig=None, base=tmp_path
        )
        assert result["valid"] is False
        assert "sig" in result["error"].lower()

    def test_invalid_version(self, session_service, tmp_path):
        result = session_service.validate_qr_params(
            v="99", sid="sid", t="tok", sig="sig", base=tmp_path
        )
        assert result["valid"] is False
        assert "version" in result["error"].lower()

    def test_missing_version(self, session_service, tmp_path):
        result = session_service.validate_qr_params(
            v=None, sid="sid", t="tok", sig="sig", base=tmp_path
        )
        assert result["valid"] is False
        assert "version" in result["error"].lower()

    def test_invalid_signature(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        session_service.load_or_create_qr_secret(base=tmp_path)
        result = session_service.validate_qr_params(
            v="1",
            sid=session["session_id"],
            t="some-token",
            sig="bad-sig",
            base=tmp_path,
        )
        assert result["valid"] is False
        assert "signature" in result["error"].lower()

    def test_session_not_found(self, session_service, tmp_path):
        # Generate a valid token+sig for a nonexistent session
        _setup_valid_env(tmp_path)
        secret = session_service.load_or_create_qr_secret(base=tmp_path)
        token = session_service.generate_session_token()
        sig = session_service.compute_signature("nonexistent", token, secret)
        result = session_service.validate_qr_params(
            v="1", sid="nonexistent", t=token, sig=sig, base=tmp_path
        )
        assert result["valid"] is False
        assert "inconnue" in result["error"].lower()

    def test_session_inactive(self, session_service, tmp_path):
        session, qr = _create_session_with_qr(session_service, tmp_path)
        # Mark session as closed
        session_path = (
            tmp_path / "data" / "sessions" / f"{session['session_id']}.json"
        )
        data = json.loads(session_path.read_text(encoding="utf-8"))
        data["status"] = "closed"
        session_path.write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )
        result = session_service.validate_qr_params(
            v="1",
            sid=session["session_id"],
            t=qr["token"],
            sig=qr["signature"],
            base=tmp_path,
        )
        assert result["valid"] is False
        assert "inactive" in result["error"].lower()

    def test_version_as_int(self, session_service, tmp_path):
        session, qr = _create_session_with_qr(session_service, tmp_path)
        result = session_service.validate_qr_params(
            v=1,
            sid=session["session_id"],
            t=qr["token"],
            sig=qr["signature"],
            base=tmp_path,
        )
        assert result["valid"] is True

    def test_empty_sid(self, session_service, tmp_path):
        result = session_service.validate_qr_params(
            v="1", sid="", t="tok", sig="sig", base=tmp_path
        )
        assert result["valid"] is False


# ---------------------------------------------------------------------------
# TestLoadQuestionnaireForSession
# ---------------------------------------------------------------------------


class TestLoadQuestionnaireForSession:
    def test_loads_questionnaire(self, session_service, tmp_path):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        q = session_service.load_questionnaire_for_session(
            session["session_id"], base=tmp_path
        )
        assert q["age_range"] == "45-50"
        assert len(q["questions"]) >= 1

    def test_raises_when_session_not_found(self, session_service, tmp_path):
        with pytest.raises(ValueError, match="inconnue"):
            session_service.load_questionnaire_for_session(
                "nonexistent", base=tmp_path
            )

    def test_raises_when_no_questionnaire_file(
        self, session_service, tmp_path
    ):
        # Create session for age range but delete questionnaire
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        (tmp_path / "config" / "questionnaires" / "45-50.json").unlink()
        with pytest.raises(ValueError, match="non disponible"):
            session_service.load_questionnaire_for_session(
                session["session_id"], base=tmp_path
            )

    def test_raises_when_questionnaire_empty(
        self, session_service, tmp_path
    ):
        _setup_valid_env(tmp_path)
        session = session_service.create_session("45-50", "H", base=tmp_path)
        # Overwrite with empty questionnaire
        qpath = tmp_path / "config" / "questionnaires" / "45-50.json"
        qpath.write_text(
            json.dumps({"age_range": "45-50", "questions": []}),
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="vide"):
            session_service.load_questionnaire_for_session(
                session["session_id"], base=tmp_path
            )
