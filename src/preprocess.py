from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import emoji
import pandas as pd
from sklearn.model_selection import train_test_split

from .data_utils import (
    build_label_audit,
    build_paths,
    discover_raw_files,
    ensure_project_dirs,
    merge_annotation_files,
    normalize_include,
    normalize_label,
    save_json,
)



RANDOM_SEED = 42



URL_PATTERN = re.compile(r"(https?://\S+|www\.\S+)")
MENTION_PATTERN = re.compile(r"(?<!\w)@\w+")
NUMBER_PATTERN = re.compile(r"\b\d+\b")

WHITESPACE_PATTERN = re.compile(r"\s+")

PUNCT_SPACING_PATTERN = re.compile(
    r"([,;:\(\)\[\]\{\}\"'])"
)

EMOJI_ALIAS_NORMALIZE_PATTERN = re.compile(
    r"[^a-z0-9]+"
)

# Hashtags
HASHTAG_PATTERN = re.compile(r"#(\w+)")

# Laughter patterns
LAUGHTER_K_PATTERN = re.compile(r"\b(k){3,}\b")
LAUGHTER_HA_PATTERN = re.compile(r"\b(ha){2,}\b")
LAUGHTER_HE_PATTERN = re.compile(r"\b(he){2,}\b")
LAUGHTER_LOL_PATTERN = re.compile(r"\b(lo){2,}l\b")
LAUGHTER_LMAO_PATTERN = re.compile(r"\blmao+\b")

# Repeated characters
REPEATED_CHAR_PATTERN = re.compile(r"([a-z])\1{2,}")

# Repeated punctuation
MULTI_EXCLAMATION_PATTERN = re.compile(r"!{3,}")
MULTI_QUESTION_PATTERN = re.compile(r"\?{3,}")
MULTI_PERIOD_PATTERN = re.compile(r"\.{3,}")


def normalize_unicode(text: str) -> str:
    """
    Normalize unicode characters into a standard form.
    """
    return unicodedata.normalize("NFKC", text)


def process_hashtags(text: str) -> str:
    """
    Convert:
        #Malawi -> Malawi
        #FootballNews -> FootballNews
    """
    return HASHTAG_PATTERN.sub(r"\1", text)


def normalize_laughter(text: str) -> str:
    """
    Normalize common social media laughter expressions.

    Examples:
        kkkkkkk     -> laugh
        hahaha      -> laugh
        hehehe      -> laugh
        lololol     -> laugh
        lmaoooo     -> laugh
    """

    text = LAUGHTER_K_PATTERN.sub(" laugh ", text)
    text = LAUGHTER_HA_PATTERN.sub(" laugh ", text)
    text = LAUGHTER_HE_PATTERN.sub(" laugh ", text)
    text = LAUGHTER_LOL_PATTERN.sub(" laugh ", text)
    text = LAUGHTER_LMAO_PATTERN.sub(" laugh ", text)

    return text


def normalize_repeated_chars(text: str) -> str:
    """
    Reduce long character repetitions to two characters.

    Examples:
        sooooo   -> soo
        goooood  -> good
        niiiice  -> niice
    """

    return REPEATED_CHAR_PATTERN.sub(r"\1\1", text)


def normalize_punctuation(text: str) -> str:
    """
    Normalize excessive punctuation.

    Examples:
        !!!!!!!! -> !!
        ???????  -> ??
        ......   -> ..
    """

    text = MULTI_EXCLAMATION_PATTERN.sub("!!", text)
    text = MULTI_QUESTION_PATTERN.sub("??", text)
    text = MULTI_PERIOD_PATTERN.sub("..", text)

    return text




def normalize_emoji_alias(alias: str) -> str:
    normalized = (
        EMOJI_ALIAS_NORMALIZE_PATTERN
        .sub("_", alias.lower())
        .strip("_")
    )

    return f"emoji_{normalized}" if normalized else ""


def extract_emoji_aliases(text: object) -> list[str]:

    if pd.isna(text):
        return []

    value = normalize_unicode(str(text)).lower().strip()

    aliases = []

    for emoji_match in emoji.emoji_list(value):

        demojized = emoji.demojize(
            emoji_match["emoji"],
            language="en"
        ).strip(":")

        alias = normalize_emoji_alias(demojized)

        if alias:
            aliases.append(alias)

    return aliases




def clean_text(
    text: object,
    emoji_aliases: list[str] | None = None
) -> str:

    if pd.isna(text):
        return ""

    value = normalize_unicode(str(text))
    value = value.lower().strip()

    aliases = (
        extract_emoji_aliases(value)
        if emoji_aliases is None
        else emoji_aliases
    )



    value = process_hashtags(value)

    value = URL_PATTERN.sub(" <url> ", value)

    value = MENTION_PATTERN.sub(" <user> ", value)

    value = NUMBER_PATTERN.sub(" <num> ", value)

    value = normalize_laughter(value)

    value = normalize_repeated_chars(value)

    value = normalize_punctuation(value)



    value = PUNCT_SPACING_PATTERN.sub(
        r" \1 ",
        value
    )



    if aliases:
        value = f"{value} {' '.join(aliases)}"



    value = WHITESPACE_PATTERN.sub(
        " ",
        value
    ).strip()

    return value



def tokenize_text(text: str) -> list[str]:
    return text.split()


def add_clean_text_features(
    df: pd.DataFrame
) -> pd.DataFrame:

    enriched = df.copy()

    emoji_alias_lists = (
        enriched["text"]
        .apply(extract_emoji_aliases)
    )

    enriched["emoji_aliases"] = (
        emoji_alias_lists.apply(" ".join)
    )

    enriched["emoji_count"] = (
        emoji_alias_lists.apply(len)
    )

    enriched["cleaned_text"] = [
        clean_text(text, aliases)
        for text, aliases
        in zip(enriched["text"], emoji_alias_lists)
    ]

    enriched["tokens"] = (
        enriched["cleaned_text"]
        .apply(tokenize_text)
    )

    enriched["token_count_cleaned"] = (
        enriched["tokens"]
        .apply(len)
    )

    return enriched
