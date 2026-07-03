"""
src/llm_insights.py
───────────────────
Groq-powered insight and recommendation engine for the Malawian
Economic Sentiment Analysis project.

PURPOSE
-------
After the ML model has classified Facebook comments as Positive /
Negative / Neutral, this module answers the question: "So what?"
It sends a stratified sample of the classified comments to a
Groq-hosted LLM (Llama 3) and asks it to:

  1. Interpret the overall public opinion.
  2. Summarise what the sentiment distribution means in context.
  3. Identify recurring concerns / issues from the comment text.
  4. Explain likely reasons behind the dominant sentiment using
     evidence from the actual comments.
  5. Generate dynamic, comment-grounded recommendations.

The LLM is explicitly instructed NOT to re-classify sentiment —
that has already been done by the ML model.

RETURNED STRUCTURE
------------------
{
    "overall_interpretation":   str,
    "summary_of_public_opinion": str,
    "possible_reasons":         list[str],
    "recommendations":          list[str]
}

On any failure (missing key, network error, parse failure) the
function returns None so the caller can degrade gracefully.
"""

from __future__ import annotations

import json
import logging
import os
import random
from typing import Any

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────

# Maximum total comments sent to the LLM (to stay within token limits).
MAX_SAMPLE_SIZE = 40

# Preferred model — falls back automatically if unavailable.
PRIMARY_MODEL   = "llama-3.3-70b-versatile"
FALLBACK_MODEL  = "llama3-8b-8192"


# ── Sampling ─────────────────────────────────────────────────────────────────

