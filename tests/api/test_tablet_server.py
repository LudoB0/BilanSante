"""Tests for the tablet_server Flask app."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _full_settings(**overrides) -> dict:
    data = {
        "nom_pharmacie": "Pharmacie Test",
        "adresse": "1 rue de Test",
        "code_postal": "75001",
        "ville": "Paris",
        "telephone": "0102030405",
        "fournisseur_ia": "openai",
        "cle_api": "sk-test-key-123",
    }
    data.update(overrides)
    return data


def _write_settings(base: Path, data: dict | None = None) -> None:
    cfg = base / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "settings.json").write_text(
        json.dumps(data or _full_settings(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _write_logo(base: Path) -> None:
    img_dir = base / "config" / "img"
    img_dir.mkdir(parents=True, exist_ok=True)
    (img_dir / "logo.png").write_bytes(b"png-bytes")


def _write_questionnaire(base: Path, age_range: str = "45-50") -> None:
    qdir = base / "config" / "questionnaires"
    qdir.mkdir(parents=True, exist_ok=True)
    data = {
        "age_range": age_range,
        "version": 1,
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00",
        "questions": [
            {
                "id": "q1",
                "order": 0,
                "type": "boolean",
                "label": "Test question ?",
                "required": True,
                "sex_target": "M",
                "options": [],
                "scale_config": None,
            },
            {
                "id": "q2",
                "order": 1,
                "type": "single_choice",
                "label": "Choix ?",
                "required": True,
                "sex_target": "M",
                "options": ["Option A", "Option B"],
                "scale_config": None,
            },
        ],
    }
    (qdir / f"{age_range}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _setup_valid_env(base: Path) -> None:
    _write_settings(base)
    _write_logo(base)
    _write_questionnaire(base)


def _create_session_and_qr(svc, base: Path, sex: str = "H") -> tuple[dict, dict]:
    """Create a valid session and generate QR data."""
    session = svc.create_session("45-50", sex, base=base)
    qr = svc.generate_qr_data(session["session_id"], base=base)
    return session, qr


@pytest.fixture
def app_with_env(tmp_path, session_service, tablet_server_module):
    """Set up a valid environment and return (Flask test client, session, qr_data)."""
    _setup_valid_env(tmp_path)
    session, qr = _create_session_and_qr(session_service, tmp_path)
    app = tablet_server_module.create_app(base=tmp_path)
    app.config["TESTING"] = True
    client = app.test_client()
    return client, session, qr, tmp_path


# ---------------------------------------------------------------------------
# TestGetQuestionnaire
# ---------------------------------------------------------------------------


class TestGetQuestionnaire:
    def test_valid_qr_returns_200(self, app_with_env):
        client, session, qr, _ = app_with_env
        resp = client.get(
            f"/questionnaire?v=1&sid={session['session_id']}"
            f"&t={qr['token']}&sig={qr['signature']}"
        )
        assert resp.status_code == 200
        assert b"text/html" in resp.content_type.encode()

    def test_page_contains_questionnaire(self, app_with_env):
        client, session, qr, _ = app_with_env
        resp = client.get(
            f"/questionnaire?v=1&sid={session['session_id']}"
            f"&t={qr['token']}&sig={qr['signature']}"
        )
        html = resp.data.decode("utf-8")
        assert "Test question" in html
        assert "Choix" in html
        assert "Option A" in html
        assert "Option B" in html

    def test_page_contains_pharmacy_name(self, app_with_env):
        client, session, qr, _ = app_with_env
        resp = client.get(
            f"/questionnaire?v=1&sid={session['session_id']}"
            f"&t={qr['token']}&sig={qr['signature']}"
        )
        html = resp.data.decode("utf-8")
        assert "Pharmacie Test" in html

    def test_page_contains_session_id_for_submit(self, app_with_env):
        client, session, qr, _ = app_with_env
        resp = client.get(
            f"/questionnaire?v=1&sid={session['session_id']}"
            f"&t={qr['token']}&sig={qr['signature']}"
        )
        html = resp.data.decode("utf-8")
        assert session["session_id"] in html

    def test_missing_params_returns_403(self, app_with_env):
        client, _, _, _ = app_with_env
        resp = client.get("/questionnaire")
        assert resp.status_code == 403

    def test_missing_sid_returns_403(self, app_with_env):
        client, _, qr, _ = app_with_env
        resp = client.get(
            f"/questionnaire?v=1&t={qr['token']}&sig={qr['signature']}"
        )
        assert resp.status_code == 403

    def test_bad_signature_returns_403(self, app_with_env):
        client, session, _, _ = app_with_env
        resp = client.get(
            f"/questionnaire?v=1&sid={session['session_id']}"
            "&t=fake-token&sig=bad-sig"
        )
        assert resp.status_code == 403

    def test_bad_version_returns_403(self, app_with_env):
        client, session, qr, _ = app_with_env
        resp = client.get(
            f"/questionnaire?v=99&sid={session['session_id']}"
            f"&t={qr['token']}&sig={qr['signature']}"
        )
        assert resp.status_code == 403

    def test_unknown_session_returns_403(self, app_with_env):
        client, _, qr, _ = app_with_env
        resp = client.get(
            f"/questionnaire?v=1&sid=nonexistent"
            f"&t={qr['token']}&sig={qr['signature']}"
        )
        assert resp.status_code == 403

    def test_inactive_session_returns_403(self, app_with_env):
        client, session, qr, tmp_path = app_with_env
        session_path = (
            tmp_path / "data" / "sessions" / f"{session['session_id']}.json"
        )
        data = json.loads(session_path.read_text(encoding="utf-8"))
        data["status"] = "closed"
        session_path.write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )
        resp = client.get(
            f"/questionnaire?v=1&sid={session['session_id']}"
            f"&t={qr['token']}&sig={qr['signature']}"
        )
        assert resp.status_code == 403

    def test_missing_questionnaire_returns_404(self, app_with_env):
        client, session, qr, tmp_path = app_with_env
        (tmp_path / "config" / "questionnaires" / "45-50.json").unlink()
        resp = client.get(
            f"/questionnaire?v=1&sid={session['session_id']}"
            f"&t={qr['token']}&sig={qr['signature']}"
        )
        assert resp.status_code == 404

    def test_error_page_shows_message(self, app_with_env):
        client, _, _, _ = app_with_env
        resp = client.get("/questionnaire?v=1&sid=x&t=y&sig=z")
        html = resp.data.decode("utf-8")
        assert "Acces non autorise" in html

    def test_successful_load_adds_to_loaded_sessions(
        self, app_with_env, tablet_server_module
    ):
        client, session, qr, _ = app_with_env
        sid = session["session_id"]
        tablet_server_module.loaded_sessions.discard(sid)
        resp = client.get(
            f"/questionnaire?v=1&sid={sid}"
            f"&t={qr['token']}&sig={qr['signature']}"
        )
        assert resp.status_code == 200
        assert sid in tablet_server_module.loaded_sessions

    def test_failed_load_does_not_add_to_loaded_sessions(
        self, app_with_env, tablet_server_module
    ):
        client, _, _, _ = app_with_env
        tablet_server_module.loaded_sessions.clear()
        client.get("/questionnaire?v=1&sid=x&t=y&sig=z")
        assert "x" not in tablet_server_module.loaded_sessions

    def test_filters_questions_by_sex_target(
        self, tmp_path, session_service, tablet_server_module
    ):
        """Questions whose sex_target != session.sex and != 'M' are excluded."""
        _write_settings(tmp_path)
        _write_logo(tmp_path)
        # Questionnaire with mixed sex_target
        qdir = tmp_path / "config" / "questionnaires"
        qdir.mkdir(parents=True, exist_ok=True)
        data = {
            "age_range": "45-50",
            "version": 1,
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:00",
            "questions": [
                {"id": "q1", "order": 0, "type": "boolean", "label": "Mixte ?",
                 "required": True, "sex_target": "M", "options": [], "scale_config": None},
                {"id": "q2", "order": 1, "type": "boolean", "label": "Hommes seulement ?",
                 "required": True, "sex_target": "H", "options": [], "scale_config": None},
                {"id": "q3", "order": 2, "type": "boolean", "label": "Femmes seulement ?",
                 "required": True, "sex_target": "F", "options": [], "scale_config": None},
            ],
        }
        (qdir / "45-50.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        # Session with sex=H
        session, qr = _create_session_and_qr(session_service, tmp_path, sex="H")
        app = tablet_server_module.create_app(base=tmp_path)
        app.config["TESTING"] = True
        client = app.test_client()

        resp = client.get(
            f"/questionnaire?v=1&sid={session['session_id']}"
            f"&t={qr['token']}&sig={qr['signature']}"
        )
        html = resp.data.decode("utf-8")
        assert "Mixte" in html
        assert "Hommes seulement" in html
        assert "Femmes seulement" not in html

    def test_session_without_sex_returns_403(
        self, tmp_path, session_service, tablet_server_module
    ):
        """A session without a sex field should return 403."""
        _setup_valid_env(tmp_path)
        session, qr = _create_session_and_qr(session_service, tmp_path)
        # Remove sex from the session file
        session_path = (
            tmp_path / "data" / "sessions" / f"{session['session_id']}.json"
        )
        data = json.loads(session_path.read_text(encoding="utf-8"))
        data.pop("sex", None)
        session_path.write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )
        app = tablet_server_module.create_app(base=tmp_path)
        app.config["TESTING"] = True
        client = app.test_client()

        resp = client.get(
            f"/questionnaire?v=1&sid={session['session_id']}"
            f"&t={qr['token']}&sig={qr['signature']}"
        )
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# TestPostSubmit
# ---------------------------------------------------------------------------


class TestPostSubmit:
    def test_valid_submission_returns_200(self, app_with_env):
        client, session, _, _ = app_with_env
        resp = client.post(
            "/questionnaire/submit",
            json={
                "sid": session["session_id"],
                "submitted_at": "2026-02-10T12:00:00",
                "responses": [
                    {"question_id": "q1", "type": "boolean", "value": True},
                ],
            },
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["session_id"] == session["session_id"]
        assert data["responses_count"] == 1

    def test_persists_responses_to_disk(self, app_with_env):
        client, session, _, tmp_path = app_with_env
        client.post(
            "/questionnaire/submit",
            json={
                "sid": session["session_id"],
                "submitted_at": "2026-02-10T12:00:00",
                "responses": [
                    {"question_id": "q1", "type": "boolean", "value": True},
                ],
            },
        )
        path = (
            tmp_path
            / "data"
            / "sessions"
            / f"{session['session_id']}_responses.json"
        )
        assert path.is_file()

    def test_missing_sid_returns_400(self, app_with_env):
        client, _, _, _ = app_with_env
        resp = client.post(
            "/questionnaire/submit",
            json={"responses": []},
        )
        assert resp.status_code == 400

    def test_missing_responses_returns_400(self, app_with_env):
        client, session, _, _ = app_with_env
        resp = client.post(
            "/questionnaire/submit",
            json={"sid": session["session_id"]},
        )
        assert resp.status_code == 400

    def test_invalid_json_returns_400(self, app_with_env):
        client, _, _, _ = app_with_env
        resp = client.post(
            "/questionnaire/submit",
            data="not json",
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_unknown_session_returns_400(self, app_with_env):
        client, _, _, _ = app_with_env
        resp = client.post(
            "/questionnaire/submit",
            json={
                "sid": "nonexistent",
                "responses": [
                    {"question_id": "q1", "value": True},
                ],
            },
        )
        assert resp.status_code == 400

    def test_invalid_responses_structure_returns_400(self, app_with_env):
        client, session, _, _ = app_with_env
        resp = client.post(
            "/questionnaire/submit",
            json={
                "sid": session["session_id"],
                "responses": [{"bad": "format"}],
            },
        )
        assert resp.status_code == 400

    def test_response_contains_submitted_at(self, app_with_env):
        client, session, _, _ = app_with_env
        resp = client.post(
            "/questionnaire/submit",
            json={
                "sid": session["session_id"],
                "submitted_at": "2026-02-10T12:00:00",
                "responses": [
                    {"question_id": "q1", "value": True},
                ],
            },
        )
        data = resp.get_json()
        assert data["submitted_at"] == "2026-02-10T12:00:00"

    def test_responses_stored_as_is(self, app_with_env):
        client, session, _, _ = app_with_env
        responses = [
            {"question_id": "q1", "type": "boolean", "value": True},
            {"question_id": "q2", "type": "single_choice", "value": "Option A"},
        ]
        resp = client.post(
            "/questionnaire/submit",
            json={
                "sid": session["session_id"],
                "responses": responses,
            },
        )
        data = resp.get_json()
        assert data["responses"] == responses
