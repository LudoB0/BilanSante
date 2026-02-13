"""CustomTkinter co-production screen.

Displayed after the pharmacist clicks 'Demander a l'IA' in the
SessionScreen.  Launches the AI vigilance call in a daemon thread,
displays the result, then offers 3 action-point inputs and a
Validate button.

The SessionScreen is destroyed before this screen is created in the
same root CTk window.
"""

from __future__ import annotations

import importlib.util
import sys
import threading
from pathlib import Path

import customtkinter as ctk

# ---------------------------------------------------------------------------
# Module loading (hyphenated directories)
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


_bilan_svc = _load_module(
    "bilan_assembly_service",
    _PROJECT_ROOT
    / "apps"
    / "api"
    / "modules"
    / "bilan-assembly"
    / "service.py",
)
_co_ui = _load_module(
    "co_production_ui",
    _THIS_DIR / "co_production_ui.py",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_POLL_INTERVAL_MS = 200


# ---------------------------------------------------------------------------
# CoProductionScreen
# ---------------------------------------------------------------------------


class CoProductionScreen(ctk.CTkFrame):
    """Co-production avec l'IA screen."""

    def __init__(
        self,
        master,
        session_id: str,
        md_path: str,
        base_path: Path | None = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self._session_id = session_id
        self._md_path = md_path
        self._base = base_path
        self._state = _co_ui.create_co_production_state()

        # Thread result storage
        self._ai_result: dict | None = None
        self._ai_error: str | None = None

        self._build_layout()
        self._launch_ai_call()

    # ---------------------------------------------------------------
    # Layout
    # ---------------------------------------------------------------

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Title
        title = ctk.CTkLabel(
            self,
            text="Co-production avec l'IA",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1a73e8",
        )
        title.grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        # Content area (scrollable)
        scroll = ctk.CTkScrollableFrame(self)
        scroll.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        scroll.grid_columnconfigure(0, weight=1)
        self._scroll = scroll

        # Status indicator
        self._status_label = ctk.CTkLabel(
            scroll,
            text="Analyse en cours...",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#e65100",
            anchor="w",
        )
        self._status_label.grid(row=0, column=0, sticky="w", padx=8, pady=(12, 8))

        # AI response area (initially empty)
        self._response_textbox = ctk.CTkTextbox(
            scroll, height=300, wrap="word", state="disabled"
        )
        self._response_textbox.grid(
            row=1, column=0, sticky="nsew", padx=8, pady=(4, 12)
        )

        # Action points frame (hidden until AI result is received)
        self._action_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self._action_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=(8, 4))
        self._action_frame.grid_remove()
        self._action_frame.grid_columnconfigure(0, weight=1)

        action_title = ctk.CTkLabel(
            self._action_frame,
            text="Plan d'action - 3 points pharmacien",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        action_title.grid(row=0, column=0, sticky="w", pady=(0, 8))

        self._action_textboxes: list[ctk.CTkTextbox] = []
        for i in range(3):
            label = ctk.CTkLabel(
                self._action_frame,
                text=f"Point {i + 1}",
                font=ctk.CTkFont(weight="bold"),
                anchor="w",
            )
            label.grid(row=1 + i * 2, column=0, sticky="w", pady=(4, 0))

            tb = ctk.CTkTextbox(self._action_frame, height=60, wrap="word")
            tb.grid(row=2 + i * 2, column=0, sticky="ew", pady=(2, 8))
            self._action_textboxes.append(tb)

        self._validate_btn = ctk.CTkButton(
            self._action_frame,
            text="Valider",
            width=220,
            command=self._on_validate,
            state="disabled",
        )
        self._validate_btn.grid(row=7, column=0, pady=(8, 16))

        # Confirmation label (hidden initially)
        self._confirm_label = ctk.CTkLabel(
            scroll,
            text="",
            text_color="#2e7d32",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        self._confirm_label.grid(row=3, column=0, sticky="w", padx=8, pady=(4, 8))
        self._confirm_label.grid_remove()

    # ---------------------------------------------------------------
    # AI call (thread daemon)
    # ---------------------------------------------------------------

    def _launch_ai_call(self):
        """Start the AI vigilance call in a background thread."""
        self._state = _co_ui.mark_loading(self._state)

        thread = threading.Thread(
            target=self._ai_worker,
            daemon=True,
        )
        thread.start()
        self._poll_ai_result()

    def _ai_worker(self):
        """Worker running in a daemon thread."""
        try:
            result = _bilan_svc.identify_vigilance_points(
                self._session_id, base=self._base
            )
            self._ai_result = result
        except Exception as exc:
            self._ai_error = str(exc)

    def _poll_ai_result(self):
        """Poll for the AI thread result using .after()."""
        if self._ai_result is not None:
            self._on_ai_success(self._ai_result)
            return
        if self._ai_error is not None:
            self._on_ai_error(self._ai_error)
            return
        self.after(_POLL_INTERVAL_MS, self._poll_ai_result)

    def _on_ai_success(self, result: dict):
        """Handle successful AI response."""
        self._state = _co_ui.load_vigilance_result(self._state, result)

        # Display AI result
        self._status_label.configure(
            text="Analyse terminee", text_color="#2e7d32"
        )
        self._response_textbox.configure(state="normal")
        self._response_textbox.delete("1.0", "end")
        self._response_textbox.insert("1.0", result["vigilance_text"])
        self._response_textbox.configure(state="disabled")

        # Show action points section
        self._action_frame.grid()
        self._update_validate_button()

    def _on_ai_error(self, message: str):
        """Handle AI call error."""
        self._state = _co_ui.mark_vigilance_error(self._state, [message])
        self._status_label.configure(
            text=f"Erreur : {message}", text_color="#c62828"
        )

    # ---------------------------------------------------------------
    # Action points & validation
    # ---------------------------------------------------------------

    def _update_validate_button(self):
        """Enable Valider button only when all 3 points are filled."""
        all_filled = all(
            tb.get("1.0", "end-1c").strip()
            for tb in self._action_textboxes
        )
        state = "normal" if all_filled else "disabled"
        self._validate_btn.configure(state=state)

    def _on_validate(self):
        """Handle click on 'Valider': save action points."""
        # Collect action points
        points = []
        for i, tb in enumerate(self._action_textboxes):
            text = tb.get("1.0", "end-1c")
            self._state = _co_ui.update_action_point(self._state, i, text)
            points.append(text)

        # Save
        self._state = _co_ui.mark_saving(self._state)
        self._validate_btn.configure(state="disabled")

        try:
            _bilan_svc.save_action_points(
                session_id=self._session_id,
                action_points=points,
                base=self._base,
            )
        except (ValueError, OSError) as exc:
            self._state = _co_ui.mark_save_error(self._state, [str(exc)])
            self._status_label.configure(
                text=f"Erreur sauvegarde : {exc}", text_color="#c62828"
            )
            self._validate_btn.configure(state="normal")
            return

        # Success
        self._state = _co_ui.mark_saved(self._state)
        self._confirm_label.configure(
            text="Points du plan d'action enregistres avec succes."
        )
        self._confirm_label.grid()

        # Disable inputs
        for tb in self._action_textboxes:
            tb.configure(state="disabled")


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("BilanSante - Co-production avec l'IA")
    root.geometry("900x600")

    screen = CoProductionScreen(
        root,
        session_id="demo-session-id",
        md_path="/tmp/demo.md",
    )
    screen.pack(fill="both", expand=True, padx=20, pady=20)

    root.mainloop()
