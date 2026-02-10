"""Tests for the application-context service."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_settings(base: Path, data: dict) -> None:
    """Write a settings.json inside base/config/."""
    cfg = base / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "settings.json").write_text(
        json.dumps(data, ensure_ascii=False), encoding="utf-8"
    )


def _write_logo(base: Path, content: bytes = b"png-bytes") -> None:
    """Write a fake logo.png inside base/config/img/."""
    img_dir = base / "config" / "img"
    img_dir.mkdir(parents=True, exist_ok=True)
    (img_dir / "logo.png").write_bytes(content)


def _full_payload(**overrides) -> dict:
    """Return a valid payload, optionally overridden."""
    data = {
        "nom_pharmacie": "Pharmacie Test",
        "adresse": "1 rue de Test",
        "code_postal": "75001",
        "ville": "Paris",
        "telephone": "0102030405",
        "fournisseur_ia": "openai",
        "cle_api": "sk-test-key",
        "logo_image": b"fake-png",
        "site_web": "",
        "instagram": "",
        "facebook": "",
        "x": "",
        "linkedin": "",
    }
    data.update(overrides)
    return data


# ===================================================================
# load_config
# ===================================================================


class TestLoadConfig:
    def test_returns_empty_when_no_settings(self, service, tmp_path):
        result = service.load_config(base=tmp_path)
        assert result["nom_pharmacie"] == ""
        assert result["cle_api"] == ""
        assert result["logo_image"] == ""

    def test_loads_existing_settings(self, service, tmp_path):
        _write_settings(tmp_path, {
            "nom_pharmacie": "Ma Pharmacie",
            "adresse": "10 rue X",
            "code_postal": "69001",
            "ville": "Lyon",
            "telephone": "0400000000",
            "fournisseur_ia": "anthropic",
            "cle_api": "sk-abc",
            "site_web": "https://example.com",
            "instagram": "",
            "facebook": "",
            "x": "",
            "linkedin": "",
        })
        result = service.load_config(base=tmp_path)
        assert result["nom_pharmacie"] == "Ma Pharmacie"
        assert result["ville"] == "Lyon"
        assert result["fournisseur_ia"] == "anthropic"
        assert result["logo_image"] == ""  # no logo file

    def test_detects_logo_when_present(self, service, tmp_path):
        _write_settings(tmp_path, {"nom_pharmacie": "P"})
        _write_logo(tmp_path)
        result = service.load_config(base=tmp_path)
        assert result["logo_image"] != ""
        assert "logo.png" in result["logo_image"]


# ===================================================================
# validate_config
# ===================================================================


class TestValidateConfig:
    def test_valid_payload_no_errors(self, service):
        errors = service.validate_config(_full_payload())
        assert errors == []

    def test_missing_required_field(self, service):
        payload = _full_payload(nom_pharmacie="")
        errors = service.validate_config(payload)
        assert any("nom_pharmacie" in e for e in errors)

    def test_missing_cle_api_specific_error(self, service):
        payload = _full_payload(cle_api="")
        errors = service.validate_config(payload)
        assert any("cle_api" in e.lower() or "Cle API" in e for e in errors)

    def test_missing_logo(self, service):
        payload = _full_payload(logo_image="")
        errors = service.validate_config(payload)
        assert any("logo_image" in e for e in errors)

    def test_whitespace_only_is_invalid(self, service):
        payload = _full_payload(telephone="   ")
        errors = service.validate_config(payload)
        assert any("telephone" in e for e in errors)

    def test_all_required_missing(self, service):
        payload = {k: "" for k in (
            "nom_pharmacie", "adresse", "code_postal", "ville",
            "telephone", "fournisseur_ia", "cle_api", "logo_image",
        )}
        errors = service.validate_config(payload)
        # At least one error per required field + logo
        assert len(errors) >= 8


# ===================================================================
# save_config
# ===================================================================


class TestSaveConfig:
    def test_saves_valid_payload(self, service, tmp_path):
        service.save_config(_full_payload(), base=tmp_path)

        settings = tmp_path / "config" / "settings.json"
        assert settings.is_file()
        data = json.loads(settings.read_text(encoding="utf-8"))
        assert data["nom_pharmacie"] == "Pharmacie Test"
        assert data["fournisseur_ia"] == "openai"

        logo = tmp_path / "config" / "img" / "logo.png"
        assert logo.is_file()
        assert logo.read_bytes() == b"fake-png"

    def test_creates_directories(self, service, tmp_path):
        service.save_config(_full_payload(), base=tmp_path)
        assert (tmp_path / "config").is_dir()
        assert (tmp_path / "config" / "img").is_dir()

    def test_save_logo_from_file_path(self, service, tmp_path):
        # Create a source logo file
        source = tmp_path / "source_logo.png"
        source.write_bytes(b"source-png-content")

        payload = _full_payload(logo_image=str(source))
        service.save_config(payload, base=tmp_path)

        dest = tmp_path / "config" / "img" / "logo.png"
        assert dest.is_file()
        assert dest.read_bytes() == b"source-png-content"

    def test_rejects_invalid_payload(self, service, tmp_path):
        payload = _full_payload(nom_pharmacie="")
        with pytest.raises(ValueError, match="Validation"):
            service.save_config(payload, base=tmp_path)

    def test_rejects_nonexistent_logo_path(self, service, tmp_path):
        payload = _full_payload(logo_image="/nonexistent/logo.png")
        with pytest.raises(ValueError, match="logo introuvable"):
            service.save_config(payload, base=tmp_path)

    def test_overwrites_existing_config(self, service, tmp_path):
        service.save_config(_full_payload(ville="Paris"), base=tmp_path)
        service.save_config(_full_payload(ville="Lyon"), base=tmp_path)

        data = json.loads(
            (tmp_path / "config" / "settings.json").read_text(encoding="utf-8")
        )
        assert data["ville"] == "Lyon"


# ===================================================================
# is_configured
# ===================================================================


class TestIsConfigured:
    def test_false_when_nothing_exists(self, service, tmp_path):
        assert service.is_configured(base=tmp_path) is False

    def test_false_when_settings_incomplete(self, service, tmp_path):
        _write_settings(tmp_path, {"nom_pharmacie": "P"})
        _write_logo(tmp_path)
        assert service.is_configured(base=tmp_path) is False

    def test_false_when_no_logo(self, service, tmp_path):
        _write_settings(tmp_path, {
            "nom_pharmacie": "P",
            "adresse": "A",
            "code_postal": "C",
            "ville": "V",
            "telephone": "T",
            "fournisseur_ia": "F",
            "cle_api": "K",
        })
        assert service.is_configured(base=tmp_path) is False

    def test_true_when_fully_configured(self, service, tmp_path):
        _write_settings(tmp_path, {
            "nom_pharmacie": "P",
            "adresse": "A",
            "code_postal": "C",
            "ville": "V",
            "telephone": "T",
            "fournisseur_ia": "F",
            "cle_api": "K",
        })
        _write_logo(tmp_path)
        assert service.is_configured(base=tmp_path) is True
