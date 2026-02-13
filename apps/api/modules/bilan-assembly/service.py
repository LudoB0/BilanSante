"""Bilan-assembly service.

Business logic for BuildQuestionnaireSummarySection and
IdentifyVigilancePoints.  Assembles questionnaire questions + patient
responses into a structured summary, generates markdown files, and
calls AI providers for vigilance point identification.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[4]

DATA_DIR = "data"
SESSIONS_SUBDIR = "sessions"
CONFIG_DIR = "config"
QUESTIONNAIRES_SUBDIR = "questionnaires"

SHORT_ID_LENGTH = 8
PROMPTS_SUBDIR = "prompts"
VIGILANCE_PROMPT_FILE = "promptvigilance.txt"

# Dedicated question IDs for weight/height
_POIDS_QUESTION_ID = "obligatoire1"
_TAILLE_QUESTION_ID = "Obligatoire2"

# AI provider configuration
_ALLOWED_PROVIDERS = ("openai", "anthropic", "mistral")

_ECO_MODELS: Dict[str, str] = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-sonnet-4-5-20250929",
    "mistral": "mistral-small-latest",
}

_PERFORMANT_MODELS: Dict[str, str] = {
    "openai": "gpt-4o",
    "anthropic": "claude-opus-4-20250514",
    "mistral": "mistral-large-latest",
}

_MODEL_TIERS: Dict[str, Dict[str, str]] = {
    "eco": _ECO_MODELS,
    "performant": _PERFORMANT_MODELS,
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_base(base: Path | None) -> Path:
    return base if base is not None else PROJECT_ROOT


def _sessions_dir(base: Path) -> Path:
    return base / DATA_DIR / SESSIONS_SUBDIR


def _questionnaires_dir(base: Path) -> Path:
    return base / CONFIG_DIR / QUESTIONNAIRES_SUBDIR


def _load_json(path: Path) -> dict | None:
    """Load a JSON file. Returns None on missing/corrupt file."""
    if not path.is_file():
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None


def format_response_value(value: Any, qtype: str) -> str:
    """Format a response value for human-readable display.

    Returns ``"non renseigne"`` for missing or empty values.
    """
    if value is None:
        return "non renseigne"

    if qtype == "boolean":
        if isinstance(value, bool):
            return "Oui" if value else "Non"
        return str(value)

    if qtype == "multiple_choice":
        if isinstance(value, list):
            if not value:
                return "non renseigne"
            return ", ".join(str(v) for v in value)
        return str(value)

    if qtype == "scale":
        return str(value)

    # single_choice, short_text, or unknown type
    if isinstance(value, str) and value.strip() == "":
        return "non renseigne"
    return str(value)


def _parse_numeric(value: Any) -> float | None:
    """Parse a numeric value, accepting ``,`` or ``.`` as decimal separator.

    Returns ``None`` when *value* cannot be interpreted as a finite
    positive number.
    """
    if value is None:
        return None
    raw = str(value).strip().replace(",", ".")
    try:
        num = float(raw)
    except (ValueError, TypeError):
        return None
    if num <= 0 or not __import__("math").isfinite(num):
        return None
    return num


def _extract_metrics(
    items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Extract poids/taille from items and compute IMC.

    Strategy:
      1. Look for dedicated ``question_id`` (``q12`` = poids, ``q13`` = taille).
      2. Fallback: scan labels containing ``poids`` / ``taille``.

    Returns ``{poids_kg, taille_m, imc, imc_display}``.
    """
    poids_raw: Any = None
    taille_raw: Any = None

    # Priority 1: dedicated IDs
    for item in items:
        if item["question_id"] == _POIDS_QUESTION_ID:
            poids_raw = item["response_value"]
        elif item["question_id"] == _TAILLE_QUESTION_ID:
            taille_raw = item["response_value"]

    # Priority 2: fallback on label
    if poids_raw is None:
        for item in items:
            if "poids" in item.get("label", "").lower():
                poids_raw = item["response_value"]
                break
    if taille_raw is None:
        for item in items:
            if "taille" in item.get("label", "").lower():
                taille_raw = item["response_value"]
                break

    poids_kg = _parse_numeric(poids_raw)
    taille_m = _parse_numeric(taille_raw)

    imc: float | None = None
    imc_display = "non calculable"

    if poids_kg is not None and taille_m is not None and taille_m > 0:
        imc = poids_kg / (taille_m ** 2)
        imc_display = f"{imc:.1f}"

    return {
        "poids_kg": poids_kg,
        "taille_m": taille_m,
        "imc": imc,
        "imc_display": imc_display,
    }


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------


