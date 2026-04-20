from __future__ import annotations

from dataclasses import dataclass

from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer


@dataclass
class FeatureBundle:
    name: str
    vectorizer: object
    X_train: csr_matrix
    X_val: csr_matrix
    X_test: csr_matrix


def build_word_tfidf(train_texts, val_texts, test_texts) -> FeatureBundle:
    vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        sublinear_tf=True,
    )
    X_train = vectorizer.fit_transform(train_texts)
    X_val = vectorizer.transform(val_texts)
    X_test = vectorizer.transform(test_texts)
    return FeatureBundle("word_tfidf", vectorizer, X_train, X_val, X_test)


def build_char_tfidf(train_texts, val_texts, test_texts) -> FeatureBundle:
    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=1,
        sublinear_tf=True,
    )
    X_train = vectorizer.fit_transform(train_texts)
    X_val = vectorizer.transform(val_texts)
    X_test = vectorizer.transform(test_texts)
    return FeatureBundle("char_tfidf", vectorizer, X_train, X_val, X_test)


def build_combined_tfidf(train_texts, val_texts, test_texts) -> FeatureBundle:
    word_bundle = build_word_tfidf(train_texts, val_texts, test_texts)
    char_bundle = build_char_tfidf(train_texts, val_texts, test_texts)
    X_train = hstack([word_bundle.X_train, char_bundle.X_train]).tocsr()
    X_val = hstack([word_bundle.X_val, char_bundle.X_val]).tocsr()
    X_test = hstack([word_bundle.X_test, char_bundle.X_test]).tocsr()
    vectorizer = {"word": word_bundle.vectorizer, "char": char_bundle.vectorizer}
    return FeatureBundle("combined_tfidf", vectorizer, X_train, X_val, X_test)


def build_feature_sets(train_texts, val_texts, test_texts) -> list[FeatureBundle]:
    return [
        build_word_tfidf(train_texts, val_texts, test_texts),
        build_char_tfidf(train_texts, val_texts, test_texts),
        build_combined_tfidf(train_texts, val_texts, test_texts),
    ]
