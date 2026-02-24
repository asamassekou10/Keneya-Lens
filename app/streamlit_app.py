"""
Keneya Lens — Clinical Decision Support System
A step-by-step, CHW-friendly medical consultation interface powered by Google HAI-DEF.

Design: Conversational progressive reveal — each agent stage appears as a card.
Built for the MedGemma Impact Challenge 2026.
"""
import json
import streamlit as st
import requests
from pathlib import Path
import logging
from typing import Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000"

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Keneya Lens | Clinical Decision Support",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Demo cases ─────────────────────────────────────────────────────────────────
DEMO_CASES_PATH = Path(__file__).parent.parent / "data" / "demo_cases.json"
try:
    with open(DEMO_CASES_PATH, encoding="utf-8") as _f:
        DEMO_CASES = json.load(_f)
except Exception:
    DEMO_CASES = []

# ── Translations ───────────────────────────────────────────────────────────────
TRANSLATIONS = {
    "en": {
        "tab_consult":    "Guided Consultation",
        "tab_image":      "Image Analysis",
        "tab_history":    "Query History",
        "tab_about":      "System Information",
        "patient_label":  "Patient Presentation",
        "patient_ph":     (
            "Describe the patient's symptoms, age, vital signs and any relevant history.\n\n"
            "Example: 4-year-old boy, 3-day cough, fever 38.8°C, respiratory rate 42/min, "
            "mild chest indrawing, refusing food."
        ),
        "demo_label":     "Or load a demo case",
        "demo_none":      "— Select a demo case —",
        "begin_btn":      "Begin Consultation",
        "reset_btn":      "New Consultation",
        "stage_1":        "Patient Intake",
        "stage_2":        "Triage Assessment",
        "stage_3":        "Clinical Guidelines",
        "stage_4":        "Clinical Recommendations",
        "running":        "Processing...",
        "complete":       "Complete",
        "pending":        "Waiting",
        "export_btn":     "Export Consultation Summary",
        "disclaimer":     (
            "Clinical Disclaimer: Keneya Lens is a decision support tool for trained healthcare "
            "professionals. It does not replace clinical judgment. All recommendations must be "
            "verified by qualified medical personnel before patient care decisions are made."
        ),
        "immediate":      "Immediate Actions",
        "refer_if":       "Refer Immediately If",
        "monitor":        "Monitoring Plan",
        "follow_up":      "Follow-Up",
        "safety":         "Safety Notes",
        "treatment":      "Treatment Notes",
        "red_flags":      "Red Flags Identified",
        "differentials":  "Possible Diagnoses",
        "triage_reason":  "Triage Reasoning",
        "guidelines_src": "Guideline Sources",
        "no_context":     "No local guidelines indexed.",
        "load_model":     "Load Model",
        "lang_label":     "Interface Language",
        "status_ready":   "Model Ready",
        "status_loading": "Model Loading",
        "status_standby": "Model Standby",
        "status_error":   "Low Memory",
    },
    "fr": {
        "tab_consult":    "Consultation Guidée",
        "tab_image":      "Analyse d'Image",
        "tab_history":    "Historique",
        "tab_about":      "Informations Système",
        "patient_label":  "Présentation du Patient",
        "patient_ph":     (
            "Décrivez les symptômes du patient, son âge, ses signes vitaux et ses antécédents.\n\n"
            "Exemple: Garçon de 4 ans, toux depuis 3 jours, fièvre 38,8°C, FR 42/min, tirage sous-costal."
        ),
        "demo_label":     "Ou charger un cas de démonstration",
        "demo_none":      "— Sélectionner un cas —",
        "begin_btn":      "Démarrer la Consultation",
        "reset_btn":      "Nouvelle Consultation",
        "stage_1":        "Recueil du Patient",
        "stage_2":        "Évaluation du Triage",
        "stage_3":        "Recommandations Cliniques",
        "stage_4":        "Plan de Prise en Charge",
        "running":        "En cours...",
        "complete":       "Terminé",
        "pending":        "En attente",
        "export_btn":     "Exporter le Résumé",
        "disclaimer":     (
            "Avertissement clinique: Keneya Lens est un outil d'aide à la décision pour les "
            "professionnels de santé formés. Il ne remplace pas le jugement clinique."
        ),
        "immediate":      "Actions Immédiates",
        "refer_if":       "Référer Immédiatement Si",
        "monitor":        "Plan de Surveillance",
        "follow_up":      "Suivi",
        "safety":         "Notes de Sécurité",
        "treatment":      "Notes de Traitement",
        "red_flags":      "Signes d'Alerte Identifiés",
        "differentials":  "Diagnostics Possibles",
        "triage_reason":  "Raisonnement du Triage",
        "guidelines_src": "Sources des Recommandations",
        "no_context":     "Aucune recommandation locale indexée.",
        "load_model":     "Charger le Modèle",
        "lang_label":     "Langue de l'Interface",
        "status_ready":   "Modèle Prêt",
        "status_loading": "Modèle en Chargement",
        "status_standby": "Modèle en Veille",
        "status_error":   "Mémoire Insuffisante",
    },
}

# ── CSS ────────────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    /* Core palette */
    --navy-900: #061220;
    --navy-800: #0D2137;
    --navy-700: #143154;
    --navy-600: #1C4270;
    --navy-400: #2D6CB4;
    --navy-100: #E8F0FB;
    --navy-50:  #F2F6FD;

    /* Text */
    --text:       #0F1A2B;
    --text-2:     #3A4A5C;
    --text-3:     #7A8A9C;
    --border:     #CDD8EA;
    --bg:         #EDF1F8;
    --card:       #FFFFFF;

    /* Triage */
    --critical:    #991B1B;
    --critical-bg: #FEF2F2;
    --critical-b:  #FECACA;
    --critical-t:  #7F1D1D;

    --urgent:      #9A3412;
    --urgent-bg:   #FFF7ED;
    --urgent-b:    #FED7AA;
    --urgent-t:    #7C2D12;

    --moderate:    #92400E;
    --moderate-bg: #FFFBEB;
    --moderate-b:  #FDE68A;
    --moderate-t:  #78350F;

    --stable:      #166534;
    --stable-bg:   #F0FDF4;
    --stable-b:    #BBF7D0;
    --stable-t:    #14532D;

    /* Accent */
    --info-bg:  #EFF6FF;
    --info-b:   #BFDBFE;
    --info-t:   #1E40AF;

    --warn-bg:  #FFFBEB;
    --warn-b:   #FCD34D;
    --warn-t:   #92400E;

    /* Agents */
    --agent-1: #6366F1;   /* Intake — indigo */
    --agent-2: #0891B2;   /* Triage — cyan */
    --agent-3: #059669;   /* Guidelines — emerald */
    --agent-4: #0D2137;   /* Recommendations — navy */

    --font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --mono: 'JetBrains Mono', 'Fira Code', monospace;
    --r: 8px;
    --r-lg: 12px;
    --sh: 0 1px 4px rgba(6,18,32,.07), 0 4px 16px rgba(6,18,32,.06);
    --sh-sm: 0 1px 3px rgba(6,18,32,.08);
}

