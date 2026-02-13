"""Tests for bilan-assembly service (BuildQuestionnaireSummarySection)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_session(
    tmp_path: Path, session_id: str, age_range: str = "45-50", sex: str = "H",
):
    """Create a minimal session file."""
    sessions_dir = tmp_path / "data" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    session = {
        "session_id": session_id,
        "age_range": age_range,
        "sex": sex,
        "created_at": "2026-02-10T10:00:00",
        "status": "active",
        "metadata": {"pharmacie": {"nom_pharmacie": "Pharmacie Test"}},
    }
    with open(sessions_dir / f"{session_id}.json", "w", encoding="utf-8") as fh:
        json.dump(session, fh, ensure_ascii=False, indent=2)
    return session


def _create_responses(
    tmp_path: Path,
    session_id: str,
    responses: list | None = None,
):
    """Create a responses file."""
    sessions_dir = tmp_path / "data" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    if responses is None:
        responses = [
            {"question_id": "q1", "type": "single_choice", "value": "Un homme"},
            {"question_id": "q2", "type": "boolean", "value": True},
            {"question_id": "q3", "type": "multiple_choice", "value": ["A", "B"]},
            {"question_id": "q4", "type": "short_text", "value": "Some text"},
            {"question_id": "q5", "type": "scale", "value": 7},
        ]
    record = {
        "session_id": session_id,
        "submitted_at": "2026-02-10T10:05:00",
        "responses_count": len(responses),
        "responses": responses,
    }
    with open(
        sessions_dir / f"{session_id}_responses.json", "w", encoding="utf-8"
    ) as fh:
        json.dump(record, fh, ensure_ascii=False, indent=2)
    return record


def _create_questionnaire(
    tmp_path: Path,
    age_range: str = "45-50",
    questions: list | None = None,
):
    """Create a questionnaire source file."""
    q_dir = tmp_path / "config" / "questionnaires"
    q_dir.mkdir(parents=True, exist_ok=True)
    if questions is None:
        questions = [
            {"id": "q1", "order": 0, "type": "single_choice", "label": "Genre", "options": ["Un homme", "Une femme"]},
            {"id": "q2", "order": 1, "type": "boolean", "label": "Enfants a la maison", "options": []},
            {"id": "q3", "order": 2, "type": "multiple_choice", "label": "Maladies", "options": ["A", "B", "C"]},
            {"id": "q4", "order": 3, "type": "short_text", "label": "Precisions", "options": []},
            {"id": "q5", "order": 4, "type": "scale", "label": "Bien-etre", "options": [], "scale_config": {"min": 1, "max": 10, "step": 1}},
        ]
    questionnaire = {
        "age_range": age_range,
        "version": 1,
        "questions": questions,
    }
    with open(q_dir / f"{age_range}.json", "w", encoding="utf-8") as fh:
        json.dump(questionnaire, fh, ensure_ascii=False, indent=2)
    return questionnaire


SID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"


# ---------------------------------------------------------------------------
# Tests: format_response_value
# ---------------------------------------------------------------------------


class TestFormatResponseValue:
    def test_boolean_true(self, bilan_assembly_service):
        assert bilan_assembly_service.format_response_value(True, "boolean") == "Oui"

    def test_boolean_false(self, bilan_assembly_service):
        assert bilan_assembly_service.format_response_value(False, "boolean") == "Non"

    def test_boolean_none(self, bilan_assembly_service):
        assert bilan_assembly_service.format_response_value(None, "boolean") == "non renseigne"

    def test_single_choice(self, bilan_assembly_service):
        assert bilan_assembly_service.format_response_value("Un homme", "single_choice") == "Un homme"

    def test_single_choice_empty(self, bilan_assembly_service):
        assert bilan_assembly_service.format_response_value("", "single_choice") == "non renseigne"

    def test_single_choice_none(self, bilan_assembly_service):
        assert bilan_assembly_service.format_response_value(None, "single_choice") == "non renseigne"

    def test_multiple_choice_list(self, bilan_assembly_service):
        assert bilan_assembly_service.format_response_value(["A", "B"], "multiple_choice") == "A, B"

    def test_multiple_choice_empty_list(self, bilan_assembly_service):
        assert bilan_assembly_service.format_response_value([], "multiple_choice") == "non renseigne"

    def test_multiple_choice_none(self, bilan_assembly_service):
        assert bilan_assembly_service.format_response_value(None, "multiple_choice") == "non renseigne"

    def test_short_text(self, bilan_assembly_service):
        assert bilan_assembly_service.format_response_value("Some text", "short_text") == "Some text"

    def test_short_text_empty(self, bilan_assembly_service):
        assert bilan_assembly_service.format_response_value("", "short_text") == "non renseigne"

    def test_short_text_whitespace(self, bilan_assembly_service):
        assert bilan_assembly_service.format_response_value("  ", "short_text") == "non renseigne"

    def test_scale_value(self, bilan_assembly_service):
        assert bilan_assembly_service.format_response_value(7, "scale") == "7"

    def test_scale_none(self, bilan_assembly_service):
        assert bilan_assembly_service.format_response_value(None, "scale") == "non renseigne"


# ---------------------------------------------------------------------------
# Tests: build_questionnaire_summary
# ---------------------------------------------------------------------------


class TestBuildQuestionnaireSummary:
    def test_success(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)

        assert result["session_id"] == SID
        assert result["short_id"] == "a1b2c3d4"
        assert result["age_range"] == "45-50"
        assert len(result["items"]) == 5
        assert result["md_path"] is not None

    def test_items_structure(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        item = result["items"][0]

        assert "question_id" in item
        assert "label" in item
        assert "type" in item
        assert "options" in item
        assert "response_value" in item
        assert "response_display" in item

    def test_items_values(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        items = result["items"]

        assert items[0]["response_display"] == "Un homme"
        assert items[1]["response_display"] == "Oui"
        assert items[2]["response_display"] == "A, B"
        assert items[3]["response_display"] == "Some text"
        assert items[4]["response_display"] == "7"

    def test_unknown_session(self, bilan_assembly_service, tmp_path):
        with pytest.raises(ValueError, match="Session inconnue"):
            bilan_assembly_service.build_questionnaire_summary("unknown", base=tmp_path)

    def test_missing_responses(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_questionnaire(tmp_path)

        with pytest.raises(ValueError, match="Fichier reponses absent"):
            bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)

    def test_missing_questionnaire(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)

        with pytest.raises(ValueError, match="Questionnaire source absent"):
            bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)

    def test_empty_questionnaire(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path, questions=[])

        with pytest.raises(ValueError, match="Questionnaire vide"):
            bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)

    def test_session_without_age_range(self, bilan_assembly_service, tmp_path):
        sessions_dir = tmp_path / "data" / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        session = {"session_id": SID, "status": "active"}
        with open(sessions_dir / f"{SID}.json", "w", encoding="utf-8") as fh:
            json.dump(session, fh)

        with pytest.raises(ValueError, match="Session sans tranche d'age"):
            bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)

    def test_missing_response_for_question(self, bilan_assembly_service, tmp_path):
        """A question with no matching response should display 'non renseigne'."""
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID, responses=[
            {"question_id": "q1", "type": "single_choice", "value": "Un homme"},
        ])
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        # q2 has no response
        assert result["items"][1]["response_display"] == "non renseigne"
        assert result["items"][1]["response_value"] is None

    def test_filters_questions_by_sex(self, bilan_assembly_service, tmp_path):
        """Questions whose sex_target doesn't match session sex are excluded."""
        questions = [
            {"id": "q1", "order": 0, "type": "boolean", "label": "Mixte", "sex_target": "M", "options": []},
            {"id": "q2", "order": 1, "type": "boolean", "label": "Hommes", "sex_target": "H", "options": []},
            {"id": "q3", "order": 2, "type": "boolean", "label": "Femmes", "sex_target": "F", "options": []},
        ]
        responses = [
            {"question_id": "q1", "type": "boolean", "value": True},
            {"question_id": "q2", "type": "boolean", "value": False},
            {"question_id": "q3", "type": "boolean", "value": True},
        ]
        _create_session(tmp_path, SID, sex="H")
        _create_responses(tmp_path, SID, responses)
        _create_questionnaire(tmp_path, questions=questions)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        labels = [item["label"] for item in result["items"]]
        assert "Mixte" in labels
        assert "Hommes" in labels
        assert "Femmes" not in labels

    def test_no_filter_when_session_has_no_sex(self, bilan_assembly_service, tmp_path):
        """Old sessions without sex field should show all questions (retrocompat)."""
        questions = [
            {"id": "q1", "order": 0, "type": "boolean", "label": "Mixte", "sex_target": "M", "options": []},
            {"id": "q2", "order": 1, "type": "boolean", "label": "Femmes", "sex_target": "F", "options": []},
        ]
        responses = [
            {"question_id": "q1", "type": "boolean", "value": True},
            {"question_id": "q2", "type": "boolean", "value": True},
        ]
        # Create session without sex field
        sessions_dir = tmp_path / "data" / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        session = {
            "session_id": SID,
            "age_range": "45-50",
            "created_at": "2026-02-10T10:00:00",
            "status": "active",
            "metadata": {"pharmacie": {"nom_pharmacie": "Pharmacie Test"}},
        }
        with open(sessions_dir / f"{SID}.json", "w", encoding="utf-8") as fh:
            json.dump(session, fh, ensure_ascii=False, indent=2)
        _create_responses(tmp_path, SID, responses)
        _create_questionnaire(tmp_path, questions=questions)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        assert len(result["items"]) == 2


