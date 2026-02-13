"""CustomTkinter session initialisation screen for Module C.

Standalone launch:
    python apps/desktop/session-and-tablet-access/session_screen.py
"""

from __future__ import annotations

import importlib.util
import sys
import threading
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
_tablet = _load_module(
    "tablet_server",
    _PROJECT_ROOT
    / "apps"
    / "api"
    / "modules"
    / "session-and-tablet-access"
    / "tablet_server.py",
)
_bilan_svc = _load_module(
    "bilan_assembly_service",
    _PROJECT_ROOT
    / "apps"
    / "api"
    / "modules"
    / "bilan-assembly"
    / "service.py",
)
_summary_ui = _load_module(
    "questionnaire_summary_ui",
    _PROJECT_ROOT
    / "apps"
    / "desktop"
    / "bilan-assembly"
    / "questionnaire_summary_ui.py",
)
_co_production_screen_mod = _load_module(
    "co_production_screen",
    _PROJECT_ROOT
    / "apps"
    / "desktop"
    / "co-production"
    / "co_production_screen.py",
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
    "qr_generating": "Generation du QR code...",
    "qr_ready": "QR code pret",
    "erreur": "Erreur",
}

_STATUS_COLOR = {
    "initial": "gray",
    "ready": "#1a73e8",
    "starting": "#1a73e8",
    "created": "#2e7d32",
    "qr_generating": "#1a73e8",
    "qr_ready": "#2e7d32",
    "erreur": "#c62828",
}

_QUESTIONNAIRE_STATUS_TEXT = {
    "disponible": "Disponible",
    "en_cours": "En Cours",
    "termine": "Termine",
}

_QUESTIONNAIRE_STATUS_COLOR = {
    "disponible": "#c62828",      # Red
    "en_cours": "#e65100",        # Orange
    "termine": "#2e7d32",         # Green
}

