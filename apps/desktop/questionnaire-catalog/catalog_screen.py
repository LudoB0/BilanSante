"""CustomTkinter screen for the questionnaire-catalog module.

Standalone launch:
    python apps/desktop/questionnaire-catalog/catalog_screen.py
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from tkinter import messagebox

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


_ui = _load_module(
    "questionnaire_catalog_ui", _THIS_DIR / "questionnaire_catalog_ui.py"
)
_svc = _load_module(
    "questionnaire_catalog_service",
    _PROJECT_ROOT / "apps" / "api" / "modules" / "questionnaire-catalog" / "service.py",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SECTION_PAD = {"padx": 16, "pady": (16, 4)}
_FIELD_PAD = {"padx": 24, "pady": 2}

_QUESTION_TYPES_LABELS = {
    "boolean": "Oui / Non",
    "single_choice": "Choix unique",
    "multiple_choice": "Choix multiple",
    "short_text": "Texte court",
    "scale": "Echelle",
}

_TYPE_VALUES = list(_QUESTION_TYPES_LABELS.keys())
_TYPE_DISPLAY = list(_QUESTION_TYPES_LABELS.values())

_STATUS_TEXT = {
    "initial": "Selectionnez une tranche d'age",
    "creation": "Nouveau questionnaire",
    "edition": "Modification en cours...",
    "valide": "Questionnaire enregistre",
    "erreur": "Erreurs de validation",
}

_STATUS_COLOR = {
    "initial": "gray",
    "creation": "#1a73e8",
    "edition": "#1a73e8",
    "valide": "#2e7d32",
    "erreur": "#c62828",
}


# ---------------------------------------------------------------------------
# CatalogScreen
# ---------------------------------------------------------------------------


class CatalogScreen(ctk.CTkFrame):
    """Questionnaire catalog editor (DEV-ENV section 9.3, Step 2)."""

    def __init__(
        self,
        master,
        base_path: Path | None = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self._base = base_path
        self._state = _ui.create_ui_state(
            configured_ranges=_svc.list_questionnaires(base=self._base)
        )
        self._question_frames: list[ctk.CTkFrame] = []
        self._age_range_buttons: dict[str, ctk.CTkButton] = {}

        self._build_layout()

    # ---------------------------------------------------------------
    # Layout
    # ---------------------------------------------------------------

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0, minsize=200)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_right_panel()
        self._build_bottom_bar()

    # --- Left panel: age range list ---

    def _build_left_panel(self):
        panel = ctk.CTkFrame(self, width=200)
        panel.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=(8, 0))
        panel.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            panel,
            text="Tranches d'age",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        title.grid(row=0, column=0, sticky="w", **_SECTION_PAD)

        for i, age_range in enumerate(_svc.VALID_AGE_RANGES):
            is_configured = self._state["age_ranges_status"].get(age_range, False)
            icon = "\u2713 " if is_configured else "  "
            btn = ctk.CTkButton(
                panel,
                text=f"{icon}{age_range} ans",
                width=170,
                anchor="w",
                command=lambda ar=age_range: self._on_select_age_range(ar),
            )
            btn.grid(row=i + 1, column=0, padx=12, pady=4)
            self._age_range_buttons[age_range] = btn

    # --- Right panel: question editor ---

    def _build_right_panel(self):
        self._right_frame = ctk.CTkFrame(self)
        self._right_frame.grid(row=0, column=1, sticky="nsew", padx=8, pady=(8, 0))
        self._right_frame.grid_columnconfigure(0, weight=1)
        self._right_frame.grid_rowconfigure(0, weight=1)

        self._placeholder = ctk.CTkLabel(
            self._right_frame,
            text="Selectionnez une tranche d'age\npour creer ou editer un questionnaire",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        self._placeholder.grid(row=0, column=0, sticky="nsew")

        # Scrollable editor (hidden initially)
        self._editor_scroll = ctk.CTkScrollableFrame(self._right_frame)
        self._editor_scroll.grid_columnconfigure(0, weight=1)

        self._add_btn = ctk.CTkButton(
            self._right_frame,
            text="+ Ajouter une question",
            command=self._on_add_question,
        )

    # --- Bottom bar ---

    def _build_bottom_bar(self):
        bar = ctk.CTkFrame(self)
        bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=8)
        bar.grid_columnconfigure(0, weight=1)

        self._status_label = ctk.CTkLabel(bar, text="", anchor="w")
        self._status_label.grid(row=0, column=0, sticky="w", padx=8)

        self._error_label = ctk.CTkLabel(
            bar, text="", text_color="#c62828", anchor="w", wraplength=500
        )
        self._error_label.grid(row=1, column=0, sticky="w", padx=8)

        save_btn = ctk.CTkButton(
            bar, text="Enregistrer", width=180, command=self._on_save
        )
        save_btn.grid(row=0, column=1, rowspan=2, padx=8, pady=4)

        self._update_status()

    # ---------------------------------------------------------------
    # Question editor rebuild
    # ---------------------------------------------------------------

    def _show_editor(self):
        self._placeholder.grid_forget()
        self._editor_scroll.grid(row=0, column=0, sticky="nsew")
        self._add_btn.grid(row=1, column=0, pady=8)

    def _hide_editor(self):
        self._editor_scroll.grid_forget()
        self._add_btn.grid_forget()
        self._placeholder.grid(row=0, column=0, sticky="nsew")

    def _rebuild_question_editor(self):
        for frame in self._question_frames:
            frame.destroy()
        self._question_frames.clear()

        questionnaire = self._state.get("questionnaire")
        if not questionnaire:
            self._show_editor()
            return

        self._show_editor()
        questions = questionnaire.get("questions", [])

        for i, q in enumerate(questions):
            card = self._build_question_card(i, q, len(questions))
            card.grid(row=i, column=0, sticky="ew", padx=8, pady=4)
            self._question_frames.append(card)

    def _build_question_card(
        self, index: int, question: dict, total: int
    ) -> ctk.CTkFrame:
        card = ctk.CTkFrame(self._editor_scroll, corner_radius=8)
        card.grid_columnconfigure(1, weight=1)

        # Header row: number + move + delete
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=3, sticky="ew", padx=8, pady=(8, 2))
        header.grid_columnconfigure(1, weight=1)

        num_label = ctk.CTkLabel(
            header,
            text=f"Question {index + 1}",
            font=ctk.CTkFont(weight="bold"),
        )
        num_label.grid(row=0, column=0, sticky="w")

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.grid(row=0, column=2, sticky="e")

        if index > 0:
            up_btn = ctk.CTkButton(
                btn_frame, text="\u25B2", width=32,
                command=lambda idx=index: self._on_move_question(idx, idx - 1),
            )
            up_btn.grid(row=0, column=0, padx=2)

        if index < total - 1:
            down_btn = ctk.CTkButton(
                btn_frame, text="\u25BC", width=32,
                command=lambda idx=index: self._on_move_question(idx, idx + 1),
            )
            down_btn.grid(row=0, column=1, padx=2)

        del_btn = ctk.CTkButton(
            btn_frame, text="Supprimer", width=80,
            fg_color="#c62828", hover_color="#b71c1c",
            command=lambda idx=index: self._on_remove_question(idx),
        )
        del_btn.grid(row=0, column=2, padx=(8, 0))

        # Type dropdown
        type_label = ctk.CTkLabel(card, text="Type", anchor="w")
        type_label.grid(row=1, column=0, sticky="w", padx=8, pady=2)

        current_type = question.get("type", "boolean")
        display_idx = _TYPE_VALUES.index(current_type) if current_type in _TYPE_VALUES else 0
        type_menu = ctk.CTkOptionMenu(
            card,
            values=_TYPE_DISPLAY,
            command=lambda val, idx=index: self._on_type_change(idx, val),
        )
        type_menu.set(_TYPE_DISPLAY[display_idx])
        type_menu.grid(row=1, column=1, sticky="w", padx=8, pady=2)

        # Label entry
        label_label = ctk.CTkLabel(card, text="Libelle", anchor="w")
        label_label.grid(row=2, column=0, sticky="w", padx=8, pady=2)

        label_entry = ctk.CTkEntry(card, width=400)
        label_entry.insert(0, question.get("label", ""))
        label_entry.bind(
            "<KeyRelease>",
            lambda _e, idx=index, entry=label_entry: self._on_label_change(
                idx, entry.get()
            ),
        )
        label_entry.grid(row=2, column=1, columnspan=2, sticky="ew", padx=8, pady=2)

        row = 3

        # Conditional: options for choice types
        if current_type in ("single_choice", "multiple_choice"):
            row = self._build_options_section(card, row, index, question)

        # Conditional: scale config
        if current_type == "scale":
            row = self._build_scale_section(card, row, index, question)

        # Bottom padding
        spacer = ctk.CTkLabel(card, text="", height=4)
        spacer.grid(row=row, column=0)

        return card

    def _build_options_section(
        self, parent: ctk.CTkFrame, row: int, q_index: int, question: dict
    ) -> int:
        opts_label = ctk.CTkLabel(parent, text="Options", anchor="w")
        opts_label.grid(row=row, column=0, sticky="nw", padx=8, pady=2)
        row += 1

        options = question.get("options", [])
        for j, opt in enumerate(options):
            opt_frame = ctk.CTkFrame(parent, fg_color="transparent")
            opt_frame.grid(row=row, column=1, columnspan=2, sticky="ew", padx=8, pady=1)
            opt_frame.grid_columnconfigure(0, weight=1)

            opt_entry = ctk.CTkEntry(opt_frame, width=350)
            opt_entry.insert(0, opt)
            opt_entry.bind(
                "<KeyRelease>",
                lambda _e, qi=q_index, oi=j, entry=opt_entry: self._on_option_change(
                    qi, oi, entry.get()
                ),
            )
            opt_entry.grid(row=0, column=0, sticky="ew")

            rm_btn = ctk.CTkButton(
                opt_frame, text="X", width=32,
                command=lambda qi=q_index, oi=j: self._on_remove_option(qi, oi),
            )
            rm_btn.grid(row=0, column=1, padx=(4, 0))
            row += 1

        add_opt_btn = ctk.CTkButton(
            parent, text="+ Option", width=100,
            command=lambda qi=q_index: self._on_add_option(qi),
        )
        add_opt_btn.grid(row=row, column=1, sticky="w", padx=8, pady=4)
        row += 1

        return row

    def _build_scale_section(
        self, parent: ctk.CTkFrame, row: int, q_index: int, question: dict
    ) -> int:
        sc = question.get("scale_config") or {"min": 1, "max": 10, "step": 1}

        scale_frame = ctk.CTkFrame(parent, fg_color="transparent")
        scale_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=8, pady=4)

        for col, (field, label_text) in enumerate([
            ("min", "Min"), ("max", "Max"), ("step", "Pas")
        ]):
            lbl = ctk.CTkLabel(scale_frame, text=label_text, anchor="w")
            lbl.grid(row=0, column=col * 2, padx=(8, 2))

            entry = ctk.CTkEntry(scale_frame, width=60)
            entry.insert(0, str(sc.get(field, "")))
            entry.bind(
                "<KeyRelease>",
                lambda _e, qi=q_index, f=field, ent=entry: self._on_scale_change(
                    qi, f, ent.get()
                ),
            )
            entry.grid(row=0, column=col * 2 + 1, padx=(0, 8))

        row += 1
        return row

    # ---------------------------------------------------------------
    # Callbacks
    # ---------------------------------------------------------------

    def _on_select_age_range(self, age_range: str):
        questionnaire = _svc.load_questionnaire(age_range, base=self._base)
        has_questions = bool(questionnaire.get("questions"))
        self._state = _ui.select_age_range(
            self._state, age_range,
            questionnaire if has_questions else None,
        )
        self._rebuild_question_editor()
        self._update_status()
        self._clear_errors()

    def _on_add_question(self):
        questions = []
        if self._state["questionnaire"]:
            questions = self._state["questionnaire"].get("questions", [])
        new_q = _svc.new_question(questions)
        self._state = _ui.add_question(self._state, new_q)
        self._rebuild_question_editor()
        self._update_status()

    def _on_remove_question(self, index: int):
        self._state = _ui.remove_question(self._state, index)
        self._rebuild_question_editor()
        self._update_status()

    def _on_type_change(self, index: int, display_value: str):
        idx = _TYPE_DISPLAY.index(display_value) if display_value in _TYPE_DISPLAY else 0
        type_value = _TYPE_VALUES[idx]
        self._state = _ui.update_question(self._state, index, "type", type_value)
        self._rebuild_question_editor()
        self._update_status()

    def _on_label_change(self, index: int, value: str):
        self._state = _ui.update_question(self._state, index, "label", value)
        self._update_status()

    def _on_option_change(self, q_index: int, opt_index: int, value: str):
        self._state = _ui.update_option(self._state, q_index, opt_index, value)
        self._update_status()

    def _on_add_option(self, q_index: int):
        self._state = _ui.add_option(self._state, q_index)
        self._rebuild_question_editor()
        self._update_status()

    def _on_remove_option(self, q_index: int, opt_index: int):
        self._state = _ui.remove_option(self._state, q_index, opt_index)
        self._rebuild_question_editor()
        self._update_status()

    def _on_move_question(self, from_idx: int, to_idx: int):
        self._state = _ui.move_question(self._state, from_idx, to_idx)
        self._rebuild_question_editor()
        self._update_status()

    def _on_scale_change(self, q_index: int, field: str, raw_value: str):
        try:
            value = int(raw_value)
        except (ValueError, TypeError):
            return
        q = self._state["questionnaire"]["questions"][q_index]
        sc = dict(q.get("scale_config") or {"min": 1, "max": 10, "step": 1})
        sc[field] = value
        self._state = _ui.update_question(
            self._state, q_index, "scale_config", sc
        )
        self._update_status()

    def _on_save(self):
        self._clear_errors()

        try:
            payload = _ui.build_submission_payload(self._state)
        except ValueError:
            errors = _ui.validate_ui_state(self._state)
            self._state = _ui.mark_error(self._state, errors)
            self._display_errors(errors)
            self._update_status()
            return

        try:
            _svc.save_questionnaire(payload, base=self._base)
        except (ValueError, OSError) as exc:
            messagebox.showerror("Erreur", str(exc))
            self._state = _ui.mark_error(self._state, [str(exc)])
            self._update_status()
            return

        self._state = _ui.mark_saved(self._state)
        self._update_left_panel()
        self._update_status()

    # ---------------------------------------------------------------
    # Status & errors
    # ---------------------------------------------------------------

    def _update_status(self):
        status = self._state.get("status", "initial")
        text = _STATUS_TEXT.get(status, status)
        color = _STATUS_COLOR.get(status, "gray")

        selected = self._state.get("selected_age_range")
        if selected:
            text = f"[{selected} ans] {text}"

        self._status_label.configure(text=text, text_color=color)

    def _update_left_panel(self):
        for age_range, btn in self._age_range_buttons.items():
            is_configured = self._state["age_ranges_status"].get(age_range, False)
            icon = "\u2713 " if is_configured else "  "
            btn.configure(text=f"{icon}{age_range} ans")

    def _display_errors(self, errors: list[str]):
        self._error_label.configure(text="\n".join(errors))

    def _clear_errors(self):
        self._error_label.configure(text="")


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("BilanSante - Questionnaires par tranche d'age")
    root.geometry("1000x700")

    screen = CatalogScreen(root)
    screen.pack(fill="both", expand=True, padx=10, pady=10)

    root.mainloop()