def _generate_markdown(
    session_id: str,
    short_id: str,
    age_range: str,
    items: List[Dict[str, Any]],
    metrics: Dict[str, Any],
    pharmacist_notes: Dict[str, str] | None = None,
    pharmacist_blood_pressure: str = "",
    pharmacist_report: str = "",
) -> str:
    """Generate the markdown content for the questionnaire summary.

    When *pharmacist_notes*, *pharmacist_blood_pressure* or
    *pharmacist_report* are provided the generated markdown includes the
    pharmacist's text in the appropriate sections.
    """
    notes = pharmacist_notes or {}

    lines: list[str] = []
    lines.append(f"# Questionnaire Complet - Session {short_id}")
    lines.append("")
    lines.append(f"**Session**: {session_id}")
    lines.append(f"**Tranche d'age**: {age_range} ans")
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, item in enumerate(items):
        qid = item["question_id"]
        lines.append(f"## {i + 1}. {item['label']}")
        lines.append("")
        lines.append(f"**Reponse**: {item['response_display']}")
        lines.append("")
        lines.append("_Notes pharmacien:_")
        note = notes.get(qid, "")
        if note.strip():
            lines.append("")
            lines.append(note)
        lines.append("")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Mesures patient section
    poids_display = (
        f"{metrics['poids_kg']:.1f}" if metrics["poids_kg"] is not None else "non renseigne"
    )
    taille_display = (
        f"{metrics['taille_m']:.2f}" if metrics["taille_m"] is not None else "non renseigne"
    )
    lines.append("## Mesures patient")
    lines.append("")
    lines.append(f"- **Poids (kg)**: {poids_display}")
    lines.append(f"- **Taille (m)**: {taille_display}")
    lines.append(f"- **IMC**: {metrics['imc_display']}")
    tension_value = pharmacist_blood_pressure.strip() if pharmacist_blood_pressure else ""
    lines.append(f"- **Tension (mmHg)**: {tension_value}")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Rapport du pharmacien")
    lines.append("")
    if pharmacist_report.strip():
        lines.append(pharmacist_report)
    lines.append("")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_questionnaire_summary(
    session_id: str, base: Path | None = None
) -> Dict[str, Any]:
    """Build the questionnaire summary from session data.

    Loads the session, its questionnaire source, and the patient
    responses.  Matches each question to its response, generates
    a markdown file at
    ``data/sessions/QuestionnaireComplet_<short_id>.md``, and
    returns structured data for UI display.

    Returns a dict with:
    - ``session_id``
    - ``short_id`` (first 8 chars of UUID)
    - ``age_range``
    - ``md_path`` (str, absolute path to generated markdown)
    - ``items``: list of ``{question_id, label, type, options,
      response_value, response_display}``

    Raises ``ValueError`` if preconditions are not met.
    """
    base = _resolve_base(base)
    sessions_dir = _sessions_dir(base)

    # 1. Load session
    session_path = sessions_dir / f"{session_id}.json"
    session = _load_json(session_path)
    if session is None:
        raise ValueError(f"Session inconnue: {session_id}")

    age_range = session.get("age_range")
    if not age_range:
        raise ValueError("Session sans tranche d'age")

    # 2. Load responses
    responses_path = sessions_dir / f"{session_id}_responses.json"
    responses_data = _load_json(responses_path)
    if responses_data is None:
        raise ValueError(
            f"Fichier reponses absent pour la session: {session_id}"
        )

    responses_list = responses_data.get("responses", [])
    responses_map: Dict[str, Dict[str, Any]] = {}
    for resp in responses_list:
        qid = resp.get("question_id")
        if qid:
            responses_map[qid] = resp

    # 3. Load questionnaire source
    q_path = _questionnaires_dir(base) / f"{age_range}.json"
    questionnaire = _load_json(q_path)
    if questionnaire is None:
        raise ValueError(
            f"Questionnaire source absent pour la tranche d'age: {age_range}"
        )

    questions = questionnaire.get("questions", [])
    if not questions:
        raise ValueError(
            f"Questionnaire vide pour la tranche d'age: {age_range}"
        )

    # 3b. Filter questions by session sex (if present)
    session_sex = session.get("sex")
    if session_sex in ("H", "F"):
        questions = [
            q for q in questions
            if q.get("sex_target", "M") in (session_sex, "M")
        ]

    # 4. Build items
    items: List[Dict[str, Any]] = []
    for q in questions:
        qid = q.get("id", "")
        qtype = q.get("type", "")

        resp = responses_map.get(qid)
        value = resp.get("value") if resp is not None else None
        display = format_response_value(value, qtype)

        items.append({
            "question_id": qid,
            "label": q.get("label", ""),
            "type": qtype,
            "options": q.get("options", []),
            "response_value": value,
            "response_display": display,
        })

    # 5. Extract metrics (poids, taille, IMC)
    metrics = _extract_metrics(items)

    # 6. Generate markdown file
    short_id = session_id[:SHORT_ID_LENGTH]
    md_path = sessions_dir / f"QuestionnaireComplet_{short_id}.md"
    md_content = _generate_markdown(session_id, short_id, age_range, items, metrics)

    sessions_dir.mkdir(parents=True, exist_ok=True)
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(md_content)

    return {
        "session_id": session_id,
        "short_id": short_id,
        "age_range": age_range,
        "md_path": str(md_path),
        "items": items,
        "metrics": metrics,
    }


