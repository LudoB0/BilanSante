"""CustomTkinter session initialisation screen for Module C.

Standalone launch:
    python apps/desktop/session-and-tablet-access/session_screen.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from tkinter import StringVar

import customtkinter as ctk

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


_ui = _load_module("session_ui", _THIS_DIR / "session_ui.py")
_svc = _load_module(
    "session_service",
    _PROJECT_ROOT
    / "apps"
    / "api"
    / "modules"
    / "session-and-tablet-access"
    / "service.py",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SECTION_PAD = {"padx": 16, "pady": (16, 4)}
_FIELD_PAD = {"padx": 24, "pady": 2}

_WEB_LINK_LABELS = {
    "site_web": "Site web",
    "instagram": "Instagram",
    "facebook": "Facebook",
    "x": "X",
    "linkedin": "LinkedIn",
}

_STATUS_TEXT = {
    "initial": "Chargement...",
    "ready": "Pret a demarrer un entretien",
    "starting": "Creation de la session...",
    "created": "Session creee",
    "erreur": "Erreur",
}

_STATUS_COLOR = {
    "initial": "gray",
    "ready": "#1a73e8",
    "starting": "#1a73e8",
    "created": "#2e7d32",
    "erreur": "#c62828",
}


# ---------------------------------------------------------------------------
# SessionScreen
# ---------------------------------------------------------------------------


class SessionScreen(ctk.CTkFrame):
    """Session initialisation screen (PRD Step 3)."""

    def __init__(
        self,
        master,
        base_path: Path | None = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self._base = base_path
        self._state = _ui.create_ui_state()
        self._age_range_var = StringVar(value="")

        self._build_layout()
        self._load_data()

    # ---------------------------------------------------------------
    # Layout
    # ---------------------------------------------------------------

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(self)
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)
        self._scroll = scroll

        row = 0
        row = self._section_pharmacy(scroll, row)
        row = self._section_age_range(scroll, row)
        row = self._section_session_info(scroll, row)

        # Action bar (outside scroll)
        bar = ctk.CTkFrame(self)
        bar.grid(row=1, column=0, sticky="ew", padx=16, pady=8)
        bar.grid_columnconfigure(0, weight=1)

        self._status_label = ctk.CTkLabel(bar, text="", anchor="w")
        self._status_label.grid(row=0, column=0, sticky="w", padx=8)

        self._error_label = ctk.CTkLabel(
            bar, text="", text_color="#c62828", anchor="w", wraplength=500
        )
        self._error_label.grid(row=1, column=0, sticky="w", padx=8)

        self._start_btn = ctk.CTkButton(
            bar,
            text="Demarrer l'entretien",
            width=220,
            command=self._on_start_session,
            state="disabled",
        )
        self._start_btn.grid(row=0, column=1, rowspan=2, padx=8, pady=4)

        self._update_status()

    # --- Pharmacy context section ---

    def _section_pharmacy(self, parent, row: int) -> int:
        # Logo + name header
        self._header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self._header_frame.grid(row=row, column=0, sticky="ew", **_SECTION_PAD)
        row += 1

        self._logo_label = ctk.CTkLabel(
            self._header_frame, text="", width=80, height=80
        )
        self._logo_label.grid(row=0, column=0, padx=(0, 16), pady=4)

        self._name_label = ctk.CTkLabel(
            self._header_frame,
            text="",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w",
        )
        self._name_label.grid(row=0, column=1, sticky="w")

        # Address
        self._address_label = ctk.CTkLabel(parent, text="", anchor="w")
        self._address_label.grid(row=row, column=0, sticky="w", **_FIELD_PAD)
        row += 1

        # Web links frame (only visible if at least one link is non-empty)
        self._links_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self._links_frame.grid(row=row, column=0, sticky="w", **_FIELD_PAD)
        self._links_frame.grid_remove()
        self._link_labels: list[ctk.CTkLabel] = []
        row += 1

        return row

    # --- Age range selection section ---

    def _section_age_range(self, parent, row: int) -> int:
        title = ctk.CTkLabel(
            parent,
            text="Tranche d'age du patient",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        title.grid(row=row, column=0, sticky="w", **_SECTION_PAD)
        row += 1

        self._radio_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self._radio_frame.grid(row=row, column=0, sticky="w", **_FIELD_PAD)
        row += 1

        self._no_questionnaire_label = ctk.CTkLabel(
            parent,
            text="Aucun questionnaire disponible",
            text_color="#c62828",
            anchor="w",
        )
        self._no_questionnaire_label.grid(
            row=row, column=0, sticky="w", **_FIELD_PAD
        )
        self._no_questionnaire_label.grid_remove()
        row += 1

        return row

    # --- Session info section (visible after creation) ---

    def _section_session_info(self, parent, row: int) -> int:
        self._session_info_frame = ctk.CTkFrame(parent)
        self._session_info_frame.grid(
            row=row, column=0, sticky="ew", **_SECTION_PAD
        )
        self._session_info_frame.grid_remove()
        row += 1

        title = ctk.CTkLabel(
            self._session_info_frame,
            text="Session creee",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#2e7d32",
        )
        title.grid(row=0, column=0, sticky="w", padx=12, pady=(8, 4))

        self._session_id_label = ctk.CTkLabel(
            self._session_info_frame, text="", anchor="w"
        )
        self._session_id_label.grid(row=1, column=0, sticky="w", padx=12, pady=2)

        self._session_age_label = ctk.CTkLabel(
            self._session_info_frame, text="", anchor="w"
        )
        self._session_age_label.grid(row=2, column=0, sticky="w", padx=12, pady=(2, 8))

        return row

    # ---------------------------------------------------------------
    # Data loading
    # ---------------------------------------------------------------

    def _load_data(self):
        precondition_errors = _svc.check_preconditions(base=self._base)
        pharmacy_context = _svc.load_pharmacy_context(base=self._base)
        available_ranges = _svc.list_available_age_ranges(base=self._base)

        self._state = _ui.load_context(
            self._state, pharmacy_context, available_ranges, precondition_errors
        )

        self._populate_pharmacy(pharmacy_context)
        self._populate_age_ranges(available_ranges)
        self._update_button_state()
        self._update_status()

    def _populate_pharmacy(self, ctx: dict):
        # Logo
        logo_path = ctx.get("logo_path", "")
        if logo_path and Path(logo_path).is_file():
            try:
                from PIL import Image

                img = Image.open(logo_path)
                img.thumbnail((80, 80))
                ctk_img = ctk.CTkImage(
                    light_image=img, dark_image=img, size=img.size
                )
                self._logo_label.configure(image=ctk_img, text="")
                self._logo_label._ctk_image = ctk_img  # prevent GC
            except Exception:
                self._logo_label.configure(text="[logo]")
        else:
            self._logo_label.configure(text="[logo]")

        # Name
        self._name_label.configure(text=ctx.get("nom_pharmacie", ""))

        # Address line
        address_parts = []
        adresse = ctx.get("adresse", "")
        if adresse:
            address_parts.append(adresse)
        cp = ctx.get("code_postal", "")
        ville = ctx.get("ville", "")
        if cp or ville:
            address_parts.append(f"{cp} {ville}".strip())
        self._address_label.configure(text=" - ".join(address_parts))

        # Web links (only non-empty)
        for lbl in self._link_labels:
            lbl.destroy()
        self._link_labels.clear()

        col = 0
        for field, display_name in _WEB_LINK_LABELS.items():
            value = ctx.get(field, "")
            if value:
                lbl = ctk.CTkLabel(
                    self._links_frame,
                    text=f"{display_name}: {value}",
                    text_color="#1a73e8",
                    anchor="w",
                )
                lbl.grid(row=0, column=col, padx=(0, 16), pady=2)
                self._link_labels.append(lbl)
                col += 1

        if self._link_labels:
            self._links_frame.grid()
        else:
            self._links_frame.grid_remove()

    def _populate_age_ranges(self, ranges: list[str]):
        for widget in self._radio_frame.winfo_children():
            widget.destroy()

        if not ranges:
            self._no_questionnaire_label.grid()
            return
        self._no_questionnaire_label.grid_remove()

        self._age_range_var.set("")
        for i, age_range in enumerate(ranges):
            rb = ctk.CTkRadioButton(
                self._radio_frame,
                text=f"{age_range} ans",
                variable=self._age_range_var,
                value=age_range,
                command=self._on_age_range_select,
            )
            rb.grid(row=0, column=i, padx=(0, 16), pady=4)

    # ---------------------------------------------------------------
    # Callbacks
    # ---------------------------------------------------------------

    def _on_age_range_select(self):
        age_range = self._age_range_var.get()
        if age_range:
            self._state = _ui.select_age_range(self._state, age_range)
        else:
            self._state = _ui.deselect_age_range(self._state)
        self._error_label.configure(text="")
        self._update_button_state()
        self._update_status()

    def _on_start_session(self):
        self._error_label.configure(text="")

        errors = _ui.validate_ui_state(self._state)
        if errors:
            self._state = _ui.mark_error(self._state, errors)
            self._error_label.configure(text="; ".join(errors))
            self._update_status()
            return

        self._state = _ui.mark_starting(self._state)
        self._update_status()
        self._start_btn.configure(state="disabled")

        try:
            age_range = _ui.build_submission_payload(self._state)
            session = _svc.create_session(age_range, base=self._base)
        except (ValueError, RuntimeError, OSError) as exc:
            self._state = _ui.mark_error(self._state, [str(exc)])
            self._error_label.configure(text=str(exc))
            self._update_status()
            return

        self._state = _ui.mark_created(self._state, session)
        self._show_session_info(session)
        self._update_status()

    # ---------------------------------------------------------------
    # Display helpers
    # ---------------------------------------------------------------

    def _show_session_info(self, session: dict):
        self._session_id_label.configure(
            text=f"ID : {session['session_id']}"
        )
        self._session_age_label.configure(
            text=f"Tranche d'age : {session['age_range']} ans"
        )
        self._session_info_frame.grid()

    def _update_button_state(self):
        if _ui.can_start(self._state):
            self._start_btn.configure(state="normal")
        else:
            self._start_btn.configure(state="disabled")

    def _update_status(self):
        status = self._state.get("status", "initial")
        text = _STATUS_TEXT.get(status, status)
        color = _STATUS_COLOR.get(status, "gray")
        self._status_label.configure(text=text, text_color=color)

        if status == "created":
            self._start_btn.configure(state="disabled")


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("BilanSante - Initialisation de session")
    root.geometry("900x600")

    screen = SessionScreen(root)
    screen.pack(fill="both", expand=True, padx=20, pady=20)

    root.mainloop()
