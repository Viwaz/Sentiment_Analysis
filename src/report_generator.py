import os
import tempfile
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from fpdf import FPDF


def sanitize_for_pdf(text: str) -> str:
    """Strip or replace characters outside the Helvetica-supported Latin-1 range.

    Replaces common typographic quotes/dashes with their ASCII equivalents,
    then encodes to latin-1 with 'replace' so that emoji and other multi-byte
    characters become '?' rather than crashing fpdf.
    """
    if not isinstance(text, str):
        return ""
    # Common unicode → ASCII look-alikes
    _replacements = {
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",  # non-breaking space
    }
    for src, dst in _replacements.items():
        text = text.replace(src, dst)
    return text.encode("latin-1", "replace").decode("latin-1")


class SentimentReportPDF(FPDF):
    def header(self):
        # Dark slate header banner
        self.set_fill_color(30, 41, 59)
        self.rect(0, 0, 210, 40, "F")

        self.set_text_color(255, 255, 255)
        self.set_font("helvetica", "B", 18)
        self.set_xy(10, 12)
        self.cell(0, 10, "Facebook Sentiment Analysis Report", border=0, align="L")

        self.set_font("helvetica", "I", 10)
        self.set_xy(10, 22)
        self.cell(0, 10, "Low-Resource Post Sentiment Classification", border=0, align="L")

        self.ln(25)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", border=0, align="C")


def _save_pil_to_temp(pil_img) -> str | None:
    """Save a PIL Image to a temp PNG file and return the path."""
    try:
        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        pil_img.save(path)
        return path
    except Exception:
        return None


def _cleanup(*paths: str | None) -> None:
    for p in paths:
        if p and os.path.exists(p):
            try:
                os.remove(p)
            except OSError:
                pass


