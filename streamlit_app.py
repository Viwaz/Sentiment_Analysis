import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import os
import subprocess
import time
from pathlib import Path

# Set up page configurations
st.set_page_config(
    page_title="Low-Resource Sentiment Classifier",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        color: darkslategray !important;
        fill: darkslategray !important;
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
    """Runs a pipeline script in the background and returns status code, stdout, stderr"""
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


def render_batch_analysis(baseline_model, baseline_vec, transformers, paths, is_developer=True):
    st.markdown("### 📁 Batch Sentiment Analysis")
    st.write("Upload a CSV file containing comments, run the model, and download predictions.")
    
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
    
    # Initialize session state for batch results if not exists
    if "batch_df" not in st.session_state:
        st.session_state.batch_df = None
    if "batch_text_col" not in st.session_state:
        st.session_state.batch_text_col = None
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully!")
            
            # Find candidate text columns
            text_cols = [c for c in df.columns if any(x in c.lower() for x in ["text", "comment", "body"])]
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
                with st.spinner("Processing batch..."):
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
                    
            # Render results panel if we have results in session state
            if st.session_state.batch_df is not None:
                df_results = st.session_state.batch_df
                text_col = st.session_state.batch_text_col
                
                st.markdown("---")
                st.markdown("### 📊 Results Panel")
                
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
                    label="📥 Download Predictions CSV",
                    data=csv_data,
                    file_name="sentiment_predictions.csv",
                    mime="text/csv"
                )
                
        except Exception as e:
            st.error(f"Error processing CSV file: {e}")

# ----------------- UI Sidebar -----------------

