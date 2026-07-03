from __future__ import annotations

import numpy as np
from scipy.special import softmax

def predict(logits: object) -> tuple[str, float]:
    """
    Applies softmax on model logits to output a (label, confidence_score) tuple.
    
    Args:
        logits: List, tuple, or numpy array of raw logits for ['negative', 'neutral', 'positive'].
        
    Returns:
        A tuple of (label, confidence_score) where confidence_score is between 0.0 and 1.0.
    """
    arr = np.asarray(logits)
    if arr.ndim == 2:
        probs = softmax(arr, axis=1)
        idx = np.argmax(probs, axis=1)[0]
        confidence = float(probs[0, idx])
    else:
        probs = softmax(arr)
        idx = np.argmax(probs)
        confidence = float(probs[idx])
        
    labels = ["negative", "neutral", "positive"]
    return labels[idx], confidence


def generate_wordcloud(
    texts: list[str],
    sentiment_filter: str | None = None,
    predicted_sentiments: list[str] | None = None,
    stopwords_path: str | None = None,
    background_color: str = "white",
    width: int = 800,
    height: int = 400,
    colormap: str = "viridis",
    max_words: int = 150,
):
    """Generate a WordCloud for a given sentiment class.

    Args:
        texts: List of comment strings.
        sentiment_filter: One of 'positive', 'negative', 'neutral', or None (use all).
        predicted_sentiments: Parallel list of predicted labels corresponding to *texts*.
            Required when *sentiment_filter* is not None.
        stopwords_path: Optional path to a plain-text stopwords file (one word per line).
        background_color: WordCloud background colour.
        width: Image width in pixels.
        height: Image height in pixels.
        colormap: Matplotlib colormap name for word colours.
        max_words: Maximum number of words to include.

    Returns:
        A :class:`wordcloud.WordCloud` object, or ``None`` if there are no words.
    """
    from wordcloud import WordCloud, STOPWORDS, get_single_color_func
    # 1. Define the exact Hex color sets matching your charts and tables
    WORDCLOUD_PALETTES = {
        "All": "#1E293B",       # Slate Blue
        "Positive": "#10B981",  # Emerald Green
        "Neutral": "#F59E0B",   # Amber / Orange
        "Negative": "#EF4444"   # Crimson Red
    }
    # Optional external stopwords (e.g. Chichewa)
    extra_stopwords: set[str] = set()
    if stopwords_path:
        try:
            with open(stopwords_path, encoding="utf-8") as fh:
                extra_stopwords = {w.strip().lower() for w in fh if w.strip()}
        except OSError:
            pass

    all_stopwords = STOPWORDS | extra_stopwords

    # Filter by sentiment if requested
    if sentiment_filter is not None and predicted_sentiments is not None:
        filtered = [
            t
            for t, s in zip(texts, predicted_sentiments)
            if str(s).lower() == sentiment_filter.lower()
        ]
    else:
        filtered = list(texts)

    corpus = " ".join(str(t) for t in filtered if t)
    if not corpus.strip():
        return None
    # Get the target color code; default to Slate Blue if not found
    palette_key = sentiment_filter.capitalize() if sentiment_filter else "All"
    target_hex = WORDCLOUD_PALETTES.get(palette_key, "#1E293B")

    wc = WordCloud(
        background_color=background_color,
        stopwords=all_stopwords,
        width=width,
        height=height,
        colormap=colormap,
        max_words=max_words,
        collocations=False,
    ).generate(corpus)

     # 3. Force the generator to use the exact Hex palette match
    color_func = get_single_color_func(target_hex)
    wc.recolor(color_func=color_func)
    return wc
