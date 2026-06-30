import os
import tempfile
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from fpdf import FPDF

class SentimentReportPDF(FPDF):
    def header(self):
        # Header banner
        self.set_fill_color(30, 41, 59) # Slate 800
        self.rect(0, 0, 210, 40, 'F')
        
        self.set_text_color(255, 255, 255)
        self.set_font('helvetica', 'B', 18)
        self.set_xy(10, 12)
        self.cell(0, 10, 'Facebook Sentiment Analysis Report', border=0, align='L')
        
        self.set_font('helvetica', 'I', 10)
        self.set_xy(10, 22)
        self.cell(0, 10, 'Low-Resource Post Sentiment Classification', border=0, align='L')
        
        self.ln(25)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', border=0, align='C')

def create_report_pdf(url: str, timestamp: str, df: pd.DataFrame) -> bytes:
    # 1. Calculate stats
    total = len(df)
    sent_col = "predicted_sentiment" if "predicted_sentiment" in df.columns else ("sentiment_label" if "sentiment_label" in df.columns else None)
    conf_col = "model_confidence" if "model_confidence" in df.columns else None
    
    if sent_col:
        df["_sent_clean"] = df[sent_col].fillna("neutral").str.lower()
        pos = int((df["_sent_clean"] == "positive").sum())
        neg = int((df["_sent_clean"] == "negative").sum())
        neu = int((df["_sent_clean"] == "neutral").sum())
    else:
        pos, neg, neu = 0, 0, 0

    # 2. Draw standard Matplotlib charts and save to temp file
    temp_img_path = None
    if total > 0 and sent_col:
        labels = ['Positive', 'Neutral', 'Negative']
        sizes = [pos, neu, neg]
        filtered_labels = [l for l, s in zip(labels, sizes) if s > 0]
        filtered_sizes = [s for s in sizes if s > 0]
        colors = ['#10B981', '#F59E0B', '#EF4444']
        filtered_colors = [c for c, s in zip(colors, sizes) if s > 0]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
        
        # Pie chart
        explode = [0.05] * len(filtered_sizes)
        ax1.pie(
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
        ax1.axis('equal')
        ax1.set_title("Sentiment Distribution", fontsize=12, pad=10, weight="bold")
        
        # Bar chart
        sentiment_df = pd.DataFrame({'Sentiment': filtered_labels, 'Count': filtered_sizes})
        sns.barplot(x='Count', y='Sentiment', data=sentiment_df, palette=filtered_colors, ax=ax2, hue='Sentiment', legend=False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_color('#CBD5E1')
        ax2.spines['bottom'].set_color('#CBD5E1')
        ax2.tick_params(colors='#475569', labelsize=10)
        ax2.set_ylabel('')
        ax2.set_xlabel('Count')
        ax2.set_title("Sentiment Counts", fontsize=12, pad=10, weight="bold")
        for container in ax2.containers:
            ax2.bar_label(container, fmt='%d', padding=5, color='#1E293B', weight='bold', fontsize=10)
            
        plt.tight_layout()
        fd, temp_img_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        plt.savefig(temp_img_path, dpi=200)
        plt.close(fig)

    # 3. Compile PDF
    pdf = SentimentReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # ── Section: Session Summary ──
    pdf.set_text_color(30, 41, 59)
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, 'Session Analysis Summary', border=0, align='L')
    pdf.ln(8)
    
    pdf.set_font('helvetica', '', 10)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(40, 6, 'Post / Source URL:', border=0)
    pdf.set_font('helvetica', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    # limit URL display length for clean wrap
    display_url = url if len(url) <= 75 else url[:72] + "..."
    pdf.cell(0, 6, display_url, border=0)
    pdf.ln(6)
    
    pdf.set_font('helvetica', '', 10)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(40, 6, 'Date Run:', border=0)
    pdf.set_font('helvetica', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, str(timestamp), border=0)
    pdf.ln(6)
    
    pdf.set_font('helvetica', '', 10)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(40, 6, 'Total Comments:', border=0)
    pdf.set_font('helvetica', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, str(total), border=0)
    pdf.ln(12)
    
    # Draw Metrics Grid
    if total > 0:
        pdf.set_fill_color(248, 250, 252) # light gray background
        pdf.rect(10, pdf.get_y(), 190, 20, 'F')
        
        pdf.set_font('helvetica', 'B', 10)
        pdf.set_text_color(22, 163, 74) # green
        pdf.set_xy(15, pdf.get_y() + 4)
        pdf.cell(60, 6, f'Positive: {pos} ({pos/total:.1%})', border=0)
        
        pdf.set_text_color(217, 119, 6) # amber
        pdf.set_x(75)
        pdf.cell(60, 6, f'Neutral: {neu} ({neu/total:.1%})', border=0)
        
        pdf.set_text_color(220, 38, 38) # red
        pdf.set_x(135)
        pdf.cell(60, 6, f'Negative: {neg} ({neg/total:.1%})', border=0)
        
        pdf.ln(16)
        
    # Append Chart Image
    if temp_img_path and os.path.exists(temp_img_path):
        pdf.image(temp_img_path, x=10, y=pdf.get_y(), w=190)
        pdf.ln(92) # Leave space for the chart
        
    # Add page for comment log table
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, 'Sample Comment Predictions Log', border=0)
    pdf.ln(10)
    
    # Table headers
    pdf.set_fill_color(30, 41, 59)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(115, 8, ' Comment Text', border=1, fill=True)
    pdf.cell(35, 8, ' Sentiment', border=1, fill=True, align='C')
    pdf.cell(40, 8, ' Confidence', border=1, fill=True, align='C')
    pdf.ln(8)
    
    # Table rows
    pdf.set_text_color(15, 23, 42)
    pdf.set_font('helvetica', '', 8.5)
    
    # We display up to 45 comments for report layout
    display_rows = df.head(45)
    
    fill = False
    text_col_name = next((c for c in ("text", "comment_text", "commentText") if c in df.columns), None)
    
    for idx, row in display_rows.iterrows():
        # Zebra striping
        if fill:
            pdf.set_fill_color(248, 250, 252)
        else:
            pdf.set_fill_color(255, 255, 255)
            
        txt = str(row.get(text_col_name, ""))
        # Truncate comment text to fit in one line cell cleanly
        if len(txt) > 65:
            txt = txt[:62] + "..."
            
        sent = str(row.get(sent_col, "neutral")).upper()
        conf_val = row.get(conf_col)
        conf_str = f"{float(conf_val):.1%}" if conf_val is not None and pd.notna(conf_val) else "N/A"
        
        pdf.cell(115, 7, f' {txt}', border=1, fill=True)
        # Highlight sentiment column text color
        if sent == "POSITIVE":
            pdf.set_text_color(22, 163, 74)
        elif sent == "NEGATIVE":
            pdf.set_text_color(220, 38, 38)
        else:
            pdf.set_text_color(217, 119, 6)
            
        pdf.cell(35, 7, f' {sent}', border=1, fill=True, align='C')
        pdf.set_text_color(15, 23, 42) # reset to dark
        pdf.cell(40, 7, f' {conf_str}', border=1, fill=True, align='C')
        pdf.ln(7)
        fill = not fill
        
    # Clean up temp image
    if temp_img_path and os.path.exists(temp_img_path):
        try:
            os.remove(temp_img_path)
        except OSError:
            pass
            
    # Output bytes
    return bytes(pdf.output())
