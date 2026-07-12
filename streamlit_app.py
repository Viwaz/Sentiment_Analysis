import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import os
from src.db.users import create_user, authenticate_user
import subprocess
import time
import re
from urllib.parse import urlparse
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

    /* ── Fix: wrapper around the input + show/hide-password eye icon ──
       The input element above is painted white, but its parent
       div[data-baseweb="input"] (which also holds the reveal-password
       button) was never styled, so it kept Streamlit's dark theme
       background — showing as a black strip on every password field. */
    [data-testid="stTextInput"] div[data-baseweb="input"] {
        background: #FFFFFF !important;
        border-radius: 10px !important;
    }
    [data-testid="stTextInput"] div[data-baseweb="input"] button {
        background: #FFFFFF !important;
    }
    [data-testid="stTextInput"] div[data-baseweb="input"] button svg {
        fill: #1E293B !important;
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

/* ══════════════════════════════════════
   LANDING PAGE — Full-screen layout
══════════════════════════════════════ */

/* Hide Streamlit chrome on login page */
.landing-active [data-testid="stHeader"],
.landing-active [data-testid="stToolbar"],
.landing-active [data-testid="stDecoration"] { display: none !important; }

/* Wrapper that fills the whole viewport */
/* ── Left hero panel (now a standalone column card, not a full-bleed flex child) ── */
.landing-hero {
    background: linear-gradient(145deg, #0F172A 0%, #1E1B4B 55%, #312E81 100%);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    padding: 48px 44px;
    min-height: 560px;
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(15,23,42,0.18), 0 2px 8px rgba(0,0,0,0.08);
    position: relative;
    overflow: hidden;
}
.landing-hero::before {
    content: '';
    position: absolute;
    top: -120px; right: -120px;
    width: 420px; height: 420px;
    background: radial-gradient(circle, rgba(139,92,246,0.28) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.landing-hero::after {
    content: '';
    position: absolute;
    bottom: -80px; left: -80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(59,130,246,0.18) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.landing-hero .hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(139,92,246,0.18);
    border: 1px solid rgba(139,92,246,0.4);
    border-radius: 999px;
    padding: 6px 16px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #C4B5FD;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 28px;
}
.landing-hero h1 {
    font-size: 2.8rem !important;
    font-weight: 900 !important;
    color: #ffffff !important;
    line-height: 1.15 !important;
    margin: 0 0 20px !important;
    letter-spacing: -1px;
}
.landing-hero h1 span {
    background: linear-gradient(90deg, #818CF8, #C084FC);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.landing-hero .hero-desc {
    font-size: 1rem;
    color: #94A3B8;
    line-height: 1.7;
    max-width: 380px;
    margin-bottom: 40px;
}
.landing-hero .hero-features {
    display: flex;
    flex-direction: column;
    gap: 14px;
}
.landing-hero .hero-feature {
    display: flex;
    align-items: center;
    gap: 12px;
    color: #CBD5E1;
    font-size: 0.92rem;
}
.landing-hero .hero-feature .feat-icon {
    width: 34px; height: 34px;
    background: rgba(99,102,241,0.2);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}

/* ── Login card ──
   The card is a real st.container(border=True, key="auth_card"), so its
   header + tabs + forms render inside ONE box in normal document flow —
   which is what keeps it aligned on the same row as the hero column.
   Target both selectors for compatibility across Streamlit versions. */
.st-key-auth_card,
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border-radius: 20px !important;
    box-shadow: 0 8px 32px rgba(15,23,42,0.1), 0 2px 8px rgba(0,0,0,0.06) !important;
    border: 1px solid #E2E8F0 !important;
    padding: 32px 32px 24px !important;
    min-height: 560px;
    position: relative;
}
.st-key-auth_card::before,
[data-testid="stVerticalBlockBorderWrapper"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366F1, #8B5CF6, #EC4899);
    border-radius: 20px 20px 0 0;
}

/* Card header */
.auth-card-header {
    text-align: center;
    margin-bottom: 24px;
}
.auth-card-header .auth-icon {
    font-size: 2.4rem;
    display: block;
    margin-bottom: 12px;
    line-height: 1;
}
.auth-card-header h2 {
    font-size: 1.45rem !important;
    font-weight: 800 !important;
    color: #0F172A !important;
    margin: 0 0 6px !important;
    letter-spacing: -0.3px;
}
.auth-card-header p {
    color: #64748B;
    font-size: 0.84rem;
    margin: 0;
}
.landing-login-footer {
    margin-top: 24px;
    font-size: 0.78rem;
    color: #94A3B8;
    text-align: center;
}

/* ── Dashboard Header ── */


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

    /* ── Sidebar selectbox: disable typing / search behaviour ── */
    /* Hides the editable cursor and blocks keyboard input on the inner
       search <input> that Streamlit renders inside a searchable selectbox.
       The displayed selection text and the dropdown arrow remain fully
       functional — only free-text entry is suppressed.               */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] input {
        caret-color: transparent !important;
        pointer-events: none !important;
        user-select: none !important;
        -webkit-user-select: none !important;
    }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] {
        cursor: pointer !important;
    }


    /* ── AI Insights Panel ── */
    .ai-insights-panel {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%);
        border: 1px solid rgba(139,92,246,0.35);
        border-radius: 20px;
        padding: 28px 32px;
        margin: 28px 0 20px;
        box-shadow: 0 8px 40px rgba(79,70,229,0.18);
    }
    .ai-insights-panel h3 {
        color: #C4B5FD !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.25rem !important;
        margin-bottom: 4px !important;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .ai-insights-panel .ai-meta {
        color: #6366F1;
        font-size: 0.78rem;
        margin-bottom: 18px;
        letter-spacing: 0.04em;
    }
    .ai-summary-block {
        background: rgba(255,255,255,0.06);
        border-left: 4px solid #818CF8;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 20px;
        color: #E0E7FF;
        font-size: 0.97rem;
        line-height: 1.65;
    }
    .ai-section-title {
        color: #A5B4FC;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.10em;
        text-transform: uppercase;
        margin: 16px 0 8px;
    }
    .ai-tag {
        display: inline-block;
        background: rgba(99,102,241,0.22);
        color: #C7D2FE;
        border: 1px solid rgba(99,102,241,0.4);
        border-radius: 999px;
        padding: 4px 14px;
        font-size: 0.83rem;
        margin: 4px 4px 4px 0;
        font-weight: 500;
    }
    .ai-rec-item {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        background: rgba(255,255,255,0.04);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
        color: #E0E7FF;
        font-size: 0.92rem;
        line-height: 1.5;
    }
    .ai-rec-num {
        min-width: 24px;
        height: 24px;
        border-radius: 50%;
        background: linear-gradient(135deg,#4F46E5,#7C3AED);
        color: white;
        font-size: 0.75rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .ai-cached-badge {
        display: inline-block;
        background: rgba(16,185,129,0.18);
        color: #6EE7B7;
        border: 1px solid rgba(16,185,129,0.3);
        border-radius: 999px;
        padding: 2px 10px;
        font-size: 0.73rem;
        font-weight: 600;
        margin-left: 8px;
        letter-spacing: 0.05em;
    }
    .ai-fresh-badge {
        display: inline-block;
        background: rgba(245,158,11,0.18);
        color: #FCD34D;
        border: 1px solid rgba(245,158,11,0.3);
        border-radius: 999px;
        padding: 2px 10px;
        font-size: 0.73rem;
        font-weight: 600;
        margin-left: 8px;
        letter-spacing: 0.05em;
    }
                /* Append the new tab scaling rule: */
    div[data-testid="stTabs"] button {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
    }
    div[data-testid="stTabs"] button p {
        font-size: 1.2rem !important;
    }

    /* Phase 1: unified Sentilytics brand system */
    :root {
        --brand-ink: #10233F;
        --brand-muted: #5B6B82;
        --brand-primary: #2563EB;
        --brand-primary-dark: #1D4ED8;
        --brand-accent: #14B8A6;
        --brand-warm: #F59E0B;
        --brand-danger: #EF4444;
        --brand-surface: #FFFFFF;
        --brand-soft: #F7FAFC;
        --brand-line: #DCE5F2;
        --brand-shadow: 0 18px 45px rgba(16, 35, 63, 0.10);
    }

    .stApp {
        background:
            linear-gradient(180deg, rgba(255,255,255,0.94), rgba(247,250,252,0.96)),
            radial-gradient(circle at top left, rgba(37,99,235,0.12), transparent 34%),
            radial-gradient(circle at bottom right, rgba(20,184,166,0.12), transparent 30%) !important;
    }

    .ui-icon,
    .material-symbols-rounded.ui-icon {
        font-family: 'Material Symbols Rounded' !important;
        font-weight: normal !important;
        font-style: normal !important;
        font-size: 1.05em;
        line-height: 1;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        vertical-align: -0.16em;
        font-variation-settings: 'FILL' 0, 'wght' 500, 'GRAD' 0, 'opsz' 24;
    }

    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 6px 18px;
    }
    .brand-mark {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--brand-primary), var(--brand-accent));
        color: #FFFFFF !important;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 12px 28px rgba(37,99,235,0.26);
    }
    .brand-mark .ui-icon {
        color: #FFFFFF !important;
        font-size: 24px;
    }
    .brand-title {
        color: #FFFFFF !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.18rem;
        font-weight: 800;
        line-height: 1.05;
        letter-spacing: 0;
    }
    .brand-subtitle {
        color: #A9B7CC !important;
        font-size: 0.76rem;
        margin-top: 4px;
    }
    .sidebar-user-card,
    .sidebar-panel {
        background: rgba(255,255,255,0.075);
        border: 1px solid rgba(220,229,242,0.12);
        border-radius: 14px;
        padding: 12px 14px;
        margin: 10px 0 14px;
    }
    .sidebar-user-card {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .sidebar-user-avatar {
        width: 32px;
        height: 32px;
        border-radius: 10px;
        background: rgba(37,99,235,0.22);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .sidebar-user-avatar .ui-icon {
        color: #BFDBFE !important;
    }
    .sidebar-kicker {
        color: #94A3B8 !important;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 800;
    }
    .sidebar-value {
        color: #FFFFFF !important;
        font-size: 0.92rem;
        font-weight: 700;
        margin-top: 2px;
    }
    .sidebar-section-title {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #DCEBFF !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.88rem;
        font-weight: 800;
        margin: 16px 0 8px;
    }

    .page-shell {
        background: rgba(255,255,255,0.72);
        border: 1px solid rgba(220,229,242,0.85);
        border-radius: 18px;
        padding: clamp(18px, 3vw, 30px);
        box-shadow: var(--brand-shadow);
        margin-bottom: 18px;
    }
    .page-heading {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 18px;
        margin-bottom: 18px;
    }
    .page-heading h2,
    .page-heading h3 {
        margin: 0 !important;
        color: var(--brand-ink) !important;
    }
    .page-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: var(--brand-primary);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .page-subtitle {
        color: var(--brand-muted);
        font-size: 0.95rem;
        line-height: 1.55;
        margin-top: 6px;
    }

    .landing-hero {
        background:
            linear-gradient(145deg, rgba(16,35,63,0.97) 0%, rgba(29,78,216,0.88) 58%, rgba(20,184,166,0.78) 100%),
            linear-gradient(45deg, #10233F, #2563EB) !important;
        border-radius: 18px !important;
    }
    .landing-hero::before,
    .landing-hero::after {
        display: none !important;
    }
    .landing-hero .hero-badge {
        background: rgba(255,255,255,0.12) !important;
        border-color: rgba(255,255,255,0.24) !important;
        color: #DBEAFE !important;
    }
    .landing-hero h1 {
        letter-spacing: 0 !important;
    }
    .landing-hero h1 span {
        background: linear-gradient(90deg, #DBEAFE, #99F6E4) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
    }
    .landing-hero .hero-feature .feat-icon {
        background: rgba(255,255,255,0.12) !important;
        border: 1px solid rgba(255,255,255,0.14);
        color: #DDF8F4 !important;
    }
    .auth-card-header .auth-icon {
        width: 46px;
        height: 46px;
        border-radius: 14px;
        margin: 0 auto 14px;
        background: linear-gradient(135deg, var(--brand-primary), var(--brand-accent));
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 14px 28px rgba(37,99,235,0.22);
    }
    .auth-card-header .auth-icon .ui-icon {
        color: #FFFFFF !important;
        font-size: 24px;
    }

    @media (max-width: 900px) {
        .landing-hero,
        .st-key-auth_card,
        [data-testid="stVerticalBlockBorderWrapper"] {
            min-height: auto !important;
        }
        .landing-hero {
            padding: 34px 26px !important;
        }
        .landing-hero h1 {
            font-size: 2.2rem !important;
        }
        .page-heading {
            flex-direction: column;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------- Helper Functions -----------------

def ms_icon(name: str, class_name: str = "ui-icon") -> str:
    """Render a Material Symbols icon for HTML snippets."""
    return f"<span class='material-symbols-rounded {class_name}' aria-hidden='true'>{name}</span>"


def section_title(icon_name: str, eyebrow: str, title: str, subtitle: str = "") -> None:
    subtitle_html = f"<div class='page-subtitle'>{subtitle}</div>" if subtitle else ""
    st.markdown(
        f"""
        <div class="page-heading">
            <div>
                <div class="page-eyebrow">{ms_icon(icon_name)} {eyebrow}</div>
                <h2>{title}</h2>
                {subtitle_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_styled_predictions_df(df: pd.DataFrame, text_col: str, sentiment_col: str, confidence_col: str | None = None) -> None:
    # Build display frame
    cols = []
    if text_col in df.columns:
        cols.append(text_col)
    if "cleaned_text" in df.columns:
        cols.append("cleaned_text")
    if sentiment_col in df.columns:
        cols.append(sentiment_col)
    if confidence_col and confidence_col in df.columns:
        cols.append(confidence_col)
        
    preview_df = df[cols].head(100).copy()
    
    # Rename columns for presentation
    renames = {
        text_col: "Comment",
        "cleaned_text": "Cleaned Text",
        sentiment_col: "Sentiment"
    }
    if confidence_col:
        renames[confidence_col] = "Model Confidence"
    preview_df.rename(columns=renames, inplace=True)
    
    # Row highlight for low confidence
    def highlight_low_confidence(row):
        if "Model Confidence" in row.index:
            val = row["Model Confidence"]
            try:
                if val is not None and pd.notna(val) and float(val) < 0.60:
                    return ["background-color: #FFE4E4; color: #7F1D1D;"] * len(row)
            except (TypeError, ValueError):
                pass
        return [""] * len(row)
        
    sentiment_colors = {
        "positive": "#16A34A",
        "negative": "#DC2626",
        "neutral": "#D97706",
    }
    
    styled = preview_df.style.apply(highlight_low_confidence, axis=1)
    
    if "Model Confidence" in preview_df.columns:
        styled = styled.format({"Model Confidence": "{:.1%}"})
        
    def colour_sentiment(val):
        color = sentiment_colors.get(str(val).lower(), "#475569")
        return f"color: {color}; font-weight: 700; text-transform: capitalize;"
        
    if "Sentiment" in preview_df.columns:
        styled = styled.map(colour_sentiment, subset=["Sentiment"])
        
    st.dataframe(styled, use_container_width=True)

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
    pred_labels = [labels_order[idx] for idx in pred_indices]
    pred_confidences = ensemble_probs.max(axis=1).tolist()
    return pred_labels, pred_confidences


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
                            from scipy.special import softmax as _softmax
                            X_batch = transform_with_saved_vectorizer(baseline_vec, df_run["cleaned_text"])
                            if hasattr(baseline_model, "predict_proba"):
                                probs_batch = baseline_model.predict_proba(X_batch)
                            elif hasattr(baseline_model, "decision_function"):
                                dec = baseline_model.decision_function(X_batch)
                                probs_batch = _softmax(dec if dec.ndim == 2 else np.column_stack([-dec, dec]), axis=1)
                            else:
                                probs_batch = None
                            predictions = baseline_model.predict(X_batch)
                            confidences = probs_batch.max(axis=1).tolist() if probs_batch is not None else [1.0] * len(predictions)
                        elif batch_model_choice.startswith("Transformer ("):
                            from scipy.special import softmax as _softmax
                            run_id = batch_model_choice.replace("Transformer (", "").rstrip(")")
                            t_model, t_tokenizer = load_transformer_model(run_id)
                            
                            import torch
                            predictions = []
                            confidences = []
                            id_to_label = getattr(t_model.config, "id2label", {0: "negative", 1: "neutral", 2: "positive"})
                            
                            # Process texts
                            for txt in df_run["cleaned_text"]:
                                inputs = t_tokenizer(txt, return_tensors="pt", truncation=True, max_length=128)
                                with torch.no_grad():
                                    logits = t_model(**inputs).logits.numpy()[0]
                                    probs = _softmax(logits)
                                    pred_idx = int(np.argmax(probs))
                                    predictions.append(id_to_label[pred_idx].lower())
                                    confidences.append(float(probs[pred_idx]))
                        else:
                            # Parallel Ensemble
                            predictions, confidences = run_parallel_predictions(
                                df_run, baseline_model, baseline_vec, transformers, paths
                            )
                                    
                        df_run["predicted_sentiment"] = predictions
                        df_run["model_confidence"] = confidences
                        st.session_state.batch_df = df_run
                        st.session_state.batch_text_col = text_column

                        # ── Cache word cloud images once, right after prediction ──
                        try:
                            from src.models import generate_wordcloud as _gen_wc_cache
                            _cache_texts = df_run[text_column].tolist()
                            _cache_sents = df_run["predicted_sentiment"].tolist()
                            _wc_cache: dict = {}
                            for _lbl in ["All", "Positive", "Negative", "Neutral"]:
                                _f = None if _lbl == "All" else _lbl.lower()
                                _wc_o = _gen_wc_cache(
                                    texts=_cache_texts,
                                    sentiment_filter=_f,
                                    predicted_sentiments=_cache_sents,
                                    stopwords_path="stopwords_chichewa.txt",
                                    width=900, height=380, max_words=120,
                                )
                                _wc_cache[_lbl] = _wc_o.to_image() if _wc_o else None
                            st.session_state.batch_wordclouds = _wc_cache
                        except Exception:
                            st.session_state.batch_wordclouds = {}

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

                total_comments = len(df_results)
                pos_count = sum(df_results["predicted_sentiment"] == "positive")
                neu_count = sum(df_results["predicted_sentiment"] == "neutral")
                neg_count = sum(df_results["predicted_sentiment"] == "negative")
                pos_pct = pos_count / total_comments if total_comments > 0 else 0
                neu_pct = neu_count / total_comments if total_comments > 0 else 0
                neg_pct = neg_count / total_comments if total_comments > 0 else 0

                labels = ['Positive', 'Neutral', 'Negative']
                sizes = [pos_count, neu_count, neg_count]
                filtered_labels = [l for l, s in zip(labels, sizes) if s > 0]
                filtered_sizes = [s for s in sizes if s > 0]
                colors_ch = ['#10B981', '#F59E0B', '#EF4444']
                filtered_colors = [c for c, s in zip(colors_ch, sizes) if s > 0]

                # ── Export action pinned to the top ───────────────────────────
                st.markdown("---")
                col_res_hdr, col_res_export = st.columns([0.7, 0.3])
                with col_res_hdr:
                    st.markdown(f"### {ms_icon('analytics')} Results Panel", unsafe_allow_html=True)
                with col_res_export:
                    _export_tabs = st.tabs(["Export"])
                    with _export_tabs[0]:
                        csv_data = df_results.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label="Download CSV",
                            data=csv_data,
                            file_name="sentiment_predictions.csv",
                            mime="text/csv",
                            use_container_width=True,
                        )
                    from src.report_generator import create_report_pdf
                    import datetime

                    # 1. Define a clean data acquisition function to build bytes on demand
                    def get_pdf_bytes():
                        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        return create_report_pdf(
                            url=uploaded_file.name,
                            timestamp=now_str,
                            df=df_results,
                            wordclouds=st.session_state.get("batch_wordclouds"),
                        )

                    # 2. Render ONLY the single action button
                    # Streamlit will evaluate the function and stream the file immediately upon invocation
                    try:
                        st.download_button(
                            label="Generate & Download PDF Report",
                            data=get_pdf_bytes(),  # Triggers generation instantly when clicked
                            file_name=f"sentiment_report_{datetime.date.today()}.pdf",
                            mime="application/pdf",
                            key="batch_pdf_direct_download",
                            use_container_width=True,
                        )
                    except Exception as pdf_ex:
                        st.error(f"Could not process download execution: {pdf_ex}")
        except Exception as e:
            st.error(f"Error processing CSV file: {e}")

# ----------------- UI Sidebar -----------------

def get_password_requirements(password):
    password = password or ""
    return {
        "At least 8 characters": len(password) >= 8,
        "Contains uppercase and lowercase letters": any(char.isupper() for char in password) and any(char.islower() for char in password),
        "Contains at least one number": any(char.isdigit() for char in password),
        "Contains at least one special character": any(not char.isalnum() for char in password),
    }


def render_password_requirements(password):
    requirements = get_password_requirements(password)
    met_count = sum(requirements.values())
    strength_pct = int((met_count / len(requirements)) * 100)
    strength_label = "Strong" if met_count == len(requirements) else "Almost there" if met_count >= 3 else "Weak"
    strength_color = "#16A34A" if met_count == len(requirements) else "#D97706" if met_count >= 3 else "#DC2626"
    rows = []
    for label, is_met in requirements.items():
        icon_name = "check_circle" if is_met else "radio_button_unchecked"
        color = "#16A34A" if is_met else "#DC2626"
        status = "met" if is_met else "not met"
        rows.append(
            f"<li style='color:{color}; margin: 6px 0; display:flex; align-items:center; gap:8px;'>"
            f"{ms_icon(icon_name)} <span>{label} <span style='font-size: 0.85em;'>({status})</span></span>"
            "</li>"
        )
    rows.insert(
        0,
        "<li style='list-style:none; margin: 8px 0 10px;'>"
        f"<div style='display:flex; justify-content:space-between; color:#334155; font-size:0.82rem; font-weight:700;'>"
        f"<span>Password strength</span><span style='color:{strength_color};'>{strength_label}</span></div>"
        "<div style='height:7px; border-radius:999px; background:#E2E8F0; overflow:hidden; margin-top:6px;'>"
        f"<div style='height:100%; width:{strength_pct}%; background:{strength_color}; border-radius:999px;'></div>"
        "</div></li>",
    )
    return rows
    st.markdown(
        "<div style='margin: 0.35rem 0 0.85rem 0;'>"
        "<p style='margin-bottom: 0.25rem; font-weight: 700;'>Password requirements</p>"
        "<ul style='padding-left: 1.15rem; margin-top: 0;'>"
        + "".join(rows)
        + "</ul></div>",
        unsafe_allow_html=True,
    )
    return all(requirements.values())


def is_valid_email(value: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (value or "").strip()))


def split_url_input(value: str) -> list[str]:
    return [u.strip() for u in re.split(r"[,\n]+|\s+", value or "") if u.strip()]


def is_facebook_url(value: str) -> bool:
    try:
        parsed = urlparse(value.strip())
    except Exception:
        return False
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return False
    host = parsed.netloc.lower()
    return host == "facebook.com" or host.endswith(".facebook.com") or host == "fb.watch"


def invalid_facebook_urls(urls: list[str]) -> list[str]:
    return [url for url in urls if not is_facebook_url(url)]


def reset_user_scoped_state(clear_widget_keys: bool = True) -> None:
    """Clear session-state values that must not cross user accounts."""
    keys_to_clear = [
        "sessions_cache",
        "sessions_cache_user_id",
        "comments_cache",
        "comments_cache_session_id",
        "cached_insights",
        "cached_insights_key",
        "batch_wordclouds",
        "_hist_wc_session",
        "history_pdf_bytes",
        "history_pdf_cache_key",
        "_force_history_nav",
        "_force_new_nav",
        "user_scrape_results",
        "user_active_urls",
        "user_active_file",
        "user_processing",
        "trigger_user_scrape",
        "user_scrape_phase",
        "user_cancel_requested",
        "dev_active_url",
        "dev_active_file",
        "dev_processing",
        "trigger_dev_scrape",
        "dev_scrape_results",
        "dev_cancel_requested",
        "dev_scrape_phase",
        "batch_df",
    ]
    if clear_widget_keys:
        keys_to_clear.extend([
            "history_session_selectbox",
            "sidebar_workspace_nav",
        ])
    for key in keys_to_clear:
        st.session_state.pop(key, None)
    st.session_state.view_mode = "new"
    st.session_state.current_session_id = None
    st.session_state.sessions_cache_dirty = True


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

# ════════════════════════════════════════
# LANDING PAGE — full-screen split layout
# ════════════════════════════════════════
if not st.session_state.logged_in:
    # Hero and login card are rendered as two columns in a SINGLE st.columns()
    # call so they share one row and stay aligned side-by-side.
    hero_col, card_col = st.columns([1.1, 0.9], gap="large")

    with hero_col:
        st.markdown(f"""
        <div class="landing-hero">
          <div class="hero-badge">{ms_icon("verified")} Sentilytics Intelligence</div>
    
          <h1>Facebook<br><span>Sentiment</span><br>Classifier</h1>
          <p class="hero-desc">
            A low-resource NLP dashboard for analysing sentiment in
            Facebook posts — powered by transformer models trained on
            Malawian social media data.
          </p>
          <div class="hero-features">
            <div class="hero-feature">
              <div class="feat-icon">{ms_icon("monitoring")}</div>
              Real-time sentiment analysis &amp; visualisations
            </div>
            <div class="hero-feature">
              <div class="feat-icon">{ms_icon("model_training")}</div>
              Baseline &amp; transformer model comparisons
            </div>
            <div class="hero-feature">
              <div class="feat-icon">{ms_icon("forum")}</div>
              AI chatbot assistant for result exploration
            </div>
            <div class="hero-feature">
              <div class="feat-icon">{ms_icon("database")}</div>
              Session history &amp; database export
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with card_col:
        # A real Streamlit bordered container IS the card, so the header and
        # the form widgets render inside the same box instead of two blocks.
        with st.container(border=True, key="auth_card"):
            st.markdown(f"""
            <div class="auth-card-header">
                <span class="auth-icon">{ms_icon("lock")}</span>
                <h2>Sentilytics Dashboard</h2>
                <p>Sign in to analyse public conversation with one consistent workspace.</p>
            </div>
            """, unsafe_allow_html=True)

            auth_tabs = st.tabs(["Sign In", "Create Account"])

            with auth_tabs[0]:
                with st.form("login_form"):
                    login_email = st.text_input("Email address", key="login_email_input", placeholder="you@example.com")
                    password = st.text_input("Password", type="password", key="login_password_input")
                    submit = st.form_submit_button("Sign In", use_container_width=True)
                    if submit:
                        if not login_email or not password:
                            st.error("Please fill out all fields.")
                        elif not is_valid_email(login_email):
                            st.error("Please enter a valid email address.")
                        else:
                            from src.database import authenticate_user
                            user = authenticate_user(login_email, password)
                            if user:
                                cookie_controller.set("logged_in_user", user["username"])
                                st.session_state.logged_in = True
                                st.session_state.user_id = user["user_id"]
                                st.session_state.username = user["username"]
                                st.session_state.current_user = {"user_id": user["user_id"], "username": user["username"], "role": user.get("role", "general")}
                                st.session_state.logged_in_as_dev = user.get("role") in ("developer", "admin")
                                reset_user_scoped_state()
                                st.success(f"Welcome back, {user['username']}!")
                                st.query_params.clear()
                                st.rerun()
                            else:
                                st.error("Invalid email or password.")

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
                                reset_user_scoped_state()
                                st.query_params.clear()
                                st.rerun()

            with auth_tabs[1]:
                reg_email = st.text_input("Email address", key="register_email_input", placeholder="you@example.com")
                reg_password = st.text_input("Create password", type="password", key="register_password_input")
                rows = render_password_requirements(reg_password)
                html_rows = " ".join(rows)
                st.markdown(f"<ul style='list-style:none; padding-left:0; margin-top:0.35rem;'>{html_rows}</ul>", unsafe_allow_html=True)
                reg_confirm = st.text_input("Confirm password", type="password", key="register_confirm_input")

                submit_reg = st.button("Create Account", use_container_width=True, key="register_submit_btn")
                if submit_reg:
                    if not reg_email or not reg_password or not reg_confirm:
                        st.error("Please fill out all fields.")
                    elif not is_valid_email(reg_email):
                        st.error("Please enter a valid email address.")
                    elif reg_password != reg_confirm:
                        st.error("Passwords do not match.")
                    elif not all(get_password_requirements(reg_password).values()):
                        st.error("Your password does not meet all security requirements.")
                    else:
                        from src.database import create_user
                        try:
                            create_user(reg_email, reg_password)
                            st.success("Account created successfully. Please sign in using your email.")
                        except ValueError as ve:
                            st.error(str(ve))
                        except Exception as e:
                            st.error(f"Failed to create account: {e}")

    st.stop()

# Handle shareable URL query parameter redirect
if "session_id" in st.query_params:
    try:
        param_sess_id = int(st.query_params["session_id"])
        if st.session_state.current_session_id != param_sess_id or st.session_state.view_mode != "history":
            st.session_state.current_session_id = param_sess_id
            st.session_state.view_mode = "history"
            st.session_state.user_scrape_results = None
            st.session_state._force_history_nav = True
            st.rerun()
    except ValueError:
        pass

is_developer = st.session_state.logged_in_as_dev

# ── Sidebar ──
st.sidebar.markdown(
    f"""
    <div class="brand-lockup">
        <div class="brand-mark">{ms_icon("analytics")}</div>
        <div>
            <div class="brand-title">Sentilytics</div>
            <div class="brand-subtitle">Facebook sentiment intelligence</div>
        </div>
    </div>
    <div class="sidebar-user-card">
        <div class="sidebar-user-avatar">{ms_icon("person")}</div>
        <div>
            <div class="sidebar-kicker">Signed in</div>
            <div class="sidebar-value">{st.session_state.username}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if st.session_state.pop("_force_history_nav", False):
    st.session_state.sidebar_workspace_nav = "Session History"
elif st.session_state.pop("_force_new_nav", False):
    st.session_state.sidebar_workspace_nav = "New Analysis"

workspace_choice = st.sidebar.radio(
    "Workspace",
    ["New Analysis", "Session History"],
    index=0 if st.session_state.view_mode != "history" else 1,
    key="sidebar_workspace_nav",
)
history_nav_requested = workspace_choice == "Session History"
if workspace_choice == "New Analysis" and st.session_state.view_mode == "history":
    st.session_state.view_mode = "new"
    st.session_state.current_session_id = None
    st.session_state.user_scrape_results = None
    st.query_params.clear()
    st.rerun()

# 1. "Analyze New URL" button fixed at the top
if st.sidebar.button("Analyze New URL", type="primary", use_container_width=True, key="new_analysis_sidebar_btn"):
    st.session_state.view_mode = "new"
    st.session_state.current_session_id = None
    st.session_state.user_scrape_results = None
    st.session_state._force_new_nav = True
    st.query_params.clear()
    st.rerun()

st.sidebar.markdown(f"<div class='sidebar-section-title'>{ms_icon('history')} History Sessions</div>", unsafe_allow_html=True)

# Cache sessions in session state to improve page performance, keyed by logged-in user
if (
    "sessions_cache" not in st.session_state
    or st.session_state.get("sessions_cache_dirty", True)
    or st.session_state.get("sessions_cache_user_id") != st.session_state.user_id
):
    from src.database import get_user_sessions
    st.session_state.sessions_cache = get_user_sessions(st.session_state.user_id)
    st.session_state.sessions_cache_user_id = st.session_state.user_id
    st.session_state.sessions_cache_dirty = False

sessions = st.session_state.sessions_cache
owned_session_ids = {s["session_id"] for s in sessions}

if (
    st.session_state.view_mode == "history"
    and st.session_state.current_session_id is not None
    and st.session_state.current_session_id not in owned_session_ids
):
    st.warning("That analysis session is not available for this account.")
    st.session_state.view_mode = "new"
    st.session_state.current_session_id = None
    st.session_state.comments_cache_session_id = None
    if "session_id" in st.query_params:
        st.query_params.clear()
    st.rerun()

if history_nav_requested and sessions and st.session_state.view_mode != "history":
    st.session_state.view_mode = "history"
    if st.session_state.current_session_id is None:
        st.session_state.current_session_id = sessions[0]["session_id"]
    st.rerun()
elif history_nav_requested and not sessions:
    st.sidebar.info("No sessions yet. Start a new analysis first.")

if sessions:
    # Build dictionary for dropdown selection options
    session_options = {s["session_id"]: s.get("display_title") or f"Analysis Run ({s.get('timestamp')})" for s in sessions}
    
    current_sid = st.session_state.current_session_id
    if current_sid not in session_options:
        current_sid = sessions[0]["session_id"]
        if st.session_state.view_mode == "history":
            st.session_state.current_session_id = current_sid

    options_list = list(session_options.keys())
    try:
        select_index = options_list.index(current_sid)
    except ValueError:
        select_index = 0


    # ── Navigation callback: only fires when the user explicitly picks a session ──
    def _navigate_to_session():
        sid = st.session_state.get("history_session_selectbox")
        if sid and sid != st.session_state.get("current_session_id"):
            st.session_state.current_session_id = sid
            st.session_state.view_mode = "history"
            st.session_state.user_scrape_results = None
            st.session_state.comments_cache_session_id = None
            # Streamlit auto-reruns after on_change; no explicit st.rerun() needed

    st.sidebar.selectbox(
        "Select Past Session",
        options=options_list,
        format_func=lambda x: session_options[x],
        index=select_index,
        key="history_session_selectbox",
        on_change=_navigate_to_session,
    )
    selected_session_id = st.session_state.get("history_session_selectbox", options_list[select_index])

    active_s = next((s for s in sessions if s["session_id"] == selected_session_id), None)
    if active_s:
        session_id = active_s["session_id"]
        rename_flag_key = f"show_rename_{session_id}"
        if rename_flag_key not in st.session_state:
            st.session_state[rename_flag_key] = False

        with st.sidebar.popover("Session Settings", use_container_width=True):
            if not st.session_state[rename_flag_key]:
                url_val = active_s.get("url") or "#"
                st.markdown(
                    f'<a href="{url_val}" target="_blank" class="menu-link-item">Original Post</a>',
                    unsafe_allow_html=True
                )
                if st.button("Rename", key=f"rename_trigger_{session_id}", use_container_width=True):
                    st.session_state[rename_flag_key] = True
                    st.rerun()
                if st.button("Share", key=f"share_btn_{session_id}", use_container_width=True):
                    st.query_params["session_id"] = str(session_id)
                    st.info("Link set in query parameters!")
                if st.button("Delete", key=f"delete_btn_{session_id}", type="primary", use_container_width=True):
                    from src.database import delete_session
                    delete_session(session_id)
                    st.session_state.sessions_cache_dirty = True
                    st.session_state.current_session_id = None
                    st.session_state.view_mode = "new"
                    st.session_state.comments_cache_session_id = None
                    st.success("Deleted!")
                    st.rerun()
            else:
                rename_title = st.text_input(
                    "Rename Session", 
                    value=active_s.get("custom_title") or "", 
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
                        st.session_state.sessions_cache_dirty = True
                        st.success("Session renamed!")
                        st.rerun()
                with col_cancel:
                    if st.button("Cancel", key=f"cancel_rename_btn_{session_id}", use_container_width=True):
                        st.session_state[rename_flag_key] = False
                        st.rerun()
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
if st.sidebar.button("Log Out", use_container_width=True, key="logout_sidebar_btn"):
    cookie_controller.remove("logged_in_user")
    reset_user_scoped_state(clear_widget_keys=False)
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.current_user = {"user_id": "guest", "username": "Guest", "role": "general"}
    st.session_state.logged_in_as_dev = False
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
        if session.get("user_id") != st.session_state.user_id:
            st.error("Selected session is not available for this account.")
            st.session_state.view_mode = "new"
            st.session_state.current_session_id = None
            st.session_state.comments_cache_session_id = None
            st.query_params.clear()
            st.rerun()
            
        # Cache comments for this active session to avoid redundant database calls
        current_sess_id = st.session_state.current_session_id
        if "comments_cache" not in st.session_state or st.session_state.get("comments_cache_session_id") != current_sess_id:
            st.session_state.comments_cache = get_session_comments(current_sess_id)
            st.session_state.comments_cache_session_id = current_sess_id
            
        comments_list = st.session_state.comments_cache
        
        if not comments_list:
            section_title("analytics", "Session", "Analysis Session", f"Source: `{session['url']}`")
            st.markdown(f"**Analyzed on:** `{session['timestamp']}`")
            st.info("No comments found for this session.")
        else:
            df_user = pd.DataFrame(comments_list)

            # Cache word clouds for this history session (regenerate only when session changes)
            if st.session_state.get("_hist_wc_session") != st.session_state.current_session_id:
                st.session_state._hist_wc_session = st.session_state.current_session_id
                try:
                    from src.models import generate_wordcloud as _gen_wc_hist
                    _hist_texts = df_user["comment_text"].tolist()
                    _hist_sents = df_user["sentiment_label"].fillna("neutral").tolist()
                    _hist_cache: dict = {}
                    for _lbl in ["All", "Positive", "Negative", "Neutral"]:
                        _f = None if _lbl == "All" else _lbl.lower()
                        _wc_o = _gen_wc_hist(
                            texts=_hist_texts,
                            sentiment_filter=_f,
                            predicted_sentiments=_hist_sents,
                            stopwords_path="stopwords_chichewa.txt",
                            width=900, height=380, max_words=120,
                        )
                        _hist_cache[_lbl] = _wc_o.to_image() if _wc_o else None
                    st.session_state.batch_wordclouds = _hist_cache
                except Exception:
                    st.session_state.batch_wordclouds = {}

            # Count sentiments
            df_user["sentiment_label_clean"] = df_user["sentiment_label"].fillna("neutral").str.lower()
            total_comments = len(df_user)
            pos_count = int((df_user["sentiment_label_clean"] == "positive").sum())
            neg_count = int((df_user["sentiment_label_clean"] == "negative").sum())
            neu_count = int((df_user["sentiment_label_clean"] == "neutral").sum())
            
            pos_pct = pos_count / total_comments if total_comments > 0 else 0
            neg_pct = neg_count / total_comments if total_comments > 0 else 0
            neu_pct = neu_count / total_comments if total_comments > 0 else 0
            current_insights_key = (
                st.session_state.get("current_session_id"),
                pos_count + neg_count + neu_count,
            )
            current_insights = st.session_state.get("cached_insights")
            if (
                st.session_state.get("cached_insights_key") != current_insights_key
                or not current_insights
                or "error" in current_insights
            ):
                current_insights = None
            
            # Action/Export section at the top of the view
            col_hdr1, col_hdr2 = st.columns([0.75, 0.25])
            with col_hdr1:
                section_title("analytics", "Session", "Analysis Session", f"Source: `{session['url']}`")
                st.markdown(f"**Analyzed on:** `{session['timestamp']}`")
            with col_hdr2:
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                try:
                    from src.report_generator import create_report_pdf

                    pdf_insights_signature = json.dumps(current_insights or {}, sort_keys=True, default=str)
                    pdf_cache_key = (
                        "history_report",
                        session["session_id"],
                        len(df_user),
                        pdf_insights_signature,
                    )
                    if st.session_state.get("history_pdf_cache_key") != pdf_cache_key:
                        with st.spinner("Preparing report download..."):
                            st.session_state.history_pdf_bytes = create_report_pdf(
                                url=session["url"],
                                timestamp=session["timestamp"],
                                df=df_user,
                                wordclouds=st.session_state.get("batch_wordclouds"),
                                insights=current_insights,
                            )
                            st.session_state.history_pdf_cache_key = pdf_cache_key

                    st.download_button(
                        label="Generate & Download PDF Report",
                        data=st.session_state.history_pdf_bytes,
                        file_name=f"sentiment_report_{session['session_id']}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as pdf_ex:
                    st.error(f"Could not prepare PDF report: {pdf_ex}")
            
            # Tab partition for a clean non-scroll user experience
            tab_overview, tab_analytics, tab_insights = st.tabs(["Overview", "Analysis", "Insights"])
            
            with tab_overview:
                # Metrics KPI cards
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
                # Preview Data Table
                st.markdown("#### Prediction Preview")
                render_styled_predictions_df(df_user, "comment_text", "sentiment_label", "model_confidence")
                                  
            with tab_analytics:

                    
                # Aggregated Summaries
                col1, col2 = st.columns([1, 1])
                labels = ['Positive', 'Neutral', 'Negative']
                sizes = [pos_count, neu_count, neg_count]
                filtered_labels = [l for l, s in zip(labels, sizes) if s > 0]
                filtered_sizes = [s for s in sizes if s > 0]
                colors = ['#10B981', '#F59E0B', '#EF4444']
                filtered_colors = [c for c, s in zip(colors, sizes) if s > 0]
                
                with col1:
                    st.markdown("#### Sentiment Distribution (Flat Pie Chart)")
                    if filtered_sizes:
                        import matplotlib.pyplot as plt
                        fig, ax = plt.subplots(figsize=(6, 5))
                        wedges, texts, autotexts = ax.pie(
                            filtered_sizes, 
                            labels=filtered_labels, 
                            autopct='%1.1f%%',
                            shadow=False, 
                            startangle=140, 
                            colors=filtered_colors,
                            textprops=dict(color="#1E293B", weight="bold", size=10),
                            wedgeprops=dict(edgecolor='white', linewidth=1.0)
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

                                                    # Time-Series Trend Visualizer
                st.markdown(f"### {ms_icon('timeline')} Time-Series Sentiment Trend", unsafe_allow_html=True)
                df_user["created_time_dt"] = pd.to_datetime(df_user["created_time"], errors="coerce")
                valid_times = df_user["created_time_dt"].notna()
                
                if valid_times.sum() == 0:
                    st.info("No comment creation timestamps available for this session to render a time-series.")
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

                                        # Word clouds in sub-tabs within Analytics
                st.markdown(f"#### {ms_icon('cloud')} Sentiment Word Clouds", unsafe_allow_html=True)
                _wc_sentiments = ["All", "Positive", "Negative", "Neutral"]
                _wc_tabs = st.tabs(_wc_sentiments)
                _wc_cache = st.session_state.get("batch_wordclouds", {})
                for _wc_tab, _wc_label in zip(_wc_tabs, _wc_sentiments):
                    with _wc_tab:
                        _cached_img = _wc_cache.get(_wc_label)
                        if _cached_img is not None:
                            st.image(_cached_img, use_container_width=True)
                        else:
                            st.info(f"No '{_wc_label}' comments to visualise.")

            with tab_insights:
    
                # Isolate the print configurations within an clear layout container

             # ── AI Insights Panel (Groq) ──────────────────────────────────────────
                st.markdown("---")

                ai_col_head, ai_col_btn = st.columns([5, 1])
                with ai_col_head:
                    st.markdown(
                        "<h3 style='margin-bottom:2px;font-family:Outfit,sans-serif;'>"
                        f"{ms_icon('auto_awesome')} Recommendations</h3>",
                        unsafe_allow_html=True,
                    )
                with ai_col_btn:
                    refresh_insights = st.button(
                        "Refresh",
                        key="refresh_insights_btn",
                        help="Regenerate ",
                    )

                # Cache key is (session_id, total_count) so switching sessions or
                # loading a different result set always triggers a fresh generation.
                _cache_key = current_insights_key
                _need_generate = (
                    refresh_insights
                    or "cached_insights" not in st.session_state
                    or st.session_state.get("cached_insights_key") != _cache_key
                )

                if _need_generate:
                    with st.spinner("Compiling information..."):
                        try:
                            from src.llm_insights import generate_groq_insights

                            if "text" in df_user.columns:
                                _texts = df_user["text"].fillna("").astype(str).tolist()
                            elif "comment_text" in df_user.columns:
                                _texts = df_user["comment_text"].fillna("").astype(str).tolist()
                            else:
                                _texts = []

                            if "predicted_sentiment" in df_user.columns:
                                _sentiments = df_user["predicted_sentiment"].fillna("neutral").astype(str).tolist()
                            elif "sentiment_label_clean" in df_user.columns:
                                _sentiments = df_user["sentiment_label_clean"].fillna("neutral").astype(str).tolist()
                            elif "sentiment_label" in df_user.columns:
                                _sentiments = df_user["sentiment_label"].fillna("neutral").astype(str).str.lower().tolist()
                            else:
                                _sentiments = ["neutral"] * len(_texts)

                            _ai_data = generate_groq_insights(
                                texts=_texts,
                                sentiments=_sentiments,
                                pos_count=pos_count,
                                neg_count=neg_count,
                                neu_count=neu_count,
                            )
                            if _ai_data is None:
                                st.session_state.cached_insights = {"error": "unavailable"}
                            else:
                                _ai_data["_fresh"] = True
                                st.session_state.cached_insights = _ai_data
                            st.session_state.cached_insights_key = _cache_key
                        except EnvironmentError as _env_err:
                            st.session_state.cached_insights = {"error": "no_key", "detail": str(_env_err)}
                            st.session_state.cached_insights_key = _cache_key
                        except Exception as _exc:
                            st.session_state.cached_insights = {"error": "failed", "detail": str(_exc)}
                            st.session_state.cached_insights_key = _cache_key

                ai_data = st.session_state.get("cached_insights", {})

                # ── Render the panel ──────────────────────────────────────────────
                if not ai_data:
                    st.info(" Please try again.")

                elif "error" in ai_data:
                    _err_type = ai_data.get("error", "")
                    if _err_type == "no_key":
                        st.markdown(
                            "<div class='ai-insights-panel'>"
                            f"<h3>{ms_icon('auto_awesome')} Recommendations</h3>"
                            "<div class='ai-summary-block' style='color:#FCA5A5;'>"
                            f"{ms_icon('warning')} <strong>System unavailable, contact support.</strong><br><br>"
                            "</div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            "<div class='ai-insights-panel'>"
                            f"<h3>{ms_icon('auto_awesome')} Insights</h3>"
                            "<div class='ai-summary-block' style='color:#FCA5A5;'>"
                            f"{ms_icon('warning')} <strong>System currently unavailable.</strong><br>"
                            "Please check your internet connection, then click "
                            "<em>Refresh</em> to try again."
                            "</div></div>",
                            unsafe_allow_html=True,
                        )

                else:
                    # Successful result — render all sections
                    _fresh_badge = (
                        '<span class="ai-fresh-badge">fresh</span>'
                        if ai_data.get("_fresh")
                        else '<span class="ai-cached-badge">cached</span>'
                    )

                    # ── 1. Fetch Variables from ai_data ───────────────────────────────────────────
                    overall = ai_data.get("overall_interpretation", "")
                    summary = ai_data.get("summary_of_public_opinion", "")
                    reasons = ai_data.get("possible_reasons", [])
                    recs = ai_data.get("recommendations", [])

                    # New Breakdown Extractions
                    pos_talk = ai_data.get("positive_themes", "")
                    neu_talk = ai_data.get("neutral_themes", "")
                    neg_talk = ai_data.get("negative_themes", "")

                    # ── 2. Build Component Sub-blocks ─────────────────────────────────────────────
                    # Build reasons tags HTML
                    reasons_html = ""
                    for reason in reasons:
                        reasons_html += f"    <span class='ai-tag'>{ms_icon('search')} {reason}</span>\n"

                    # Build recommendations items HTML
                    recs_html = ""
                    for idx_r, rec in enumerate(recs, 1):
                        recs_html += (
                            "<div class='ai-rec-item'>"
                            f"<span class='ai-rec-num'>{idx_r}</span>"
                            f"<span>{rec}</span>"
                            "</div>"
                        )

                    # ── 3. Assemble Master HTML Block ─────────────────────────────────────────────
                    _total = pos_count + neg_count + neu_count
                    insights_html = (
                        "<div class='ai-insights-panel'>"
                        f"<h3>{ms_icon('auto_awesome')} Recommendations {_fresh_badge}</h3>"
                        f"<div class='ai-meta'>Powered by Groq &nbsp;&bull;&nbsp; Llama 3 &nbsp;&bull;&nbsp; Based on {_total} classified comments</div>"
                        
                        "<div class='ai-section-title'>Overall Interpretation</div>"
                        f"<div class='ai-summary-block'>{overall}</div>"
                        
                        "<div class='ai-section-title'>Summary of Public Opinion</div>"
                        f"<div class='ai-summary-block'>{summary}</div>"
                        
                        # ── New Sentiment Thematic Breakdown Section ──────────────────────────────────
                        "<div class='ai-section-title'>Thematic Sentiment Breakdown</div>"
                        f"<div class='ai-summary-block' style='padding-top:12px; padding-bottom:12px;'>"
                        f"  <div style='margin-bottom:10px;'><strong style='color:#10B981;'>{ms_icon('thumb_up')} Positive Discussion:</strong> {pos_talk}</div>"
                        f"  <div style='margin-bottom:10px;'><strong style='color:#F59E0B;'>{ms_icon('radio_button_unchecked')} Neutral / Indifferent:</strong> {neu_talk}</div>"
                        f"  <div><strong style='color:#EF4444;'>{ms_icon('thumb_down')} Negative Criticism:</strong> {neg_talk}</div>"
                        f"</div>"
                        # ─────────────────────────────────────────────────────────────────────────────
                        
                        "<div class='ai-section-title'>Possible Reasons Behind the Sentiment</div>"
                        f"<div style='margin-bottom:16px;'>{reasons_html}</div>"
                        
                        "<div class='ai-section-title'>Recommendations</div>"
                        f"{recs_html}"
                        "</div>"
                    )
                    st.markdown(insights_html, unsafe_allow_html=True)
                
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
            
        # Top-of-page input for URL(s) - supports one or many, separated by comma/newline/whitespace
        if not st.session_state.user_processing and not st.session_state.get("batch_processing", False):
            with st.container(border=True):
                user_url_text = st.text_area(
                    "Facebook Post URL(s)",
                    placeholder="https://www.facebook.com/.../posts/...\nPaste multiple Facebook URLs on separate lines.",
                    height=92,
                    key="user_url_text_input",
                )
                url_action_col, file_action_col = st.columns([1, 1])
                with url_action_col:
                    if st.button("Use Facebook URL(s)", type="primary", use_container_width=True, key="user_use_urls_btn"):
                        parsed_urls = split_url_input(user_url_text)
                        bad_urls = invalid_facebook_urls(parsed_urls)
                        if not parsed_urls:
                            st.error("Please paste at least one Facebook URL.")
                        elif bad_urls:
                            st.error("Only Facebook URLs are allowed. Please check: " + ", ".join(bad_urls[:3]))
                        else:
                            st.session_state.user_active_urls = parsed_urls
                            st.session_state.user_active_file = None
                with file_action_col:
                    uploaded_user_csv = st.file_uploader(
                        "Or upload CSV",
                        type=["csv"],
                        key="user_top_csv_uploader",
                        label_visibility="collapsed",
                    )
                if uploaded_user_csv is not None:
                    st.session_state.user_active_file = uploaded_user_csv
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
                    user_scrape_limit = st.number_input("Max Comments to Collect", min_value=1, max_value=10000, value=50, key="user_scrape_limit")
                with u_col2:
                    user_token_path = Path("secret/token.txt")
                    default_user_token = user_token_path.read_text(encoding="utf-8").strip() if user_token_path.exists() else (os.getenv("APIFY_API_TOKEN") or "")
                    user_has_token = bool(default_user_token)
                    if user_has_token:
                        user_scrape_token = default_user_token
                    else:
                        user_scrape_token = st.text_input("Apify API Token", type="password", placeholder="Required if not pre-configured", help="Enter your Apify API token to enable scraping.", key="user_apify_token")
                        
                if st.button("Run Scrape & Analyse", type="primary", key="user_scrape_btn"):
                    bad_urls = invalid_facebook_urls(st.session_state.user_active_urls or [])
                    if bad_urls:
                        st.error("Only Facebook URLs can be analysed. Please remove: " + ", ".join(bad_urls[:3]))
                    elif not user_scrape_token and not user_has_token:
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
                        "Scraping comments from Facebook... (this may take a while)"
                        if n_urls == 1
                        else f"Scraping {n_urls} Facebook posts... (this may take a while)"
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
                                    from scipy.special import softmax as _sm
                                    X = transform_with_saved_vectorizer(baseline_vec, df_user["cleaned_text"])
                                    preds = baseline_model.predict(X)
                                    if hasattr(baseline_model, "predict_proba"):
                                        _probs = baseline_model.predict_proba(X)
                                    elif hasattr(baseline_model, "decision_function"):
                                        _dec = baseline_model.decision_function(X)
                                        _probs = _sm(_dec if _dec.ndim == 2 else np.column_stack([-_dec, _dec]), axis=1)
                                    else:
                                        _probs = None
                                    df_user["predicted_sentiment"] = preds
                                    df_user["model_confidence"] = _probs.max(axis=1).tolist() if _probs is not None else [1.0] * len(preds)
                                else:
                                    df_user["predicted_sentiment"] = "neutral"
                                    df_user["model_confidence"] = None
                                    
                                # Save using new save_analysis (join multiple source URLs for the session record)
                                session = save_analysis(
                                    user_id=st.session_state.user_id,
                                    url=", ".join(st.session_state.user_active_urls),
                                    df=df_user
                                )
                                st.session_state.current_session_id = session["session_id"]
                                st.session_state.view_mode = "history"
                                st.session_state.user_active_urls = None
                                st.session_state._force_history_nav = True
                                st.session_state.sessions_cache_dirty = True
                                st.session_state.comments_cache_session_id = None
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
                            from scipy.special import softmax as _sm
                            X_batch = transform_with_saved_vectorizer(baseline_vec, df_run["cleaned_text"])
                            predictions = baseline_model.predict(X_batch)
                            if hasattr(baseline_model, "predict_proba"):
                                _probs = baseline_model.predict_proba(X_batch)
                            elif hasattr(baseline_model, "decision_function"):
                                _dec = baseline_model.decision_function(X_batch)
                                _probs = _sm(_dec if _dec.ndim == 2 else np.column_stack([-_dec, _dec]), axis=1)
                            else:
                                _probs = None
                            df_run["predicted_sentiment"] = predictions
                            df_run["model_confidence"] = _probs.max(axis=1).tolist() if _probs is not None else [1.0] * len(predictions)
                        else:
                            df_run["predicted_sentiment"] = "neutral"
                            df_run["model_confidence"] = None
                            
                        # Save
                        session = save_analysis(
                            user_id=st.session_state.user_id,
                            url="CSV Upload: " + st.session_state.user_active_file.name,
                            df=df_run
                        )
                        st.session_state.current_session_id = session["session_id"]
                        st.session_state.view_mode = "history"
                        st.session_state.user_active_file = None
                        st.session_state._force_history_nav = True
                        st.session_state.sessions_cache_dirty = True
                        st.session_state.comments_cache_session_id = None
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
            
        enable_translation = st.toggle("Translate Chichewa Comments", value=True)
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

                    # Compute max confidence for the badge
                    _badge_conf = float(np.max(probs)) if probs is not None else None
                    _conf_str   = f" · {_badge_conf:.1%}" if _badge_conf is not None else ""

                    if pred_label == "positive":
                        st.markdown(
                            f"<span class='badge badge-positive'>POSITIVE{_conf_str}</span>",
                            unsafe_allow_html=True,
                        )
                    elif pred_label == "negative":
                        st.markdown(
                            f"<span class='badge badge-negative'>NEGATIVE{_conf_str}</span>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"<span class='badge badge-neutral'>NEUTRAL{_conf_str}</span>",
                            unsafe_allow_html=True,
                        )

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
        
    # Render top input if not processing
    if not st.session_state.dev_processing and not st.session_state.get("batch_processing", False):
        with st.container(border=True):
            dev_url_text = st.text_input(
                "Facebook Post URL",
                placeholder="https://www.facebook.com/.../posts/...",
                key="dev_url_text_input",
            )
            dev_url_col, dev_file_col = st.columns([1, 1])
            with dev_url_col:
                if st.button("Use Facebook URL", type="primary", use_container_width=True, key="dev_use_url_btn"):
                    parsed_dev_urls = split_url_input(dev_url_text)
                    if len(parsed_dev_urls) != 1:
                        st.error("Please paste one Facebook URL for this scraper run.")
                    elif not is_facebook_url(parsed_dev_urls[0]):
                        st.error("Only Facebook URLs are allowed.")
                    else:
                        st.session_state.dev_active_url = parsed_dev_urls[0]
                        st.session_state.dev_active_file = None
                        st.session_state.batch_df = None
                        st.session_state.dev_scrape_results = None
            with dev_file_col:
                uploaded_dev_csv = st.file_uploader(
                    "Or upload CSV",
                    type=["csv"],
                    key="dev_top_csv_uploader",
                    label_visibility="collapsed",
                )
            if uploaded_dev_csv is not None:
                st.session_state.dev_active_file = uploaded_dev_csv
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
                if not is_facebook_url(st.session_state.dev_active_url):
                    st.error("Only Facebook URLs can be scraped. Please enter a valid Facebook URL.")
                elif not scrape_token and not has_token_file:
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
            if st.button("Stop Scrape", key="dev_cancel_scrape", type="secondary", use_container_width=True):
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
                            confidences = []
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
                                confidences.append(conf)
                                try:
                                    insert_prediction(comment_id=c_id, predicted_label=p_label, predicted_confidence=conf, score_negative=s_neg, score_neutral=s_neu, score_positive=s_pos, model_name=scrape_model_val, model_version=ver, model_family=fam)
                                    log_action(user_id=None, action_type="predict", comment_id=c_id, details={"source": "apify_scrape"})
                                    saved_preds += 1
                                except Exception:
                                    pass
                            
                            df_run["model_confidence"] = confidences
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
                    wedges_d, texts_d, autotexts_d = ax_pie_d.pie(
                        filtered_sizes_c, labels=filtered_labels_c,
                        autopct='%1.1f%%', shadow=False, startangle=140, colors=filtered_colors_c,
                        textprops=dict(color="#1E293B", weight="bold", size=10),
                        wedgeprops=dict(edgecolor='white', linewidth=1.0)
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
            render_styled_predictions_df(df_run, "text", "predicted_sentiment", "model_confidence")
            
            if st.button("Clear Results & Start New Scrape", key="dev_clear_results_btn"):
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
