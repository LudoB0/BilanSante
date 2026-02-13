"""Flask mini web server for tablet questionnaire access.

Exposes the questionnaire on the local pharmacy network so the
tablet can load it by scanning the session QR code.

Standalone launch:
    python apps/api/modules/session-and-tablet-access/tablet_server.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime
from html import escape
from pathlib import Path

from flask import Flask, Response, jsonify, request

# ---------------------------------------------------------------------------
# Shared state: sessions whose questionnaire has been loaded on the tablet
# ---------------------------------------------------------------------------

loaded_sessions: set[str] = set()

# ---------------------------------------------------------------------------
# Module loading (hyphenated directories)
# ---------------------------------------------------------------------------

_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parents[3]


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


# ---------------------------------------------------------------------------
# HTML template helpers
# ---------------------------------------------------------------------------


def _render_question_html(question: dict, index: int) -> str:
    """Render a single question as HTML form fields."""
    qid = escape(question.get("id", f"q{index}"))
    label = escape(question.get("label", ""))
    qtype = question.get("type", "boolean")
    required = question.get("required", False)
    req_attr = "required" if required else ""
    req_mark = ' <span class="req">*</span>' if required else ""

    html = f'<div class="question" data-qid="{qid}" data-type="{qtype}">\n'
    html += f'  <label class="q-label">{index + 1}. {label}{req_mark}</label>\n'

    if qtype == "boolean":
        html += f'  <div class="options">\n'
        html += f'    <label><input type="radio" name="{qid}" value="true" {req_attr}> Oui</label>\n'
        html += f'    <label><input type="radio" name="{qid}" value="false"> Non</label>\n'
        html += f'  </div>\n'

    elif qtype == "single_choice":
        options = question.get("options", [])
        html += f'  <div class="options">\n'
        for j, opt in enumerate(options):
            opt_esc = escape(str(opt).strip())
            html += f'    <label><input type="radio" name="{qid}" value="{opt_esc}" {req_attr if j == 0 else ""}> {opt_esc}</label>\n'
        html += f'  </div>\n'

    elif qtype == "multiple_choice":
        options = question.get("options", [])
        html += f'  <div class="options">\n'
        for opt in options:
            opt_esc = escape(str(opt).strip())
            html += f'    <label><input type="checkbox" name="{qid}" value="{opt_esc}"> {opt_esc}</label>\n'
        html += f'  </div>\n'

    elif qtype == "short_text":
        html += f'  <textarea name="{qid}" rows="3" class="text-input" {req_attr}></textarea>\n'

    elif qtype == "scale":
        sc = question.get("scale_config") or {"min": 1, "max": 10, "step": 1}
        sc_min = sc.get("min", 1)
        sc_max = sc.get("max", 10)
        sc_step = sc.get("step", 1)
        html += f'  <div class="scale-container">\n'
        html += f'    <span>{sc_min}</span>\n'
        html += f'    <input type="range" name="{qid}" min="{sc_min}" max="{sc_max}" step="{sc_step}" value="{sc_min}" class="scale-input" oninput="this.nextElementSibling.textContent=this.value">\n'
        html += f'    <span>{sc_min}</span>\n'
        html += f'    <span class="scale-max">{sc_max}</span>\n'
        html += f'  </div>\n'

    html += '</div>\n'
    return html


def _render_questionnaire_page(
    questionnaire: dict, session_id: str, pharmacy_name: str
) -> str:
    """Render the full questionnaire HTML page."""
    age_range = escape(questionnaire.get("age_range", ""))
    sid_esc = escape(session_id)

    questions_html = ""
    questions = questionnaire.get("questions", [])
    for i, q in enumerate(questions):
        questions_html += _render_question_html(q, i)

    # Build question metadata for JS submission
    q_meta = json.dumps(
        [{"id": q["id"], "type": q["type"]} for q in questions],
        ensure_ascii=False,
    )

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Questionnaire - {escape(pharmacy_name)}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
         background: #f5f5f5; color: #333; padding: 16px; }}
  .container {{ max-width: 700px; margin: 0 auto; background: #fff;
               border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,.1); }}
  h1 {{ font-size: 1.4em; color: #1a73e8; margin-bottom: 4px; }}
  .subtitle {{ color: #666; margin-bottom: 24px; font-size: 0.95em; }}
  .question {{ margin-bottom: 20px; padding: 16px; background: #fafafa;
              border-radius: 8px; border-left: 4px solid #1a73e8; }}
  .q-label {{ display: block; font-weight: 600; margin-bottom: 10px; line-height: 1.4; }}
  .req {{ color: #c62828; }}
  .options label {{ display: block; padding: 6px 0; cursor: pointer; }}
  .options input {{ margin-right: 8px; }}
  .text-input {{ width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px;
                font-size: 1em; font-family: inherit; resize: vertical; }}
  .scale-container {{ display: flex; align-items: center; gap: 8px; }}
  .scale-input {{ flex: 1; }}
  .scale-max {{ color: #666; }}
  .btn {{ display: block; width: 100%; padding: 14px; margin-top: 24px;
         background: #1a73e8; color: #fff; border: none; border-radius: 8px;
         font-size: 1.1em; font-weight: 600; cursor: pointer; }}
  .btn:hover {{ background: #1557b0; }}
  .btn:disabled {{ background: #ccc; cursor: not-allowed; }}
  .msg {{ padding: 16px; border-radius: 8px; margin-top: 16px; text-align: center; }}
  .msg-ok {{ background: #e8f5e9; color: #2e7d32; }}
  .msg-err {{ background: #ffebee; color: #c62828; }}
  .hidden {{ display: none; }}
</style>
</head>
<body>
<div class="container">
  <h1>{escape(pharmacy_name)}</h1>
  <p class="subtitle">Questionnaire {age_range} ans</p>

  <form id="qform">
    {questions_html}
    <button type="submit" class="btn" id="submitBtn">Envoyer mes reponses</button>
  </form>

  <div id="msgOk" class="msg msg-ok hidden">
    Merci, vos reponses ont bien ete enregistrees.
  </div>
  <div id="msgErr" class="msg msg-err hidden"></div>
</div>

<script>
const SID = "{sid_esc}";
const Q_META = {q_meta};

document.getElementById("qform").addEventListener("submit", async function(e) {{
  e.preventDefault();
  const btn = document.getElementById("submitBtn");
  btn.disabled = true;
  btn.textContent = "Envoi en cours...";

  const form = e.target;
  const responses = [];
  for (const meta of Q_META) {{
    const qid = meta.id;
    const qtype = meta.type;
    let value = null;

    if (qtype === "boolean" || qtype === "single_choice") {{
      const checked = form.querySelector('input[name="' + qid + '"]:checked');
      if (checked) {{
        value = qtype === "boolean" ? (checked.value === "true") : checked.value;
      }}
    }} else if (qtype === "multiple_choice") {{
      const checked = form.querySelectorAll('input[name="' + qid + '"]:checked');
      value = Array.from(checked).map(c => c.value);
    }} else if (qtype === "short_text") {{
      const el = form.querySelector('textarea[name="' + qid + '"]');
      value = el ? el.value : "";
    }} else if (qtype === "scale") {{
      const el = form.querySelector('input[name="' + qid + '"]');
      value = el ? Number(el.value) : null;
    }}

    responses.push({{ question_id: qid, type: qtype, value: value }});
  }}

  try {{
    const resp = await fetch("/questionnaire/submit", {{
      method: "POST",
      headers: {{ "Content-Type": "application/json" }},
      body: JSON.stringify({{
        sid: SID,
        submitted_at: new Date().toISOString(),
        responses: responses
      }})
    }});

    if (resp.ok) {{
      document.getElementById("qform").classList.add("hidden");
      document.getElementById("msgOk").classList.remove("hidden");
    }} else {{
      const data = await resp.json().catch(() => ({{}}));
      const errDiv = document.getElementById("msgErr");
      errDiv.textContent = data.error || "Erreur lors de l'envoi.";
      errDiv.classList.remove("hidden");
      btn.disabled = false;
      btn.textContent = "Envoyer mes reponses";
    }}
  }} catch (err) {{
    const errDiv = document.getElementById("msgErr");
    errDiv.textContent = "Erreur de connexion au serveur.";
    errDiv.classList.remove("hidden");
    btn.disabled = false;
    btn.textContent = "Envoyer mes reponses";
  }}
}});
</script>
</body>
</html>"""