def _stratified_sample(
    comments_by_label: dict[str, list[str]],
    total: int = MAX_SAMPLE_SIZE,
) -> list[dict[str, str]]:
    """
    Draw a representative sample across sentiment labels.

    Returns a list of dicts: [{"sentiment": label, "text": text}, ...]
    """
    labels    = list(comments_by_label.keys())
    n_labels  = len([l for l in labels if comments_by_label[l]])
    if n_labels == 0:
        return []

    per_label = max(1, total // max(n_labels, 1))
    sampled: list[dict[str, str]] = []

    for label, texts in comments_by_label.items():
        if not texts:
            continue
        chosen = random.sample(texts, min(len(texts), per_label))
        for text in chosen:
            sampled.append({"sentiment": label, "text": text})

    # Shuffle so labels are not grouped
    random.shuffle(sampled)
    return sampled[:total]


# ── Prompt builder ───────────────────────────────────────────────────────────

def _build_prompt(
    sampled_comments: list[dict[str, str]],
    pos_count: int,
    neg_count: int,
    neu_count: int,
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for the Groq API call."""

    total = pos_count + neg_count + neu_count

    system_prompt = (
        "You are an expert economic policy analyst and public opinion researcher "
        "assisting a sentiment analysis system for Malawian Facebook posts about "
        "economic issues.\n\n"
        "STRICT RULES you must follow without exception:\n"
        "1. The comments have ALREADY been classified as Positive, Negative, or Neutral "
        "by a machine learning model. DO NOT re-classify them or question the labels.\n"
        "2. Base every statement, explanation, and recommendation ONLY on the content "
        "of the supplied comments. Do not invent facts or make unsupported claims.\n"
        "3. Do NOT assume a new discussion topic. All comments are about economic issues "
        "in Malawi — your job is to interpret what people are saying about the economy.\n"
        "4. Your recommendations must be DYNAMIC — derived from the specific concerns "
        "expressed in the comments, not from fixed rules.\n"
        "5. Respond with ONLY a valid JSON object matching the exact schema below. "
        "No markdown, no prose outside the JSON.\n\n"
        "Required JSON schema:\n"
        "{\n"
        '  "overall_interpretation": "<one-paragraph interpretation of public opinion>",\n'
        '  "summary_of_public_opinion": "<concise summary of what the distribution means in context>",\n'
        '  "positive_themes": "<one or two sentences explicitly explaining what the positive comments are praising, supporting, or happy about>",\n'
        '  "negative_themes": "<one or two sentences explicitly explaining what the negative comments are criticizing, complaining about, or angry about>",\n'
        '  "neutral_themes": "<one or two sentences explaining what the neutral comments are discussing, questioning, or expressing indifference towards>",\n'
        '  "possible_reasons": ["<reason 1>", "<reason 2>", ...],\n'
        '  "recommendations": ["<actionable recommendation 1>", "<recommendation 2>", ...]\n'
        "}"
    )

    # Format the comment list for the user message
    comments_block = "\n".join(
        f"[{i+1}] ({c['sentiment'].upper()}) {c['text']}"
        for i, c in enumerate(sampled_comments)
    )

    user_prompt = (
        f"## Sentiment Analysis Results\n\n"
        f"Total comments analysed: {total}\n"
        f"  • Positive : {pos_count} ({pos_count/total*100:.1f}% of total)\n"
        f"  • Negative : {neg_count} ({neg_count/total*100:.1f}% of total)\n"
        f"  • Neutral  : {neu_count} ({neu_count/total*100:.1f}% of total)\n\n"
        f"## Sampled Comments (representative subset — {len(sampled_comments)} of {total})\n\n"
        f"{comments_block}\n\n"
        "Using ONLY the information above, produce the JSON response as instructed."
    )

    return system_prompt, user_prompt


# ── API call ─────────────────────────────────────────────────────────────────

def _call_groq(system_prompt: str, user_prompt: str, model: str) -> str:
    """Call the Groq chat completion API and return the raw response text."""
    import groq  # imported lazily so the module loads even if groq not installed

    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. Add it to your .env file."
        )

    client = groq.Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.4,       # Balanced creativity / factuality
        max_tokens=1024,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


# ── JSON parser ───────────────────────────────────────────────────────────────

def _parse_response(raw: str) -> dict[str, Any]:
    """Parse and validate the JSON returned by the LLM."""
    data = json.loads(raw)

    required_keys = {
        "overall_interpretation",
        "summary_of_public_opinion",
        "positive_themes",  # <-- Added
        "negative_themes",  # <-- Added
        "neutral_themes",   # <-- Added
        "possible_reasons",
        "recommendations",
    }
    missing = required_keys - set(data.keys())
    if missing:
        raise ValueError(f"LLM response missing required keys: {missing}")

    # Coerce list fields in case the model returns strings
    for list_key in ("possible_reasons", "recommendations"):
        if isinstance(data[list_key], str):
            data[list_key] = [data[list_key]]

    return data


# ── Public API ────────────────────────────────────────────────────────────────

def generate_groq_insights(
    texts: list[str],
    sentiments: list[str],
    pos_count: int,
    neg_count: int,
    neu_count: int,
) -> dict[str, Any] | None:
    """
    Generate AI-powered insights using the Groq API.

    Parameters
    ----------
    texts       : list of raw comment strings (same order as `sentiments`)
    sentiments  : list of predicted labels — "positive", "negative", "neutral"
    pos_count   : number of Positive predictions
    neg_count   : number of Negative predictions
    neu_count   : number of Neutral predictions

    Returns
    -------
    dict with keys:
        overall_interpretation   (str)
        summary_of_public_opinion (str)
        possible_reasons          (list[str])
        recommendations           (list[str])

    Returns None on any failure so the caller can degrade gracefully.
    """
    try:
        # ── 1. Group comments by label ────────────────────────────────────
        comments_by_label: dict[str, list[str]] = {
            "positive": [],
            "negative": [],
            "neutral":  [],
        }
        for text, sentiment in zip(texts, sentiments):
            label = sentiment.lower().strip()
            if label in comments_by_label and text and str(text).strip():
                comments_by_label[label].append(str(text).strip())

        total = pos_count + neg_count + neu_count
        if total == 0:
            logger.warning("generate_groq_insights: no comments to analyse.")
            return None

        # ── 2. Stratified sample ──────────────────────────────────────────
        sampled = _stratified_sample(comments_by_label, total=MAX_SAMPLE_SIZE)
        if not sampled:
            logger.warning("generate_groq_insights: sampling produced no results.")
            return None

        # ── 3. Build prompt ───────────────────────────────────────────────
        system_prompt, user_prompt = _build_prompt(
            sampled, pos_count, neg_count, neu_count
        )

        # ── 4. Call Groq (primary → fallback) ────────────────────────────
        raw_response: str | None = None
        last_error: Exception | None = None

        for model in (PRIMARY_MODEL, FALLBACK_MODEL):
            try:
                raw_response = _call_groq(system_prompt, user_prompt, model)
                break  # success
            except Exception as exc:
                logger.warning("Groq model %s failed: %s", model, exc)
                last_error = exc

        if raw_response is None:
            raise last_error or RuntimeError("All Groq models failed.")

        # ── 5. Parse & return ─────────────────────────────────────────────
        return _parse_response(raw_response)

    except EnvironmentError:
        # Propagate missing-key errors so caller can show a specific warning
        raise
    except Exception as exc:
        logger.error("generate_groq_insights failed: %s", exc, exc_info=True)
        return None
