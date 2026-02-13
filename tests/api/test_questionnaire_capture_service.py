"""Tests for the questionnaire-capture service module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _write_session(base: Path, session_id: str, status: str = "active") -> None:
    sessions_dir = base / "data" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    session = {
        "session_id": session_id,
        "age_range": "45-50",
        "created_at": "2026-02-10T10:00:00",
        "status": status,
        "metadata": {"pharmacie": {"nom_pharmacie": "Test"}},
    }
    (sessions_dir / f"{session_id}.json").write_text(
        json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _valid_responses() -> list:
    return [
        {"question_id": "q1", "type": "boolean", "value": True},
        {"question_id": "q2", "type": "single_choice", "value": "Option A"},
        {"question_id": "q3", "type": "short_text", "value": "Some text"},
    ]


# ---------------------------------------------------------------------------
# TestValidateResponses
# ---------------------------------------------------------------------------


class TestValidateResponses:
    def test_valid_responses(self, capture_service):
        errors = capture_service.validate_responses(_valid_responses())
        assert errors == []

    def test_not_a_list(self, capture_service):
        errors = capture_service.validate_responses("not a list")
        assert any("liste" in e.lower() for e in errors)

    def test_missing_question_id(self, capture_service):
        responses = [{"value": True}]
        errors = capture_service.validate_responses(responses)
        assert any("question_id" in e for e in errors)

    def test_missing_value(self, capture_service):
        responses = [{"question_id": "q1"}]
        errors = capture_service.validate_responses(responses)
        assert any("value" in e for e in errors)

    def test_invalid_response_format(self, capture_service):
        responses = ["not a dict"]
        errors = capture_service.validate_responses(responses)
        assert any("invalide" in e.lower() for e in errors)

    def test_empty_list_is_valid(self, capture_service):
        errors = capture_service.validate_responses([])
        assert errors == []

    def test_multiple_errors(self, capture_service):
        responses = [
            {"question_id": "q1"},  # missing value
            {"value": True},  # missing question_id
        ]
        errors = capture_service.validate_responses(responses)
        assert len(errors) == 2


# ---------------------------------------------------------------------------
# TestSaveResponses
# ---------------------------------------------------------------------------


class TestSaveResponses:
    def test_saves_responses_file(self, capture_service, tmp_path):
        _write_session(tmp_path, "sess-1")
        capture_service.save_responses(
            "sess-1", _valid_responses(), base=tmp_path
        )
        path = tmp_path / "data" / "sessions" / "sess-1_responses.json"
        assert path.is_file()

    def test_returns_record_with_correct_structure(
        self, capture_service, tmp_path
    ):
        _write_session(tmp_path, "sess-1")
        record = capture_service.save_responses(
            "sess-1", _valid_responses(), base=tmp_path
        )
        assert record["session_id"] == "sess-1"
        assert record["responses_count"] == 3
        assert len(record["responses"]) == 3
        assert "submitted_at" in record

    def test_uses_provided_submitted_at(self, capture_service, tmp_path):
        _write_session(tmp_path, "sess-1")
        record = capture_service.save_responses(
            "sess-1",
            _valid_responses(),
            submitted_at="2026-02-10T12:00:00",
            base=tmp_path,
        )
        assert record["submitted_at"] == "2026-02-10T12:00:00"

    def test_generates_submitted_at_when_absent(
        self, capture_service, tmp_path
    ):
        _write_session(tmp_path, "sess-1")
        record = capture_service.save_responses(
            "sess-1", _valid_responses(), base=tmp_path
        )
        assert record["submitted_at"]  # not empty

    def test_file_content_matches_return(self, capture_service, tmp_path):
        _write_session(tmp_path, "sess-1")
        record = capture_service.save_responses(
            "sess-1", _valid_responses(), base=tmp_path
        )
        path = tmp_path / "data" / "sessions" / "sess-1_responses.json"
        on_disk = json.loads(path.read_text(encoding="utf-8"))
        assert on_disk == record

    def test_raises_when_session_not_found(self, capture_service, tmp_path):
        with pytest.raises(ValueError, match="inconnue"):
            capture_service.save_responses(
                "no-such-session", _valid_responses(), base=tmp_path
            )

    def test_raises_when_session_inactive(self, capture_service, tmp_path):
        _write_session(tmp_path, "sess-1", status="closed")
        with pytest.raises(ValueError, match="inactive"):
            capture_service.save_responses(
                "sess-1", _valid_responses(), base=tmp_path
            )

    def test_raises_when_responses_invalid(self, capture_service, tmp_path):
        _write_session(tmp_path, "sess-1")
        with pytest.raises(ValueError, match="invalides"):
            capture_service.save_responses(
                "sess-1", [{"bad": "format"}], base=tmp_path
            )

    def test_responses_are_stored_as_is(self, capture_service, tmp_path):
        _write_session(tmp_path, "sess-1")
        responses = [
            {"question_id": "q1", "type": "boolean", "value": True},
        ]
        record = capture_service.save_responses(
            "sess-1", responses, base=tmp_path
        )
        assert record["responses"][0]["value"] is True
        assert record["responses"][0]["question_id"] == "q1"


# ---------------------------------------------------------------------------
# TestLoadResponses
# ---------------------------------------------------------------------------


class TestLoadResponses:
    def test_loads_saved_responses(self, capture_service, tmp_path):
        _write_session(tmp_path, "sess-1")
        saved = capture_service.save_responses(
            "sess-1", _valid_responses(), base=tmp_path
        )
        loaded = capture_service.load_responses("sess-1", base=tmp_path)
        assert loaded == saved

    def test_returns_none_when_no_responses(self, capture_service, tmp_path):
        result = capture_service.load_responses("no-such", base=tmp_path)
        assert result is None

    def test_returns_none_when_file_corrupt(self, capture_service, tmp_path):
        sessions_dir = tmp_path / "data" / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        (sessions_dir / "bad_responses.json").write_text(
            "{invalid", encoding="utf-8"
        )
        result = capture_service.load_responses("bad", base=tmp_path)
        assert result is None
