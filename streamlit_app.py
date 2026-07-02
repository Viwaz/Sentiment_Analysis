import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import os

import subprocess
import time
from pathlib import Path
import base64
from streamlit_oauth import OAuth2Component
from streamlit_cookies_controller import CookieController

# Set up page configurations
st.set_page_config(
    page_title="Low-Resource Sentiment Classifier",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Read active URL query parameters (used by the Google OAuth redirect handshake below)
url_params = st.query_params

# Fix A: If a Google OAuth handshake is in progress, drop any stale local session
# hooks immediately so they can't clash with the incoming OAuth callback.
if "code" in url_params or "state" in url_params:
    if "logged_in" not in st.session_state or st.session_state.logged_in == False:
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        if "user" in url_params:
            del st.query_params["user"]

# Google OAuth client credentials (falls back to secrets.toml if not set below)
REDIRECT_URI = st.secrets.get("REDIRECT_URI", "http://localhost:8501")
GOOGLE_CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")

cookie_controller = CookieController()

# Initialise OAuth component
oauth2 = OAuth2Component(
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    "https://accounts.google.com/o/oauth2/v2/auth",
    "https://oauth2.googleapis.com/token",
    "https://oauth2.googleapis.com/token",
    "https://oauth2.googleapis.com/revoke"
)

# Helper function to render the Google Sign-In button
def login_button(client_id: str, client_secret: str, redirect_uri: str):
    """Render the Google Sign-In button and return the auth result."""
    return oauth2.authorize_button("Sign in with Google", redirect_uri, scope="openid email profile")

# Initialize database
from src.database import init_db
try:
    init_db()
except Exception as e:
    st.warning(f"Database initialization failed (is PostgreSQL running?): {e}")

# Custom Styling for a Premium UI
st.markdown("""
    <style>
    /* Google Fonts + Material Symbols (fixes sidebar icon text) */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

    /* Global font — deliberately excludes span so Material Icons aren't overridden */
    html, body, [class*="css"], .stApp, .stMarkdown, p, li, label, div {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* ── Material Symbols icons fix ── */
    .material-symbols-rounded,
    [data-testid="collapsedControl"] span,
    button[data-testid="baseButton-header"] span,
    button[kind="header"] span {
        font-family: 'Material Symbols Rounded' !important;
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    }

    /* ── Main app background ── */
    .stApp {
        background: linear-gradient(140deg, #EEF2FF 0%, #F0F9FF 50%, #F8FAFC 100%) !important;
    }

    /* ── Main content block ── */
    section.main > div {
        background: transparent !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #1E293B !important;
        border-right: none !important;
    }
    [data-testid="stSidebar"] * {
        color: #E0E7FF !important;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] *,
    [data-testid="stSidebar"] [data-testid="stTextInput"] div[data-baseweb="input"] *,
    [data-testid="stSidebar"] [data-testid="stTextInput"] [data-testid="InputInstructions"],
    [data-testid="stSidebar"] [data-testid="stTextInput"] button,
    [data-testid="stSidebar"] [data-testid="stTextInput"] svg {
        color: #1E1E1E !important;
        fill: #1E1E1E !important;
    }
    
    /* ── HIDE POPOVER DISCLOSURE ARROW (Material Icons span, not SVG) ── */
    /* Confirmed via browser inspector: the chevron is a span[data-testid="stIconMaterial"]
       rendering the "expand_more" glyph via Material Icons font */
    div[data-testid="stPopover"] span[data-testid="stIconMaterial"] {
        display: none !important;
    }
    /* Collapse the flex gap left after the span is removed */
    div[data-testid="stPopover"] button,
    div[data-testid="stPopover"] button > div {
        gap: 0px !important;
    }


    /* Popover panel container constraints */
    div[data-testid="stPopoverBody"] {
        max-width: 160px !important;
        padding: 8px !important;
        background-color: #1A2332 !important;
        border: 1px solid #2D3748 !important;
    }

    /* 2. UNIFY ALL FOUR OPTIONS (HTML LINK + NATIVE BUTTONS) */
    div[data-testid="stPopoverBody"] button,
    div[data-testid="stPopoverBody"] .menu-link-item {
        font-size: 14px !important;
        font-family: inherit !important;
        font-weight: normal !important;
        padding: 10px 16px !important;
        margin-bottom: 8px !important;

        /* Blue pill gradient matching the dashboard primary style */
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%) !important;
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;

        border: none !important;
        text-align: center !important;
        justify-content: center !important;
        display: block !important;
        width: 100% !important;
        box-sizing: border-box !important;
        text-decoration: none !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25) !important;
        transform: none !important;
        min-height: unset !important;
    }
    div[data-testid="stPopoverBody"] button * {
        color: #FFFFFF !important;
    }

    /* Remove bottom margin from last button */
    div[data-testid="stPopoverBody"] button:last-child {
        margin-bottom: 0px !important;
    }

    /* 3. HOVER ACTIONS */
    div[data-testid="stPopoverBody"] button:hover,
    div[data-testid="stPopoverBody"] .menu-link-item:hover {
        background: linear-gradient(135deg, #60A5FA 0%, #2563EB 100%) !important;
        background-color: #60A5FA !important;
        color: #FFFFFF !important;
        cursor: pointer !important;
    }
    div[data-testid="stPopoverBody"] button:hover * {
        color: #FFFFFF !important;
    }

    /* Delete button: red on hover */
    div[data-testid="stPopoverBody"] button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%) !important;
        background-color: #EF4444 !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25) !important;
        transform: none !important;
    }
    div[data-testid="stPopoverBody"] button[data-testid="baseButton-primary"] * {
        color: #FFFFFF !important;
    }
    div[data-testid="stPopoverBody"] button[data-testid="baseButton-primary"]:hover {
        background: #DC2626 !important;
        background-color: #DC2626 !important;
        color: #FFFFFF !important;
    }
    div[data-testid="stPopoverBody"] button[data-testid="baseButton-primary"]:hover * {
        color: #FFFFFF !important;
    }

    /* Catch-all text colour inside popover */
    div[data-testid="stPopoverBody"] * {
        color: #FFFFFF !important;
    }
    div[data-testid="stPopoverBody"] label {
        color: #E2E8F0 !important;
        font-size: 13px !important;
    }
    div[data-testid="stPopoverBody"] input {
        color: #1E1E1E !important;
    }

    /* Legible input texts (dark charcoal) & high-contrast placeholders (stark gray) */
    input {
        color: #1E1E1E !important;
    }
    input::placeholder {
        color: #555555 !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] strong {
        color: #FFFFFF !important;
        font-family: 'Outfit', sans-serif !important;
    }
    [data-testid="stSidebar"] .stSuccess {
        background-color: rgba(16, 185, 129, 0.2) !important;
        color: #6EE7B7 !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
    }
    [data-testid="stSidebar"] .stWarning {
        background-color: rgba(245, 158, 11, 0.2) !important;
        border: 1px solid rgba(245, 158, 11, 0.3) !important;
    }

    /* ── Page headings ── */
    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        color: #1E293B !important;
    }

    /* ── Tab bar ── */
    [data-testid="stTabs"] [role="tablist"] {
        background: white;
        padding: 6px 8px;
        border-radius: 14px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #E2E8F0;
        gap: 4px;
    }
    [data-testid="stTabs"] [role="tab"] {
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
        color: #64748B !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #4F46E5, #3B82F6) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(79,70,229,0.3) !important;
    }

    /* ── Cards ── */
    .metric-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        margin-bottom: 16px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    }
    .metric-card h4 {
        margin-top: 0 !important;
        color: #1E293B !important;
    }

    /* ── Badges ── */
    .badge {
        padding: 6px 16px;
        border-radius: 9999px;
        font-size: 1rem;
        font-weight: 700;
        display: inline-block;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }
    .badge-positive {
        background-color: #D1FAE5;
        color: #065F46;
        border: 1.5px solid #6EE7B7;
    }
    .badge-negative {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1.5px solid #FCA5A5;
    }
    .badge-neutral {
        background-color: #FEF3C7;
        color: #92400E;
        border: 1.5px solid #FCD34D;
    }

    /* ── Buttons ── */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%) !important;
        color: white !important;
        border: none !important;
        padding: 10px 28px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4) !important;
        background: linear-gradient(135deg, #4338CA 0%, #2563EB 100%) !important;
    }

    /* ── Input widgets (Text, Password, TextArea) ── */
    [data-testid="stTextArea"] textarea,
    [data-testid="stTextInput"] input {
        border-radius: 10px !important;
        border: 1.5px solid #CBD5E1 !important;
        background: #FFFFFF !important;
        color: #1E293B !important;
        font-size: 0.95rem !important;
    }
    [data-testid="stTextArea"] textarea:focus,
    [data-testid="stTextInput"] input:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    }

    /* ── Number Input ── */
    [data-testid="stNumberInput"] input {
        background: #FFFFFF !important;
        color: #1E293B !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 10px !important;
        font-size: 0.95rem !important;
    }
    [data-testid="stNumberInput"] > div {
        background: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 10px !important;
    }
    [data-testid="stNumberInput"] button {
        background: #F1F5F9 !important;
        color: #1E293B !important;
        border: none !important;
    }
    [data-testid="stNumberInput"] button:hover {
        background: #E2E8F0 !important;
    }

    /* ── Selectbox ── */
    [data-testid="stSelectbox"] > div > div {
        border-radius: 10px !important;
        border: 1.5px solid #CBD5E1 !important;
        background: #FFFFFF !important;
        color: #1E293B !important;
    }
    [data-testid="stSelectbox"] span {
        color: #1E293B !important;
    }

    /* ── File Uploader ── */
    [data-testid="stFileUploader"] {
        background: #FFFFFF !important;
        border: 2px dashed #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 8px !important;
    }

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] {
        background: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
    }

    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        background: #FFFFFF !important;
        border-radius: 14px !important;
        border: 1px solid #E2E8F0 !important;
        padding: 16px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04) !important;
    }
    [data-testid="stMetricValue"] {
        color: #1E293B !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #64748B !important;
    }

    /* ── Alerts ── */
    .stAlert {
        border-radius: 12px !important;
    }

    /* ── Progress bars ── */
    .stProgress > div > div {
        border-radius: 999px !important;
        background: linear-gradient(90deg, #6366F1, #3B82F6) !important;
    }

    /* ── Chat Input (st.chat_input) Styling ── */
    [data-testid="stChatInput"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
        padding: 4px !important;
    }
    [data-testid="stChatInput"] div {
        background-color: #FFFFFF !important;
    }
    [data-testid="stChatInputTextArea"] {
        color: #1E293B !important;
        background-color: #FFFFFF !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.95rem !important;
    }
    [data-testid="stChatInputTextArea"]::placeholder {
        color: #94A3B8 !important;
        opacity: 1 !important;
    }
    /* Buttons inside the chat input (like submit and attachment buttons) */
    [data-testid="stChatInput"] button {
        background-color: transparent !important;
        color: #4F46E5 !important;
        border: none !important;
    }
    [data-testid="stChatInput"] button:hover {
        background-color: #F1F5F9 !important;
        color: #3B82F6 !important;
    }
    /* Material symbols and icons inside chat input */
    [data-testid="stChatInput"] svg,
    [data-testid="stChatInput"] span {
        color: #4F46E5 !important;
        fill: #4F46E5 !important;
    }

/* ── Main Container / Auth Card ── */
.auth-card {
    background: #ffffff;
    padding: 32px 28px;
    border-radius: 12px; /* Subtle, formal rounding instead of overly bubbly corners */
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); /* Soft, clean shadow */
    border: 1px solid #E2E8F0;
    max-width: 440px; /* Constrains the width so fields don't stretch indefinitely */
    margin: 40px auto;
}

/* ── Dashboard Header ── */
.auth-card h1 {
    font-size: 24px; /* Reduced from massive display sizes */
    font-weight: 700;
    color: #0F172A; /* Slate 900 for executive readability */
    margin: 0 0 6px 0;
    text-align: center;
    letter-spacing: -0.3px;
}

.auth-card .subtitle {
    text-align: center;
    color: #64748B; /* Neutral slate subtext */
    font-size: 13px;
    margin-bottom: 24px;
}

/* ── Formal Tab Switcher ── */
.tab-container {
    display: flex;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 20px;
    gap: 16px;
}

.tab-btn {
    padding: 8px 4px;
    font-size: 14px;
    font-weight: 500;
    color: #64748B;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    cursor: pointer;
    transition: all 0.2s ease;
}

.tab-btn.active {
    color: #2563EB; /* Clean corporate blue anchor */
    border-bottom-color: #2563EB;
    font-weight: 600;
}

/* ── Form Fields & Labels ── */
.form-group {
    margin-bottom: 16px;
    display: flex;
    flex-direction: column;
}

.form-group label {
    font-size: 12.5px;
    font-weight: 600;
    color: #334155; /* Slate 700 */
    margin-bottom: 6px;
}

.form-group input {
    width: 100%;
    height: 38px; /* Standard professional input height */
    padding: 8px 12px;
    font-size: 14px;
    color: #1E293B;
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1; /* Clean grey border */
    border-radius: 6px;
    box-sizing: border-box;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

/* Form Interactivity */
.form-group input:focus {
    outline: none;
    border-color: #3B82F6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}
    /* ── Footer ── */
    .footer {
        text-align: center;
        margin-top: 40px;
        padding: 20px;
        color: #94A3B8;
        font-size: 0.85rem;
        border-top: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)


# ----------------- Helper Functions -----------------

@st.cache_resource
def get_project_root():
    return Path(__file__).resolve().parent

def build_paths():
    root = get_project_root()
    from src.data_utils import build_paths as src_build_paths
    return src_build_paths(root)

@st.cache_resource
def load_baseline_model():
    paths = build_paths()
    model_path = paths.models_dir / "baseline" / "best_baseline_model.joblib"
    vec_path = paths.models_dir / "baseline" / "best_baseline_vectorizer.joblib"
    if not model_path.exists() or not vec_path.exists():
        return None, None
    model = joblib.load(model_path)
    vectorizer = joblib.load(vec_path)
    return model, vectorizer

def list_transformer_models():
    paths = build_paths()
    trans_dir = paths.models_dir / "transformer"
    if not trans_dir.exists():
        return []
    models = []
    # Search for model directories with a best_model subdirectory
    for p in trans_dir.glob("**/best_model"):
        models.append(p.parent.name)
    return sorted(list(set(models)))

@st.cache_resource
def load_transformer_model(run_id):
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    paths = build_paths()
    model_dir = paths.models_dir / "transformer" / run_id / "best_model"
    tok_dir = paths.models_dir / "transformer" / run_id / "best_tokenizer"
    
    tokenizer_source = tok_dir if tok_dir.exists() else model_dir
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_source)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    return model, tokenizer

def run_script(module_name: str, args: list[str] = []) -> tuple[int, str, str]:
    """Runs a pipeline script and returns status code, stdout, stderr."""
    root = get_project_root()
    cmd = ["python", "-m", module_name] + args
    result = subprocess.run(
        cmd,
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    return result.returncode, result.stdout, result.stderr


def cancel_requested(key: str) -> bool:
    return bool(st.session_state.get(key, False))


def render_cancel_button(label: str, key: str):
    if st.button(label, key=f"{key}_btn", type="secondary"):
        st.session_state[key] = True
        st.warning("Cancellation requested. The current step will stop before the next operation.")


def save_uploaded_raw_data(uploaded_files, raw_dir: Path) -> list[str]:
    saved = []
    raw_dir.mkdir(parents=True, exist_ok=True)
    for uf in uploaded_files:
        safe_name = Path(uf.name).name
        uf.seek(0)
        df = pd.read_csv(uf)
        df.to_csv(raw_dir / safe_name, index=False, encoding="utf-8")
        saved.append(safe_name)
    return saved

# ----------------- helper components -----------------

def run_parallel_predictions(df_run, baseline_model, baseline_vec, transformers, paths):
    import numpy as np
    import torch
    from concurrent.futures import ThreadPoolExecutor
    from scipy.special import softmax
    
    texts = df_run["cleaned_text"].tolist()
    results = []
    
    # 1. Baseline prediction task
    def run_baseline():
        if baseline_model is None or baseline_vec is None:
            return None
        from src.evaluate_external import transform_with_saved_vectorizer
        X_batch = transform_with_saved_vectorizer(baseline_vec, df_run["cleaned_text"])
        
        if hasattr(baseline_model, "predict_proba"):
            probs = baseline_model.predict_proba(X_batch)
        elif hasattr(baseline_model, "decision_function"):
            decisions = baseline_model.decision_function(X_batch)
            if len(decisions.shape) == 1 or decisions.shape[1] == 1:
                decisions = np.column_stack([-decisions, decisions])
            probs = softmax(decisions, axis=1)
        else:
            preds = baseline_model.predict(X_batch)
            class_to_idx = {c: i for i, c in enumerate(baseline_model.classes_)}
            probs = np.zeros((len(preds), 3))
            for i, p in enumerate(preds):
                if p in class_to_idx:
                    probs[i, class_to_idx[p]] = 1.0
                    
        # Reorder classes to match standard ["negative", "neutral", "positive"]
        labels_order = ["negative", "neutral", "positive"]
        mapped_probs = np.zeros((len(probs), 3))
        for idx, label in enumerate(labels_order):
            if label in baseline_model.classes_:
                c_idx = list(baseline_model.classes_).index(label)
                mapped_probs[:, idx] = probs[:, c_idx]
        return mapped_probs

    # 2. Transformer prediction task
    def run_transformer(run_id):
        t_model, t_tokenizer = load_transformer_model(run_id)
        id_to_label = getattr(t_model.config, "id2label", {0: "negative", 1: "neutral", 2: "positive"})
        label_to_idx = {v.lower(): k for k, v in id_to_label.items()}
        labels_order = ["negative", "neutral", "positive"]
        class_indices = [label_to_idx.get(l, 0) for l in labels_order]
        
        probs_list = []
        batch_size = 16
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            inputs = t_tokenizer(batch_texts, return_tensors="pt", padding=True, truncation=True, max_length=128)
            with torch.no_grad():
                outputs = t_model(**inputs)
                logits = outputs.logits.numpy()
                probs = softmax(logits, axis=1)
                reordered_probs = probs[:, class_indices]
                probs_list.append(reordered_probs)
        return np.vstack(probs_list)

    # Execute concurrently
    futures = {}
    with ThreadPoolExecutor() as executor:
        if baseline_model is not None:
            futures["TF-IDF Baseline"] = executor.submit(run_baseline)
        for t in transformers:
            futures[f"Transformer ({t})"] = executor.submit(run_transformer, t)
            
        for name, fut in futures.items():
            try:
                res = fut.result()
                if res is not None:
                    results.append(res)
            except Exception as e:
                st.error(f"Error running model '{name}': {e}")
                
    if not results:
        raise ValueError("No models succeeded or are available for prediction.")
        
    # Ensemble by averaging probabilities
    ensemble_probs = np.mean(results, axis=0)
    labels_order = ["negative", "neutral", "positive"]
    pred_indices = np.argmax(ensemble_probs, axis=1)
    return [labels_order[idx] for idx in pred_indices]


def render_batch_analysis(baseline_model, baseline_vec, transformers, paths, uploaded_file, is_developer=True):
    st.markdown("### Batch Sentiment Analysis")
    if uploaded_file is None:
        return
        
    st.markdown(f"**Loaded CSV:** `{getattr(uploaded_file, 'name', 'Uploaded File')}`")
    
    # Initialize session state for batch results if not exists
    if "batch_df" not in st.session_state:
        st.session_state.batch_df = None
    if "batch_text_col" not in st.session_state:
        st.session_state.batch_text_col = None
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            # Find candidate text columns
            text_cols = [c for c in df.columns if any(x in c.lower() for x in ["text", "comment", "body"])]
            
            if not st.session_state.batch_processing:
                text_column = st.selectbox("Select Comment Column", df.columns, index=df.columns.get_loc(text_cols[0]) if text_cols else 0)
                
                # Model selector
                batch_models = []
                if baseline_model is not None:
                    batch_models.append("TF-IDF Baseline")
                for t in transformers:
                    batch_models.append(f"Transformer ({t})")
                    
                if not batch_models:
                    st.error("No models are currently available. Please train models first.")
                    return
                    
                if is_developer:
                    batch_model_choice = st.selectbox("Select Model for Batch Run", batch_models)
                else:
                    batch_model_choice = "Parallel Ensemble"
                
                if st.button("Run Batch Prediction"):
                    st.session_state.batch_text_column_val = text_column
                    st.session_state.batch_model_choice_val = batch_model_choice
                    st.session_state.batch_processing = True
                    st.session_state.trigger_batch_predict = True
                    st.rerun()
            
            if st.session_state.trigger_batch_predict:
                text_column = st.session_state.batch_text_column_val
                batch_model_choice = st.session_state.batch_model_choice_val
                with st.spinner("Processing batch..."):
                    try:
                        # Preprocess and clean text
                        from src.preprocess import clean_text
                        
                        df_run = df.copy()
                        df_run["cleaned_text"] = df_run[text_column].apply(clean_text)
                        
                        # Run predictions
                        if batch_model_choice == "TF-IDF Baseline":
                            from src.evaluate_external import transform_with_saved_vectorizer
                            X_batch = transform_with_saved_vectorizer(baseline_vec, df_run["cleaned_text"])
                            predictions = baseline_model.predict(X_batch)
                        elif batch_model_choice.startswith("Transformer ("):
                            run_id = batch_model_choice.replace("Transformer (", "").rstrip(")")
                            t_model, t_tokenizer = load_transformer_model(run_id)
                            
                            import torch
                            predictions = []
                            id_to_label = getattr(t_model.config, "id2label", {0: "negative", 1: "neutral", 2: "positive"})
                            
                            # Process texts
                            for txt in df_run["cleaned_text"]:
                                inputs = t_tokenizer(txt, return_tensors="pt", truncation=True, max_length=128)
                                with torch.no_grad():
                                    logits = t_model(**inputs).logits.numpy()[0]
                                    pred_idx = np.argmax(logits)
                                    predictions.append(id_to_label[pred_idx].lower())
                        else:
                            # Parallel Ensemble
                            predictions = run_parallel_predictions(
                                df_run, baseline_model, baseline_vec, transformers, paths
                            )
                                    
                        df_run["predicted_sentiment"] = predictions
                        st.session_state.batch_df = df_run
                        st.session_state.batch_text_col = text_column
                        st.success("Batch prediction complete!")
                    except Exception as e:
                        st.error(f"Error during batch prediction: {e}")
                    finally:
                        st.session_state.trigger_batch_predict = False
                        st.session_state.batch_processing = False
                        st.rerun()
                        
            # Render results panel if we have results in session state
            if st.session_state.batch_df is not None:
                df_results = st.session_state.batch_df
                text_col = st.session_state.batch_text_col
                
                st.markdown("---")
                st.markdown("### Results Panel")
                
                # Summary cards
                total_comments = len(df_results)
                pos_count = sum(df_results["predicted_sentiment"] == "positive")
                neu_count = sum(df_results["predicted_sentiment"] == "neutral")
                neg_count = sum(df_results["predicted_sentiment"] == "negative")
                
                pos_pct = pos_count / total_comments if total_comments > 0 else 0
                neu_pct = neu_count / total_comments if total_comments > 0 else 0
                neg_pct = neg_count / total_comments if total_comments > 0 else 0
                
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                with col_m1:
                    st.markdown(f"""
                        <div class="metric-card" style="text-align: center;">
                             <span style="font-size: 0.85rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Total Evaluated</span>
                             <h2 style="margin: 8px 0 0 0; color: #1E293B; font-size: 2rem;">{total_comments}</h2>
                        </div>
                    """, unsafe_allow_html=True)
                with col_m2:
                    st.markdown(f"""
                        <div class="metric-card" style="text-align: center; border-left: 5px solid #10B981;">
                             <span style="font-size: 0.85rem; color: #065F46; font-weight: 600; text-transform: uppercase;">Positive Sentiment</span>
                             <h2 style="margin: 8px 0 0 0; color: #065F46; font-size: 2rem;">{pos_count} <span style="font-size: 1rem; color: #34D399;">({pos_pct:.1%})</span></h2>
                        </div>
                    """, unsafe_allow_html=True)
                with col_m3:
                    st.markdown(f"""
                        <div class="metric-card" style="text-align: center; border-left: 5px solid #F59E0B;">
                             <span style="font-size: 0.85rem; color: #92400E; font-weight: 600; text-transform: uppercase;">Neutral Sentiment</span>
                             <h2 style="margin: 8px 0 0 0; color: #92400E; font-size: 2rem;">{neu_count} <span style="font-size: 1rem; color: #FBBF24;">({neu_pct:.1%})</span></h2>
                        </div>
                    """, unsafe_allow_html=True)
                with col_m4:
                    st.markdown(f"""
                        <div class="metric-card" style="text-align: center; border-left: 5px solid #EF4444;">
                             <span style="font-size: 0.85rem; color: #991B1B; font-weight: 600; text-transform: uppercase;">Negative Sentiment</span>
                             <h2 style="margin: 8px 0 0 0; color: #991B1B; font-size: 2rem;">{neg_count} <span style="font-size: 1rem; color: #F87171;">({neg_pct:.1%})</span></h2>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Visualize predictions
                col1, col2 = st.columns([1, 1])
                
                labels = ['Positive', 'Neutral', 'Negative']
                sizes = [pos_count, neu_count, neg_count]
                filtered_labels = [l for l, s in zip(labels, sizes) if s > 0]
                filtered_sizes = [s for s in sizes if s > 0]
                colors = ['#10B981', '#F59E0B', '#EF4444']
                filtered_colors = [c for c, s in zip(colors, sizes) if s > 0]
                
                with col1:
                    st.markdown("#### Sentiment Distribution (3D-like Pie Chart)")
                    if filtered_sizes:
                        import matplotlib.pyplot as plt
                        fig, ax = plt.subplots(figsize=(6, 5))
                        explode = [0.05] * len(filtered_sizes)
                        wedges, texts, autotexts = ax.pie(
                            filtered_sizes, 
                            explode=explode,
                            labels=filtered_labels, 
                            autopct='%1.1f%%',
                            shadow=True, 
                            startangle=140, 
                            colors=filtered_colors,
                            textprops=dict(color="#1E293B", weight="bold", size=10),
                            wedgeprops=dict(edgecolor='white', linewidth=1.5)
                        )
                        for autotext in autotexts:
                            autotext.set_color('white')
                            autotext.set_fontsize(11)
                        ax.axis('equal')  
                        plt.tight_layout()
                        st.pyplot(fig)
                        plt.close(fig)
                    else:
                        st.info("No sentiments to display.")
                        
                with col2:
                    st.markdown("#### Sentiment Category Counts (Bar Chart)")
                    if filtered_sizes:
                        import matplotlib.pyplot as plt
                        import seaborn as sns
                        fig_bar, ax_bar = plt.subplots(figsize=(6, 5))
                        sentiment_df = pd.DataFrame({
                            'Sentiment': filtered_labels,
                            'Count': filtered_sizes
                        })
                        sns.barplot(
                            x='Count', 
                            y='Sentiment', 
                            data=sentiment_df, 
                            palette=filtered_colors,
                            ax=ax_bar,
                            hue='Sentiment',
                            legend=False
                        )
                        ax_bar.spines['top'].set_visible(False)
                        ax_bar.spines['right'].set_visible(False)
                        ax_bar.spines['left'].set_color('#CBD5E1')
                        ax_bar.spines['bottom'].set_color('#CBD5E1')
                        ax_bar.tick_params(colors='#475569', labelsize=11)
                        ax_bar.set_ylabel('', color='#475569', fontsize=12)
                        ax_bar.set_xlabel('Count', color='#475569', fontsize=12)
                        for container in ax_bar.containers:
                            ax_bar.bar_label(container, fmt='%d', padding=5, color='#1E293B', weight='bold', fontsize=11)
                        plt.tight_layout()
                        st.pyplot(fig_bar)
                        plt.close(fig_bar)
                    else:
                        st.info("No sentiments to display.")
                        
                # Preview Data Table
                st.markdown("#### Prediction Preview")
                st.dataframe(df_results[[text_col, "cleaned_text", "predicted_sentiment"]].head(100), use_container_width=True)
                
                # Download predicted CSV
                csv_data = df_results.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Download Predictions CSV",
                    data=csv_data,
                    file_name="sentiment_predictions.csv",
                    mime="text/csv"
                )
                
        except Exception as e:
            st.error(f"Error processing CSV file: {e}")

# ----------------- UI Sidebar -----------------

# ── Session state defaults ──────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    # First check native Streamlit context, fallback to the cookie controller
    saved_user = None
    if hasattr(st, "context") and hasattr(st.context, "cookies"):
        saved_user = st.context.cookies.get("logged_in_user")
    if not saved_user:
        saved_user = cookie_controller.get("logged_in_user")

    if saved_user:
        from src.database import get_user_by_username
        user = get_user_by_username(saved_user)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user["user_id"]
            st.session_state.username = user["username"]
            st.session_state.current_user = {"user_id": user["user_id"], "username": user["username"], "role": user.get("role", "general")}
            st.session_state.logged_in_as_dev = user.get("role") in ("developer", "admin")
        else:
            st.session_state.logged_in = False
    else:
        st.session_state.logged_in = False

# Clean up any leftover query params that might re-trigger a login after a cookie restore
if st.session_state.get("logged_in") and st.session_state.get("user_id"):
    if "user" in st.query_params:
        st.query_params.clear()

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "new"
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "current_user" not in st.session_state:
    st.session_state.current_user = {"user_id": "guest", "username": "Guest", "role": "general"}
if "logged_in_as_dev" not in st.session_state:
    st.session_state.logged_in_as_dev = False

# Gating: block dashboard views for unauthenticated users
if not st.session_state.logged_in:
    st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>🔐 Sentiment Analysis Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B;'>Please sign in or create an account to proceed.</p>", unsafe_allow_html=True)
    
    auth_tabs = st.tabs(["📝 Create Account", "🔑 Sign In"])
    
    with auth_tabs[1]:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username_input")
            password = st.text_input("Password", type="password", key="login_password_input")
            submit = st.form_submit_button("Log In", use_container_width=True)
            if submit:
                if not username or not password:
                    st.error("Please fill out all fields.")
                else:
                    from src.database import authenticate_user
                    user = authenticate_user(username, password)
                    if user:
                        cookie_controller.set("logged_in_user", user["username"])
                        st.session_state.logged_in = True
                        st.session_state.user_id = user["user_id"]
                        st.session_state.username = user["username"]
                        st.session_state.current_user = {"user_id": user["user_id"], "username": user["username"], "role": user.get("role", "general")}
                        st.session_state.logged_in_as_dev = user.get("role") in ("developer", "admin")
                        st.session_state.view_mode = "new"
                        st.success(f"Welcome back, {user['username']}!")
                        st.query_params.clear()
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        st.markdown("<hr style='margin: 8px 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)
        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            st.caption("Google Sign-In is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in secrets.toml to enable it.")
        else:
            result = login_button(client_id=GOOGLE_CLIENT_ID, client_secret=GOOGLE_CLIENT_SECRET, redirect_uri=REDIRECT_URI)
            if result and "token" in result:
                id_token = result["token"].get("id_token")
                if id_token:
                    payload = id_token.split(".")[1]
                    payload += "=" * ((4 - len(payload) % 4) % 4)
                    user_info = json.loads(base64.urlsafe_b64decode(payload).decode("utf-8"))
                    email = user_info.get("email")
                    if email:
                        from src.database import create_or_get_google_user
                        user = create_or_get_google_user(email)
                        cookie_controller.set("logged_in_user", user["username"])
                        st.session_state.logged_in = True
                        st.session_state.user_id = user["user_id"]
                        st.session_state.username = user["username"]
                        st.session_state.current_user = {"user_id": user["user_id"], "username": user["username"], "role": user.get("role", "general")}
                        st.session_state.logged_in_as_dev = user.get("role") in ("developer", "admin")
                        st.session_state.view_mode = "new"
                        st.query_params.clear()
                        st.rerun()
                        
    with auth_tabs[0]:
        with st.form("register_form"):
            reg_username = st.text_input("Choose Username", key="register_username_input")
            reg_password = st.text_input("Choose Password", type="password", key="register_password_input")
            reg_confirm = st.text_input("Confirm Password", type="password", key="register_confirm_input")
            submit_reg = st.form_submit_button("Create Account", use_container_width=True)
            if submit_reg:
                if not reg_username or not reg_password or not reg_confirm:
                    st.error("Please fill out all fields.")
                elif reg_password != reg_confirm:
                    st.error("Passwords do not match.")
                else:
                    from src.database import create_user
                    try:
                        create_user(reg_username, reg_password)
                        st.success("Account created successfully! Please sign in using the 'Sign In' tab.")
                    except ValueError as ve:
                        st.error(str(ve))
                    except Exception as e:
                        st.error(f"Failed to create account: {e}")
                        
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Handle shareable URL query parameter redirect
if "session_id" in st.query_params:
    try:
        param_sess_id = int(st.query_params["session_id"])
        if st.session_state.current_session_id != param_sess_id or st.session_state.view_mode != "history":
            st.session_state.current_session_id = param_sess_id
            st.session_state.view_mode = "history"
            st.session_state.user_scrape_results = None
            st.rerun()
    except ValueError:
        pass

is_developer = st.session_state.logged_in_as_dev

# ── Sidebar ──
st.sidebar.markdown(
    """
    <div style='text-align: center; margin-bottom: 20px;'>
        <h1 style='font-size: 2.2rem; margin-bottom: 0px;'>MW</h1>
        <h2 style='font-size: 1.3rem; margin-top: 5px; color:#4F46E5;'>Sentiment Classifier</h2>
        <span style='color: #64748B; font-size: 0.8rem;'>Facebook Code-Switched Low-Resource App</span>
    </div>
    """,
    unsafe_allow_html=True
)
st.sidebar.markdown(f"👤 Logged in as: **{st.session_state.username}**")
st.sidebar.markdown("---")

# 1. "Analyze New URL" button fixed at the top
if st.sidebar.button("➕ Analyze New URL", type="primary", use_container_width=True, key="new_analysis_sidebar_btn"):
    st.session_state.view_mode = "new"
    st.session_state.current_session_id = None
    st.session_state.user_scrape_results = None
    st.query_params.clear()
    st.rerun()

st.sidebar.subheader("History Sessions")
# Query user sessions
from src.database import get_user_sessions
sessions = get_user_sessions(st.session_state.user_id)

if sessions:
    for s in sessions:
        # Determine label using display_title from database COALESCE
        btn_label = s.get("display_title") or "Analysis Run"
        session_id = s["session_id"]
        
        # Unique session state key for rename visibility flag
        rename_flag_key = f"show_rename_{session_id}"
        if rename_flag_key not in st.session_state:
            st.session_state[rename_flag_key] = False
            
        # Wrap the columns tightly inside a container to guarantee rigid vertical alignment
        with st.sidebar.container():
            col_link, col_menu = st.columns([0.85, 0.15])
            
            with col_link:
                is_active = (st.session_state.current_session_id == session_id and st.session_state.view_mode == "history")
                btn_type = "primary" if is_active else "secondary"
                if st.button(btn_label, key=f"session_btn_{session_id}", use_container_width=True, type=btn_type):
                    st.session_state.current_session_id = session_id
                    st.session_state.view_mode = "history"
                    st.session_state.user_scrape_results = None
                    st.query_params["session_id"] = str(session_id)
                    st.rerun()
                    
            with col_menu:
                # Popover context-menu – vertical dots trigger
                with st.popover("⋮", use_container_width=True, key=f"session_action_pop_{session_id}"):
                    if not st.session_state[rename_flag_key]:
                        # Default Context Menu view
                        # 1. Original Post – uniform menu-link-item anchor
                        url_val = s.get("url") or "#"
                        st.markdown(
                            f'<a href="{url_val}" target="_blank" class="menu-link-item">Original Post</a>',
                            unsafe_allow_html=True
                        )
                        
                        # 2. Trigger Rename
                        if st.button("Rename", key=f"rename_trigger_{session_id}", use_container_width=True):
                            st.session_state[rename_flag_key] = True
                            st.rerun()
                            
                        # 3. Share
                        if st.button("Share", key=f"share_btn_{session_id}", use_container_width=True):
                            st.query_params["session_id"] = str(session_id)
                            st.info("Link set in query parameters!")
                        
                        # 4. Delete
                        if st.button("Delete", key=f"delete_btn_{session_id}", type="primary", use_container_width=True):
                            from src.database import delete_session
                            delete_session(session_id)
                            if st.session_state.current_session_id == session_id:
                                st.session_state.current_session_id = None
                                st.session_state.view_mode = "new"
                                st.query_params.clear()
                            st.success("Deleted!")
                            st.rerun()
                    else:
                        # Conditional state-driven Rename Form view
                        rename_title = st.text_input(
                            "Rename Session", 
                            value=s.get("custom_title") or "", 
                            placeholder="e.g., Fuel Price Hike",
                            key=f"rename_input_{session_id}"
                        )
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("Save", key=f"save_rename_btn_{session_id}", type="primary", use_container_width=True):
                                from src.database import update_session_title
                                title_clean = rename_title.strip()
                                update_session_title(session_id, title_clean if title_clean else None)
                                st.session_state[rename_flag_key] = False
                                st.success("Session renamed!")
                                st.rerun()
                        with col_cancel:
                            if st.button("Cancel", key=f"cancel_rename_btn_{session_id}", use_container_width=True):
                                st.session_state[rename_flag_key] = False
                                st.rerun()
                                
            # Small structural gap between sessions
            st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
else:
    st.sidebar.info("No past sessions found.")

st.sidebar.markdown("---")

# Continue with existing path setup
paths = build_paths()

# Load metadata for display
meta_path = paths.processed_dir / "metadata.json"
metadata = {}
if meta_path.exists():
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    except Exception:
        pass

if is_developer:
    st.sidebar.subheader("Dataset Summary")
    if metadata:
        st.sidebar.markdown(f"**Total Raw Comments:** {metadata.get('raw_rows', 'N/A')}")
        st.sidebar.markdown(f"**Filtered Comments:** {metadata.get('rows_after_filtering', 'N/A')}")
        st.sidebar.markdown(f"**Train Size:** {metadata.get('split_sizes', {}).get('train', 'N/A')}")
        st.sidebar.markdown(f"**Val Size:** {metadata.get('split_sizes', {}).get('val', 'N/A')}")
        st.sidebar.markdown(f"**Test Size:** {metadata.get('split_sizes', {}).get('test', 'N/A')}")
        
        label_dist = metadata.get('label_distribution', {})
        if label_dist:
            st.sidebar.markdown("**Label Distribution:**")
            for k, v in label_dist.items():
                st.sidebar.markdown(f"- *{k}:* {v}")
    else:
        st.sidebar.info("Run preprocessing to populate metadata.")

baseline_model, baseline_vec = load_baseline_model()
transformers = list_transformer_models()

if is_developer:
    st.sidebar.subheader("Model Status")
    if baseline_model is not None:
        st.sidebar.success("[OK] Baseline Model: Available")
    else:
        st.sidebar.error("[ERR] Baseline Model: Missing")

    if transformers:
        st.sidebar.success(f"[OK] Transformers: {len(transformers)} Available")
        for t in transformers:
            st.sidebar.markdown(f"- `{t}`")
    else:
        st.sidebar.warning("[WARN] Transformers: None found locally")

# Secure log out button at bottom of sidebar
if st.sidebar.button("🔓 Log Out", use_container_width=True, key="logout_sidebar_btn"):
    cookie_controller.remove("logged_in_user")
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.view_mode = "new"
    st.session_state.current_session_id = None
    st.session_state.user_scrape_results = None
    st.query_params.clear()
    st.rerun()

# ----------------- UI Tabs / Views -----------------

if not is_developer:
    # ── User Mode: Dashboard views ──
    
    if st.session_state.view_mode == "history" and st.session_state.current_session_id is not None:
        # History View
        from src.database import get_session, get_session_comments
        
        session = get_session(st.session_state.current_session_id)
        if session is None:
            st.error("Selected session not found in database.")
            st.session_state.view_mode = "new"
            st.session_state.current_session_id = None
            st.rerun()
            
        comments_list = get_session_comments(st.session_state.current_session_id)
        
        st.markdown(f"### 📊 Analysis Session for: `{session['url']}`")
        st.markdown(f"**Analyzed on:** `{session['timestamp']}`")
        
        if not comments_list:
            st.info("No comments found for this session.")
        else:
            df_user = pd.DataFrame(comments_list)
            
            # Count sentiments
            df_user["sentiment_label_clean"] = df_user["sentiment_label"].fillna("neutral").str.lower()
            total_comments = len(df_user)
            pos_count = int((df_user["sentiment_label_clean"] == "positive").sum())
            neg_count = int((df_user["sentiment_label_clean"] == "negative").sum())
            neu_count = int((df_user["sentiment_label_clean"] == "neutral").sum())
            
            pos_pct = pos_count / total_comments if total_comments > 0 else 0
            neg_pct = neg_count / total_comments if total_comments > 0 else 0
            neu_pct = neu_count / total_comments if total_comments > 0 else 0
            
            # Metrics
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.markdown(f"""
                    <div class="metric-card" style="text-align: center;">
                         <span style="font-size: 0.85rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Total Evaluated</span>
                         <h2 style="margin: 8px 0 0 0; color: #1E293B; font-size: 2rem;">{total_comments}</h2>
                    </div>
                """, unsafe_allow_html=True)
            with col_m2:
                st.markdown(f"""
                    <div class="metric-card" style="text-align: center; border-left: 5px solid #10B981;">
                         <span style="font-size: 0.85rem; color: #065F46; font-weight: 600; text-transform: uppercase;">Positive Sentiment</span>
                         <h2 style="margin: 8px 0 0 0; color: #065F46; font-size: 2rem;">{pos_count} <span style="font-size: 1rem; color: #34D399;">({pos_pct:.1%})</span></h2>
                    </div>
                """, unsafe_allow_html=True)
            with col_m3:
                st.markdown(f"""
                    <div class="metric-card" style="text-align: center; border-left: 5px solid #F59E0B;">
                         <span style="font-size: 0.85rem; color: #92400E; font-weight: 600; text-transform: uppercase;">Neutral Sentiment</span>
                         <h2 style="margin: 8px 0 0 0; color: #92400E; font-size: 2rem;">{neu_count} <span style="font-size: 1rem; color: #FBBF24;">({neu_pct:.1%})</span></h2>
                    </div>
                """, unsafe_allow_html=True)
            with col_m4:
                st.markdown(f"""
                    <div class="metric-card" style="text-align: center; border-left: 5px solid #EF4444;">
                         <span style="font-size: 0.85rem; color: #991B1B; font-weight: 600; text-transform: uppercase;">Negative Sentiment</span>
                         <h2 style="margin: 8px 0 0 0; color: #991B1B; font-size: 2rem;">{neg_count} <span style="font-size: 1rem; color: #F87171;">({neg_pct:.1%})</span></h2>
                    </div>
                """, unsafe_allow_html=True)
            
            # Time-Series Trend Visualizer
            st.markdown("### 📈 Time-Series Sentiment Trend")
            df_user["created_time_dt"] = pd.to_datetime(df_user["created_time"], errors="coerce")
            valid_times = df_user["created_time_dt"].notna()
            
            if valid_times.sum() == 0:
                st.info("🕒 No comment creation timestamps available for this session to render a time-series.")
            else:
                df_ts = df_user[valid_times].copy()
                ts_res = st.radio(
                    "Aggregation Resolution",
                    ["Hour", "Day"],
                    horizontal=True,
                    key=f"ts_res_{session['session_id']}",
                    help="Choose how comments are grouped over time"
                )
                if ts_res == "Day":
                    df_ts["time_group"] = df_ts["created_time_dt"].dt.date
                else:
                    df_ts["time_group"] = df_ts["created_time_dt"].dt.floor("h")
                    
                trend_raw = df_ts.groupby(["time_group", "sentiment_label_clean"]).size().reset_index(name="count")
                trend_pivot = trend_raw.pivot(index="time_group", columns="sentiment_label_clean", values="count").fillna(0)
                for label in ["positive", "neutral", "negative"]:
                    if label not in trend_pivot.columns:
                        trend_pivot[label] = 0.0
                trend_pivot = trend_pivot[["positive", "neutral", "negative"]]
                trend_pivot.columns = ["Positive", "Neutral", "Negative"]
                trend_pivot = trend_pivot.sort_index()
                st.line_chart(trend_pivot, use_container_width=True)
                
            # Aggregated Summaries
            col1, col2 = st.columns([1, 1])
            labels = ['Positive', 'Neutral', 'Negative']
            sizes = [pos_count, neu_count, neg_count]
            filtered_labels = [l for l, s in zip(labels, sizes) if s > 0]
            filtered_sizes = [s for s in sizes if s > 0]
            colors = ['#10B981', '#F59E0B', '#EF4444']
            filtered_colors = [c for c, s in zip(colors, sizes) if s > 0]
            
            with col1:
                st.markdown("#### Sentiment Distribution (3D-like Pie Chart)")
                if filtered_sizes:
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(figsize=(6, 5))
                    explode = [0.05] * len(filtered_sizes)
                    wedges, texts, autotexts = ax.pie(
                        filtered_sizes, 
                        explode=explode,
                        labels=filtered_labels, 
                        autopct='%1.1f%%',
                        shadow=True, 
                        startangle=140, 
                        colors=filtered_colors,
                        textprops=dict(color="#1E293B", weight="bold", size=10),
                        wedgeprops=dict(edgecolor='white', linewidth=1.5)
                    )
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontsize(11)
                    ax.axis('equal')  
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close(fig)
                else:
                    st.info("No sentiments to display.")
                    
            with col2:
                st.markdown("#### Sentiment Category Counts (Bar Chart)")
                if filtered_sizes:
                    import matplotlib.pyplot as plt
                    import seaborn as sns
                    fig_bar, ax_bar = plt.subplots(figsize=(6, 5))
                    sentiment_df = pd.DataFrame({
                        'Sentiment': filtered_labels,
                        'Count': filtered_sizes
                    })
                    sns.barplot(
                        x='Count', 
                        y='Sentiment', 
                        data=sentiment_df, 
                        palette=filtered_colors,
                        ax=ax_bar,
                        hue='Sentiment',
                        legend=False
                    )
                    ax_bar.spines['top'].set_visible(False)
                    ax_bar.spines['right'].set_visible(False)
                    ax_bar.spines['left'].set_color('#CBD5E1')
                    ax_bar.spines['bottom'].set_color('#CBD5E1')
                    ax_bar.tick_params(colors='#475569', labelsize=11)
                    ax_bar.set_ylabel('', color='#475569', fontsize=12)
                    ax_bar.set_xlabel('Count', color='#475569', fontsize=12)
                    for container in ax_bar.containers:
                        ax_bar.bar_label(container, fmt='%d', padding=5, color='#1E293B', weight='bold', fontsize=11)
                    plt.tight_layout()
                    st.pyplot(fig_bar)
                    plt.close(fig_bar)
                else:
                    st.info("No sentiments to display.")
                    
            # Preview Data Table
            st.markdown("#### Prediction Preview")
            st.dataframe(
                df_user[["comment_text", "sentiment_label_clean"]].rename(
                    columns={"comment_text": "Comment", "sentiment_label_clean": "Sentiment"}
                ),
                use_container_width=True
            )
            
            if st.button("➕ Analyze New URL", key="history_back_btn"):
                st.session_state.view_mode = "new"
                st.session_state.current_session_id = None
                st.query_params.clear()
                st.rerun()
                
        st.markdown("<div class='footer'>Low-Resource Facebook Sentiment Classifier Prototype Dashboard. Powered by Streamlit.</div>", unsafe_allow_html=True)
        st.stop()
        
    else:
        # New Analysis View
        st.markdown("### Analyze a Facebook Post or Upload CSV")
        
        # URL scrape inputs
        if "user_active_urls" not in st.session_state:
            st.session_state.user_active_urls = None
        if "user_active_file" not in st.session_state:
            st.session_state.user_active_file = None
        if "user_processing" not in st.session_state:
            st.session_state.user_processing = False
        if "trigger_user_scrape" not in st.session_state:
            st.session_state.trigger_user_scrape = False
        if "user_scrape_phase" not in st.session_state:
            st.session_state.user_scrape_phase = None
        if "user_cancel_requested" not in st.session_state:
            st.session_state.user_cancel_requested = False
            
        def _user_cancel_cleanup():
            st.session_state.trigger_user_scrape = False
            st.session_state.user_processing = False
            st.session_state.user_scrape_phase = None
            st.session_state.user_cancel_requested = False
            
        # Chat-like input for URL(s) - supports one or many, separated by comma/newline/whitespace
        if not st.session_state.user_processing and not st.session_state.get("batch_processing", False):
            prompt = st.chat_input("Paste one or more Facebook Post URLs (separate with commas)...", accept_file=True, file_type=["csv"], key="user_chat")
            if prompt:
                if prompt.text:
                    import re as _re_user_urls
                    parsed_urls = [u.strip() for u in _re_user_urls.split(r"[,\n]+|\s+", prompt.text) if u.strip()]
                    st.session_state.user_active_urls = parsed_urls or None
                    st.session_state.user_active_file = None
                if prompt.get("files"):
                    st.session_state.user_active_file = prompt["files"][0]
                    st.session_state.user_active_urls = None
                    
        if st.session_state.user_active_urls:
            if not st.session_state.user_processing:
                if len(st.session_state.user_active_urls) == 1:
                    st.markdown(f"**Target URL:** `{st.session_state.user_active_urls[0]}`")
                else:
                    st.markdown(f"**Target URLs ({len(st.session_state.user_active_urls)}):**")
                    for _u in st.session_state.user_active_urls:
                        st.markdown(f"- `{_u}`")
                u_col1, u_col2 = st.columns(2)
                with u_col1:
                    user_scrape_limit = st.number_input("Max Comments to Collect", min_value=1, max_value=500, value=50, key="user_scrape_limit")
                with u_col2:
                    user_token_path = Path("secret/token.txt")
                    default_user_token = user_token_path.read_text(encoding="utf-8").strip() if user_token_path.exists() else (os.getenv("APIFY_API_TOKEN") or "")
                    user_has_token = bool(default_user_token)
                    if user_has_token:
                        user_scrape_token = default_user_token
                    else:
                        user_scrape_token = st.text_input("Apify API Token", type="password", placeholder="Required if not pre-configured", help="Enter your Apify API token to enable scraping.", key="user_apify_token")
                        
                if st.button("Run Scrape & Analyse", type="primary", key="user_scrape_btn"):
                    if not user_scrape_token and not user_has_token:
                        st.error("Please enter your Apify API Token to proceed.")
                    else:
                        st.session_state.user_scrape_limit_val = user_scrape_limit
                        st.session_state.user_scrape_token_val = user_scrape_token if not user_has_token else default_user_token
                        st.session_state.user_processing = True
                        st.session_state.trigger_user_scrape = True
                        st.session_state.user_scrape_phase = "init"
                        st.rerun()
            else:
                st.info("Scraping and analysis in progress... Please wait.")
                if st.button("Stop Scrape", key="user_cancel_scrape", type="secondary", use_container_width=True):
                    st.session_state.user_cancel_requested = True
                    st.rerun()
                    
            # Scraper logic
            if st.session_state.trigger_user_scrape:
                phase = st.session_state.get("user_scrape_phase", "init")
                
                if phase == "init":
                    if st.session_state.get("user_cancel_requested", False):
                        st.warning("Scrape cancelled.")
                        _user_cancel_cleanup()
                        st.rerun()
                    st.session_state.user_scrape_phase = "scraping"
                    st.rerun()
                    
                elif phase == "scraping":
                    if st.session_state.get("user_cancel_requested", False):
                        st.warning("Scrape cancelled.")
                        _user_cancel_cleanup()
                        st.rerun()
                    user_scrape_limit_val = st.session_state.user_scrape_limit_val
                    user_scrape_token_val = st.session_state.user_scrape_token_val
                    user_urls_val = st.session_state.user_active_urls
                    from src.collect_apify import collect_facebook_comments
                    n_urls = len(user_urls_val)
                    spinner_msg = (
                        "Scraping comments from Facebook via Apify... (this may take a minute)"
                        if n_urls == 1
                        else f"Scraping {n_urls} Facebook posts in parallel via Apify... (this may take a minute)"
                    )
                    with st.spinner(spinner_msg):
                        try:
                            # Passing all URLs in a single startUrls list lets the Apify actor
                            # crawl them concurrently instead of one run per URL.
                            collected_df = collect_facebook_comments(urls=user_urls_val, limit=user_scrape_limit_val, token=user_scrape_token_val, mode="sync")
                            st.session_state.user_collected_df = collected_df
                            st.success(f"[OK] Scraped {len(collected_df)} comments from {n_urls} URL(s)!")
                        except Exception as e:
                            st.error(f"[ERR] Scraping failed: {e}")
                            st.session_state.user_collected_df = None
                    st.session_state.user_scrape_phase = "predicting"
                    st.rerun()
                    
                elif phase == "predicting":
                    if st.session_state.get("user_cancel_requested", False):
                        st.warning("Predicting cancelled.")
                        _user_cancel_cleanup()
                        st.rerun()
                    collected_df = st.session_state.get("user_collected_df")
                    if collected_df is not None:
                        from src.evaluate_external import transform_with_saved_vectorizer
                        from src.preprocess import clean_text
                        from src.database import save_analysis
                        with st.spinner("Running sentiment predictions..."):
                            try:
                                df_user = collected_df.copy()
                                df_user["cleaned_text"] = df_user["text"].apply(clean_text)
                                if baseline_model is not None:
                                    X = transform_with_saved_vectorizer(baseline_vec, df_user["cleaned_text"])
                                    preds = baseline_model.predict(X)
                                    df_user["predicted_sentiment"] = preds
                                else:
                                    df_user["predicted_sentiment"] = "neutral"
                                    
                                # Save using new save_analysis (join multiple source URLs for the session record)
                                session = save_analysis(
                                    user_id=st.session_state.user_id,
                                    url=", ".join(st.session_state.user_active_urls),
                                    df=df_user
                                )
                                st.session_state.current_session_id = session["session_id"]
                                st.session_state.view_mode = "history"
                                st.session_state.user_active_urls = None
                                st.query_params["session_id"] = str(session["session_id"])
                                st.success("Analysis saved to database!")
                            except Exception as e:
                                st.error(f"[ERR] Error during predictions: {e}")
                    st.session_state.trigger_user_scrape = False
                    st.session_state.user_processing = False
                    st.session_state.user_scrape_phase = None
                    st.session_state.user_cancel_requested = False
                    if "user_collected_df" in st.session_state:
                        del st.session_state.user_collected_df
                    st.rerun()
                    
        elif st.session_state.user_active_file:
            # Batch CSV upload flow
            st.markdown(f"**Loaded CSV:** `{st.session_state.user_active_file.name}`")
            try:
                df = pd.read_csv(st.session_state.user_active_file)
                text_cols = [c for c in df.columns if any(x in c.lower() for x in ["text", "comment", "body"])]
                text_column = st.selectbox("Select Comment Column", df.columns, index=df.columns.get_loc(text_cols[0]) if text_cols else 0)
                
                if st.button("Run Batch Prediction"):
                    with st.spinner("Processing batch..."):
                        from src.preprocess import clean_text
                        from src.evaluate_external import transform_with_saved_vectorizer
                        from src.database import save_analysis
                        
                        df_run = df.copy()
                        df_run["cleaned_text"] = df_run[text_column].apply(clean_text)
                        if baseline_model is not None:
                            X_batch = transform_with_saved_vectorizer(baseline_vec, df_run["cleaned_text"])
                            predictions = baseline_model.predict(X_batch)
                            df_run["predicted_sentiment"] = predictions
                        else:
                            df_run["predicted_sentiment"] = "neutral"
                            
                        # Save
                        session = save_analysis(
                            user_id=st.session_state.user_id,
                            url="CSV Upload: " + st.session_state.user_active_file.name,
                            df=df_run
                        )
                        st.session_state.current_session_id = session["session_id"]
                        st.session_state.view_mode = "history"
                        st.session_state.user_active_file = None
                        st.query_params["session_id"] = str(session["session_id"])
                        st.rerun()
            except Exception as e:
                st.error(f"Error loading CSV file: {e}")
                
            if st.button("Clear CSV"):
                st.session_state.user_active_file = None
                st.rerun()
                

        st.markdown("<div class='footer'>Low-Resource Facebook Sentiment Classifier Prototype Dashboard. Powered by Streamlit.</div>", unsafe_allow_html=True)
        st.stop()

# Below is only accessible to verified Developers
tab_live, tab_analysis_scrape, tab_metrics, tab_controls, tab_db = st.tabs([
    "Live Sentiment Classifier",
    "Web Scraper & Batch Analysis",
    "Performance Dashboard",
    "Pipeline & Control Panel",
    "Database Logs"
])

# ----------------- Tab 1: Live Sentiment Classifier -----------------
with tab_live:
    st.markdown("### Single Comment Sentiment Checker")
    st.write("Type a Facebook comment (English, Chichewa, or code-switched) to predict its sentiment.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        text_input = st.text_area(
            "Enter Comment Text", 
            placeholder="Type your comment here... e.g., 'Zikomo kwambiri boma lathu for this development!'"
        )
        
        # Model selector
        available_options = []
        if baseline_model is not None:
            available_options.append("TF-IDF Baseline")
        for t in transformers:
            available_options.append(f"Transformer ({t})")
            
        if not available_options:
            st.error("No models are currently available. Please train the baseline model first.")
            model_choice = None
        else:
            model_choice = st.selectbox("Select Classification Model", available_options)
            
        submit_btn = st.button("Classify Sentiment", disabled=(model_choice is None or not text_input))
        
    with col2:
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        if submit_btn and text_input and model_choice:
            # Clean text
            from src.preprocess import clean_text
            cleaned = clean_text(text_input)
            
            st.markdown("#### Input Text Preprocessing")
            st.markdown(f"**Cleaned Text:** *`{cleaned}`*")
            
            with st.spinner("Classifying..."):
                pred_label = None
                probs = None
                classes = ["negative", "neutral", "positive"]
                
                try:
                    if model_choice == "TF-IDF Baseline":
                        from src.evaluate_external import transform_with_saved_vectorizer
                        X = transform_with_saved_vectorizer(baseline_vec, pd.Series([cleaned]))
                        pred_label = baseline_model.predict(X)[0]
                        if hasattr(baseline_model, "predict_proba"):
                            probs = baseline_model.predict_proba(X)[0]
                    else:
                        # Transformer model loading
                        run_id = model_choice.replace("Transformer (", "").rstrip(")")
                        t_model, t_tokenizer = load_transformer_model(run_id)
                        
                        import torch
                        inputs = t_tokenizer(cleaned, return_tensors="pt", truncation=True, max_length=128)
                        with torch.no_grad():
                            outputs = t_model(**inputs)
                            logits = outputs.logits.numpy()[0]
                            # Softmax
                            exp_logits = np.exp(logits - np.max(logits))
                            probs = exp_logits / exp_logits.sum()
                            pred_idx = np.argmax(probs)
                            # map idx to label
                            id_to_label = getattr(t_model.config, "id2label", {0: "negative", 1: "neutral", 2: "positive"})
                            pred_label = id_to_label[pred_idx].lower()
                            
                    # Display Results
                    st.markdown("#### Classification Result")
                    
                    if pred_label == "positive":
                        st.markdown("<span class='badge badge-positive'>POSITIVE</span>", unsafe_allow_html=True)
                    elif pred_label == "negative":
                        st.markdown("<span class='badge badge-negative'>NEGATIVE</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span class='badge badge-neutral'>NEUTRAL</span>", unsafe_allow_html=True)
                        
                    if probs is not None:
                        st.write("Confidence Breakdown:")
                        for c_label, prob in zip(classes, probs):
                            st.markdown(f"**{c_label.capitalize()}:** {prob:.2%}")
                            st.progress(float(prob))

                    # ── DB Integration: Save Prediction ──
                    try:
                        import uuid
                        from src.db.comments import insert_comment
                        from src.db.preprocess import insert_preprocessed
                        from src.db.predictions import insert_prediction
                        from src.db.activity import log_action

                        c_id = str(uuid.uuid4())
                        # Save the raw comment
                        insert_comment(
                            comment_id=c_id, 
                            comment_text=text_input, 
                            source_url="dashboard", 
                            collection_source="dashboard"
                        )
                        # Save the preprocessed text
                        insert_preprocessed(comment_id=c_id, cleaned_text=cleaned)

                        # Parse out scores safely
                        conf = float(np.max(probs)) if probs is not None else 1.0
                        s_neg = float(probs[0]) if probs is not None else (1.0 if pred_label == "negative" else 0.0)
                        s_neu = float(probs[1]) if probs is not None else (1.0 if pred_label == "neutral" else 0.0)
                        s_pos = float(probs[2]) if probs is not None else (1.0 if pred_label == "positive" else 0.0)

                        fam = "transformer" if "Transformer" in model_choice else "classical_ml"
                        # Extract the actual version id if transformer
                        ver = run_id if fam == "transformer" else "baseline"

                        # Save the prediction result
                        p_id = insert_prediction(
                            comment_id=c_id,
                            predicted_label=pred_label,
                            predicted_confidence=conf,
                            score_negative=s_neg,
                            score_neutral=s_neu,
                            score_positive=s_pos,
                            model_name=model_choice,
                            model_version=ver,
                            model_family=fam
                        )
                        
                        # Log the activity
                        log_action(
                            user_id=None, 
                            action_type="predict", 
                                comment_id=c_id, 
                            details={"source": "dashboard", "prediction_id": p_id}
                        )
                        st.success("[OK] Prediction successfully saved to the database!")
                    except Exception as db_err:
                        st.warning(f"[WARN] Prediction succeeded, but couldn't save to Database (Is the DB running?). Error: {db_err}")
                            
                except Exception as e:
                    st.error(f"Error during prediction: {e}")
                    
# ----------------- Tab 2: Web Scraper & Batch Analysis -----------------
with tab_analysis_scrape:
    st.subheader("Web Scraper & Batch Analysis")
    if "dev_active_url" not in st.session_state:
        st.session_state.dev_active_url = None
    if "dev_active_file" not in st.session_state:
        st.session_state.dev_active_file = None
    if "dev_processing" not in st.session_state:
        st.session_state.dev_processing = False
    if "trigger_dev_scrape" not in st.session_state:
        st.session_state.trigger_dev_scrape = False
    if "dev_scrape_results" not in st.session_state:
        st.session_state.dev_scrape_results = None
    if "dev_cancel_requested" not in st.session_state:
        st.session_state.dev_cancel_requested = False
    if "dev_scrape_phase" not in st.session_state:
        st.session_state.dev_scrape_phase = None
        
    def _dev_cancel_cleanup():
        st.session_state.trigger_dev_scrape = False
        st.session_state.dev_processing = False
        st.session_state.dev_scrape_phase = None
        st.session_state.dev_cancel_requested = False
        
    # Render chat input if not processing
    if not st.session_state.dev_processing and not st.session_state.get("batch_processing", False):
        prompt = st.chat_input("Paste Facebook Post URL here...", accept_file=True, file_type=["csv"], key="dev_chat")
        if prompt:
            if prompt.text:
                st.session_state.dev_active_url = prompt.text
                st.session_state.dev_active_file = None
                st.session_state.batch_df = None
                st.session_state.dev_scrape_results = None
            if prompt.get("files"):
                st.session_state.dev_active_file = prompt["files"][0]
                st.session_state.dev_active_url = None
                st.session_state.batch_df = None
                st.session_state.dev_scrape_results = None

    if st.session_state.dev_active_url:
        if not st.session_state.dev_processing:
            st.markdown(f"**Target URL:** `{st.session_state.dev_active_url}`")
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                scrape_limit = st.number_input("Max Comments to Scrape", min_value=1, max_value=1000, value=50)
            with col_s2:
                token_path = Path("secret/token.txt")
                default_token = token_path.read_text(encoding="utf-8").strip() if token_path.exists() else (os.getenv("APIFY_API_TOKEN") or "")
                has_token_file = bool(default_token)
                if has_token_file:
                    scrape_token = default_token
                else:
                    scrape_token = st.text_input("Apify API Token", type="password", placeholder="Required if not set in environment")
            with col_s3:
                available_options = []
                if baseline_model is not None:
                    available_options.append("TF-IDF Baseline")
                for t in transformers:
                    available_options.append(f"Transformer ({t})")
                scrape_model = st.selectbox("Classification Model", available_options, key="scrape_model_sel") if available_options else None

            if st.button("Run Scrape & Predict", type="primary", disabled=(scrape_model is None)):
                if not scrape_token and not has_token_file:
                    st.error("Missing Apify API Token. Please enter one above.")
                else:
                    st.session_state.dev_scrape_limit_val = scrape_limit
                    st.session_state.dev_scrape_token_val = scrape_token
                    st.session_state.dev_scrape_model_val = scrape_model
                    st.session_state.dev_processing = True
                    st.session_state.trigger_dev_scrape = True
                    st.session_state.dev_scrape_phase = "init"
                    st.rerun()
        else:
            st.info("Scraping and analysis in progress... Please wait.")
            if st.button("Stop Stop", key="dev_cancel_scrape", type="secondary", use_container_width=True):
                st.session_state.dev_cancel_requested = True
                st.rerun()

        if st.session_state.trigger_dev_scrape:
            phase = st.session_state.get("dev_scrape_phase", "init")
            
            if phase == "init":
                if st.session_state.get("dev_cancel_requested", False):
                    st.warning("Stop Operation cancelled.")
                    _dev_cancel_cleanup()
                    st.rerun()
                st.session_state.dev_scrape_phase = "scraping"
                st.rerun()
            
            elif phase == "scraping":
                if st.session_state.get("dev_cancel_requested", False):
                    st.warning("Stop Operation cancelled.")
                    _dev_cancel_cleanup()
                    st.rerun()
                scrape_limit_val = st.session_state.dev_scrape_limit_val
                scrape_token_val = st.session_state.dev_scrape_token_val
                from src.collect_apify import collect_facebook_comments
                with st.spinner("Scraping comments from Facebook using Apify... (this may take a minute)"):
                    try:
                        collected_df = collect_facebook_comments(urls=[st.session_state.dev_active_url], limit=scrape_limit_val, token=scrape_token_val, mode="sync")
                        st.session_state.dev_collected_df = collected_df
                        st.success(f"[OK] Successfully scraped {len(collected_df)} comments!")
                    except Exception as e:
                        st.error(f"Scraping failed: {e}")
                        st.session_state.dev_collected_df = None
                st.session_state.dev_scrape_phase = "saving"
                st.rerun()
            
            elif phase == "saving":
                if st.session_state.get("dev_cancel_requested", False):
                    st.warning("Stop Operation cancelled.")
                    _dev_cancel_cleanup()
                    st.rerun()
                collected_df = st.session_state.get("dev_collected_df")
                if collected_df is not None:
                    from src.collect_apify import persist_collected_comments_to_db
                    with st.spinner("Saving raw and preprocessed comments to database..."):
                        try:
                            persist_collected_comments_to_db(collected_df)
                        except Exception as e:
                            st.error(f"Error saving to database: {e}")
                st.session_state.dev_scrape_phase = "predicting"
                st.rerun()
            
            elif phase == "predicting":
                if st.session_state.get("dev_cancel_requested", False):
                    st.warning("Stop Operation cancelled.")
                    _dev_cancel_cleanup()
                    st.rerun()
                collected_df = st.session_state.get("dev_collected_df")
                scrape_model_val = st.session_state.dev_scrape_model_val
                if collected_df is not None:
                    from src.db.predictions import insert_prediction
                    from src.db.activity import log_action
                    with st.spinner(f"Running predictions using {scrape_model_val}..."):
                        try:
                            df_run = collected_df.copy()
                            
                            if scrape_model_val == "TF-IDF Baseline":
                                from src.evaluate_external import transform_with_saved_vectorizer
                                X_batch = transform_with_saved_vectorizer(baseline_vec, df_run["cleaned_text"])
                                if hasattr(baseline_model, "predict_proba"):
                                    probs = baseline_model.predict_proba(X_batch)
                                elif hasattr(baseline_model, "decision_function"):
                                    from scipy.special import softmax
                                    dec = baseline_model.decision_function(X_batch)
                                    if len(dec.shape) == 1 or dec.shape[1] == 1:
                                        dec = np.column_stack([-dec, dec])
                                    probs = softmax(dec, axis=1)
                                else:
                                    probs = None
                                preds = baseline_model.predict(X_batch)
                            else:
                                import torch
                                from scipy.special import softmax
                                run_id = scrape_model_val.replace("Transformer (", "").rstrip(")")
                                t_model, t_tokenizer = load_transformer_model(run_id)
                                id_to_label = getattr(t_model.config, "id2label", {0: "negative", 1: "neutral", 2: "positive"})
                                probs_list = []
                                preds = []
                                batch_size = 16
                                texts = df_run["cleaned_text"].tolist()
                                for i in range(0, len(texts), batch_size):
                                    batch_texts = texts[i:i+batch_size]
                                    inputs = t_tokenizer(batch_texts, return_tensors="pt", padding=True, truncation=True, max_length=128)
                                    with torch.no_grad():
                                        logits = t_model(**inputs).logits.numpy()
                                        p = softmax(logits, axis=1)
                                        probs_list.append(p)
                                        pred_idx = np.argmax(logits, axis=1)
                                        preds.extend([id_to_label[idx].lower() for idx in pred_idx])
                                probs = np.vstack(probs_list)
                                
                            df_run["predicted_sentiment"] = preds
                            fam = "transformer" if "Transformer" in scrape_model_val else "classical_ml"
                            ver = run_id if fam == "transformer" else "baseline"
                            classes = getattr(baseline_model, "classes_", ["negative", "neutral", "positive"]) if fam == "classical_ml" else ["negative", "neutral", "positive"]
                            
                            saved_preds = 0
                            for idx, row in df_run.iterrows():
                                c_id = str(row.get("comment_id")) if pd.notna(row.get("comment_id")) else f"apify_{row.get('apify_dataset_id', 'dataset')}_{row.get('apify_run_id', 'run')}_{row.get('id', idx+1)}"
                                p_label = row["predicted_sentiment"]
                                conf = 1.0
                                s_neg, s_neu, s_pos = 0.0, 0.0, 0.0
                                if probs is not None:
                                    p_row = probs[idx]
                                    conf = float(np.max(p_row))
                                    if fam == "classical_ml":
                                        s_neg = float(p_row[list(classes).index("negative")]) if "negative" in classes else 0.0
                                        s_neu = float(p_row[list(classes).index("neutral")]) if "neutral" in classes else 0.0
                                        s_pos = float(p_row[list(classes).index("positive")]) if "positive" in classes else 0.0
                                    else:
                                        id2l = getattr(t_model.config, "id2label", {0: "negative", 1: "neutral", 2: "positive"})
                                        l2id = {v.lower(): k for k, v in id2l.items()}
                                        s_neg = float(p_row[l2id.get("negative", 0)])
                                        s_neu = float(p_row[l2id.get("neutral", 1)])
                                        s_pos = float(p_row[l2id.get("positive", 2)])
                                try:
                                    insert_prediction(comment_id=c_id, predicted_label=p_label, predicted_confidence=conf, score_negative=s_neg, score_neutral=s_neu, score_positive=s_pos, model_name=scrape_model_val, model_version=ver, model_family=fam)
                                    log_action(user_id=None, action_type="predict", comment_id=c_id, details={"source": "apify_scrape"})
                                    saved_preds += 1
                                except Exception:
                                    pass
                            
                            st.session_state.dev_scrape_results = (df_run, saved_preds)
                        except Exception as e:
                            st.error(f"Error during predictions: {e}")
                st.session_state.trigger_dev_scrape = False
                st.session_state.dev_processing = False
                st.session_state.dev_scrape_phase = None
                st.session_state.dev_cancel_requested = False
                if "dev_collected_df" in st.session_state:
                    del st.session_state.dev_collected_df
                st.rerun()

        if st.session_state.dev_scrape_results is not None:
            df_run, saved_preds = st.session_state.dev_scrape_results
            st.success(f"[OK] Predicted and saved {saved_preds} comments to the database!")
            
            pos_count = int((df_run["predicted_sentiment"] == "positive").sum())
            neg_count = int((df_run["predicted_sentiment"] == "negative").sum())
            neu_count = int((df_run["predicted_sentiment"] == "neutral").sum())
            total_count = len(df_run)
            
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Total", total_count)
            r2.metric("Positive", pos_count)
            r3.metric("Negative", neg_count)
            r4.metric("Neutral", neu_count)
            
            labels_chart = ['Positive', 'Neutral', 'Negative']
            sizes_chart  = [pos_count, neu_count, neg_count]
            colors_chart = ['#10B981', '#F59E0B', '#EF4444']
            filtered_labels_c = [l for l, s in zip(labels_chart, sizes_chart) if s > 0]
            filtered_sizes_c  = [s for s in sizes_chart if s > 0]
            filtered_colors_c = [c for c, s in zip(colors_chart, sizes_chart) if s > 0]
            
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.markdown("#### Sentiment Distribution")
                if filtered_sizes_c:
                    import matplotlib.pyplot as plt
                    fig_pie_d, ax_pie_d = plt.subplots(figsize=(5, 4))
                    explode_d = [0.05] * len(filtered_sizes_c)
                    wedges_d, texts_d, autotexts_d = ax_pie_d.pie(
                        filtered_sizes_c, explode=explode_d, labels=filtered_labels_c,
                        autopct='%1.1f%%', shadow=True, startangle=140, colors=filtered_colors_c,
                        textprops=dict(color="#1E293B", weight="bold", size=10),
                        wedgeprops=dict(edgecolor='white', linewidth=1.5)
                    )
                    for at_d in autotexts_d:
                        at_d.set_color('white')
                        at_d.set_fontsize(11)
                    ax_pie_d.axis('equal')
                    plt.tight_layout()
                    st.pyplot(fig_pie_d)
                    plt.close(fig_pie_d)
                else:
                    st.info("No sentiments to display.")
            with chart_col2:
                st.markdown("#### Sentiment Counts")
                if filtered_sizes_c:
                    import matplotlib.pyplot as plt
                    import seaborn as sns
                    fig_bar_d, ax_bar_d = plt.subplots(figsize=(5, 4))
                    sentiment_df_d = pd.DataFrame({'Sentiment': filtered_labels_c, 'Count': filtered_sizes_c})
                    sns.barplot(x='Count', y='Sentiment', data=sentiment_df_d,
                        palette=filtered_colors_c, ax=ax_bar_d, hue='Sentiment', legend=False)
                    ax_bar_d.spines['top'].set_visible(False)
                    ax_bar_d.spines['right'].set_visible(False)
                    ax_bar_d.spines['left'].set_color('#CBD5E1')
                    ax_bar_d.spines['bottom'].set_color('#CBD5E1')
                    ax_bar_d.tick_params(colors='#475569', labelsize=11)
                    ax_bar_d.set_ylabel('', color='#475569', fontsize=12)
                    ax_bar_d.set_xlabel('Count', color='#475569', fontsize=12)
                    for container in ax_bar_d.containers:
                        ax_bar_d.bar_label(container, fmt='%d', padding=5, color='#1E293B', weight='bold', fontsize=11)
                    plt.tight_layout()
                    st.pyplot(fig_bar_d)
                    plt.close(fig_bar_d)
                else:
                    st.info("No sentiments to display.")
            
            st.markdown("#### Scraped Results")
            st.dataframe(df_run[["text", "cleaned_text", "predicted_sentiment"]].head(100), use_container_width=True)
            
            if st.button("Clear Clear Results & Start New Scrape", key="dev_clear_results_btn"):
                st.session_state.dev_active_url = None
                st.session_state.dev_scrape_results = None
                st.rerun()

    elif st.session_state.dev_active_file:
        render_batch_analysis(baseline_model, baseline_vec, transformers, paths, st.session_state.dev_active_file, is_developer=True)
        if st.button("Clear CSV"):
            st.session_state.dev_active_file = None
            st.session_state.batch_df = None
            st.rerun()

# ----------------- Tab 4: Performance Dashboard -----------------
with tab_metrics:
    st.markdown("### Performance Dashboard & Model Comparison")
    st.write("Compare trained models across validation and test splits using metrics and confusion matrices.")
    
    compare_path = paths.results_dir / "model_comparison.csv"
    if compare_path.exists():
        compare_df = pd.read_csv(compare_path)
        
        # Extract best model
        best_row = compare_df.sort_values(by="macro_f1", ascending=False).iloc[0]
        st.success(
            f"**Top Model:** `{best_row['model_name']}` ({best_row['model_family']}) "
            f"with **Macro F1 of {best_row['macro_f1']:.4f}** and **Accuracy of {best_row['accuracy']:.4f}** "
            f"on the `{best_row['split']}` split."
        )
        
        st.markdown("#### Model Rankings & Metrics")
        
        # 1. Graphical Metrics Table
        presentation_df = compare_df.copy()
        presentation_df = presentation_df.sort_values(by=["split", "macro_f1"], ascending=[True, False])
        
        family_map = {
            "classical_ml": "Classical ML",
            "transformer": "Transformer"
        }
        presentation_df["model_family"] = presentation_df["model_family"].map(family_map).fillna(presentation_df["model_family"])
        
        presentation_df = presentation_df.rename(columns={
            "model_family": "Family",
            "model_name": "Model Name",
            "feature_set": "Feature Set",
            "split": "Split",
            "macro_f1": "Macro F1",
            "accuracy": "Accuracy",
            "weighted_f1": "Weighted F1"
        })
        presentation_df = presentation_df.drop(columns=["source_file"], errors="ignore")
        
        st.dataframe(
            presentation_df,
            column_config={
                "Family": st.column_config.TextColumn("Family", width="medium"),
                "Model Name": st.column_config.TextColumn("Model Name", width="medium"),
                "Feature Set": st.column_config.TextColumn("Feature Set", width="small"),
                "Split": st.column_config.TextColumn("Split", width="small"),
                "Macro F1": st.column_config.NumberColumn(
                    "Macro F1 Score",
                    help="Macro-averaged F1 Score",
                    format="%.4f",
                ),
                "Accuracy": st.column_config.NumberColumn(
                    "Accuracy Score",
                    help="Overall classification accuracy",
                    format="%.4f",
                ),
                "Weighted F1": st.column_config.NumberColumn(
                    "Weighted F1 Score",
                    help="Weighted-averaged F1 Score",
                    format="%.4f",
                ),
            },
            use_container_width=True,
            hide_index=True
        )
        
        # 2. Performance Comparison Bar Chart
        st.markdown("#### F1-Score Performance Comparison")
        chart_df = compare_df.copy()
        chart_df["Model (Split)"] = chart_df["model_name"] + " (" + chart_df["split"] + ")"
        chart_df = chart_df.sort_values(by="macro_f1", ascending=True)
        
        st.bar_chart(
            data=chart_df,
            x="Model (Split)",
            y="macro_f1",
            color="model_family",
            use_container_width=True
        )
            
    else:
        st.info("No model comparisons (`model_comparison.csv`) found. Run model training scripts first.")
        
    st.markdown("#### Model Confusion Matrices")
    
    fig_cols = st.columns(3)
    fig_types = [
        ("Baseline Internal Test", paths.figures_dir / "baseline_confusion_matrix.png"),
        ("Baseline External Test", paths.figures_dir / "external_baseline_confusion_matrix.png"),
        ("Transformer Internal Test", paths.figures_dir / "transformer_confusion_matrix.png")
    ]
    
    for col, (title, path) in zip(fig_cols, fig_types):
        with col:
            st.markdown(f"**{title}**")
            if path.exists():
                st.image(str(path), width='stretch')
            else:
                st.warning("Confusion matrix not generated yet.")
                
# ----------------- Tab 5: Pipeline & Control Panel -----------------
with tab_controls:
    st.markdown("### Pipeline Control Panel")
    st.markdown(
        "Follow the pipeline steps in order: upload raw data, preprocess, train a baseline model, "
        "then optionally fine-tune a transformer."
    )

    # ── Step 1: Upload Raw Data ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        """
        <div class='metric-card'>
            <h4>Step 1: Upload Raw Training Data</h4>
            <p style='color:#64748B;'>Upload a new CSV file with raw comments to add to the training pool.
            The file will be saved to <code>data/raw/</code> so the pipeline can consume it.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_raw_files = st.file_uploader(
        "Upload Raw CSV Files (select one or more)",
        type=["csv"],
        accept_multiple_files=True,
        key="raw_data_uploader",
        help="Upload one or more CSV files with raw comments."
    )

    if uploaded_raw_files:
        st.markdown(f"**{len(uploaded_raw_files)} file(s) selected:**")
        all_preview_dfs = {}
        for uf in uploaded_raw_files:
            try:
                df_preview = pd.read_csv(uf)
                all_preview_dfs[uf.name] = df_preview
                with st.expander(f"{uf.name} \u2014 {len(df_preview)} rows \u00b7 {len(df_preview.columns)} cols"):
                    st.dataframe(df_preview.head(5), use_container_width=True)
            except Exception as e:
                st.error(f"Could not read `{uf.name}`: {e}")

        if all_preview_dfs:
            st.markdown("---")
            save_col1, save_col2 = st.columns([1, 1])
            with save_col1:
                if st.button("Save All Files to data/raw/", key="save_raw_btn", use_container_width=True):
                    saved = []
                    for fname, fdf in all_preview_dfs.items():
                        fdf.to_csv(paths.raw_dir / fname, index=False, encoding="utf-8")
                        saved.append(fname)
                    st.success(f"[OK] Saved {len(saved)} file(s) to `data/raw/`: {', '.join(saved)}")

            with save_col2:
                if st.button("Run Save & Retrain (Baseline)", type="primary", key="retrain_baseline_btn", use_container_width=True):
                    for fname, fdf in all_preview_dfs.items():
                        fdf.to_csv(paths.raw_dir / fname, index=False, encoding="utf-8")
                    st.info(f"[OK] Saved {len(all_preview_dfs)} file(s). Starting retraining pipeline \u2026")

                    with st.spinner("Step 2/4 \u2014 Running Preprocessing \u2026"):
                        ret_code, stdout, stderr = run_script("src.preprocess")
                        if ret_code != 0:
                            st.error(f"[ERR] Preprocessing failed:\n{stderr[:500]}")
                            st.stop()
                        st.success("[OK] Preprocessing complete!")

                    with st.spinner("Step 3/4 \u2014 Training Baseline Models \u2026"):
                        ret_code, stdout, stderr = run_script("src.train_baseline")
                        if ret_code == 0:
                            run_script("src.compare_models")
                            st.success("[OK] Baseline retraining complete! Models have been updated.")
                            with st.expander("View Training Log"):
                                st.text(stdout[-3000:] if stdout else "(no output)")
                            st.balloons()
                        else:
                            st.error(f"[ERR] Training failed:\n{stderr[:500]}")

    # ── Step 2: Run Preprocessing ───────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        """
        <div class='metric-card'>
            <h4>Step 2: Run Preprocessing Pipeline</h4>
            <p style='color:#64748B;'>Reads raw csv comments from <code>data/raw/</code>, normalizes labels,
            filters noise, deduplicates, and splits data into train/val/test CSVs.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    run_prep = st.button("Run Preprocessing", key="run_prep_btn", use_container_width=True)
    if run_prep:
        with st.spinner("Executing Preprocessing..."):
            ret_code, stdout, stderr = run_script("src.preprocess")
            if ret_code == 0:
                st.success("Preprocessing executed successfully!")
                with st.expander("View Preprocessing Log"):
                    st.text(stdout[-3000:] if stdout else "(no output)")
            else:
                st.error(f"Preprocessing failed with exit code: {ret_code}")
                with st.expander("View Error Log"):
                    st.text(stderr[-3000:] if stderr else "(no output)")

    # ── Step 3: Train Baseline Models ───────────────────────────────────────
    st.markdown("---")
    st.markdown(
        """
        <div class='metric-card'>
            <h4>Step 3: Train Baseline Models</h4>
            <p style='color:#64748B;'>Trains Logistic Regression, SVM, and Naive Bayes on the processed splits,
            compares TF-IDF features, and saves the best baseline model.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    run_baseline = st.button("Run Train Baseline Models", key="run_baseline_btn", use_container_width=True)
    if run_baseline:
        with st.spinner("Training models (takes a few seconds)..."):
            ret_code, stdout, stderr = run_script("src.train_baseline")
            if ret_code == 0:
                run_script("src.compare_models")
                st.success("Baseline training completed! Best model saved and comparison updated.")
                with st.expander("View Training Log"):
                    st.text(stdout[-3000:] if stdout else "(no output)")
            else:
                st.error(f"Baseline training failed with exit code: {ret_code}")
                with st.expander("View Error Log"):
                    st.text(stderr[-3000:] if stderr else "(no output)")

    # ── Step 4: Fine-tune Transformer ───────────────────────────────────────
    st.markdown("---")
    st.markdown(
        """
        <div class='metric-card'>
            <h4>Step 4: Fine-tune a Transformer</h4>
            <p style='color:#64748B;'>Fine-tune a Hugging Face transformer on the preprocessed training data.
            Requires preprocessing to have been run first. Training can take several minutes.
            The default model is <code>castorini/afriberta_small</code> which works well for
            code-switched African language text.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    trans_col1, trans_col2 = st.columns(2)
    with trans_col1:
        transformer_model_name = st.text_input(
            "Hugging Face Model ID",
            value="castorini/afriberta_small",
            key="transformer_model_name_input",
            help="Enter a Hugging Face model ID (e.g. castorini/afriberta_small, bert-base-multilingual-cased)."
        )
    with trans_col2:
        transformer_run_name = st.text_input(
            "Run Name (optional)",
            value="",
            placeholder="e.g. afriberta_v2",
            key="transformer_run_name_input",
            help="Optional short name for this training run. Used to label saved model files."
        )

    trans_train_args = ["--model_name", transformer_model_name]
    if transformer_run_name.strip():
        trans_train_args += ["--run_name", transformer_run_name.strip()]

    if st.button("Start Transformer Training", type="primary", key="train_transformer_btn", use_container_width=True):
        with st.spinner(f"Fine-tuning `{transformer_model_name}` \u2026 This may take several minutes."):
            ret_code, stdout, stderr = run_script("src.train_transformer", trans_train_args)
            if ret_code == 0:
                run_script("src.compare_models")
                st.success("[OK] Transformer training complete! Model is now available for inference.")
                with st.expander("View Training Log"):
                    st.text(stdout[-3000:] if stdout else "(no output)")
                st.balloons()
            else:
                st.error(f"[ERR] Transformer training failed (exit code {ret_code}).")
                with st.expander("View Error Log"):
                    st.text(stderr[-3000:] if stderr else "(no output)")

# ----------------- Tab 6: Database Logs -----------------
with tab_db:
    st.markdown("### Database Logs")
    st.write("View recent predictions saved to the PostgreSQL database.")
    
    col_db1, col_db2 = st.columns([4, 1])
    with col_db1:
        st.info("**Tip**: When you classify a single comment in the 'Live Sentiment Classifier' tab, it is automatically saved to the database and will appear here.")
    with col_db2:
        if st.button("Refresh Data", use_container_width=True):
            pass # Button natively reruns the app and fetches fresh data
            
    try:
        from src.db.predictions import fetch_predictions_with_comments
        db_rows = fetch_predictions_with_comments()
        
        if not db_rows:
            st.warning("No records found in the database. Go to the 'Live Sentiment Classifier' tab and test a comment!")
        else:
            db_df = pd.DataFrame(db_rows)
            # Reorder and format columns for display
            display_cols = ["predicted_at", "comment_text", "cleaned_text", "predicted_label", "predicted_confidence", "model_name"]
            st.dataframe(
                db_df[display_cols].sort_values(by="predicted_at", ascending=False), 
                use_container_width=True,
                column_config={
                    "predicted_at": st.column_config.DatetimeColumn("Predicted At", format="MMM D, h:mm a"),
                    "comment_text": "Original Comment",
                    "cleaned_text": "Cleaned Text",
                    "predicted_label": "Sentiment",
                    "predicted_confidence": st.column_config.NumberColumn("Confidence", format="%.2f"),
                    "model_name": "Model Used"
                }
            )
            
            # Simple db metrics
            st.markdown("#### Database Summary")
            t_col1, t_col2, t_col3 = st.columns(3)
            t_col1.metric("Total Records Saved", len(db_df))
            
            pos_db = sum(db_df["predicted_label"] == "positive")
            neg_db = sum(db_df["predicted_label"] == "negative")
            neu_db = sum(db_df["predicted_label"] == "neutral")
            
            t_col2.metric("Most Common Sentiment", db_df["predicted_label"].mode()[0].capitalize() if not db_df.empty else "N/A")
            t_col3.markdown(f"<span style='color:#10B981;font-weight:bold;'>{pos_db} Pos</span> | <span style='color:#EF4444;font-weight:bold;'>{neg_db} Neg</span> | <span style='color:#F59E0B;font-weight:bold;'>{neu_db} Neu</span>", unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Failed to connect to the database or fetch records. Error: {e}")

st.markdown(
    """
    <div class='footer'>
        Low-Resource Facebook Sentiment Classifier Prototype Dashboard. Powered by Streamlit.
    </div>
    """,
    unsafe_allow_html=True
)