def create_report_pdf(
    url: str,
    timestamp: str,
    df: pd.DataFrame,
    wordclouds: dict | None = None,
) -> bytes:
    """Generate a professional multi-page PDF report.

    Args:
        url: Source URL / filename for the session.
        timestamp: Human-readable timestamp string.
        df: DataFrame containing predictions (columns: text / comment_text,
            predicted_sentiment / sentiment_label, model_confidence).
        wordclouds: Optional dict mapping label → PIL Image  (keys: "All",
            "Positive", "Negative", "Neutral").  These are embedded as a
            dedicated Word Cloud page in the PDF.

    Returns:
        Raw PDF bytes.
    """
    df = df.copy()

    # ── 1. Stats ──────────────────────────────────────────────────────────────
    total = len(df)
    sent_col = (
        "predicted_sentiment"
        if "predicted_sentiment" in df.columns
        else ("sentiment_label" if "sentiment_label" in df.columns else None)
    )
    conf_col = "model_confidence" if "model_confidence" in df.columns else None

    if sent_col:
        df["_sent_clean"] = df[sent_col].fillna("neutral").str.lower()
        pos = int((df["_sent_clean"] == "positive").sum())
        neg = int((df["_sent_clean"] == "negative").sum())
        neu = int((df["_sent_clean"] == "neutral").sum())
    else:
        pos = neg = neu = 0

    # ── 2. Sentiment distribution chart (pie + bar) ───────────────────────────
    temp_chart_path = None
    if total > 0 and sent_col:
        labels_all    = ["Positive", "Neutral", "Negative"]
        sizes_all     = [pos, neu, neg]
        colors_all    = ["#10B981", "#F59E0B", "#EF4444"]
        f_labels      = [l for l, s in zip(labels_all, sizes_all) if s > 0]
        f_sizes       = [s for s in sizes_all if s > 0]
        f_colors      = [c for c, s in zip(colors_all, sizes_all) if s > 0]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

        ax1.pie(
            f_sizes,
            explode=[0.05] * len(f_sizes),
            labels=f_labels,
            autopct="%1.1f%%",
            shadow=True,
            startangle=140,
            colors=f_colors,
            textprops=dict(color="#1E293B", weight="bold", size=10),
            wedgeprops=dict(edgecolor="white", linewidth=1.5),
        )
        ax1.axis("equal")
        ax1.set_title("Sentiment Distribution", fontsize=12, pad=10, weight="bold")

        sdf = pd.DataFrame({"Sentiment": f_labels, "Count": f_sizes})
        sns.barplot(
            x="Count", y="Sentiment", data=sdf,
            palette=f_colors, ax=ax2, hue="Sentiment", legend=False,
        )
        for sp in ("top", "right"):
            ax2.spines[sp].set_visible(False)
        ax2.spines["left"].set_color("#CBD5E1")
        ax2.spines["bottom"].set_color("#CBD5E1")
        ax2.tick_params(colors="#475569", labelsize=10)
        ax2.set_ylabel("")
        ax2.set_xlabel("Count")
        ax2.set_title("Sentiment Counts", fontsize=12, pad=10, weight="bold")
        for container in ax2.containers:
            ax2.bar_label(container, fmt="%d", padding=5, color="#1E293B",
                          weight="bold", fontsize=10)

        plt.tight_layout()
        fd, temp_chart_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        plt.savefig(temp_chart_path, dpi=200)
        plt.close(fig)

    # ── 3. Build PDF ──────────────────────────────────────────────────────────
    pdf = SentimentReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # Session summary
    pdf.set_text_color(30, 41, 59)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Session Analysis Summary", border=0, align="L")
    pdf.ln(8)

    def _meta_row(label: str, value: str) -> None:
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(40, 6, label, border=0)
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 6, sanitize_for_pdf(value), border=0)
        pdf.ln(6)

    display_url = url if len(url) <= 75 else url[:72] + "..."
    _meta_row("Post / Source URL:", display_url)
    _meta_row("Date Run:", str(timestamp))
    _meta_row("Total Comments:", str(total))
    pdf.ln(6)

    # Metrics colour band
    if total > 0:
        pdf.set_fill_color(248, 250, 252)
        pdf.rect(10, pdf.get_y(), 190, 20, "F")
        pdf.set_font("helvetica", "B", 10)

        pdf.set_text_color(22, 163, 74)
        pdf.set_xy(15, pdf.get_y() + 4)
        pdf.cell(60, 6, f"Positive: {pos} ({pos/total:.1%})", border=0)

        pdf.set_text_color(217, 119, 6)
        pdf.set_x(75)
        pdf.cell(60, 6, f"Neutral:  {neu} ({neu/total:.1%})", border=0)

        pdf.set_text_color(220, 38, 38)
        pdf.set_x(135)
        pdf.cell(60, 6, f"Negative: {neg} ({neg/total:.1%})", border=0)

        pdf.ln(16)

    # Embed distribution chart
    if temp_chart_path and os.path.exists(temp_chart_path):
        pdf.image(temp_chart_path, x=10, y=pdf.get_y(), w=190)
        pdf.ln(92)

    # ── 4. Word Cloud page ────────────────────────────────────────────────────
    if wordclouds:
        wc_temp_paths: list[str | None] = []
        wc_items = [
            ("All Comments Word Cloud",  wordclouds.get("All")),
            ("Positive Comments Cloud",  wordclouds.get("Positive")),
            ("Negative Comments Cloud",  wordclouds.get("Negative")),
            ("Neutral Comments Cloud",   wordclouds.get("Neutral")),
        ]
        available = [(title, img) for title, img in wc_items if img is not None]

        if available:
            pdf.add_page()
            pdf.set_text_color(30, 41, 59)
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, "Sentiment Word Cloud Visualisations", border=0)
            pdf.ln(10)

            for title, pil_img in available:
                tp = _save_pil_to_temp(pil_img)
                wc_temp_paths.append(tp)
                if tp:
                    pdf.set_font("helvetica", "B", 11)
                    pdf.set_text_color(71, 85, 105)
                    pdf.cell(0, 7, title, border=0)
                    pdf.ln(7)
                    pdf.image(tp, x=10, y=pdf.get_y(), w=190)
                    pdf.ln(62)

            _cleanup(*wc_temp_paths)

    # ── 5. Comment predictions log ────────────────────────────────────────────
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, "Sample Comment Predictions Log", border=0)
    pdf.ln(10)

    # Header row
    pdf.set_fill_color(30, 41, 59)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(115, 8, " Comment Text",  border=1, fill=True)
    pdf.cell(35,  8, " Sentiment",     border=1, fill=True, align="C")
    pdf.cell(40,  8, " Confidence",    border=1, fill=True, align="C")
    pdf.ln(8)

    text_col_name = next(
        (c for c in ("text", "comment_text", "commentText") if c in df.columns),
        None,
    )
    pdf.set_font("helvetica", "", 8.5)
    fill_row = False

    for _, row in df.head(45).iterrows():
        pdf.set_fill_color(248, 250, 252) if fill_row else pdf.set_fill_color(255, 255, 255)

        raw_txt = str(row.get(text_col_name, "")) if text_col_name else ""
        txt = sanitize_for_pdf(raw_txt)
        if len(txt) > 65:
            txt = txt[:62] + "..."

        sent_raw = str(row.get(sent_col, "neutral")) if sent_col else "neutral"
        sent = sanitize_for_pdf(sent_raw).upper()

        conf_val = row.get(conf_col) if conf_col else None
        conf_str = f"{float(conf_val):.1%}" if conf_val is not None and pd.notna(conf_val) else "N/A"

        pdf.set_text_color(15, 23, 42)
        pdf.cell(115, 7, f" {txt}", border=1, fill=True)

        if sent == "POSITIVE":
            pdf.set_text_color(22, 163, 74)
        elif sent == "NEGATIVE":
            pdf.set_text_color(220, 38, 38)
        else:
            pdf.set_text_color(217, 119, 6)

        pdf.cell(35, 7, f" {sent}", border=1, fill=True, align="C")
        pdf.set_text_color(15, 23, 42)
        pdf.cell(40, 7, f" {conf_str}", border=1, fill=True, align="C")
        pdf.ln(7)
        fill_row = not fill_row

    # ── 6. Cleanup temp files ─────────────────────────────────────────────────
    _cleanup(temp_chart_path)

    return bytes(pdf.output())