def capture_interview_notes(
    session_id: str,
    pharmacist_notes: Dict[str, str],
    pharmacist_blood_pressure: str,
    pharmacist_report: str,
    base: Path | None = None,
) -> Dict[str, Any]:
    """Capture pharmacist notes and regenerate the markdown file.

    Re-derives the summary from the source files (session, questionnaire,
    responses) and regenerates ``QuestionnaireComplet_<short_id>.md``
    with the pharmacist's text injected.

    Returns ``{session_id, short_id, md_path}``.

    Raises ``ValueError`` if preconditions are not met (delegates to
    :func:`build_questionnaire_summary`).
    """
    # Build summary to get items, metrics, and validate preconditions
    summary = build_questionnaire_summary(session_id, base=base)

    short_id = summary["short_id"]
    md_path = Path(summary["md_path"])

    # Regenerate markdown with pharmacist data
    md_content = _generate_markdown(
        session_id=summary["session_id"],
        short_id=short_id,
        age_range=summary["age_range"],
        items=summary["items"],
        metrics=summary["metrics"],
        pharmacist_notes=pharmacist_notes,
        pharmacist_blood_pressure=pharmacist_blood_pressure,
        pharmacist_report=pharmacist_report,
    )

    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(md_content)

    return {
        "session_id": session_id,
        "short_id": short_id,
        "md_path": str(md_path),
    }


# ---------------------------------------------------------------------------
# IdentifyVigilancePoints
# ---------------------------------------------------------------------------


def _prompt_path(base: Path) -> Path:
    return base / CONFIG_DIR / PROMPTS_SUBDIR / VIGILANCE_PROMPT_FILE