st.sidebar.markdown(
    """
    <div style='text-align: center; margin-bottom: 20px;'>
        <h1 style='font-size: 2.2rem; margin-bottom: 0px;'>🇲🇼</h1>
        <h2 style='font-size: 1.3rem; margin-top: 5px; color:#4F46E5;'>Sentiment Classifier</h2>
        <span style='color: #64748B; font-size: 0.8rem;'>Facebook Code-Switched Low-Resource App</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")
if "logged_in_as_dev" not in st.session_state:
    st.session_state.logged_in_as_dev = False

is_developer = st.session_state.logged_in_as_dev

if not is_developer:
    st.sidebar.subheader("🔐 Access Control")
    role_choice = st.sidebar.selectbox("Select Role", ["User", "Developer"], index=0)
    if role_choice == "Developer":
        passcode = st.sidebar.text_input("Developer Passcode", type="password", help="Enter passcode to access developer controls.")
        # We can either use a submit button or just trigger on enter.
        # Streamlit natively handles "Enter to apply" on text inputs.
        if passcode == "dev123":
            st.session_state.logged_in_as_dev = True
            st.rerun()
        elif passcode != "":
            st.sidebar.error("❌ Invalid Passcode")
            st.sidebar.info("Enter 'dev123' to unlock.")
    else:
        st.sidebar.info("👥 General User mode active.")
else:
    st.sidebar.success("🔑 Developer access active")
    if st.sidebar.button("Logout", key="sidebar_logout", use_container_width=True):
        st.session_state.logged_in_as_dev = False
        st.rerun()

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
        st.sidebar.success("✅ Baseline Model: Available")
    else:
        st.sidebar.error("❌ Baseline Model: Missing")

    if transformers:
        st.sidebar.success(f"✅ Transformers: {len(transformers)} Available")
        for t in transformers:
            st.sidebar.markdown(f"- `{t}`")
    else:
        st.sidebar.warning("⚠️ Transformers: None found locally")

# ----------------- UI Tabs / Views -----------------

if not is_developer:
    # ── User Mode: Web Scraper ──────────────────────────────────────────────
    st.markdown("### 🔗 Analyse a Facebook Post")
    st.write("Paste a Facebook post URL below. We will automatically collect the comments, analyse the sentiment, and store everything in the database.")

    user_url_path = Path("secret/url.txt")
    default_user_url = user_url_path.read_text(encoding="utf-8").strip() if user_url_path.exists() else ""
    user_scrape_url = st.text_input("Facebook Post URL", value=default_user_url, placeholder="https://www.facebook.com/...", key="user_scrape_url")

    u_col1, u_col2 = st.columns(2)
    with u_col1:
        user_scrape_limit = st.number_input("Max Comments to Collect", min_value=1, max_value=500, value=50, key="user_scrape_limit")
    with u_col2:
        user_token_path = Path("secret/token.txt")
        default_user_token = user_token_path.read_text(encoding="utf-8").strip() if user_token_path.exists() else (os.getenv("APIFY_API_TOKEN") or "")
        user_has_token = bool(default_user_token)
        if user_has_token:
            st.success("✅ Apify API Token loaded from configuration.")
            user_scrape_token = default_user_token
        else:
            user_scrape_token = st.text_input(
                "Apify API Token",
                type="password",
                placeholder="Required if not pre-configured",
                help="Enter your Apify API token to enable scraping.",
                key="user_apify_token"
            )

    if st.button("🚀 Scrape & Analyse", type="primary", disabled=not user_scrape_url, key="user_scrape_btn"):
        if not user_scrape_token and not user_has_token:
            st.error("⚠️ Please enter your Apify API Token to proceed.")
        else:
            with st.spinner("🔍 Scraping comments from Facebook via Apify... (this may take a minute)"):
                try:
                    from src.collect_apify import collect_facebook_comments, persist_collected_comments_to_db
                    token_to_use = user_scrape_token if user_scrape_token else None
                    collected_df = collect_facebook_comments(
                        urls=[user_scrape_url],
                        limit=user_scrape_limit,
                        token=token_to_use,
                        mode="sync"
                    )
                    st.success(f"✅ Scraped {len(collected_df)} comments!")

                    with st.spinner("💾 Saving to database..."):
                        persist_collected_comments_to_db(collected_df)

                    with st.spinner("🤖 Running sentiment predictions..."):
                        from src.evaluate_external import transform_with_saved_vectorizer
                        from src.db.predictions import insert_prediction
                        from src.db.activity import log_action
                        import uuid

                        df_user = collected_df.copy()

                        if baseline_model is not None:
                            X = transform_with_saved_vectorizer(baseline_vec, df_user["cleaned_text"])
                            preds = baseline_model.predict(X)
                            if hasattr(baseline_model, "predict_proba"):
                                probs = baseline_model.predict_proba(X)
                            else:
                                probs = None

                            df_user["predicted_sentiment"] = preds
                            classes = list(getattr(baseline_model, "classes_", ["negative", "neutral", "positive"]))

                            for i, row in df_user.iterrows():
                                c_id = str(row.get("comment_id")) if pd.notna(row.get("comment_id")) else str(uuid.uuid4())
                                p_label = row["predicted_sentiment"]
                                conf = float(np.max(probs[i])) if probs is not None else 1.0
                                s_neg = float(probs[i][classes.index("negative")]) if probs is not None and "negative" in classes else 0.0
                                s_neu = float(probs[i][classes.index("neutral")]) if probs is not None and "neutral" in classes else 0.0
                                s_pos = float(probs[i][classes.index("positive")]) if probs is not None and "positive" in classes else 0.0
                                try:
                                    insert_prediction(
                                        comment_id=c_id, predicted_label=p_label,
                                        predicted_confidence=conf, score_negative=s_neg,
                                        score_neutral=s_neu, score_positive=s_pos,
                                        model_name="TF-IDF Baseline", model_version="baseline",
                                        model_family="classical_ml"
                                    )
                                    log_action(user_id=None, action_type="predict", comment_id=c_id, details={"source": "user_apify_scrape"})
                                except Exception:
                                    pass

                        st.success("🎉 Analysis complete! Results are shown below.")

                        # Display a nice results table
                        pos_count = (df_user["predicted_sentiment"] == "positive").sum()
                        neg_count = (df_user["predicted_sentiment"] == "negative").sum()
                        neu_count = (df_user["predicted_sentiment"] == "neutral").sum()

                        r1, r2, r3 = st.columns(3)
                        r1.metric("😊 Positive", pos_count)
                        r2.metric("😠 Negative", neg_count)
                        r3.metric("😐 Neutral", neu_count)

                        st.markdown("#### Comment Breakdown")
                        st.dataframe(
                            df_user[["text", "predicted_sentiment"]].rename(columns={"text": "Comment", "predicted_sentiment": "Sentiment"}),
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"❌ Something went wrong during scraping: {e}")

    st.markdown("---")
    st.markdown("### 📁 Or Upload a CSV File for Batch Analysis")
    render_batch_analysis(baseline_model, baseline_vec, transformers, paths, is_developer=False)
    st.markdown(
        """
        <div class='footer'>
            Low-Resource Facebook Sentiment Classifier Prototype Dashboard. Powered by Streamlit.
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

# Below is only accessible to verified Developers
tab_live, tab_batch, tab_scrape, tab_active, tab_metrics, tab_controls, tab_db = st.tabs([
    "💬 Live Sentiment Classifier", 
    "📁 Batch Analysis (CSV)", 
    "🔗 Web Scraper (Apify)",
    "🎯 Active Learning Assistant", 
    "📊 Performance Dashboard", 
    "⚙️ Pipeline & Control Panel",
    "🗄️ Database Logs"
])

# ----------------- Tab 1: Live Sentiment Classifier -----------------
with tab_live:
    st.markdown("### 💬 Single Comment Sentiment Checker")
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
                        st.success("✅ Prediction successfully saved to the database!")
                    except Exception as db_err:
                        st.warning(f"⚠️ Prediction succeeded, but couldn't save to Database (Is the DB running?). Error: {db_err}")
                            
                except Exception as e:
                    st.error(f"Error during prediction: {e}")
                    
# ----------------- Tab 2: Batch Sentiment Analysis -----------------
with tab_batch:
    render_batch_analysis(baseline_model, baseline_vec, transformers, paths, is_developer=is_developer)
            
# ----------------- Tab 3: Web Scraper (Apify) -----------------
with tab_scrape:
    st.subheader("🔗 Web Scraper (Apify)")
    st.write("Automate comment collection directly from Facebook. Data is automatically cleaned and saved to the database.")
    
    # Check if URL exists in file
    url_path = Path("secret/url.txt")
    default_url = url_path.read_text(encoding="utf-8").strip() if url_path.exists() else ""
    scrape_url = st.text_input("Facebook Post URL", value=default_url, placeholder="https://www.facebook.com/...", key="scrape_url")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        scrape_limit = st.number_input("Max Comments to Scrape", min_value=1, max_value=1000, value=50)
    with col_s2:
        # Check if token exists in file/env
        token_path = Path("secret/token.txt")
        default_token = token_path.read_text(encoding="utf-8").strip() if token_path.exists() else (os.getenv("APIFY_API_TOKEN") or "")
        has_token_file = bool(default_token)
        if has_token_file:
            st.success("✅ Apify API Token loaded from configuration.")
            scrape_token = default_token
        else:
            scrape_token = st.text_input("Apify API Token", type="password", placeholder="Required if not set in environment", help="Enter your Apify token if not configured in the system.")
    with col_s3:
        available_options = []
        if baseline_model is not None:
            available_options.append("TF-IDF Baseline")
        for t in transformers:
            available_options.append(f"Transformer ({t})")
            
        scrape_model = st.selectbox("Classification Model", available_options, key="scrape_model_sel") if available_options else None
        
    if st.button("🚀 Scrape & Predict", type="primary", disabled=(not scrape_url or scrape_model is None)):
        if not scrape_token and not has_token_file:
            st.error("Missing Apify API Token. Please enter one above.")
        else:
            with st.spinner("Scraping comments from Facebook using Apify... (this may take a minute)"):
                try:
                    from src.collect_apify import collect_facebook_comments, persist_collected_comments_to_db
                    
                    # 1. Scrape comments
                    token_to_use = scrape_token if scrape_token else None
                    collected_df = collect_facebook_comments(
                        urls=[scrape_url],
                        limit=scrape_limit,
                        token=token_to_use,
                        mode="sync" # sync mode since we want results immediately in UI for demo limit
                    )
                    
                    st.success(f"✅ Successfully scraped {len(collected_df)} comments!")
                    
                    # 2. Save to database
                    with st.spinner("Saving raw and preprocessed comments to database..."):
                        db_res = persist_collected_comments_to_db(collected_df)
                        
                    # 3. Predict sentiment
                    with st.spinner(f"Running predictions using {scrape_model}..."):
                        from src.db.predictions import insert_prediction
                        from src.db.activity import log_action
                        
                        df_run = collected_df.copy()
                        # Run predictions just like batch logic
                        if scrape_model == "TF-IDF Baseline":
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
                            run_id = scrape_model.replace("Transformer (", "").rstrip(")")
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
                        
                        # Save predictions to database
                        fam = "transformer" if "Transformer" in scrape_model else "classical_ml"
                        ver = run_id if fam == "transformer" else "baseline"
                        
                        classes = getattr(baseline_model, "classes_", ["negative", "neutral", "positive"]) if fam == "classical_ml" else ["negative", "neutral", "positive"]
                        
                        saved_preds = 0
                        for idx, row in df_run.iterrows():
                            # ID logic matching persist_collected_comments_to_db
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
                                p_id = insert_prediction(
                                    comment_id=c_id,
                                    predicted_label=p_label,
                                    predicted_confidence=conf,
                                    score_negative=s_neg,
                                    score_neutral=s_neu,
                                    score_positive=s_pos,
                                    model_name=scrape_model,
                                    model_version=ver,
                                    model_family=fam
                                )
                                log_action(user_id=None, action_type="predict", comment_id=c_id, details={"source": "apify_scrape"})
                                saved_preds += 1
                            except Exception:
                                pass
                                
                    st.success(f"✅ Predicted and saved {saved_preds} comments to the database!")
                    
                    st.markdown("#### Scraped Results")
                    st.dataframe(df_run[["text", "cleaned_text", "predicted_sentiment"]].head(100), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Error during scraping pipeline: {e}")

# ----------------- Tab 4: Active Learning Assistant -----------------
with tab_active:
    st.markdown("### 🎯 Active Learning Annotation Assistant")
    st.write(
        "Upload a pool of unlabeled comments. The system will run the baseline model to find the most "
        "uncertain comments (high entropy/least confidence), allowing you to annotate them here and expand the training set."
    )
    
    # Check if baseline model is trained
    if baseline_model is None:
        st.error("Baseline model is required for Active Learning uncertainty estimation. Please train it first.")
    else:
        # Load unlabeled file
        scratch_dir = paths.root / "data" / "scratch"
        scratch_dir.mkdir(parents=True, exist_ok=True)
        unlabeled_files = sorted(list(scratch_dir.glob("*.csv")))
        
        col_pool, col_params = st.columns([2, 1])
        with col_pool:
            pool_source = st.radio("Unlabeled Data Source:", ["Select Scratch CSV File", "Upload Custom CSV File"])
            
            unlabeled_path = None
            unlabeled_df = None
            
            if pool_source == "Select Scratch CSV File":
                if not unlabeled_files:
                    st.warning("No CSV files found in data/scratch/. Please upload one.")
                else:
                    file_names = [f.name for f in unlabeled_files]
                    selected_file_name = st.selectbox("Select Scratch CSV File", file_names)
                    unlabeled_path = scratch_dir / selected_file_name
                    if unlabeled_path.exists():
                        unlabeled_df = pd.read_csv(unlabeled_path)
            else:
                uploaded_pool = st.file_uploader("Upload Unlabeled CSV File", type=["csv"], key="pool_uploader")
                if uploaded_pool is not None:
                    unlabeled_df = pd.read_csv(uploaded_pool)
                    
        with col_params:
            strategy = st.selectbox("Uncertainty Query Strategy", ["entropy", "margin", "lc"], index=0, 
                                    help="Entropy: highest randomness. Margin: closest top-2. Least Confidence: smallest maximum probability.")
            n_query = st.number_input("Number of samples to query", min_value=1, max_value=500, value=20)
            
        if unlabeled_df is not None:
            st.write(f"Total Comments in Pool: {len(unlabeled_df)}")
            
            # Find text and ID columns
            text_cols = [c for c in unlabeled_df.columns if any(x in c.lower() for x in ["text", "comment", "body"])]
            text_col = st.selectbox("Unlabeled Comment Column", unlabeled_df.columns, index=unlabeled_df.columns.get_loc(text_cols[0]) if text_cols else 0)
            
            id_cols = [c for c in unlabeled_df.columns if any(x in c.lower() for x in ["id", "index"])]
            id_col = st.selectbox("Unlabeled ID Column (Optional)", ["None"] + list(unlabeled_df.columns), 
                                   index=unlabeled_df.columns.get_loc(id_cols[0]) + 1 if id_cols else 0)
            
            run_al_btn = st.button("🔍 Find Uncertain Comments")
            
            # Keep active learning query state in Streamlit session state
            if "al_df" not in st.session_state:
                st.session_state.al_df = None
            if "al_index" not in st.session_state:
                st.session_state.al_index = 0
            if "al_annotations" not in st.session_state:
                st.session_state.al_annotations = []
                
            if run_al_btn:
                with st.spinner("Analyzing comment uncertainties..."):
                    try:
                        # Clean texts
                        from src.preprocess import clean_text
                        df_al = unlabeled_df.copy()
                        df_al = df_al.rename(columns={text_col: "text"})
                        
                        if id_col != "None" and id_col != "text":
                            df_al = df_al.rename(columns={id_col: "id"})
                        else:
                            df_al["id"] = range(10000, 10000 + len(df_al))
                            
                        # Drop missing text
                        df_al = df_al[df_al["text"].notna() & df_al["text"].astype(str).str.strip().ne("")].copy()
                        df_al["cleaned_text"] = df_al["text"].apply(clean_text)
                        
                        # Calculate features and uncertainty scores
                        # LinearSVC doesn't support predict_proba — use decision_function fallback
                        from src.evaluate_external import transform_with_saved_vectorizer
                        from src.active_learning import compute_entropy, compute_margin, compute_least_confidence
                        X_al = transform_with_saved_vectorizer(baseline_vec, df_al["cleaned_text"])

                        if hasattr(baseline_model, "predict_proba"):
                            probs = baseline_model.predict_proba(X_al)
                            if strategy == "entropy":
                                scores = compute_entropy(probs)
                            elif strategy == "margin":
                                scores = compute_margin(probs)
                            else:
                                scores = compute_least_confidence(probs)
                        elif hasattr(baseline_model, "decision_function"):
                            # LinearSVC fallback — use margin of top-2 decision scores as uncertainty
                            st.info(
                                "ℹ️ The saved model (LinearSVC) does not support probability estimates. "
                                "Using decision function margin as uncertainty score instead."
                            )
                            decisions = baseline_model.decision_function(X_al)
                            if len(decisions.shape) == 1 or decisions.shape[1] == 1:
                                scores = -np.abs(decisions)
                            else:
                                sorted_dec = np.sort(decisions, axis=1)
                                scores = -(sorted_dec[:, -1] - sorted_dec[:, -2])
                        else:
                            raise AttributeError(
                                "The saved baseline model supports neither predict_proba nor decision_function. "
                                "Please retrain the baseline with a Logistic Regression or Naive Bayes model."
                            )
                            
                        df_al["uncertainty_score"] = scores
                        
                        # Filter duplicates from existing cleaned comments
                        cleaned_path = paths.interim_dir / "cleaned_comments.csv"
                        if cleaned_path.exists():
                            annotated_df = pd.read_csv(cleaned_path)
                            if "cleaned_text" in annotated_df.columns:
                                annotated_texts = set(annotated_df["cleaned_text"].tolist())
                                df_al = df_al[~df_al["cleaned_text"].isin(annotated_texts)].copy()
                                
                        # Sort and get top
                        df_al_sorted = df_al.sort_values(by="uncertainty_score", ascending=False).head(n_query)
                        
                        st.session_state.al_df = df_al_sorted.reset_index(drop=True)
                        st.session_state.al_index = 0
                        st.session_state.al_annotations = []
                        st.success(f"Successfully queried {len(df_al_sorted)} uncertain comments!")
                    except Exception as e:
                        st.error(f"Failed to query comments: {e}")
                        
            # ── Bulk Annotation Interface ──
            if st.session_state.al_df is not None and len(st.session_state.al_df) > 0:
                al_df = st.session_state.al_df

                st.markdown("---")
                st.markdown(
                    f"#### 📝 Annotate All {len(al_df)} Uncertain Comments",
                )
                st.caption(
                    "Label every comment below, then click **Submit All Annotations** at the bottom. "
                    "You can skip any comment by unchecking *Include in Training Pool*."
                )

                # Column headers
                hcol1, hcol2, hcol3, hcol4 = st.columns([5, 2, 1, 2])
                with hcol1:
                    st.markdown("**Comment**")
                with hcol2:
                    st.markdown("**Sentiment Label**")
                with hcol3:
                    st.markdown("**Include**")
                with hcol4:
                    st.markdown("**Uncertainty Score**")

                st.markdown("<hr style='margin:4px 0 10px 0; border-color:#E2E8F0;'>", unsafe_allow_html=True)

                # One row per comment
                bulk_labels   = {}
                bulk_includes = {}

                for i, row in al_df.iterrows():
                     col_text, col_label, col_inc, col_score = st.columns([5, 2, 1, 2])

                     with col_text:
                         st.markdown(
                             f"""
                             <div style='padding:10px 12px; background:white; border-radius:10px;
                                         border:1px solid #E2E8F0; font-size:0.92rem; line-height:1.5;
                                         box-shadow:0 2px 6px rgba(0,0,0,0.04);'>
                                 {row["text"]}
                             </div>
                             """,
                             unsafe_allow_html=True,
                         )

                     with col_label:
                         bulk_labels[i] = st.selectbox(
                             label="label",
                             options=["positive", "negative", "neutral"],
                             index=0,
                             key=f"bulk_label_{i}",
                             label_visibility="collapsed",
                         )

                     with col_inc:
                         bulk_includes[i] = st.checkbox(
                             label="inc",
                             value=True,
                             key=f"bulk_inc_{i}",
                             label_visibility="collapsed",
                         )

                     with col_score:
                         score_val = row["uncertainty_score"]
                         bar_pct   = min(abs(score_val) / max(al_df["uncertainty_score"].abs().max(), 1e-9), 1.0)
                         bar_color = "#6366F1"
                         st.markdown(
                             f"""
                             <div style='padding:8px 0;'>
                                 <span style='font-weight:600; font-size:0.9rem; color:#1E293B;'>{score_val:.4f}</span>
                                 <div style='background:#EEF2FF; border-radius:999px; height:6px; margin-top:4px;'>
                                     <div style='width:{bar_pct*100:.1f}%; background:{bar_color};
                                                 border-radius:999px; height:6px;'></div>
                                 </div>
                             </div>
                             """,
                             unsafe_allow_html=True,
                         )

                     st.markdown("<div style='margin-bottom:6px;'></div>", unsafe_allow_html=True)

                st.markdown("---")

                # Summary preview
                included_count = sum(1 for v in bulk_includes.values() if v)
                st.markdown(
                    f"**{included_count} of {len(al_df)} comments** marked for inclusion in the training pool.",
                    help="Uncheck *Include* on any comment you want to skip."
                )

                if st.button("✅ Submit All Annotations", type="primary"):
                    annotations = []
                    for i, row in al_df.iterrows():
                        annotations.append({
                            "id":              int(row["id"]),
                            "text":            row["text"],
                            "sentiment_label": bulk_labels[i],
                            "include":         "Yes" if bulk_includes[i] else "No",
                            "notes":           f"[AL {strategy}: {row['uncertainty_score']:.4f}]",
                        })
                    st.session_state.al_annotations = annotations
                    st.session_state.al_submitted = True
                    st.rerun()

            # ── Save Section (shown after submission) ──
            if st.session_state.get("al_submitted") and st.session_state.al_annotations:
                st.balloons()
                st.success(f"🎉 {len(st.session_state.al_annotations)} annotations ready to save!")

                new_anno_df = pd.DataFrame(st.session_state.al_annotations)
                st.dataframe(new_anno_df, use_container_width=True)

                from src.data_utils import discover_raw_files
                raw_files = discover_raw_files(paths.raw_dir)
                raw_file_options = [f.name for f in raw_files] + ["Create New File (active_annotations.csv)"]
                target_file_choice = st.selectbox(
                    "Select Target CSV File in data/raw/", raw_file_options, key="al_target_file"
                )

                if st.button("💾 Append & Save to Raw Training Pool"):
                    try:
                        target_path = (
                            paths.raw_dir / "active_annotations.csv"
                            if target_file_choice == "Create New File (active_annotations.csv)"
                            else paths.raw_dir / target_file_choice
                        )
                        if target_path.exists():
                            existing_raw = pd.read_csv(target_path)
                            for col in ["id", "text", "sentiment_label", "include", "notes"]:
                                if col not in existing_raw.columns:
                                    existing_raw[col] = ""
                            combined = pd.concat([existing_raw, new_anno_df], ignore_index=True)
                        else:
                            combined = new_anno_df

                        combined.to_csv(target_path, index=False, encoding="utf-8")
                        st.success(f"✅ Saved {len(new_anno_df)} annotations to **{target_path.name}**!")

                        # Reset state
                        st.session_state.al_df          = None
                        st.session_state.al_index       = 0
                        st.session_state.al_annotations = []
                        st.session_state.al_submitted   = False
                    except Exception as e:
                        st.error(f"Failed to save annotations: {e}")


# ----------------- Tab 4: Performance Dashboard -----------------
with tab_metrics:
    st.markdown("### 📊 Performance Dashboard & Model Comparison")
    st.write("Compare trained models across validation and test splits using metrics and confusion matrices.")
    
    compare_path = paths.results_dir / "model_comparison.csv"
    if compare_path.exists():
        compare_df = pd.read_csv(compare_path)
        # Highlight best model
        st.markdown("#### Model Rankings")
        st.dataframe(
            compare_df.sort_values(by="macro_f1", ascending=False).style.highlight_max(axis=0, subset=["macro_f1", "accuracy"], color="#BCF0DA"),
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
    st.markdown("### ⚙️ Pipeline Control Panel")
    st.write("Run the core data preprocessing and baseline model training scripts directly from this dashboard.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            """
            <div class='metric-card'>
                <h4>1. Run Preprocessing Pipeline</h4>
                <p style='color:#64748B;'>Reads raw csv comments from data/raw/, normalizes labels, filters noise, deduplicates, and splits data into train/val/test CSVs.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        run_prep = st.button("🚀 Run Preprocessing")
        if run_prep:
            with st.spinner("Executing Preprocessing..."):
                ret_code, stdout, stderr = run_script("src.preprocess")
                if ret_code == 0:
                    st.success("Preprocessing executed successfully!")
                    st.text_area("Execution Log (Stdout)", stdout, height=200)
                    st.rerun() # Refresh layout to load new metadata
                else:
                    st.error(f"Preprocessing failed with exit code: {ret_code}")
                    st.text_area("Error Log (Stderr)", stderr, height=200)
                    
    with col2:
        st.markdown(
            """
            <div class='metric-card'>
                <h4>2. Train Baseline Models</h4>
                <p style='color:#64748B;'>Trains Logistic Regression, SVM, and Naive Bayes on processed splits, compares TF-IDF features, and saves the best baseline model.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        run_baseline = st.button("🚀 Train Baseline Models")
        if run_baseline:
            with st.spinner("Training models (takes a few seconds)..."):
                ret_code, stdout, stderr = run_script("src.train_baseline")
                if ret_code == 0:
                    st.success("Baseline training completed!")
                    st.text_area("Execution Log (Stdout)", stdout, height=200)
                    # Automatically rebuild model comparison
                    run_script("src.compare_models")
                    st.rerun()
                else:
                    st.error(f"Baseline training failed with exit code: {ret_code}")
                    st.text_area("Error Log (Stderr)", stderr, height=200)

# ----------------- Tab 6: Database Logs -----------------
with tab_db:
    st.markdown("### 🗄️ Database Logs")
    st.write("View recent predictions saved to the PostgreSQL database.")
    
    col_db1, col_db2 = st.columns([4, 1])
    with col_db1:
        st.info("💡 **Tip**: When you classify a single comment in the 'Live Sentiment Classifier' tab, it is automatically saved to the database and will appear here.")
    with col_db2:
        if st.button("🔄 Refresh Data", use_container_width=True):
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