/* ── Reset ── */
.stApp { font-family: var(--font); background: var(--bg); color: var(--text); }
#MainMenu, footer, header { visibility: hidden; }
*, *::before, *::after { box-sizing: border-box; }
p { line-height: 1.65; }

/* ── App header ── */
.kl-header {
    background: linear-gradient(135deg, var(--navy-800) 0%, var(--navy-900) 100%);
    color: #fff;
    padding: 1rem 1.5rem;
    margin: -1rem -1rem 1.5rem -1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(255,255,255,.07);
}
.kl-header-brand { font-size: 1.25rem; font-weight: 700; letter-spacing: -.02em; }
.kl-header-sub   { font-size: .72rem; opacity: .55; font-weight: 400; margin-top: 2px; }
.kl-header-meta  { font-size: .68rem; opacity: .45; text-align: right; line-height: 1.6; }

/* ── Disclaimer ── */
.kl-disclaimer {
    background: var(--warn-bg);
    border: 1px solid var(--warn-b);
    border-left: 4px solid #F59E0B;
    border-radius: var(--r);
    padding: .75rem 1rem;
    margin-bottom: 1.25rem;
    font-size: .8rem;
    color: var(--warn-t);
    line-height: 1.5;
}
.kl-disclaimer strong { color: #78350F; }

/* ── Alert boxes ── */
.kl-alert {
    border-radius: var(--r);
    padding: .875rem 1.125rem;
    margin: .75rem 0;
    border: 1px solid;
}
.kl-alert-critical { background:var(--critical-bg); border-color:var(--critical-b); border-left:4px solid var(--critical); }
.kl-alert-urgent   { background:var(--urgent-bg);   border-color:var(--urgent-b);   border-left:4px solid var(--urgent);   }
.kl-alert-moderate { background:var(--moderate-bg); border-color:var(--moderate-b); border-left:4px solid var(--moderate); }
.kl-alert-stable   { background:var(--stable-bg);   border-color:var(--stable-b);   border-left:4px solid var(--stable);   }
.kl-alert-info     { background:var(--info-bg);     border-color:var(--info-b);     border-left:4px solid #3B82F6; color:var(--info-t); font-size:.875rem; }

.kl-alert-label   { font-size:.68rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; margin-bottom:.2rem; }
.kl-alert-heading { font-size:1rem; font-weight:600; margin-bottom:.25rem; }
.kl-alert-body    { font-size:.8375rem; line-height:1.55; }

/* ── Status pills ── */
.kl-pill {
    display:inline-flex; align-items:center; gap:5px;
    padding:.25rem .625rem; border-radius:9999px;
    font-size:.69rem; font-weight:600; letter-spacing:.04em;
}
.kl-pill-dot { width:6px; height:6px; border-radius:50%; background:currentColor; }
.kl-pill-ready   { background:#D1FAE5; color:#065F46; }
.kl-pill-loading { background:#FEF3C7; color:#92400E; }
.kl-pill-error   { background:#FEE2E2; color:#991B1B; }
.kl-pill-offline { background:#F3F4F6; color:#6B7280; }

/* ── Agent consultation cards ── */
.kl-agent-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--r-lg);
    box-shadow: var(--sh);
    margin: 1rem 0;
    overflow: hidden;
}
.kl-agent-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: .875rem 1.25rem;
    border-bottom: 1px solid var(--border);
}
.kl-agent-title {
    display: flex;
    align-items: center;
    gap: .625rem;
    font-size: .9rem;
    font-weight: 600;
    color: var(--text);
}
.kl-agent-icon {
    width: 28px; height: 28px;
    border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: .75rem;
    font-weight: 700;
    color: white;
    flex-shrink: 0;
}
.kl-agent-badge {
    font-size: .68rem; font-weight: 600;
    padding: .2rem .5rem;
    border-radius: 9999px;
}
.kl-badge-complete { background:#D1FAE5; color:#065F46; }
.kl-badge-running  { background:#FEF3C7; color:#92400E; }
.kl-badge-pending  { background:#F3F4F6; color:#6B7280; }

.kl-agent-body { padding: 1rem 1.25rem; }

/* ── Triage level display ── */
.kl-triage-block {
    border-radius: var(--r);
    padding: .875rem 1.125rem;
    margin-bottom: .75rem;
}
.kl-triage-level  { font-size: 1.25rem; font-weight: 700; letter-spacing: -.01em; }
.kl-triage-desc   { font-size: .85rem; margin-top: .125rem; opacity: .85; }

/* ── List items in agent output ── */
.kl-list { margin: 0; padding: 0; list-style: none; }
.kl-list li {
    display: flex; align-items: flex-start; gap: .625rem;
    padding: .4rem 0;
    border-bottom: 1px solid var(--border);
    font-size: .875rem;
    line-height: 1.55;
    color: var(--text);
}
.kl-list li:last-child { border-bottom: none; }
.kl-list-num {
    flex-shrink: 0;
    width: 20px; height: 20px;
    background: var(--navy-100);
    color: var(--navy-600);
    border-radius: 50%;
    font-size: .7rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    margin-top: .125rem;
}
.kl-list-dot {
    flex-shrink: 0;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--navy-400);
    margin-top: .5rem;
}

/* ── Sub-section label ── */
.kl-section {
    font-size: .69rem;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--text-3);
    margin: .875rem 0 .375rem 0;
}

/* ── Guideline quote ── */
.kl-guideline-quote {
    background: var(--navy-50);
    border: 1px solid var(--border);
    border-left: 3px solid var(--navy-400);
    border-radius: 0 var(--r) var(--r) 0;
    padding: .75rem 1rem;
    font-size: .8375rem;
    line-height: 1.6;
    color: var(--text-2);
    margin: .5rem 0;
}
.kl-guideline-source {
    font-size: .7rem;
    color: var(--text-3);
    margin-top: .25rem;
}

/* ── Vitals monospace ── */
.kl-vital {
    font-family: var(--mono);
    font-size: .8rem;
    background: var(--navy-50);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: .125rem .375rem;
    color: var(--text-2);
}

/* ── Export button ── */
.kl-export-btn {
    display: inline-block;
    margin-top: 1rem;
    padding: .5rem 1rem;
    background: var(--navy-600);
    color: white;
    border-radius: var(--r);
    font-size: .875rem;
    font-weight: 500;
    text-decoration: none;
    cursor: pointer;
}

/* ── Section heading ── */
.kl-page-title {
    font-size: 1.0625rem;
    font-weight: 600;
    color: var(--text);
    margin: 0 0 1rem 0;
    padding-bottom: .5rem;
    border-bottom: 2px solid var(--navy-600);
    letter-spacing: -.01em;
}

/* ── RAM info in sidebar ── */
.kl-ram {
    font-size: .69rem;
    color: rgba(255,255,255,.5);
    margin-top: .3rem;
    padding-left: 2px;
}

/* ── Step connector ── */
.kl-connector {
    width: 2px;
    height: 16px;
    background: var(--border);
    margin: 0 auto;
    display: block;
}

/* ── Sidebar overrides ── */
section[data-testid="stSidebar"] {
    background: var(--navy-800);
    border-right: 1px solid var(--navy-700);
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSlider label { color: rgba(255,255,255,.82) !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: rgba(255,255,255,.93) !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.1) !important; }

/* Sidebar widgets — keep light backgrounds so text stays readable */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,.1) !important;
    border-color: rgba(255,255,255,.2) !important;
    color: #ffffff !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] svg { color: rgba(255,255,255,.7) !important; }
section[data-testid="stSidebar"] .stButton > button {
    background-color: var(--navy-600) !important;
    border-color: var(--navy-500, #2D6CB4) !important;
    color: #ffffff !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: var(--navy-400) !important;
    color: #ffffff !important;
}
section[data-testid="stSidebar"] .stSlider [data-testid="stSliderThumb"] { background: var(--navy-400) !important; }
section[data-testid="stSidebar"] .stNumberInput input {
    background-color: rgba(255,255,255,.1) !important;
    color: #ffffff !important;
    border-color: rgba(255,255,255,.2) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap:0; border-bottom:2px solid var(--border); }
.stTabs [data-baseweb="tab"] {
    font-family:var(--font); font-weight:500; font-size:.875rem;
    color:var(--text-2); padding:.625rem 1.25rem;
    border-bottom:2px solid transparent; margin-bottom:-2px;
}
.stTabs [data-baseweb="tab"]:hover { color:var(--navy-600); }
.stTabs [aria-selected="true"] {
    color:var(--navy-600) !important;
    border-bottom-color:var(--navy-600) !important;
    font-weight:600 !important;
}

/* ── Inputs ── */
.stTextArea textarea,
.stTextInput input,
div[data-baseweb="textarea"] textarea,
div[data-baseweb="input"] input {
    font-family: var(--font) !important;
    font-size: .9375rem !important;
    line-height: 1.65 !important;
    background-color: #ffffff !important;
    color: #0F1A2B !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
}
.stTextArea textarea:focus,
.stTextInput input:focus {
    border-color: var(--navy-600) !important;
    box-shadow: 0 0 0 2px rgba(28,66,112,.15) !important;
    outline: none !important;
}
/* Selectbox */
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #0F1A2B !important;
    border-color: var(--border) !important;
}
div[data-baseweb="select"] svg { color: var(--text-2) !important; }

/* ── Buttons — base (secondary / default) ── */
.stButton > button {
    font-family: var(--font) !important;
    font-weight: 500 !important;
    border-radius: var(--r) !important;
    padding: .5rem 1.125rem !important;
    font-size: .875rem !important;
    transition: background .15s ease, border-color .15s ease, color .15s ease !important;
    background-color: #ffffff !important;
    color: var(--navy-700) !important;
    border: 1px solid var(--border) !important;
}
.stButton > button:hover {
    background-color: var(--navy-50) !important;
    border-color: var(--navy-400) !important;
    color: var(--navy-600) !important;
}
/* Primary buttons (type="primary") */
.stButton > button[kind="primary"],
button[data-testid="baseButton-primary"] {
    background-color: var(--navy-600) !important;
    border-color: var(--navy-600) !important;
    color: #ffffff !important;
}
.stButton > button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover {
    background-color: var(--navy-700) !important;
    border-color: var(--navy-700) !important;
    color: #ffffff !important;
}
/* Download buttons */
.stDownloadButton > button {
    font-family: var(--font) !important;
    font-weight: 500 !important;
    border-radius: var(--r) !important;
    background-color: var(--navy-600) !important;
    border-color: var(--navy-600) !important;
    color: #ffffff !important;
    transition: background .15s ease !important;
}
.stDownloadButton > button:hover {
    background-color: var(--navy-700) !important;
    border-color: var(--navy-700) !important;
    color: #ffffff !important;
}

/* ── Metrics ── */
.stMetric { background:var(--card); border:1px solid var(--border); border-radius:var(--r-lg); padding:.875rem 1rem; box-shadow:var(--sh-sm); }
[data-testid="stMetricValue"] { font-size:1.5rem !important; font-weight:700 !important; }

/* ── File uploader ── */
.stFileUploader > section { border:2px dashed var(--border) !important; border-radius:var(--r) !important; background:var(--navy-50) !important; }
.stFileUploader > section:hover { border-color:var(--navy-400) !important; }

/* ── App footer ── */
.kl-footer {
    background:#F9FAFB; border-top:1px solid var(--border);
    padding:.7rem 1.5rem; margin:2rem -1rem -1rem -1rem;
    font-size:.68rem; color:var(--text-3); text-align:center;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ── API helpers ────────────────────────────────────────────────────────────────

def _api_get(path: str, params: dict = None, timeout: int = 5) -> Optional[dict]:
    try:
        r = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=timeout)
        return r.json() if r.ok else None
    except Exception:
        return None


def _api_post(path: str, json_body: dict = None, timeout: int = 30) -> Optional[dict]:
    try:
        r = requests.post(f"{API_BASE_URL}{path}", json=json_body, timeout=timeout)
        return r.json() if r.ok else None
    except Exception:
        return None


def check_api_health() -> Optional[dict]:
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=4)
        return r.json() if r.ok else None
    except Exception:
        return None


def check_memory_status() -> Optional[dict]:
    return _api_get("/memory")


def trigger_model_load() -> Optional[dict]:
    return _api_post("/load-model", timeout=10)


def call_stage(stage: int, context: dict, language: str = "en") -> dict:
    """Call a single agent stage endpoint. Always returns a dict."""
    try:
        r = requests.post(
            f"{API_BASE_URL}/consult/stage",
            json={"stage": stage, "context": context, "language": language},
            timeout=600,
        )
        if r.ok:
            return r.json()
        try:
            detail = r.json().get("detail", r.text[:200])
        except Exception:
            detail = r.text[:200]
        return {"success": False, "error": f"API error {r.status_code}: {detail}"}
    except requests.exceptions.ReadTimeout:
        return {"success": False, "error": "Agent stage timed out (model may be slow on CPU)."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Connection to API server lost."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def upload_and_ingest_pdf(file) -> Optional[dict]:
    try:
        r = requests.post(
            f"{API_BASE_URL}/ingest/upload",
            files={"file": (file.name, file.getvalue(), "application/pdf")},
            timeout=120,
        )
        return r.json() if r.ok else None
    except Exception:
        return None


def ingest_pdf_path(pdf_path: str) -> Optional[dict]:
    try:
        r = requests.post(f"{API_BASE_URL}/ingest", json={"pdf_path": pdf_path}, timeout=120)
        return r.json() if r.ok else None
    except Exception:
        return None


# ── UI helpers ─────────────────────────────────────────────────────────────────

TRIAGE_STYLE = {
    "CRITICAL": ("var(--critical)", "var(--critical-bg)", "var(--critical-b)",
                 "var(--critical-t)", "kl-alert-critical"),
    "URGENT":   ("var(--urgent)",   "var(--urgent-bg)",   "var(--urgent-b)",
                 "var(--urgent-t)", "kl-alert-urgent"),
    "MODERATE": ("var(--moderate)", "var(--moderate-bg)", "var(--moderate-b)",
                 "var(--moderate-t)", "kl-alert-moderate"),
    "NON-URGENT": ("var(--stable)", "var(--stable-bg)",   "var(--stable-b)",
                   "var(--stable-t)", "kl-alert-stable"),
}
TRIAGE_LABELS = {
    "en": {
        "CRITICAL":   ("CRITICAL",   "Immediate medical attention required — do not delay."),
        "URGENT":     ("URGENT",     "Referral or treatment required within 24 hours."),
        "MODERATE":   ("MODERATE",   "Medical attention needed — not immediately life-threatening."),
        "NON-URGENT": ("NON-URGENT", "Can be managed locally with standard first-line treatment."),
    },
    "fr": {
        "CRITICAL":   ("CRITIQUE",        "Attention médicale immédiate requise — ne pas différer."),
        "URGENT":     ("URGENT",          "Référer ou traiter dans les 24 heures."),
        "MODERATE":   ("MODÉRÉ",          "Soins médicaux nécessaires — pas immédiatement urgent."),
        "NON-URGENT": ("NON-URGENT",      "Peut être géré localement en première ligne."),
    },
}

AGENT_COLOURS = {
    1: "#6366F1",  # indigo
    2: "#0891B2",  # cyan
    3: "#059669",  # emerald
    4: "#1C4270",  # navy
}


def _pill(text: str, cls: str) -> str:
    return f'<span class="kl-pill {cls}"><span class="kl-pill-dot"></span>{text}</span>'


def _agent_card_header(stage: int, title: str, status: str, T: dict) -> str:
    """Render an agent card header with stage number, title, and status badge."""
    colour = AGENT_COLOURS[stage]
    badge_cls = "kl-badge-complete" if status == "complete" else (
        "kl-badge-running" if status == "running" else "kl-badge-pending"
    )
    badge_label = T["complete"] if status == "complete" else (
        T["running"] if status == "running" else T["pending"]
    )
    return f"""
    <div class="kl-agent-header">
      <div class="kl-agent-title">
        <span class="kl-agent-icon" style="background:{colour};">{stage}</span>
        <span>Step {stage} / 4 &nbsp;&mdash;&nbsp; {title}</span>
      </div>
      <span class="kl-agent-badge {badge_cls}">{badge_label}</span>
    </div>"""


def _triage_html(level: str, lang: str) -> str:
    colour, bg, border, text_col, _ = TRIAGE_STYLE.get(level, TRIAGE_STYLE["MODERATE"])
    label, desc = TRIAGE_LABELS.get(lang, TRIAGE_LABELS["en"]).get(level, ("UNKNOWN", ""))
    return f"""
    <div class="kl-triage-block" style="background:{bg};border:1px solid {border};border-left:4px solid {colour};">
      <div class="kl-triage-level" style="color:{colour};">{label}</div>
      <div class="kl-triage-desc" style="color:{text_col};">{desc}</div>
    </div>"""


def _numbered_list(items: list) -> str:
    if not items:
        return "<p style='font-size:.875rem;color:var(--text-3);margin:0;'>None identified.</p>"
    lis = "".join(
        f'<li><span class="kl-list-num">{i + 1}</span><span>{item}</span></li>'
        for i, item in enumerate(items)
    )
    return f'<ul class="kl-list">{lis}</ul>'


def _bullet_list(items: list) -> str:
    if not items:
        return "<p style='font-size:.875rem;color:var(--text-3);margin:0;'>None identified.</p>"
    lis = "".join(
        f'<li><span class="kl-list-dot"></span><span>{item}</span></li>'
        for item in items
    )
    return f'<ul class="kl-list">{lis}</ul>'


def _section_label(text: str) -> str:
    return f'<div class="kl-section">{text}</div>'


def render_agent_card_1(intake: dict, T: dict):
    """Render Stage 1 — Patient Intake card."""
    vitals = intake.get("vital_signs", {})
    vital_parts = [
        f"T {vitals.get('temperature','')}" if vitals.get("temperature") else None,
        f"HR {vitals.get('heart_rate','')}" if vitals.get("heart_rate") else None,
        f"RR {vitals.get('respiratory_rate','')}" if vitals.get("respiratory_rate") else None,
        f"SpO2 {vitals.get('spo2','')}" if vitals.get("spo2") else None,
        f"BP {vitals.get('blood_pressure','')}" if vitals.get("blood_pressure") else None,
    ]
    vital_str = " &nbsp;|&nbsp; ".join(v for v in vital_parts if v)

    st.markdown(
        f'<div class="kl-agent-card">'
        f'{_agent_card_header(1, T["stage_1"], "complete", T)}'
        f'<div class="kl-agent-body">'
        f'<p style="margin:0;font-size:.9375rem;">'
        f'<strong>{intake.get("age","")} {intake.get("sex","")}</strong>'
        f' &mdash; {intake.get("chief_complaint","")}</p>'
        f'<p style="margin:.25rem 0 0;font-size:.8375rem;color:var(--text-2);">'
        f'Duration: {intake.get("duration","not specified")}</p>'
        + (f'<p style="margin:.5rem 0 0;"><span class="kl-vital">{vital_str}</span></p>' if vital_str else "")
        + (f'<p style="margin:.5rem 0 0;font-size:.8125rem;color:var(--text-2);">History: {intake.get("relevant_history","")}</p>'
           if intake.get("relevant_history") else "")
        + f'</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="kl-connector"></div>', unsafe_allow_html=True)


def render_agent_card_2(triage: dict, T: dict, lang: str):
    """Render Stage 2 — Triage Assessment card."""
    level = triage.get("triage_level", "MODERATE")
    st.markdown(
        f'<div class="kl-agent-card">'
        f'{_agent_card_header(2, T["stage_2"], "complete", T)}'
        f'<div class="kl-agent-body">'
        f'{_triage_html(level, lang)}'
        + (f'{_section_label(T["red_flags"])}'
           f'{_bullet_list(triage.get("red_flags",[]))}'
           if triage.get("red_flags") else "")
        + f'{_section_label(T["differentials"])}'
        + f'{_bullet_list(triage.get("differential_diagnoses",[]))}'
        + (f'{_section_label(T["triage_reason"])}'
           f'<p style="font-size:.8375rem;color:var(--text-2);margin:0;line-height:1.6;">'
           f'{triage.get("reasoning","")}</p>'
           if triage.get("reasoning") else "")
        + f'</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="kl-connector"></div>', unsafe_allow_html=True)


def render_agent_card_3(guidelines: dict, T: dict):
    """Render Stage 3 — Clinical Guidelines card."""
    gl = guidelines.get("guidelines", [])
    citations = guidelines.get("citations", [])

    if not gl:
        body = (f'<div class="kl-alert kl-alert-info">'
                f'{T["no_context"]} Responses based on MedGemma model knowledge.</div>')
    else:
        body = ""
        for i, passage in enumerate(gl[:3]):
            source = citations[i] if i < len(citations) else "Clinical Guidelines"
            body += (
                f'<div class="kl-guideline-quote">{passage}</div>'
                f'<div class="kl-guideline-source">{T["guidelines_src"]}: {source}</div>'
            )

    st.markdown(
        f'<div class="kl-agent-card">'
        f'{_agent_card_header(3, T["stage_3"], "complete", T)}'
        f'<div class="kl-agent-body">{body}</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="kl-connector"></div>', unsafe_allow_html=True)


def render_agent_card_4(recs: dict, T: dict, triage_level: str, lang: str):
    """Render Stage 4 — Clinical Recommendations card (final card)."""
    _, bg, border, _, cls = TRIAGE_STYLE.get(triage_level, TRIAGE_STYLE["MODERATE"])

    body = (
        f'{_section_label(T["immediate"])}'
        f'{_numbered_list(recs.get("immediate_actions",[]))}'
        + (f'{_section_label(T["treatment"])}'
           f'<p style="font-size:.875rem;color:var(--text-2);margin:0;line-height:1.6;">'
           f'{recs.get("treatment_notes","")}</p>'
           if recs.get("treatment_notes") else "")
        + (f'{_section_label(T["refer_if"])}'
           f'{_bullet_list(recs.get("referral_criteria",[]))}'
           if recs.get("referral_criteria") else "")
        + (f'{_section_label(T["monitor"])}'
           f'<p style="font-size:.875rem;color:var(--text-2);margin:0;">{recs.get("monitoring_plan","")}</p>'
           if recs.get("monitoring_plan") else "")
        + (f'{_section_label(T["follow_up"])}'
           f'<p style="font-size:.875rem;color:var(--text-2);margin:0;">{recs.get("follow_up","")}</p>'
           if recs.get("follow_up") else "")
        + (f'{_section_label(T["safety"])}'
           f'<div class="kl-alert kl-alert-info" style="margin-top:.25rem;">'
           f'{recs.get("safety_notes","")}</div>'
           if recs.get("safety_notes") else "")
    )

    st.markdown(
        f'<div class="kl-agent-card" style="border-top:3px solid {bg};">'
        f'{_agent_card_header(4, T["stage_4"], "complete", T)}'
        f'<div class="kl-agent-body">{body}</div></div>',
        unsafe_allow_html=True,
    )


def render_export_button(result: dict, T: dict):
    """Render a plain-text consultation export."""
    intake = result.get("intake", {})
    triage = result.get("triage", {})
    recs   = result.get("recommendations", {})
    gl     = result.get("guidelines", {})

    summary = (
        f"KENEYA LENS — CONSULTATION SUMMARY\n"
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"{'='*60}\n\n"
        f"PATIENT\n"
        f"  Age/Sex:   {intake.get('age','')} {intake.get('sex','')}\n"
        f"  Complaint: {intake.get('chief_complaint','')}\n"
        f"  Duration:  {intake.get('duration','')}\n\n"
        f"TRIAGE: {triage.get('triage_level','')}\n"
        f"  Red flags: {', '.join(triage.get('red_flags',[]) or ['None'])}\n"
        f"  Differentials: {', '.join(triage.get('differential_diagnoses',[]) or ['Not determined'])}\n\n"
        f"GUIDELINES SOURCES: {', '.join(gl.get('citations',[]) or ['MedGemma knowledge'])}\n\n"
        f"IMMEDIATE ACTIONS\n"
        + "\n".join(f"  {i+1}. {a}" for i, a in enumerate(recs.get("immediate_actions", [])))
        + f"\n\nREFER IMMEDIATELY IF\n"
        + "\n".join(f"  - {r}" for r in recs.get("referral_criteria", []))
        + f"\n\nMONITORING: {recs.get('monitoring_plan','')}\n"
        f"FOLLOW-UP:  {recs.get('follow_up','')}\n\n"
        f"SAFETY: {recs.get('safety_notes','')}\n\n"
        f"{'='*60}\n"
        f"DISCLAIMER: This is a decision support summary. Always confirm\n"
        f"with a qualified healthcare professional before acting.\n"
    )

    st.download_button(
        label=T["export_btn"],
        data=summary,
        file_name=f"consultation_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
    )


# ── Main app ───────────────────────────────────────────────────────────────────

def main():
    # ── Language selection (init early for all UI) ───────────────────────────
    lang = st.session_state.get("lang", "en")
    T = TRANSLATIONS[lang]

    # ── API health ───────────────────────────────────────────────────────────
    health = check_api_health()
    api_online     = health is not None
    model_loaded   = health.get("model_loaded", False) if api_online else False
    model_loading  = health.get("model_loading", False) if api_online else False
    engine_error   = health.get("error") if api_online else None
    has_mem_issue  = bool(engine_error and (
        "memory" in engine_error.lower() or "insufficient" in engine_error.lower()
    ))

    # ── Header ───────────────────────────────────────────────────────────────
    if api_online:
        if model_loaded:
            status_pill = _pill(T["status_ready"], "kl-pill-ready")
        elif model_loading:
            status_pill = _pill(T["status_loading"], "kl-pill-loading")
        elif has_mem_issue:
            status_pill = _pill(T["status_error"], "kl-pill-error")
        else:
            status_pill = _pill(T["status_standby"], "kl-pill-loading")
        api_pill = _pill("API Online", "kl-pill-ready")
    else:
        status_pill = ""
        api_pill = _pill("API Offline", "kl-pill-error")

    st.markdown(
        f'<div class="kl-header">'
        f'<div><div class="kl-header-brand">Keneya Lens</div>'
        f'<div class="kl-header-sub">Clinical Decision Support — HAI-DEF (MedGemma)</div></div>'
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'{api_pill}{status_pill}'
        f'<span style="color:rgba(255,255,255,.25);margin:0 4px;">|</span>'
        f'<span class="kl-header-meta">v2.1 &nbsp; Feb 2026</span></div></div>',
        unsafe_allow_html=True,
    )

    # ── Disclaimer ───────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="kl-disclaimer"><strong>Clinical Disclaimer:</strong> {T["disclaimer"]}</div>',
        unsafe_allow_html=True,
    )

    # ── API offline ──────────────────────────────────────────────────────────
    if not api_online:
        st.markdown(
            '<div class="kl-alert kl-alert-critical">'
            '<div class="kl-alert-label" style="color:var(--critical);">API Server Offline</div>'
            '<div class="kl-alert-heading" style="color:var(--critical);">Backend service unavailable</div>'
            '<div class="kl-alert-body" style="color:var(--critical-t);">Start the API server, then refresh.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.code("python run_api.py", language="bash")
        st.stop()

    # ── Memory / engine warnings ─────────────────────────────────────────────
    if has_mem_issue:
        mem_info = check_memory_status() or {}
        avail = mem_info.get("available_gb", "?")
        total = mem_info.get("total_gb", "?")
        st.markdown(
            f'<div class="kl-alert kl-alert-urgent">'
            f'<div class="kl-alert-label" style="color:var(--urgent);">System Resource Warning</div>'
            f'<div class="kl-alert-heading" style="color:var(--urgent);">Insufficient Memory to Load Model</div>'
            f'<div class="kl-alert-body" style="color:var(--urgent-t);">'
            f'Available RAM: <strong>{avail} GB</strong> of {total} GB (4 GB minimum required). '
            f'Close other applications, then click <strong>{T["load_model"]}</strong> in the sidebar.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    elif model_loading:
        st.markdown(
            '<div class="kl-alert kl-alert-info">'
            '<strong>Model Loading:</strong> The AI model is initialising. '
            'This may take several minutes on first startup.</div>',
            unsafe_allow_html=True,
        )
    elif not model_loaded:
        st.markdown(
            f'<div class="kl-alert kl-alert-info">'
            f'<strong>Model Standby:</strong> Click <strong>{T["load_model"]}</strong> in the sidebar '
            f'to pre-load the model, or submit a consultation to load it automatically.</div>',
            unsafe_allow_html=True,
        )

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"### {T['lang_label']}")
        new_lang = st.selectbox(
            "Interface Language", ["English", "Français"],
            index=0 if lang == "en" else 1,
            label_visibility="collapsed",
        )
        if (new_lang == "English" and lang != "en") or (new_lang == "Français" and lang != "fr"):
            st.session_state["lang"] = "en" if new_lang == "English" else "fr"
            st.rerun()

        st.markdown("---")
        st.markdown("### System Status")

        if model_loaded:
            st.markdown(f'<div>{_pill("Connected — Model Ready", "kl-pill-ready")}</div>', unsafe_allow_html=True)
        elif model_loading:
            st.markdown(f'<div>{_pill("Connected — Loading...", "kl-pill-loading")}</div>', unsafe_allow_html=True)
        elif has_mem_issue:
            st.markdown(f'<div>{_pill("Connected — Low Memory", "kl-pill-error")}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div>{_pill("Connected — Standby", "kl-pill-loading")}</div>', unsafe_allow_html=True)

        mem_info = check_memory_status() or {}
        if "available_gb" in mem_info:
            used_pct = mem_info.get("used_percent", 0)
            col = "rgba(255,120,120,.9)" if used_pct > 85 else "rgba(255,255,255,.5)"
            st.markdown(
                f'<div class="kl-ram" style="color:{col};">'
                f'RAM: {mem_info["available_gb"]} GB free / {mem_info.get("total_gb","?")} GB ({used_pct:.0f}%)'
                f'</div>',
                unsafe_allow_html=True,
            )

        if not model_loaded and not model_loading:
            st.markdown("<div style='margin-top:.6rem;'></div>", unsafe_allow_html=True)
            if st.button(T["load_model"], type="primary", use_container_width=True):
                res = trigger_model_load()
                if not res:
                    st.error("Could not reach API server.")
                elif res.get("status") == "insufficient_memory":
                    st.error(res.get("message", "Not enough memory."))
                elif res.get("status") == "loading_started":
                    st.success("Loading started. Please wait...")
                    st.rerun()
                elif res.get("status") == "already_loaded":
                    st.success("Model is already loaded.")
                    st.rerun()

        st.markdown("---")
        st.markdown("### Generation Parameters")
        max_tokens = st.slider("Max Response Length", 128, 1024, 512, 64)
        temperature = st.slider("Response Variability", 0.0, 1.0, 0.3, 0.1,
                                help="Lower = more focused, deterministic. Recommended: 0.3")

        st.markdown("---")
        st.markdown("### Knowledge Base")

        with st.expander("Upload Clinical Guidelines", expanded=False):
            uploaded_pdf = st.file_uploader("Select PDF document", type=["pdf"],
                                             help="WHO guidelines, IMCI protocols, national standards (max 50 MB)")
            if uploaded_pdf:
                if st.button("Process Document", type="primary", use_container_width=True):
                    with st.spinner("Processing..."):
                        res = upload_and_ingest_pdf(uploaded_pdf)
                    if res:
                        st.success(f"Ingested: {res.get('filename', uploaded_pdf.name)}")
                    else:
                        st.error("Failed. Ensure model is loaded first.")

        with st.expander("Load from Server Path", expanded=False):
            pdf_path_val = st.text_input("Server-side path", value="./data/guidelines.pdf")
            if st.button("Load Document", use_container_width=True):
                with st.spinner("Loading..."):
                    res = ingest_pdf_path(pdf_path_val)
                st.success("Loaded.") if res else st.error("Failed.")

    # ── Main tabs ─────────────────────────────────────────────────────────────
    tab_c, tab_img, tab_hist, tab_info = st.tabs([
        T["tab_consult"], T["tab_image"], T["tab_history"], T["tab_about"]
    ])

    # ════════════════════════════════════════════════════════════════════════
    # Tab 1 — Guided Consultation (Agentic Pipeline)
    # ════════════════════════════════════════════════════════════════════════
    with tab_c:
        st.markdown(f'<div class="kl-page-title">{T["tab_consult"]}</div>', unsafe_allow_html=True)

        # Initialise session state for this consultation
        if "consult_stage" not in st.session_state:
            st.session_state.consult_stage = 0  # 0 = not started
        if "consult_context" not in st.session_state:
            st.session_state.consult_context = {}
        if "consult_results" not in st.session_state:
            st.session_state.consult_results = {}

        # ── Input phase (shown only when not started) ────────────────────
        if st.session_state.consult_stage == 0:
            # Demo case selector
            demo_options = [T["demo_none"]] + [c["label"] for c in DEMO_CASES]
            selected_demo = st.selectbox(T["demo_label"], demo_options, label_visibility="visible")

            default_text = ""
            default_lang = lang
            if selected_demo != T["demo_none"]:
                for case in DEMO_CASES:
                    if case["label"] == selected_demo:
                        default_text = case["input"]
                        default_lang = case.get("language", "en")
                        break

            symptoms_input = st.text_area(
                T["patient_label"],
                value=default_text,
                height=180,
                placeholder=T["patient_ph"],
            )

            col_btn, col_note = st.columns([2, 5])
            with col_btn:
                begin = st.button(T["begin_btn"], type="primary", use_container_width=True)
            with col_note:
                st.markdown(
                    "<small style='color:var(--text-3);line-height:2;'>"
                    "Each agent stage calls MedGemma separately. "
                    "On CPU without GPU this may take several minutes per stage.</small>",
                    unsafe_allow_html=True,
                )

            if begin:
                if not symptoms_input or len(symptoms_input.strip()) < 10:
                    st.warning("Please provide a detailed patient presentation (minimum 10 characters).")
                else:
                    st.session_state.consult_stage = 1
                    st.session_state.consult_context = {
                        "raw_input": symptoms_input,
                        "language": default_lang if selected_demo != T["demo_none"] else lang,
                    }
                    st.session_state.consult_results = {}
                    st.rerun()

        # ── Running / showing agent stages ───────────────────────────────
        else:
            # Reset button
            if st.button(T["reset_btn"], use_container_width=False):
                st.session_state.consult_stage = 0
                st.session_state.consult_context = {}
                st.session_state.consult_results = {}
                st.rerun()

            st.markdown("<div style='margin-top:.5rem;'></div>", unsafe_allow_html=True)

            context = st.session_state.consult_context
            results = st.session_state.consult_results
            current_stage = st.session_state.consult_stage
            consult_lang  = context.get("language", "en")
            T_consult = TRANSLATIONS.get(consult_lang, T)

            # Show completed stage cards
            if "intake" in results:
                render_agent_card_1(results["intake"], T_consult)
            if "triage" in results:
                render_agent_card_2(results["triage"], T_consult, consult_lang)
            if "guidelines" in results:
                render_agent_card_3(results["guidelines"], T_consult)
            if "recommendations" in results:
                render_agent_card_4(
                    results["recommendations"], T_consult,
                    results.get("triage", {}).get("triage_level", "MODERATE"), consult_lang
                )
                render_export_button(results, T_consult)
                # All done — stay on page so user can read
                st.stop()

            # ── Run the next pending stage ────────────────────────────────
            stage_names = {
                1: T_consult["stage_1"],
                2: T_consult["stage_2"],
                3: T_consult["stage_3"],
                4: T_consult["stage_4"],
            }

            with st.spinner(f"Stage {current_stage} / 4 — {stage_names.get(current_stage, '')} {T_consult['running']}"):
                stage_response = call_stage(current_stage, {**context, **results}, consult_lang)

            if stage_response is None or not stage_response.get("success", True):
                err = (stage_response or {}).get("error", "Unknown error")
                st.error(f"Stage {current_stage} failed: {err}")
                if st.button("Retry Stage"):
                    st.rerun()
            else:
                stage_result = stage_response.get("result", {})

                # Store stage result
                key_map = {1: "intake", 2: "triage", 3: "guidelines", 4: "recommendations"}
                results[key_map[current_stage]] = stage_result
                st.session_state.consult_results = results
                st.session_state.consult_stage = current_stage + 1
                st.rerun()

    # ════════════════════════════════════════════════════════════════════════
    # Tab 2 — Image Analysis
    # ════════════════════════════════════════════════════════════════════════
    with tab_img:
        st.markdown(f'<div class="kl-page-title">{T["tab_image"]}</div>', unsafe_allow_html=True)

        st.markdown(
            '<div class="kl-alert kl-alert-info">'
            'Upload a medical image for AI-assisted analysis using Google HAI-DEF foundation models. '
            '<strong>CXR Foundation</strong> processes chest radiographs; '
            '<strong>Derm Foundation</strong> analyses skin lesions. '
            'Results are combined with MedGemma clinical reasoning.</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            image_type = st.selectbox(
                "Image Modality",
                ["Chest Radiograph", "Skin Lesion", "Pathology Slide", "Ultrasound", "Other"],
            )
        with col2:
            clinical_ctx = st.text_input(
                "Clinical Context (optional)",
                placeholder="Patient age, relevant history, specific concern…",
            )

        uploaded_image = st.file_uploader(
            "Select Medical Image",
            type=["jpg", "jpeg", "png"],
            help="JPEG or PNG, maximum 10 MB.",
        )

        if uploaded_image:
            c_img, c_meta = st.columns([2, 1])
            with c_img:
                st.image(uploaded_image, caption=uploaded_image.name, use_container_width=True)
            with c_meta:
                st.markdown(f"**File:** {uploaded_image.name}")
                st.markdown(f"**Modality:** {image_type}")
                if clinical_ctx:
                    st.markdown(f"**Context:** {clinical_ctx}")
                analyze_img = st.button("Analyse Image", type="primary", use_container_width=True)

            if analyze_img:
                st.markdown(
                    '<div class="kl-alert kl-alert-info">Image analysis may take 2–5 minutes.</div>',
                    unsafe_allow_html=True,
                )
                with st.spinner("Analysing with HAI-DEF foundation models..."):
                    try:
                        r = requests.post(
                            f"{API_BASE_URL}/analyze/image",
                            files={"file": (uploaded_image.name, uploaded_image.getvalue(), uploaded_image.type)},
                            params={"image_type": image_type.lower().replace(" ", "_")},
                            timeout=300,
                        )
                        r.raise_for_status()
                        res = r.json()
                        response_text = res.get("response", "No analysis available.")

                        # Determine triage from response
                        t = response_text.lower()
                        if any(k in t for k in ["critical", "emergency", "immediate"]):
                            level = "CRITICAL"
                        elif any(k in t for k in ["urgent", "refer immediately", "24 hour"]):
                            level = "URGENT"
                        elif any(k in t for k in ["moderate", "schedule", "appointment"]):
                            level = "MODERATE"
                        else:
                            level = "NON-URGENT"

                        st.markdown(_triage_html(level, lang), unsafe_allow_html=True)
                        st.markdown("#### Analysis Results")
                        st.markdown(
                            f'<div class="kl-guideline-quote" style="font-size:.9375rem;">'
                            f'{response_text}</div>',
                            unsafe_allow_html=True,
                        )

                        img_analysis = res.get("image_analysis", {})
                        if img_analysis and img_analysis.get("findings"):
                            with st.expander("Foundation Model Findings"):
                                st.json(img_analysis)

                        img_meta = res.get("image_metadata", {})
                        if img_meta:
                            with st.expander("Image Metadata"):
                                st.json(img_meta)

                    except requests.exceptions.Timeout:
                        st.error("Analysis timed out. Check system resources.")
                    except requests.exceptions.ConnectionError:
                        st.error("API connection lost. Restart the server after freeing memory.")
                        st.code("python run_api.py", language="bash")
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")

    # ════════════════════════════════════════════════════════════════════════
    # Tab 3 — Query History
    # ════════════════════════════════════════════════════════════════════════
    with tab_hist:
        st.markdown(f'<div class="kl-page-title">{T["tab_history"]}</div>', unsafe_allow_html=True)

        c_lim, c_ref = st.columns([3, 1])
        with c_lim:
            limit = st.slider("Records to display", 5, 50, 10)
        with c_ref:
            if st.button("Refresh", use_container_width=True):
                st.rerun()

        history = _api_get("/history", params={"limit": limit})
        if history:
            queries = history.get("queries", [])
            if queries:
                for q in queries:
                    qid = (q.get("id") or "")[:8]
                    ts  = q.get("timestamp", "")
                    with st.expander(f"Query {qid}  |  {ts}"):
                        st.markdown(f"**Input:** {q.get('input', 'N/A')}")
                        st.markdown("---")
                        st.markdown(f"**Response:** {q.get('response', 'N/A')}")
                        if q.get("sources"):
                            st.markdown(f"**Sources:** {', '.join(q['sources'])}")
                        st.caption(f"Context chunks: {q.get('context_count', 0)}")
            else:
                st.info("No query history yet.")
        else:
            st.error("Could not retrieve history from the API.")

        st.markdown("---")
        st.markdown("#### Usage Statistics")
        stats = _api_get("/stats")
        if stats:
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Total Queries", stats.get("total_queries", 0))
            with c2: st.metric("Avg Context Chunks", f"{stats.get('average_context_count', 0):.1f}")
            with c3: st.metric("Knowledge Base Docs", stats.get("kb_documents", "N/A"))
        else:
            st.info("Statistics unavailable.")

    # ════════════════════════════════════════════════════════════════════════
    # Tab 4 — System Information
    # ════════════════════════════════════════════════════════════════════════
    with tab_info:
        st.markdown(f'<div class="kl-page-title">{T["tab_about"]}</div>', unsafe_allow_html=True)

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("""
**Keneya Lens** is an offline-first clinical decision support system designed for community
health workers (CHWs) in resource-limited settings.

*"Keneya"* means **health** in Bambara, the lingua franca of Mali.

Built on Google's **Health AI Developer Foundations (HAI-DEF)**, the system runs entirely
on local hardware after setup — no internet connection required for patient consultations.

**Agentic Consultation Pipeline**
The Guided Consultation tab runs a 4-stage multi-agent pipeline:
1. **IntakeAgent** — structures free-text into a patient record
2. **TriageAgent** — IMCI-informed urgency assessment
3. **GuidelineAgent** — RAG retrieval from indexed clinical guidelines
4. **RecommendationAgent** — actionable CHW management plan
""")
        with col_r:
            st.markdown("""
**Model Stack**

| Component | Model |
|-----------|-------|
| Clinical Reasoning | MedGemma 4B-IT (HAI-DEF) |
| Chest Radiograph | CXR Foundation (HAI-DEF) |
| Dermatology | Derm Foundation (HAI-DEF) |
| Embeddings | Sentence Transformers MiniLM |
| Vector Database | ChromaDB |
| Backend | FastAPI + Uvicorn |
| Interface | Streamlit |

**Languages**
- Interface: English, Français
- Model output: follows interface language selection
""")

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
**Intended Use**
Decision support tool for trained healthcare professionals.
Not a substitute for clinical judgment or physician consultation.

**Data Privacy**
All inference is local. No patient data leaves the device.
Query logs are stored on-device only. HIPAA-aligned.
""")
        with c2:
            st.markdown("""
**Limitations**
- Model accuracy is unvalidated against clinical gold standard
- Foundation model inference currently uses simulation stubs
  pending data-access agreement for `google/cxr-foundation`
- Image analysis is text-based fallback when multimodal model unavailable
- Performance on low-resource devices (< 8 GB RAM) may be degraded

**Regulatory Notice**
Research prototype only. Not cleared for clinical use.
""")

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.text("Application:  v2.1.0")
            st.text("API:          v1.1.0")
        with c2:
            st.text("MedGemma:     4B-IT (HAI-DEF)")
            st.text("Agent stages: 4")
        with c3:
            st.text(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
            st.text("Challenge: MedGemma Impact 2026")

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="kl-footer">'
        'Keneya Lens Clinical Decision Support &nbsp;|&nbsp; '
        'Google HAI-DEF (MedGemma 4B) &nbsp;|&nbsp; '
        'Not for diagnostic use &nbsp;|&nbsp; '
        'Confirm all recommendations with a qualified healthcare professional'
        '</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
