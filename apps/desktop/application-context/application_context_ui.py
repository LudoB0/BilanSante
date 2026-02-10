"""UI contract adapter for application-context module.

This file implements UI-side validation and payload building without
introducing any framework-specific behavior.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


REQUIRED_UI_FIELDS = (
    "nom_pharmacie",
    "adresse",
    "code_postal",
    "ville",
    "telephone",
    "logo_image",
    "fournisseur_ia",
    "cle_api",
)

OPTIONAL_UI_FIELDS = (
    "site_web",
    "instagram",
    "facebook",
    "x",
    "linkedin",
)


def _empty_state() -> Dict[str, Any]:
    state: Dict[str, Any] = {"status": "initial"}
    for field in REQUIRED_UI_FIELDS:
        state[field] = ""
    for field in OPTIONAL_UI_FIELDS:
        state[field] = ""
    return state


def create_ui_state(existing: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = _empty_state()
    if existing:
        for key, value in existing.items():
            if key in state and key != "status":
                state[key] = value
        state["status"] = "edition"
    return state


def update_ui_state(state: Dict[str, Any], field: str, value: Any) -> Dict[str, Any]:
    if field not in state:
        raise ValueError(f"Unknown field: {field}")

    updated = deepcopy(state)
    updated[field] = value
    updated["status"] = "edition"
    return updated


def validate_ui_state(state: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    for field in REQUIRED_UI_FIELDS:
        value = state.get(field)
        if isinstance(value, str):
            if value.strip() == "":
                errors.append(f"Champ obligatoire manquant: {field}")
        elif value in (None, b""):
            errors.append(f"Champ obligatoire manquant: {field}")

    # The contract only requires explicit signalement for missing or invalid API key.
    api_key = state.get("cle_api")
    if isinstance(api_key, str) and api_key.strip() == "":
        if "Champ obligatoire manquant: cle_api" not in errors:
            errors.append("Cle API manquante ou invalide")

    return errors


def build_submission_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    errors = validate_ui_state(state)
    if errors:
        raise ValueError("Validation UI bloquante: " + "; ".join(errors))

    payload: Dict[str, Any] = {}
    for field in REQUIRED_UI_FIELDS:
        payload[field] = state[field]
    for field in OPTIONAL_UI_FIELDS:
        payload[field] = state.get(field, "")
    return payload
