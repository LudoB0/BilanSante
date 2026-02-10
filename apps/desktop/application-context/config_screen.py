"""CustomTkinter configuration screen for the application-context module.

Standalone launch:
    python apps/desktop/application-context/config_screen.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

# ---------------------------------------------------------------------------
# Module loading (hyphenated directories cannot use standard imports)
# ---------------------------------------------------------------------------

_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parents[2]


def _load_module(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_ui = _load_module(
    "application_context_ui", _THIS_DIR / "application_context_ui.py"
)
_svc = _load_module(
    "application_context_service",
    _PROJECT_ROOT / "apps" / "api" / "modules" / "application-context" / "service.py",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SECTION_PAD = {"padx": 16, "pady": (16, 4)}
_FIELD_PAD = {"padx": 24, "pady": 2}
_PROVIDERS = ("openai", "anthropic", "mistral")

_LABELS = {
    "nom_pharmacie": "Nom de la pharmacie *",
    "adresse": "Adresse *",
    "code_postal": "Code postal *",
    "ville": "Ville *",
    "telephone": "Telephone *",
    "site_web": "Site web",
    "instagram": "Instagram",
    "facebook": "Facebook",
    "x": "X",
    "linkedin": "LinkedIn",
    "fournisseur_ia": "Fournisseur IA *",
    "cle_api": "Cle API *",
}

_STATUS_TEXT = {
    "initial": "Parametrage non renseigne",
    "edition": "Modification en cours...",
    "valide": "Parametrage enregistre",
    "erreur": "Erreurs de validation",
}

_STATUS_COLOR = {
    "initial": "gray",
    "edition": "#1a73e8",
    "valide": "#2e7d32",
    "erreur": "#c62828",
}


# ---------------------------------------------------------------------------
# ConfigScreen
# ---------------------------------------------------------------------------


class ConfigScreen(ctk.CTkFrame):
    """Pharmacy configuration form (DEV-ENV section 9.2)."""

    def __init__(
        self,
        master,
        base_path: Path | None = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self._base = base_path
        self._state = _ui.create_ui_state()
        self._logo_source: str | None = None
        self._widgets: dict[str, ctk.CTkEntry | ctk.CTkOptionMenu] = {}
        self._error_labels: dict[str, ctk.CTkLabel] = {}
        self._show_api_key = False

        self._build_layout()
        self._load_existing()

    # ---------------------------------------------------------------
    # Layout
    # ---------------------------------------------------------------

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(self)
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        row = 0
        row = self._section_identity(scroll, row)
        row = self._section_logo(scroll, row)
        row = self._section_optional(scroll, row)
        row = self._section_ia(scroll, row)

        # Action bar (outside scroll)
        bar = ctk.CTkFrame(self)
        bar.grid(row=1, column=0, sticky="ew", padx=16, pady=8)
        bar.grid_columnconfigure(0, weight=1)

        self._status_label = ctk.CTkLabel(bar, text="", anchor="w")
        self._status_label.grid(row=0, column=0, sticky="w", padx=8)

        save_btn = ctk.CTkButton(
            bar, text="Enregistrer", width=180, command=self._on_save
        )
        save_btn.grid(row=0, column=1, padx=8, pady=4)

        self._update_status()

    # --- Identity section ---

    def _section_identity(self, parent, row: int) -> int:
        title = ctk.CTkLabel(
            parent, text="Identite pharmacie", font=ctk.CTkFont(size=15, weight="bold")
        )
        title.grid(row=row, column=0, sticky="w", **_SECTION_PAD)
        row += 1

        for field in ("nom_pharmacie", "adresse", "code_postal", "ville", "telephone"):
            row = self._add_text_field(parent, row, field)
        return row

    # --- Logo section ---

    def _section_logo(self, parent, row: int) -> int:
        title = ctk.CTkLabel(
            parent, text="Logo et habillage", font=ctk.CTkFont(size=15, weight="bold")
        )
        title.grid(row=row, column=0, sticky="w", **_SECTION_PAD)
        row += 1

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", **_FIELD_PAD)
        row += 1

        btn = ctk.CTkButton(
            frame, text="Choisir un logo *", width=180, command=self._on_logo_select
        )
        btn.grid(row=0, column=0, padx=(0, 12), pady=4)

        self._logo_preview = ctk.CTkLabel(frame, text="Aucun logo", width=150, height=150)
        self._logo_preview.grid(row=0, column=1, pady=4)

        err = ctk.CTkLabel(parent, text="", text_color="#c62828", anchor="w")
        err.grid(row=row, column=0, sticky="w", **_FIELD_PAD)
        self._error_labels["logo_image"] = err
        row += 1

        return row

    # --- Optional contact section ---

    def _section_optional(self, parent, row: int) -> int:
        title = ctk.CTkLabel(
            parent,
            text="Informations de contact (optionnel)",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        title.grid(row=row, column=0, sticky="w", **_SECTION_PAD)
        row += 1

        for field in ("site_web", "instagram", "facebook", "x", "linkedin"):
            row = self._add_text_field(parent, row, field)
        return row

    # --- IA section ---

    def _section_ia(self, parent, row: int) -> int:
        title = ctk.CTkLabel(
            parent,
            text="Configuration IA",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        title.grid(row=row, column=0, sticky="w", **_SECTION_PAD)
        row += 1

        # Provider dropdown
        lbl = ctk.CTkLabel(parent, text=_LABELS["fournisseur_ia"], anchor="w")
        lbl.grid(row=row, column=0, sticky="w", **_FIELD_PAD)
        row += 1

        menu = ctk.CTkOptionMenu(
            parent,
            values=list(_PROVIDERS),
            command=lambda v: self._on_dropdown_change("fournisseur_ia", v),
        )
        menu.set(self._state.get("fournisseur_ia") or _PROVIDERS[0])
        menu.grid(row=row, column=0, sticky="w", **_FIELD_PAD)
        self._widgets["fournisseur_ia"] = menu
        row += 1

        # API key entry
        lbl = ctk.CTkLabel(parent, text=_LABELS["cle_api"], anchor="w")
        lbl.grid(row=row, column=0, sticky="w", **_FIELD_PAD)
        row += 1

        key_frame = ctk.CTkFrame(parent, fg_color="transparent")
        key_frame.grid(row=row, column=0, sticky="ew", **_FIELD_PAD)
        row += 1

        entry = ctk.CTkEntry(key_frame, show="*", width=400)
        entry.grid(row=0, column=0, padx=(0, 8))
        entry.bind("<KeyRelease>", lambda _e: self._on_field_change("cle_api"))
        self._widgets["cle_api"] = entry

        toggle = ctk.CTkButton(
            key_frame, text="Afficher", width=90, command=self._toggle_api_key
        )
        toggle.grid(row=0, column=1)
        self._toggle_btn = toggle

        err = ctk.CTkLabel(parent, text="", text_color="#c62828", anchor="w")
        err.grid(row=row, column=0, sticky="w", **_FIELD_PAD)
        self._error_labels["cle_api"] = err
        row += 1

        return row

    # --- Helpers ---

    def _add_text_field(self, parent, row: int, field: str) -> int:
        lbl = ctk.CTkLabel(parent, text=_LABELS[field], anchor="w")
        lbl.grid(row=row, column=0, sticky="w", **_FIELD_PAD)
        row += 1

        entry = ctk.CTkEntry(parent, width=400)
        entry.bind("<KeyRelease>", lambda _e, f=field: self._on_field_change(f))
        entry.grid(row=row, column=0, sticky="w", **_FIELD_PAD)
        self._widgets[field] = entry
        row += 1

        err = ctk.CTkLabel(parent, text="", text_color="#c62828", anchor="w")
        err.grid(row=row, column=0, sticky="w", **_FIELD_PAD)
        self._error_labels[field] = err
        row += 1

        return row

    # ---------------------------------------------------------------
    # Callbacks
    # ---------------------------------------------------------------

    def _on_field_change(self, field: str):
        widget = self._widgets[field]
        if isinstance(widget, ctk.CTkEntry):
            value = widget.get()
        elif isinstance(widget, ctk.CTkOptionMenu):
            value = widget.get()
        else:
            return
        self._state = _ui.update_ui_state(self._state, field, value)
        if field in self._error_labels:
            self._error_labels[field].configure(text="")
        self._update_status()

    def _on_dropdown_change(self, field: str, value: str):
        self._state = _ui.update_ui_state(self._state, field, value)
        self._update_status()

    def _on_logo_select(self):
        path = filedialog.askopenfilename(
            title="Choisir un logo",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
            ],
        )
        if not path:
            return
        self._logo_source = path
        self._state = _ui.update_ui_state(self._state, "logo_image", path)
        self._show_logo_preview(path)
        if "logo_image" in self._error_labels:
            self._error_labels["logo_image"].configure(text="")
        self._update_status()

    def _show_logo_preview(self, path: str):
        try:
            img = Image.open(path)
            img.thumbnail((150, 150))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self._logo_preview.configure(image=ctk_img, text="")
            self._logo_preview._ctk_image = ctk_img  # prevent GC
        except Exception:
            self._logo_preview.configure(image=None, text="Erreur chargement")

    def _toggle_api_key(self):
        self._show_api_key = not self._show_api_key
        entry = self._widgets["cle_api"]
        if self._show_api_key:
            entry.configure(show="")
            self._toggle_btn.configure(text="Masquer")
        else:
            entry.configure(show="*")
            self._toggle_btn.configure(text="Afficher")

    def _on_save(self):
        self._clear_errors()

        # Collect current values from widgets into state
        for field, widget in self._widgets.items():
            if isinstance(widget, (ctk.CTkEntry, ctk.CTkOptionMenu)):
                self._state = _ui.update_ui_state(self._state, field, widget.get())

        try:
            payload = _ui.build_submission_payload(self._state)
        except ValueError:
            errors = _ui.validate_ui_state(self._state)
            self._display_errors(errors)
            self._state["status"] = "erreur"
            self._update_status()
            return

        try:
            _svc.save_config(payload, base=self._base)
        except (ValueError, OSError) as exc:
            messagebox.showerror("Erreur", str(exc))
            self._state["status"] = "erreur"
            self._update_status()
            return

        self._state["status"] = "valide"
        self._update_status()

    # ---------------------------------------------------------------
    # Load existing config
    # ---------------------------------------------------------------

    def _load_existing(self):
        data = _svc.load_config(base=self._base)
        if any(v for k, v in data.items() if k != "logo_image"):
            self._state = _ui.create_ui_state(existing=data)
        else:
            self._state = _ui.create_ui_state()

        # Populate widgets
        for field, widget in self._widgets.items():
            value = self._state.get(field, "")
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, "end")
                if isinstance(value, str):
                    widget.insert(0, value)
            elif isinstance(widget, ctk.CTkOptionMenu):
                if isinstance(value, str) and value:
                    widget.set(value)

        # Logo preview
        logo_path = data.get("logo_image", "")
        if logo_path and Path(logo_path).is_file():
            self._logo_source = logo_path
            self._show_logo_preview(logo_path)

        self._update_status()

    # ---------------------------------------------------------------
    # Status & errors
    # ---------------------------------------------------------------

    def _update_status(self):
        status = self._state.get("status", "initial")
        text = _STATUS_TEXT.get(status, status)
        color = _STATUS_COLOR.get(status, "gray")
        if self._status_label:
            self._status_label.configure(text=text, text_color=color)

    def _display_errors(self, errors: list[str]):
        for err in errors:
            for field, label in self._error_labels.items():
                if field in err:
                    label.configure(text=err)
                    break

    def _clear_errors(self):
        for label in self._error_labels.values():
            label.configure(text="")


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("BilanSante - Configuration")
    root.geometry("900x750")

    screen = ConfigScreen(root)
    screen.pack(fill="both", expand=True, padx=20, pady=20)

    root.mainloop()