# ---------------------------------------------------------------------------
# Tests: markdown file generation
# ---------------------------------------------------------------------------


class TestMarkdownGeneration:
    def test_creates_file(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        md_path = Path(result["md_path"])

        assert md_path.is_file()

    def test_file_name(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        md_path = Path(result["md_path"])

        assert md_path.name == "QuestionnaireComplet_a1b2c3d4.md"

    def test_file_in_sessions_dir(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        md_path = Path(result["md_path"])

        assert md_path.parent == tmp_path / "data" / "sessions"

    def test_markdown_contains_title(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        content = Path(result["md_path"]).read_text(encoding="utf-8")

        assert "# Questionnaire Complet - Session a1b2c3d4" in content

    def test_markdown_contains_session_id(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        content = Path(result["md_path"]).read_text(encoding="utf-8")

        assert f"**Session**: {SID}" in content

    def test_markdown_contains_age_range(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        content = Path(result["md_path"]).read_text(encoding="utf-8")

        assert "**Tranche d'age**: 45-50 ans" in content

    def test_markdown_contains_questions(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        content = Path(result["md_path"]).read_text(encoding="utf-8")

        assert "## 1. Genre" in content
        assert "## 2. Enfants a la maison" in content

    def test_markdown_contains_responses(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        content = Path(result["md_path"]).read_text(encoding="utf-8")

        assert "**Reponse**: Un homme" in content
        assert "**Reponse**: Oui" in content

    def test_markdown_contains_pharmacist_note_placeholders(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        content = Path(result["md_path"]).read_text(encoding="utf-8")

        assert content.count("_Notes pharmacien:_") == 5

    def test_markdown_contains_raport_section(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        content = Path(result["md_path"]).read_text(encoding="utf-8")

        assert "## Rapport du pharmacien" in content

    def test_short_id_length(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)

        assert len(result["short_id"]) == 8
        assert result["short_id"] == SID[:8]

    def test_markdown_contains_mesures_section(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        content = Path(result["md_path"]).read_text(encoding="utf-8")

        assert "## Mesures patient" in content

    def test_markdown_contains_tension_placeholder(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        content = Path(result["md_path"]).read_text(encoding="utf-8")

        assert "**Tension (mmHg)**:" in content


# ---------------------------------------------------------------------------
# Tests: _parse_numeric
# ---------------------------------------------------------------------------


class TestParseNumeric:
    def test_integer(self, bilan_assembly_service):
        assert bilan_assembly_service._parse_numeric(75) == 75.0

    def test_float_dot(self, bilan_assembly_service):
        assert bilan_assembly_service._parse_numeric("1.75") == 1.75

    def test_float_comma(self, bilan_assembly_service):
        assert bilan_assembly_service._parse_numeric("1,75") == 1.75

    def test_string_integer(self, bilan_assembly_service):
        assert bilan_assembly_service._parse_numeric("80") == 80.0

    def test_none(self, bilan_assembly_service):
        assert bilan_assembly_service._parse_numeric(None) is None

    def test_empty_string(self, bilan_assembly_service):
        assert bilan_assembly_service._parse_numeric("") is None

    def test_non_numeric_string(self, bilan_assembly_service):
        assert bilan_assembly_service._parse_numeric("abc") is None

    def test_zero(self, bilan_assembly_service):
        assert bilan_assembly_service._parse_numeric(0) is None

    def test_negative(self, bilan_assembly_service):
        assert bilan_assembly_service._parse_numeric(-5) is None

    def test_whitespace_around(self, bilan_assembly_service):
        assert bilan_assembly_service._parse_numeric("  80  ") == 80.0


# ---------------------------------------------------------------------------
# Tests: _extract_metrics / IMC
# ---------------------------------------------------------------------------


def _questions_with_poids_taille():
    """Questionnaire with obligatoire1 (poids) and Obligatoire2 (taille)."""
    return [
        {"id": "q1", "order": 0, "type": "single_choice", "label": "Genre", "options": ["Un homme", "Une femme"]},
        {"id": "obligatoire1", "order": 1, "type": "short_text", "label": "Indiquer votre poids (en Kg)", "options": []},
        {"id": "Obligatoire2", "order": 2, "type": "short_text", "label": "Indiquer votre taille (en m)", "options": []},
    ]


def _responses_with_poids_taille(poids_val, taille_val):
    """Build responses list with poids and taille values."""
    return [
        {"question_id": "q1", "type": "single_choice", "value": "Un homme"},
        {"question_id": "obligatoire1", "type": "short_text", "value": poids_val},
        {"question_id": "Obligatoire2", "type": "short_text", "value": taille_val},
    ]


class TestExtractMetrics:
    def test_imc_calculation(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID, _responses_with_poids_taille("80", "1.75"))
        _create_questionnaire(tmp_path, questions=_questions_with_poids_taille())

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        metrics = result["metrics"]

        assert metrics["poids_kg"] == 80.0
        assert metrics["taille_m"] == 1.75
        expected_imc = 80.0 / (1.75 ** 2)
        assert metrics["imc"] == pytest.approx(expected_imc, rel=1e-2)
        assert metrics["imc_display"] == f"{expected_imc:.1f}"

    def test_imc_with_comma(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID, _responses_with_poids_taille("80", "1,75"))
        _create_questionnaire(tmp_path, questions=_questions_with_poids_taille())

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        metrics = result["metrics"]

        assert metrics["taille_m"] == 1.75
        assert metrics["imc"] is not None

    def test_imc_poids_missing(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID, [
            {"question_id": "q1", "type": "single_choice", "value": "Un homme"},
            {"question_id": "Obligatoire2", "type": "short_text", "value": "1.75"},
        ])
        _create_questionnaire(tmp_path, questions=_questions_with_poids_taille())

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        metrics = result["metrics"]

        assert metrics["poids_kg"] is None
        assert metrics["imc"] is None
        assert metrics["imc_display"] == "non calculable"

    def test_imc_taille_missing(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID, [
            {"question_id": "q1", "type": "single_choice", "value": "Un homme"},
            {"question_id": "obligatoire1", "type": "short_text", "value": "80"},
        ])
        _create_questionnaire(tmp_path, questions=_questions_with_poids_taille())

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        metrics = result["metrics"]

        assert metrics["taille_m"] is None
        assert metrics["imc"] is None
        assert metrics["imc_display"] == "non calculable"

    def test_imc_non_numeric_poids(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID, _responses_with_poids_taille("abc", "1.75"))
        _create_questionnaire(tmp_path, questions=_questions_with_poids_taille())

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        metrics = result["metrics"]

        assert metrics["poids_kg"] is None
        assert metrics["imc"] is None
        assert metrics["imc_display"] == "non calculable"

    def test_imc_taille_zero(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID, _responses_with_poids_taille("80", "0"))
        _create_questionnaire(tmp_path, questions=_questions_with_poids_taille())

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        metrics = result["metrics"]

        assert metrics["taille_m"] is None
        assert metrics["imc"] is None
        assert metrics["imc_display"] == "non calculable"

    def test_imc_fallback_on_label(self, bilan_assembly_service, tmp_path):
        """When question IDs are not q12/q13, fallback on label containing poids/taille."""
        questions = [
            {"id": "a1", "order": 0, "type": "short_text", "label": "Votre poids en kg", "options": []},
            {"id": "a2", "order": 1, "type": "short_text", "label": "Votre taille en metres", "options": []},
        ]
        responses = [
            {"question_id": "a1", "type": "short_text", "value": "70"},
            {"question_id": "a2", "type": "short_text", "value": "1.80"},
        ]
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID, responses)
        _create_questionnaire(tmp_path, questions=questions)

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        metrics = result["metrics"]

        assert metrics["poids_kg"] == 70.0
        assert metrics["taille_m"] == 1.80
        assert metrics["imc"] is not None

    def test_metrics_in_markdown(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID, _responses_with_poids_taille("80", "1.75"))
        _create_questionnaire(tmp_path, questions=_questions_with_poids_taille())

        result = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        content = Path(result["md_path"]).read_text(encoding="utf-8")

        assert "**Poids (kg)**: 80.0" in content
        assert "**Taille (m)**: 1.75" in content
        assert "**IMC**:" in content


# ---------------------------------------------------------------------------
# Tests: capture_interview_notes
# ---------------------------------------------------------------------------


class TestCaptureInterviewNotes:
    def test_captures_notes_into_markdown(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.capture_interview_notes(
            session_id=SID,
            pharmacist_notes={"q1": "Note pour q1", "q3": "Note pour q3"},
            pharmacist_blood_pressure="120/80",
            pharmacist_report="Mon rapport pharmacien",
            base=tmp_path,
        )

        content = Path(result["md_path"]).read_text(encoding="utf-8")
        assert "Note pour q1" in content
        assert "Note pour q3" in content
        assert "120/80" in content
        assert "Mon rapport pharmacien" in content

    def test_returns_session_id_and_short_id(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.capture_interview_notes(
            session_id=SID,
            pharmacist_notes={},
            pharmacist_blood_pressure="",
            pharmacist_report="",
            base=tmp_path,
        )

        assert result["session_id"] == SID
        assert result["short_id"] == SID[:8]
        assert result["md_path"] is not None

    def test_overwrites_existing_markdown(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        # First build without notes
        first = bilan_assembly_service.build_questionnaire_summary(SID, base=tmp_path)
        content_before = Path(first["md_path"]).read_text(encoding="utf-8")
        assert "Note specifique" not in content_before

        # Capture with notes
        bilan_assembly_service.capture_interview_notes(
            session_id=SID,
            pharmacist_notes={"q1": "Note specifique"},
            pharmacist_blood_pressure="",
            pharmacist_report="",
            base=tmp_path,
        )
        content_after = Path(first["md_path"]).read_text(encoding="utf-8")
        assert "Note specifique" in content_after

    def test_empty_notes_produces_valid_markdown(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.capture_interview_notes(
            session_id=SID,
            pharmacist_notes={},
            pharmacist_blood_pressure="",
            pharmacist_report="",
            base=tmp_path,
        )

        content = Path(result["md_path"]).read_text(encoding="utf-8")
        assert "## Rapport du pharmacien" in content
        assert "## Mesures patient" in content

    def test_raises_on_unknown_session(self, bilan_assembly_service, tmp_path):
        with pytest.raises(ValueError, match="Session inconnue"):
            bilan_assembly_service.capture_interview_notes(
                session_id="unknown",
                pharmacist_notes={},
                pharmacist_blood_pressure="",
                pharmacist_report="",
                base=tmp_path,
            )

    def test_raises_on_missing_responses(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_questionnaire(tmp_path)

        with pytest.raises(ValueError, match="Fichier reponses absent"):
            bilan_assembly_service.capture_interview_notes(
                session_id=SID,
                pharmacist_notes={},
                pharmacist_blood_pressure="",
                pharmacist_report="",
                base=tmp_path,
            )

    def test_tension_in_mesures_section(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.capture_interview_notes(
            session_id=SID,
            pharmacist_notes={},
            pharmacist_blood_pressure="130/85",
            pharmacist_report="",
            base=tmp_path,
        )

        content = Path(result["md_path"]).read_text(encoding="utf-8")
        assert "**Tension (mmHg)**: 130/85" in content

    def test_report_in_markdown(self, bilan_assembly_service, tmp_path):
        _create_session(tmp_path, SID)
        _create_responses(tmp_path, SID)
        _create_questionnaire(tmp_path)

        result = bilan_assembly_service.capture_interview_notes(
            session_id=SID,
            pharmacist_notes={},
            pharmacist_blood_pressure="",
            pharmacist_report="Rapport detaille du pharmacien.",
            base=tmp_path,
        )

        content = Path(result["md_path"]).read_text(encoding="utf-8")
        assert "Rapport detaille du pharmacien." in content


# ---------------------------------------------------------------------------
# Helpers: IdentifyVigilancePoints
# ---------------------------------------------------------------------------


def _create_settings(tmp_path: Path, fournisseur="openai", cle_api="sk-test-123", modele_ia=""):
    """Create a minimal settings.json with IA config."""
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "nom_pharmacie": "Pharmacie Test",
        "adresse": "1 rue de Test",
        "code_postal": "75001",
        "ville": "Paris",
        "telephone": "0102030405",
        "fournisseur_ia": fournisseur,
        "cle_api": cle_api,
        "modele_ia": modele_ia,
    }
    with open(config_dir / "settings.json", "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def _create_prompt(tmp_path: Path, content="Identifie les points de vigilance."):
    """Create the promptvigilance.txt file."""
    prompts_dir = tmp_path / "config" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    with open(prompts_dir / "promptvigilance.txt", "w", encoding="utf-8") as fh:
        fh.write(content)


def _create_questionnaire_complet_md(tmp_path: Path, session_id: str):
    """Create a QuestionnaireComplet markdown file."""
    sessions_dir = tmp_path / "data" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    short_id = session_id[:8]
    md_path = sessions_dir / f"QuestionnaireComplet_{short_id}.md"
    md_path.write_text("# Questionnaire Complet\n\nContenu test.\n", encoding="utf-8")
    return md_path


def _create_vigilance_md(tmp_path: Path, session_id: str, content=None):
    """Create a Vigilance markdown file."""
    sessions_dir = tmp_path / "data" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    short_id = session_id[:8]
    md_path = sessions_dir / f"Vigilance_{short_id}.md"
    if content is None:
        content = (
            "# Vigilance - Session {short_id}\n\n"
            "## Points de vigilance\n\n"
            "1. Point A\n2. Point B\n"
        )
    md_path.write_text(content, encoding="utf-8")
    return md_path


# ---------------------------------------------------------------------------
# Tests: _normalize_provider
# ---------------------------------------------------------------------------


class TestNormalizeProvider:
    def test_openia(self, bilan_assembly_service):
        assert bilan_assembly_service._normalize_provider("OpenIA") == "openai"

    def test_openai_lowercase(self, bilan_assembly_service):
        assert bilan_assembly_service._normalize_provider("openai") == "openai"

    def test_anthropic(self, bilan_assembly_service):
        assert bilan_assembly_service._normalize_provider("Anthropic") == "anthropic"

    def test_mistral(self, bilan_assembly_service):
        assert bilan_assembly_service._normalize_provider("Mistral") == "mistral"

    def test_unknown(self, bilan_assembly_service):
        assert bilan_assembly_service._normalize_provider("unknown") == ""

    def test_case_insensitive(self, bilan_assembly_service):
        assert bilan_assembly_service._normalize_provider("ANTHROPIC") == "anthropic"


# ---------------------------------------------------------------------------
# Tests: _resolve_ai_model
# ---------------------------------------------------------------------------


class TestResolveAiModel:
    def test_custom_model(self, bilan_assembly_service):
        assert bilan_assembly_service._resolve_ai_model("openai", "gpt-4") == "gpt-4"

    def test_default_openai(self, bilan_assembly_service):
        assert bilan_assembly_service._resolve_ai_model("openai", "") == "gpt-4o-mini"

    def test_default_anthropic(self, bilan_assembly_service):
        result = bilan_assembly_service._resolve_ai_model("anthropic", "")
        assert result == "claude-sonnet-4-5-20250929"

    def test_default_mistral(self, bilan_assembly_service):
        assert bilan_assembly_service._resolve_ai_model("mistral", "") == "mistral-small-latest"

    def test_whitespace_only_uses_default(self, bilan_assembly_service):
        assert bilan_assembly_service._resolve_ai_model("openai", "   ") == "gpt-4o-mini"

    def test_eco_tier_openai(self, bilan_assembly_service):
        assert bilan_assembly_service._resolve_ai_model("openai", "eco") == "gpt-4o-mini"

    def test_eco_tier_anthropic(self, bilan_assembly_service):
        assert bilan_assembly_service._resolve_ai_model("anthropic", "eco") == "claude-sonnet-4-5-20250929"

    def test_eco_tier_mistral(self, bilan_assembly_service):
        assert bilan_assembly_service._resolve_ai_model("mistral", "eco") == "mistral-small-latest"

    def test_performant_tier_openai(self, bilan_assembly_service):
        assert bilan_assembly_service._resolve_ai_model("openai", "performant") == "gpt-4o"

    def test_performant_tier_anthropic(self, bilan_assembly_service):
        assert bilan_assembly_service._resolve_ai_model("anthropic", "performant") == "claude-opus-4-20250514"

    def test_performant_tier_mistral(self, bilan_assembly_service):
        assert bilan_assembly_service._resolve_ai_model("mistral", "performant") == "mistral-large-latest"

    def test_tier_case_insensitive(self, bilan_assembly_service):
        assert bilan_assembly_service._resolve_ai_model("openai", "Eco") == "gpt-4o-mini"
        assert bilan_assembly_service._resolve_ai_model("openai", "PERFORMANT") == "gpt-4o"


# ---------------------------------------------------------------------------
# Tests: _load_ia_config
# ---------------------------------------------------------------------------


class TestLoadIaConfig:
    def test_loads_valid_config(self, bilan_assembly_service, tmp_path):
        _create_settings(tmp_path, fournisseur="openai", cle_api="sk-test")
        result = bilan_assembly_service._load_ia_config(tmp_path)
        assert result["fournisseur"] == "openai"
        assert result["cle_api"] == "sk-test"

    def test_loads_openia_as_openai(self, bilan_assembly_service, tmp_path):
        _create_settings(tmp_path, fournisseur="OpenIA", cle_api="sk-test")
        result = bilan_assembly_service._load_ia_config(tmp_path)
        assert result["fournisseur"] == "openai"

    def test_raises_on_missing_settings(self, bilan_assembly_service, tmp_path):
        with pytest.raises(ValueError, match="Configuration applicative absente"):
            bilan_assembly_service._load_ia_config(tmp_path)

    def test_raises_on_missing_fournisseur(self, bilan_assembly_service, tmp_path):
        _create_settings(tmp_path, fournisseur="", cle_api="sk-test")
        with pytest.raises(ValueError, match="Fournisseur IA non configure"):
            bilan_assembly_service._load_ia_config(tmp_path)

    def test_raises_on_unsupported_fournisseur(self, bilan_assembly_service, tmp_path):
        _create_settings(tmp_path, fournisseur="unknown_provider", cle_api="sk-test")
        with pytest.raises(ValueError, match="Fournisseur IA non supporte"):
            bilan_assembly_service._load_ia_config(tmp_path)

    def test_raises_on_missing_cle_api(self, bilan_assembly_service, tmp_path):
        _create_settings(tmp_path, fournisseur="openai", cle_api="")
        with pytest.raises(ValueError, match="Cle API IA absente"):
            bilan_assembly_service._load_ia_config(tmp_path)

    def test_loads_modele_ia(self, bilan_assembly_service, tmp_path):
        _create_settings(tmp_path, modele_ia="gpt-4")
        result = bilan_assembly_service._load_ia_config(tmp_path)
        assert result["modele_ia"] == "gpt-4"


# ---------------------------------------------------------------------------
# Tests: identify_vigilance_points (precondition checks only - no real AI call)
# ---------------------------------------------------------------------------


class TestIdentifyVigilancePointsPreconditions:
    def test_raises_on_missing_questionnaire_complet(self, bilan_assembly_service, tmp_path):
        _create_settings(tmp_path)
        _create_prompt(tmp_path)
        with pytest.raises(ValueError, match="QuestionnaireComplet absent"):
            bilan_assembly_service.identify_vigilance_points(SID, base=tmp_path)

    def test_raises_on_missing_prompt(self, bilan_assembly_service, tmp_path):
        _create_questionnaire_complet_md(tmp_path, SID)
        _create_settings(tmp_path)
        with pytest.raises(ValueError, match="promptvigilance.txt absent"):
            bilan_assembly_service.identify_vigilance_points(SID, base=tmp_path)

    def test_raises_on_empty_prompt(self, bilan_assembly_service, tmp_path):
        _create_questionnaire_complet_md(tmp_path, SID)
        _create_settings(tmp_path)
        _create_prompt(tmp_path, content="")
        with pytest.raises(ValueError, match="promptvigilance.txt vide"):
            bilan_assembly_service.identify_vigilance_points(SID, base=tmp_path)

    def test_raises_on_missing_settings(self, bilan_assembly_service, tmp_path):
        _create_questionnaire_complet_md(tmp_path, SID)
        _create_prompt(tmp_path)
        with pytest.raises(ValueError, match="Configuration applicative absente"):
            bilan_assembly_service.identify_vigilance_points(SID, base=tmp_path)

    def test_raises_on_unsupported_provider(self, bilan_assembly_service, tmp_path):
        _create_questionnaire_complet_md(tmp_path, SID)
        _create_prompt(tmp_path)
        _create_settings(tmp_path, fournisseur="BadProvider")
        with pytest.raises(ValueError, match="Fournisseur IA non supporte"):
            bilan_assembly_service.identify_vigilance_points(SID, base=tmp_path)


# ---------------------------------------------------------------------------
# Tests: identify_vigilance_points (with mocked AI call)
# ---------------------------------------------------------------------------


class TestIdentifyVigilancePointsMocked:
    def test_writes_vigilance_file(self, bilan_assembly_service, tmp_path, monkeypatch):
        _create_questionnaire_complet_md(tmp_path, SID)
        _create_settings(tmp_path)
        _create_prompt(tmp_path)

        monkeypatch.setattr(
            bilan_assembly_service,
            "_call_ai_provider",
            lambda *args, **kwargs: "1. Surpoids\n2. Sedentarite",
        )

        result = bilan_assembly_service.identify_vigilance_points(SID, base=tmp_path)
        content = Path(result["vigilance_md_path"]).read_text(encoding="utf-8")

        assert "## Points de vigilance" in content
        assert "Surpoids" in content
        assert "Sedentarite" in content

    def test_returns_correct_structure(self, bilan_assembly_service, tmp_path, monkeypatch):
        _create_questionnaire_complet_md(tmp_path, SID)
        _create_settings(tmp_path)
        _create_prompt(tmp_path)

        monkeypatch.setattr(
            bilan_assembly_service,
            "_call_ai_provider",
            lambda *args, **kwargs: "Points de vigilance test",
        )

        result = bilan_assembly_service.identify_vigilance_points(SID, base=tmp_path)

        assert result["session_id"] == SID
        assert result["short_id"] == SID[:8]
        assert result["vigilance_text"] == "Points de vigilance test"
        assert "Vigilance_" in result["vigilance_md_path"]

    def test_uses_correct_model(self, bilan_assembly_service, tmp_path, monkeypatch):
        _create_questionnaire_complet_md(tmp_path, SID)
        _create_settings(tmp_path, modele_ia="gpt-4-turbo")
        _create_prompt(tmp_path)

        captured = {}

        def fake_call(fournisseur, cle_api, modele, system_prompt, user_message):
            captured["modele"] = modele
            return "Result"

        monkeypatch.setattr(bilan_assembly_service, "_call_ai_provider", fake_call)
        bilan_assembly_service.identify_vigilance_points(SID, base=tmp_path)

        assert captured["modele"] == "gpt-4-turbo"

    def test_uses_default_model_when_not_set(self, bilan_assembly_service, tmp_path, monkeypatch):
        _create_questionnaire_complet_md(tmp_path, SID)
        _create_settings(tmp_path, modele_ia="")
        _create_prompt(tmp_path)

        captured = {}

        def fake_call(fournisseur, cle_api, modele, system_prompt, user_message):
            captured["modele"] = modele
            return "Result"

        monkeypatch.setattr(bilan_assembly_service, "_call_ai_provider", fake_call)
        bilan_assembly_service.identify_vigilance_points(SID, base=tmp_path)

        assert captured["modele"] == "gpt-4o-mini"

    def test_prompt_as_system_and_md_as_user(self, bilan_assembly_service, tmp_path, monkeypatch):
        _create_questionnaire_complet_md(tmp_path, SID)
        _create_settings(tmp_path)
        _create_prompt(tmp_path, content="Mon prompt systeme")

        captured = {}

        def fake_call(fournisseur, cle_api, modele, system_prompt, user_message):
            captured["system_prompt"] = system_prompt
            captured["user_message"] = user_message
            return "Result"

        monkeypatch.setattr(bilan_assembly_service, "_call_ai_provider", fake_call)
        bilan_assembly_service.identify_vigilance_points(SID, base=tmp_path)

        assert captured["system_prompt"] == "Mon prompt systeme"
        assert "Questionnaire Complet" in captured["user_message"]


# ---------------------------------------------------------------------------
# Tests: _call_ai_provider
# ---------------------------------------------------------------------------


class TestCallAiProvider:
    def test_raises_on_unsupported_provider(self, bilan_assembly_service):
        with pytest.raises(ValueError, match="Fournisseur IA non supporte"):
            bilan_assembly_service._call_ai_provider(
                "unknown", "key", "model", "system", "user"
            )


# ---------------------------------------------------------------------------
# Tests: save_action_points
# ---------------------------------------------------------------------------


class TestSaveActionPoints:
    def test_saves_3_points(self, bilan_assembly_service, tmp_path):
        _create_vigilance_md(tmp_path, SID)

        result = bilan_assembly_service.save_action_points(
            SID, ["Point A", "Point B", "Point C"], base=tmp_path
        )

        content = Path(result["vigilance_md_path"]).read_text(encoding="utf-8")
        assert "## Plan d'action - 3 points pharmacien" in content
        assert "1. Point A" in content
        assert "2. Point B" in content
        assert "3. Point C" in content

    def test_returns_correct_structure(self, bilan_assembly_service, tmp_path):
        _create_vigilance_md(tmp_path, SID)

        result = bilan_assembly_service.save_action_points(
            SID, ["A", "B", "C"], base=tmp_path
        )

        assert result["session_id"] == SID
        assert result["short_id"] == SID[:8]
        assert "Vigilance_" in result["vigilance_md_path"]

    def test_raises_on_fewer_than_3_points(self, bilan_assembly_service, tmp_path):
        _create_vigilance_md(tmp_path, SID)
        with pytest.raises(ValueError, match="Exactement 3 points"):
            bilan_assembly_service.save_action_points(
                SID, ["A", "B"], base=tmp_path
            )

    def test_raises_on_more_than_3_points(self, bilan_assembly_service, tmp_path):
        _create_vigilance_md(tmp_path, SID)
        with pytest.raises(ValueError, match="Exactement 3 points"):
            bilan_assembly_service.save_action_points(
                SID, ["A", "B", "C", "D"], base=tmp_path
            )

    def test_raises_on_empty_point(self, bilan_assembly_service, tmp_path):
        _create_vigilance_md(tmp_path, SID)
        with pytest.raises(ValueError, match="Point 2 du plan d'action vide"):
            bilan_assembly_service.save_action_points(
                SID, ["A", "", "C"], base=tmp_path
            )

    def test_raises_on_whitespace_point(self, bilan_assembly_service, tmp_path):
        _create_vigilance_md(tmp_path, SID)
        with pytest.raises(ValueError, match="Point 1 du plan d'action vide"):
            bilan_assembly_service.save_action_points(
                SID, ["   ", "B", "C"], base=tmp_path
            )

    def test_raises_on_missing_vigilance_file(self, bilan_assembly_service, tmp_path):
        with pytest.raises(ValueError, match="Fichier Vigilance absent"):
            bilan_assembly_service.save_action_points(
                SID, ["A", "B", "C"], base=tmp_path
            )

    def test_overwrites_existing_action_section(self, bilan_assembly_service, tmp_path):
        _create_vigilance_md(tmp_path, SID)

        # First save
        bilan_assembly_service.save_action_points(
            SID, ["Old A", "Old B", "Old C"], base=tmp_path
        )

        # Second save (overwrite)
        result = bilan_assembly_service.save_action_points(
            SID, ["New A", "New B", "New C"], base=tmp_path
        )

        content = Path(result["vigilance_md_path"]).read_text(encoding="utf-8")
        assert "New A" in content
        assert "Old A" not in content

    def test_preserves_vigilance_section(self, bilan_assembly_service, tmp_path):
        _create_vigilance_md(
            tmp_path, SID,
            content="# Vigilance\n\n## Points de vigilance\n\n1. Important\n"
        )

        result = bilan_assembly_service.save_action_points(
            SID, ["A", "B", "C"], base=tmp_path
        )

        content = Path(result["vigilance_md_path"]).read_text(encoding="utf-8")
        assert "## Points de vigilance" in content
        assert "1. Important" in content
        assert "## Plan d'action - 3 points pharmacien" in content