def _render_error_page(message: str) -> str:
    msg_esc = escape(message)
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Acces refuse</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
         display: flex; align-items: center; justify-content: center;
         min-height: 100vh; background: #f5f5f5; color: #333; }}
  .card {{ background: #fff; padding: 32px; border-radius: 12px; text-align: center;
          box-shadow: 0 2px 8px rgba(0,0,0,.1); max-width: 400px; }}
  .icon {{ font-size: 3em; margin-bottom: 16px; }}
  h1 {{ color: #c62828; font-size: 1.3em; margin-bottom: 8px; }}
  p {{ color: #666; }}
</style>
</head>
<body>
<div class="card">
  <div class="icon">&#x26D4;</div>
  <h1>Acces non autorise</h1>
  <p>{msg_esc}</p>
</div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Flask app factory
# ---------------------------------------------------------------------------


def create_app(base: Path | None = None) -> Flask:
    """Create and configure the Flask tablet server.

    ``base`` overrides the project root (used for testing with
    ``tmp_path``).
    """
    resolved_base = base if base is not None else _PROJECT_ROOT

    svc = _load_module(
        "tablet_session_service",
        _THIS_DIR / "service.py",
    )
    capture_svc = _load_module(
        "tablet_capture_service",
        _PROJECT_ROOT
        / "apps"
        / "api"
        / "modules"
        / "questionnaire-capture"
        / "service.py",
    )

    app = Flask(__name__)

    @app.route("/questionnaire")
    def serve_questionnaire():
        v = request.args.get("v")
        sid = request.args.get("sid")
        t = request.args.get("t")
        sig = request.args.get("sig")

        result = svc.validate_qr_params(v, sid, t, sig, base=resolved_base)
        if not result["valid"]:
            return Response(
                _render_error_page(result["error"]),
                status=403,
                content_type="text/html; charset=utf-8",
            )

        session = result["session"]
        session_id = session["session_id"]

        # Validate session sex
        session_sex = session.get("sex")
        if session_sex not in ("H", "F"):
            return Response(
                _render_error_page("Sexe de session absent ou invalide"),
                status=403,
                content_type="text/html; charset=utf-8",
            )

        try:
            questionnaire = svc.load_questionnaire_for_session(
                session_id, base=resolved_base
            )
        except ValueError as exc:
            return Response(
                _render_error_page(str(exc)),
                status=404,
                content_type="text/html; charset=utf-8",
            )

        # Filter questions by sex_target
        questions = questionnaire.get("questions", [])
        questionnaire["questions"] = [
            q for q in questions
            if q.get("sex_target", "M") in (session_sex, "M")
        ]

        pharmacy_name = session.get("metadata", {}).get(
            "pharmacie", {}
        ).get("nom_pharmacie", "")

        loaded_sessions.add(session_id)

        return Response(
            _render_questionnaire_page(questionnaire, session_id, pharmacy_name),
            status=200,
            content_type="text/html; charset=utf-8",
        )

    @app.route("/questionnaire/submit", methods=["POST"])
    def submit_responses():
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Corps de requete JSON invalide"}), 400

        sid = data.get("sid")
        if not sid:
            return jsonify({"error": "Parametre sid manquant"}), 400

        responses = data.get("responses")
        if not isinstance(responses, list):
            return jsonify({"error": "Reponses manquantes ou invalides"}), 400

        submitted_at = data.get(
            "submitted_at",
            datetime.now().isoformat(timespec="seconds"),
        )

        try:
            record = capture_svc.save_responses(
                session_id=sid,
                responses=responses,
                submitted_at=submitted_at,
                base=resolved_base,
            )
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        return jsonify(record), 200

    return app


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
