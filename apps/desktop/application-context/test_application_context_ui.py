import importlib.util
from pathlib import Path
import sys
import unittest


def _load_module():
    module_path = Path(__file__).with_name("application_context_ui.py")
    spec = importlib.util.spec_from_file_location("application_context_ui", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load application_context_ui")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


class ApplicationContextUiTest(unittest.TestCase):
    def setUp(self):
        self.ui = _load_module()
        self.valid_state = {
            "status": "edition",
            "nom_pharmacie": "Pharmacie Test",
            "adresse": "1 rue de Test",
            "code_postal": "75001",
            "ville": "Paris",
            "telephone": "0102030405",
            "logo_image": b"logo-bytes",
            "site_web": "",
            "instagram": "",
            "facebook": "",
            "x": "",
            "linkedin": "",
            "fournisseur_ia": "provider-a",
            "cle_api": "secret-key",
        }

    def test_create_ui_state_initial(self):
        state = self.ui.create_ui_state()
        self.assertEqual(state["status"], "initial")
        self.assertEqual(state["nom_pharmacie"], "")

    def test_validate_ui_state_reports_missing_required_fields(self):
        state = self.ui.create_ui_state()
        errors = self.ui.validate_ui_state(state)
        self.assertTrue(any("nom_pharmacie" in err for err in errors))
        self.assertTrue(any("cle_api" in err for err in errors))

    def test_build_submission_payload_from_valid_state(self):
        payload = self.ui.build_submission_payload(self.valid_state)
        self.assertEqual(payload["nom_pharmacie"], "Pharmacie Test")
        self.assertEqual(payload["fournisseur_ia"], "provider-a")

    def test_update_ui_state_changes_value(self):
        state = self.ui.create_ui_state()
        updated = self.ui.update_ui_state(state, "ville", "Lyon")
        self.assertEqual(updated["ville"], "Lyon")
        self.assertEqual(updated["status"], "edition")


if __name__ == "__main__":
    unittest.main()