def _settings_path(base: Path) -> Path:
    return base / CONFIG_DIR / "settings.json"


def _normalize_provider(fournisseur: str) -> str:
    """Normalize the provider name to lowercase key.

    Accepts ``"OpenIA"``/``"openai"``, ``"Anthropic"``/``"anthropic"``,
    ``"Mistral"``/``"mistral"`` (case-insensitive).
    """
    mapping = {"openia": "openai", "openai": "openai",
               "anthropic": "anthropic",
               "mistral": "mistral"}
    return mapping.get(fournisseur.lower().strip(), "")


def _resolve_ai_model(fournisseur: str, modele_ia: str) -> str:
    """Return the model to use for the given provider.

    *modele_ia* can be a tier name (``"eco"`` or ``"performant"``),
    a direct model identifier, or empty (defaults to eco).
    """
    key = modele_ia.strip().lower() if modele_ia else ""
    if key in _MODEL_TIERS:
        return _MODEL_TIERS[key].get(fournisseur, "")
    if key:
        return modele_ia.strip()
    return _ECO_MODELS.get(fournisseur, "")


def _call_ai_provider(
    fournisseur: str,
    cle_api: str,
    modele: str,
    system_prompt: str,
    user_message: str,
) -> str:
    """Call the AI provider and return the response text.

    Raises ``ValueError`` for unsupported providers and ``RuntimeError``
    for API errors or empty responses.
    """
    if fournisseur == "openai":
        import openai

        client = openai.OpenAI(api_key=cle_api)
        response = client.chat.completions.create(
            model=modele,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        text = response.choices[0].message.content
        if not text or not text.strip():
            raise RuntimeError("Reponse IA vide")
        return text.strip()

    if fournisseur == "anthropic":
        import anthropic

        client = anthropic.Anthropic(api_key=cle_api)
        response = client.messages.create(
            model=modele,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        text = response.content[0].text
        if not text or not text.strip():
            raise RuntimeError("Reponse IA vide")
        return text.strip()

    if fournisseur == "mistral":
        from mistralai import Mistral

        client = Mistral(api_key=cle_api)
        response = client.chat.complete(
            model=modele,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        text = response.choices[0].message.content
        if not text or not text.strip():
            raise RuntimeError("Reponse IA vide")
        return text.strip()

    raise ValueError(f"Fournisseur IA non supporte: {fournisseur}")


def _load_ia_config(base: Path) -> Dict[str, str]:
    """Load IA configuration from settings.json.

    Returns ``{fournisseur, cle_api, modele_ia}``.

    Raises ``ValueError`` when required fields are missing.
    """
    settings = _settings_path(base)
    if not settings.is_file():
        raise ValueError("Configuration applicative absente (settings.json)")

    with open(settings, encoding="utf-8") as fh:
        data = json.load(fh)

    fournisseur_raw = data.get("fournisseur_ia", "")
    if not fournisseur_raw or not fournisseur_raw.strip():
        raise ValueError("Fournisseur IA non configure")

    fournisseur = _normalize_provider(fournisseur_raw)
    if fournisseur not in _ALLOWED_PROVIDERS:
        raise ValueError(
            f"Fournisseur IA non supporte: {fournisseur_raw}"
        )

    cle_api = data.get("cle_api", "")
    if not cle_api or not cle_api.strip():
        raise ValueError("Cle API IA absente")

    modele_ia = data.get("modele_ia", "")

    return {
        "fournisseur": fournisseur,
        "cle_api": cle_api.strip(),
        "modele_ia": modele_ia,
    }


def identify_vigilance_points(
    session_id: str,
    base: Path | None = None,
) -> Dict[str, Any]:
    """Identify vigilance points using the configured AI provider.

    Loads the completed questionnaire markdown, the system prompt from
    ``config/prompts/promptvigilance.txt``, and calls the AI provider.
    Writes the result to ``data/sessions/Vigilance_<short_id>.md``.

    Returns ``{session_id, short_id, vigilance_md_path, vigilance_text}``.

    Raises ``ValueError`` for precondition failures and ``RuntimeError``
    for AI call errors.
    """
    base = _resolve_base(base)
    short_id = session_id[:SHORT_ID_LENGTH]
    sessions_dir = _sessions_dir(base)

    # 1. Verify questionnaire complet exists
    md_path = sessions_dir / f"QuestionnaireComplet_{short_id}.md"
    if not md_path.is_file():
        raise ValueError(
            f"Fichier QuestionnaireComplet absent: {md_path.name}"
        )

    # 2. Load prompt
    prompt_file = _prompt_path(base)
    if not prompt_file.is_file():
        raise ValueError("Fichier promptvigilance.txt absent")
    system_prompt = prompt_file.read_text(encoding="utf-8").strip()
    if not system_prompt:
        raise ValueError("Fichier promptvigilance.txt vide")

    # 3. Load IA config
    ia_config = _load_ia_config(base)
    fournisseur = ia_config["fournisseur"]
    cle_api = ia_config["cle_api"]
    modele = _resolve_ai_model(fournisseur, ia_config["modele_ia"])

    # 4. Load questionnaire complet (user message)
    user_message = md_path.read_text(encoding="utf-8")

    # 5. Call AI
    vigilance_text = _call_ai_provider(
        fournisseur, cle_api, modele, system_prompt, user_message
    )

    # 6. Write vigilance file
    vigilance_md_path = sessions_dir / f"Vigilance_{short_id}.md"
    vigilance_content = (
        f"# Vigilance - Session {short_id}\n\n"
        f"## Points de vigilance\n\n"
        f"{vigilance_text}\n"
    )
    sessions_dir.mkdir(parents=True, exist_ok=True)
    with open(vigilance_md_path, "w", encoding="utf-8") as fh:
        fh.write(vigilance_content)

    return {
        "session_id": session_id,
        "short_id": short_id,
        "vigilance_md_path": str(vigilance_md_path),
        "vigilance_text": vigilance_text,
    }


def save_action_points(
    session_id: str,
    action_points: List[str],
    base: Path | None = None,
) -> Dict[str, Any]:
    """Save the pharmacist's 3 action points into the vigilance file.

    Appends/replaces the ``## Plan d'action`` section in
    ``data/sessions/Vigilance_<short_id>.md``.

    Returns ``{session_id, short_id, vigilance_md_path}``.

    Raises ``ValueError`` if exactly 3 non-empty points are not provided
    or if the vigilance file does not exist.
    """
    if not isinstance(action_points, list) or len(action_points) != 3:
        raise ValueError("Exactement 3 points du plan d'action requis")
    for i, point in enumerate(action_points):
        if not isinstance(point, str) or not point.strip():
            raise ValueError(
                f"Point {i + 1} du plan d'action vide ou invalide"
            )

    base = _resolve_base(base)
    short_id = session_id[:SHORT_ID_LENGTH]
    sessions_dir = _sessions_dir(base)

    vigilance_md_path = sessions_dir / f"Vigilance_{short_id}.md"
    if not vigilance_md_path.is_file():
        raise ValueError(
            f"Fichier Vigilance absent: {vigilance_md_path.name}"
        )

    # Read existing content and remove any previous action section
    content = vigilance_md_path.read_text(encoding="utf-8")
    marker = "## Plan d'action - 3 points pharmacien"
    if marker in content:
        content = content[: content.index(marker)].rstrip()

    # Append action points section
    action_section = f"\n\n{marker}\n\n"
    for i, point in enumerate(action_points):
        action_section += f"{i + 1}. {point.strip()}\n"

    with open(vigilance_md_path, "w", encoding="utf-8") as fh:
        fh.write(content + action_section)

    return {
        "session_id": session_id,
        "short_id": short_id,
        "vigilance_md_path": str(vigilance_md_path),
    }