_POLL_INTERVAL_MS = 1000


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
        self._summary_state = _summary_ui.create_summary_state()
        self._age_range_var = StringVar(value="")
        self._sex_var = StringVar(value="")

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
        row = self._section_sex(scroll, row)
        row = self._section_session_info(scroll, row)
        row = self._section_qr_code(scroll, row)
        row = self._section_questionnaire_summary(scroll, row)

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

    # --- Sex selection section ---

    def _section_sex(self, parent, row: int) -> int:
        title = ctk.CTkLabel(
            parent,
            text="Sexe du patient",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        title.grid(row=row, column=0, sticky="w", **_SECTION_PAD)
        row += 1

        self._sex_radio_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self._sex_radio_frame.grid(row=row, column=0, sticky="w", **_FIELD_PAD)
        row += 1

        self._sex_var.set("")
        for i, (display, code) in enumerate([("Homme", "H"), ("Femme", "F")]):
            rb = ctk.CTkRadioButton(
                self._sex_radio_frame,
                text=display,
                variable=self._sex_var,
                value=code,
                command=self._on_sex_select,
            )
            rb.grid(row=0, column=i, padx=(0, 16), pady=4)

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

    # --- QR code section (visible after session creation) ---

    def _section_qr_code(self, parent, row: int) -> int:
        self._qr_frame = ctk.CTkFrame(parent)
        self._qr_frame.grid(row=row, column=0, sticky="ew", **_SECTION_PAD)
        self._qr_frame.grid_remove()
        row += 1

        title = ctk.CTkLabel(
            self._qr_frame,
            text="QR Code de session",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#2e7d32",
        )
        title.grid(row=0, column=0, sticky="w", padx=12, pady=(8, 4))

        self._qr_image_label = ctk.CTkLabel(
            self._qr_frame, text="", width=250, height=250
        )
        self._qr_image_label.grid(row=1, column=0, padx=12, pady=8)

        # Questionnaire status label (right of the QR code, 20pt)
        self._questionnaire_status_label = ctk.CTkLabel(
            self._qr_frame,
            text="",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w",
        )
        self._questionnaire_status_label.grid(
            row=1, column=1, padx=12, pady=8, sticky="w"
        )

        self._qr_payload_label = ctk.CTkLabel(
            self._qr_frame,
            text="",
            anchor="w",
            wraplength=500,
            font=ctk.CTkFont(size=11),
        )
        self._qr_payload_label.grid(
            row=2, column=0, sticky="w", padx=12, pady=(2, 8)
        )

        return row

    # --- Questionnaire summary section (visible after responses received) ---

    def _section_questionnaire_summary(self, parent, row: int) -> int:
        self._summary_frame = ctk.CTkFrame(parent)
        self._summary_frame.grid(
            row=row, column=0, sticky="ew", **_SECTION_PAD
        )
        self._summary_frame.grid_remove()
        self._summary_frame.grid_columnconfigure(0, weight=1)
        self._summary_frame.grid_columnconfigure(1, weight=1)
        row += 1
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

    def _on_sex_select(self):
        sex = self._sex_var.get()
        if sex:
            self._state = _ui.select_sex(self._state, sex)
        else:
            self._state = _ui.deselect_sex(self._state)
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
            payload = _ui.build_submission_payload(self._state)
            session = _svc.create_session(
                payload["age_range"], payload["sex"], base=self._base
            )
        except (ValueError, RuntimeError, OSError) as exc:
            self._state = _ui.mark_error(self._state, [str(exc)])
            self._error_label.configure(text=str(exc))
            self._update_status()
            return

        self._state = _ui.mark_created(self._state, session)
        self._show_session_info(session)
        self._update_status()

        # Automatically generate QR code
        self._generate_qr_code(session["session_id"])

    # ---------------------------------------------------------------
    # Display helpers
    # ---------------------------------------------------------------

    def _start_tablet_server(self):
        """Start the Flask tablet server in a background thread."""
        if getattr(self, "_server_started", False):
            return
        app = _tablet.create_app(base=self._base)
        thread = threading.Thread(
            target=lambda: app.run(
                host="0.0.0.0",
                port=_svc.TABLET_SERVER_PORT,
                use_reloader=False,
            ),
            daemon=True,
        )
        thread.start()
        self._server_started = True

    def _generate_qr_code(self, session_id: str):
        self._state = _ui.mark_qr_generating(self._state)
        self._update_status()

        # Start the tablet web server before generating the QR code
        try:
            self._start_tablet_server()
        except OSError as exc:
            self._state = _ui.mark_qr_error(
                self._state, [f"Impossible de demarrer le serveur tablette: {exc}"]
            )
            self._error_label.configure(text=str(exc))
            self._update_status()
            return

        try:
            qr_data = _svc.generate_qr_data(session_id, base=self._base)
        except (ValueError, OSError) as exc:
            self._state = _ui.mark_qr_error(self._state, [str(exc)])
            self._error_label.configure(text=str(exc))
            self._update_status()
            return

        self._state = _ui.mark_qr_ready(self._state, qr_data)
        self._show_qr_code(qr_data)

        # Set questionnaire status to "Disponible" (red)
        self._state = _ui.mark_questionnaire_disponible(self._state)
        self._update_questionnaire_status()

        self._update_status()

        # Start polling for status changes
        self._poll_questionnaire_status()

    # ---------------------------------------------------------------
    # Questionnaire status polling
    # ---------------------------------------------------------------

    def _poll_questionnaire_status(self):
        """Poll for questionnaire status changes (tablet loaded / responses received)."""
        current = self._state.get("questionnaire_status")

        # Already at terminal state
        if current == "termine":
            return

        session = self._state.get("session")
        if not session:
            return
        sid = session["session_id"]

        if current == "disponible":
            # Check if the tablet has loaded the questionnaire
            if sid in _tablet.loaded_sessions:
                self._state = _ui.mark_questionnaire_en_cours(self._state)
                self._update_questionnaire_status()

        if self._state.get("questionnaire_status") in ("disponible", "en_cours"):
            # Check if the responses file exists
            base = self._base if self._base is not None else _svc.PROJECT_ROOT
            responses_path = (
                base / "data" / "sessions" / f"{sid}_responses.json"
            )
            if responses_path.is_file():
                self._state = _ui.mark_questionnaire_termine(self._state)
                self._update_questionnaire_status()
                self._build_questionnaire_summary(sid)
                return

        # Schedule next poll
        self.after(_POLL_INTERVAL_MS, self._poll_questionnaire_status)

    def _update_questionnaire_status(self):
        """Update the questionnaire status label text and color."""
        qs = self._state.get("questionnaire_status")
        if qs is None:
            self._questionnaire_status_label.configure(text="")
            return
        text = _QUESTIONNAIRE_STATUS_TEXT.get(qs, qs)
        color = _QUESTIONNAIRE_STATUS_COLOR.get(qs, "gray")
        self._questionnaire_status_label.configure(text=text, text_color=color)

    # ---------------------------------------------------------------
    # Questionnaire summary (BuildQuestionnaireSummarySection)
    # ---------------------------------------------------------------

    def _build_questionnaire_summary(self, session_id: str):
        """Build and display the questionnaire summary after responses are received."""
        self._summary_state = _summary_ui.mark_loading(self._summary_state)

        try:
            summary_data = _bilan_svc.build_questionnaire_summary(
                session_id, base=self._base
            )
        except (ValueError, OSError) as exc:
            self._summary_state = _summary_ui.mark_summary_error(
                self._summary_state, [str(exc)]
            )
            self._error_label.configure(text=str(exc))
            return

        self._summary_state = _summary_ui.load_summary(
            self._summary_state, summary_data
        )
        self._show_questionnaire_summary()

    def _show_questionnaire_summary(self):
        """Populate and display the questionnaire summary frame."""
        items = _summary_ui.get_summary_items(self._summary_state)
        if not items:
            return

        # Clear any previous content
        for widget in self._summary_frame.winfo_children():
            widget.destroy()

        # Title
        title = ctk.CTkLabel(
            self._summary_frame,
            text="Questionnaire - Reponses patient",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#1a73e8",
        )
        title.grid(
            row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(8, 12)
        )

        # Question / response items
        self._note_textboxes: dict[str, ctk.CTkTextbox] = {}
        row = 1
        for i, item in enumerate(items):
            row = self._render_summary_item(i, item, row)

        # Mesures patient section
        metrics = self._summary_state.get("metrics")
        if metrics is not None:
            row = self._render_metrics_section(metrics, row)

        # Tension du patient (mmHg) - pharmacist input
        tension_title = ctk.CTkLabel(
            self._summary_frame,
            text="Tension du patient (mmHg)",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        tension_title.grid(
            row=row, column=0, columnspan=2, sticky="w", padx=12, pady=(16, 4)
        )
        row += 1

        self._tension_textbox = ctk.CTkTextbox(
            self._summary_frame, height=40, wrap="word"
        )
        self._tension_textbox.grid(
            row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(4, 12)
        )
        row += 1

        # Final section: "Rapport du pharmacien"
        report_title = ctk.CTkLabel(
            self._summary_frame,
            text="Rapport du pharmacien",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        report_title.grid(
            row=row, column=0, columnspan=2, sticky="w", padx=12, pady=(16, 4)
        )
        row += 1

        self._report_textbox = ctk.CTkTextbox(
            self._summary_frame, height=120, wrap="word"
        )
        self._report_textbox.grid(
            row=row, column=0, columnspan=2, sticky="ew", padx=12, pady=(4, 12)
        )
        row += 1

        # "Demander a l'IA" button
        self._send_to_ai_btn = ctk.CTkButton(
            self._summary_frame,
            text="Demander a l'IA",
            width=220,
            command=self._on_send_to_ai,
        )
        self._send_to_ai_btn.grid(
            row=row, column=0, columnspan=2, pady=(8, 16)
        )

        self._summary_frame.grid()

    def _render_summary_item(
        self, index: int, item: dict, row: int
    ) -> int:
        """Render a single question/response item in the summary grid.

        Returns the next available row.
        """
        qid = item["question_id"]

        # Left column: question + response
        left = ctk.CTkFrame(self._summary_frame, fg_color="transparent")
        left.grid(row=row, column=0, sticky="new", padx=(12, 4), pady=4)
        left.grid_columnconfigure(0, weight=1)

        q_label = ctk.CTkLabel(
            left,
            text=f"{index + 1}. {item['label']}",
            font=ctk.CTkFont(weight="bold"),
            anchor="w",
            wraplength=350,
            justify="left",
        )
        q_label.grid(row=0, column=0, sticky="w")

        r_label = ctk.CTkLabel(
            left,
            text=f"Reponse : {item['response_display']}",
            anchor="w",
            wraplength=350,
            justify="left",
        )
        r_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Right column: pharmacist note textbox
        note_box = ctk.CTkTextbox(
            self._summary_frame, height=60, wrap="word"
        )
        note_box.grid(row=row, column=1, sticky="ew", padx=(4, 12), pady=4)
        self._note_textboxes[qid] = note_box

        return row + 1

    def _render_metrics_section(self, metrics: dict, row: int) -> int:
        """Render the Mesures patient block (Poids, Taille, IMC)."""
        section_title = ctk.CTkLabel(
            self._summary_frame,
            text="Mesures patient",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        section_title.grid(
            row=row, column=0, columnspan=2, sticky="w", padx=12, pady=(16, 4)
        )
        row += 1

        poids_display = (
            f"{metrics['poids_kg']:.1f} kg"
            if metrics.get("poids_kg") is not None
            else "non renseigne"
        )
        taille_display = (
            f"{metrics['taille_m']:.2f} m"
            if metrics.get("taille_m") is not None
            else "non renseigne"
        )
        imc_display = metrics.get("imc_display", "non calculable")

        for label_text in [
            f"Poids : {poids_display}",
            f"Taille : {taille_display}",
            f"IMC : {imc_display}",
        ]:
            lbl = ctk.CTkLabel(
                self._summary_frame,
                text=label_text,
                anchor="w",
            )
            lbl.grid(row=row, column=0, columnspan=2, sticky="w", padx=24, pady=1)
            row += 1

        return row

    def _on_send_to_ai(self):
        """Handle click on 'Demander a l'IA': capture notes and transition."""
        # 1. Collect pharmacist inputs from textboxes into state
        for qid, textbox in self._note_textboxes.items():
            note = textbox.get("1.0", "end-1c")
            self._summary_state = _summary_ui.update_pharmacist_note(
                self._summary_state, qid, note
            )
        tension = self._tension_textbox.get("1.0", "end-1c")
        self._summary_state = _summary_ui.update_pharmacist_blood_pressure(
            self._summary_state, tension
        )
        report = self._report_textbox.get("1.0", "end-1c")
        self._summary_state = _summary_ui.update_pharmacist_report(
            self._summary_state, report
        )

        # 2. Call service to persist notes into markdown
        self._summary_state = _summary_ui.mark_capturing(self._summary_state)
        self._send_to_ai_btn.configure(state="disabled")

        data = _summary_ui.get_pharmacist_data(self._summary_state)
        sid = self._summary_state["session_id"]
        try:
            _bilan_svc.capture_interview_notes(
                session_id=sid,
                pharmacist_notes=data["pharmacist_notes"],
                pharmacist_blood_pressure=data["pharmacist_blood_pressure"],
                pharmacist_report=data["pharmacist_report"],
                base=self._base,
            )
        except (ValueError, OSError) as exc:
            self._summary_state = _summary_ui.mark_capture_error(
                self._summary_state, [str(exc)]
            )
            self._error_label.configure(text=str(exc))
            self._send_to_ai_btn.configure(state="normal")
            return

        # 3. Transition: destroy SessionScreen, create CoProductionScreen
        self._summary_state = _summary_ui.mark_captured(self._summary_state)
        sid = self._summary_state["session_id"]
        md_path = self._summary_state["md_path"]
        root = self.winfo_toplevel()

        self.destroy()

        co_screen = _co_production_screen_mod.CoProductionScreen(
            root, session_id=sid, md_path=md_path
        )
        co_screen.pack(fill="both", expand=True, padx=20, pady=20)

    # ---------------------------------------------------------------
    # Display helpers
    # ---------------------------------------------------------------

    def _show_qr_code(self, qr_data: dict):
        payload = qr_data["payload"]
        self._qr_payload_label.configure(text=payload)

        try:
            import qrcode
            from PIL import Image as PILImage

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=6,
                border=4,
            )
            qr.add_data(payload)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            pil_img = img.get_image().resize((250, 250), PILImage.NEAREST)
            ctk_img = ctk.CTkImage(
                light_image=pil_img, dark_image=pil_img, size=(250, 250)
            )
            self._qr_image_label.configure(image=ctk_img, text="")
            self._qr_image_label._ctk_image = ctk_img  # prevent GC
        except Exception:
            self._qr_image_label.configure(text="[QR Code]")

        self._qr_frame.grid()

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
