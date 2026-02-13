"""Root pytest configuration.

Provides an importlib-based module loader to handle the project's
hyphenated directory names (e.g. 'application-context') which are
not valid Python package identifiers.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent


def load_module_from_path(module_name: str, file_path: Path):
    """Load a Python module from an absolute file path.

    Caches the module in sys.modules so subsequent calls return the
    same object.
    """
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def ui_adapter():
    """Load the application_context_ui adapter module."""
    path = (
        PROJECT_ROOT
        / "apps"
        / "desktop"
        / "application-context"
        / "application_context_ui.py"
    )
    return load_module_from_path("application_context_ui", path)


@pytest.fixture
def service():
    """Load the application-context service module."""
    path = (
        PROJECT_ROOT
        / "apps"
        / "api"
        / "modules"
        / "application-context"
        / "service.py"
    )
    return load_module_from_path("application_context_service", path)


@pytest.fixture
def valid_payload():
    """A fully valid submission payload for testing."""
    return {
        "nom_pharmacie": "Pharmacie Test",
        "adresse": "1 rue de Test",
        "code_postal": "75001",
        "ville": "Paris",
        "telephone": "0102030405",
        "logo_image": b"fake-png-bytes",
        "fournisseur_ia": "openai",
        "cle_api": "sk-test-key-123",
        "site_web": "",
        "instagram": "",
        "facebook": "",
        "x": "",
        "linkedin": "",
    }


@pytest.fixture
def valid_ui_state():
    """A fully valid UI state dict for testing."""
    return {
        "status": "edition",
        "nom_pharmacie": "Pharmacie Test",
        "adresse": "1 rue de Test",
        "code_postal": "75001",
        "ville": "Paris",
        "telephone": "0102030405",
        "logo_image": b"fake-png-bytes",
        "fournisseur_ia": "openai",
        "cle_api": "sk-test-key-123",
        "site_web": "",
        "instagram": "",
        "facebook": "",
        "x": "",
        "linkedin": "",
    }


# ---------------------------------------------------------------------------
# Questionnaire-catalog fixtures (Module B)
# ---------------------------------------------------------------------------


@pytest.fixture
def catalog_service():
    """Load the questionnaire-catalog service module."""
    path = (
        PROJECT_ROOT
        / "apps"
        / "api"
        / "modules"
        / "questionnaire-catalog"
        / "service.py"
    )
    return load_module_from_path("questionnaire_catalog_service", path)


@pytest.fixture
def catalog_ui_adapter():
    """Load the questionnaire_catalog_ui adapter module."""
    path = (
        PROJECT_ROOT
        / "apps"
        / "desktop"
        / "questionnaire-catalog"
        / "questionnaire_catalog_ui.py"
    )
    return load_module_from_path("questionnaire_catalog_ui", path)


# ---------------------------------------------------------------------------
# Session fixtures (Module C - session-and-tablet-access)
# ---------------------------------------------------------------------------


@pytest.fixture
def session_service():
    """Load the session-and-tablet-access service module."""
    path = (
        PROJECT_ROOT
        / "apps"
        / "api"
        / "modules"
        / "session-and-tablet-access"
        / "service.py"
    )
    return load_module_from_path("session_service", path)


@pytest.fixture
def session_ui_adapter():
    """Load the session_ui adapter module."""
    path = (
        PROJECT_ROOT
        / "apps"
        / "desktop"
        / "session-and-tablet-access"
        / "session_ui.py"
    )
    return load_module_from_path("session_ui", path)


# ---------------------------------------------------------------------------
# Questionnaire-capture fixtures (CaptureQuestionnaireResponses)
# ---------------------------------------------------------------------------


@pytest.fixture
def capture_service():
    """Load the questionnaire-capture service module."""
    path = (
        PROJECT_ROOT
        / "apps"
        / "api"
        / "modules"
        / "questionnaire-capture"
        / "service.py"
    )
    return load_module_from_path("capture_service", path)


# ---------------------------------------------------------------------------
# Tablet server fixtures (ServeQuestionnaireOnTablet)
# ---------------------------------------------------------------------------


@pytest.fixture
def tablet_server_module():
    """Load the tablet_server module."""
    path = (
        PROJECT_ROOT
        / "apps"
        / "api"
        / "modules"
        / "session-and-tablet-access"
        / "tablet_server.py"
    )
    return load_module_from_path("tablet_server", path)


# ---------------------------------------------------------------------------
# Bilan-assembly fixtures (BuildQuestionnaireSummarySection)
# ---------------------------------------------------------------------------


@pytest.fixture
def bilan_assembly_service():
    """Load the bilan-assembly service module."""
    path = (
        PROJECT_ROOT
        / "apps"
        / "api"
        / "modules"
        / "bilan-assembly"
        / "service.py"
    )
    return load_module_from_path("bilan_assembly_service", path)


@pytest.fixture
def summary_ui_adapter():
    """Load the questionnaire_summary_ui adapter module."""
    path = (
        PROJECT_ROOT
        / "apps"
        / "desktop"
        / "bilan-assembly"
        / "questionnaire_summary_ui.py"
    )
    return load_module_from_path("questionnaire_summary_ui", path)


# ---------------------------------------------------------------------------
# Co-production fixtures (IdentifyVigilancePoints)
# ---------------------------------------------------------------------------


@pytest.fixture
def co_production_ui_adapter():
    """Load the co_production_ui adapter module."""
    path = (
        PROJECT_ROOT
        / "apps"
        / "desktop"
        / "co-production"
        / "co_production_ui.py"
    )
    return load_module_from_path("co_production_ui", path)
