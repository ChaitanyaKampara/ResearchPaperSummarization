from typing import List, Union
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sentence_transformers import SentenceTransformer, util
import numpy as np

# Paths
MODEL_PATH = "utils/classifier_model.pkl"
VEC_PATH = "utils/tfidf_vectorizer.pkl"

# Training Data (extendable)
TRAIN_TEXTS = [
    "This paper discusses a new treatment for cancer diagnosis.",
    "The experiment was conducted using chemical compounds.",
    "Stock market prediction using AI models.",
    "This study explores the political implications of economic policy.",
    "A new approach to teaching children in schools.",
    "Advanced robotics using reinforcement learning in manufacturing.",
    "Climate change mitigation strategies in agriculture."
]
TRAIN_LABELS = [
    "Medical Research",
    "Scientific Research",
    "Financial Research",
    "Social Sciences",
    "Education",
    "Engineering",
    "Environmental Science"
]

# Sentence-BERT model
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

# Topics for semantic classification
TOPIC_LABELS = list(set(TRAIN_LABELS))


def train_model():
    vectorizer = TfidfVectorizer()
    X_train = vectorizer.fit_transform(TRAIN_TEXTS)
    model = MultinomialNB()
    model.fit(X_train, TRAIN_LABELS)

    os.makedirs("utils", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VEC_PATH)
    return model, vectorizer


def load_model():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VEC_PATH):
        return train_model()
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VEC_PATH)
    return model, vectorizer


def classify_content(text: str) -> str:
    model, vectorizer = load_model()
    X_text = vectorizer.transform([text])
    probas = model.predict_proba(X_text)[0]
    max_idx = np.argmax(probas)
    confidence = probas[max_idx]

    predicted_label = model.classes_[max_idx]

    # Fallback to semantic if confidence is too low
    if confidence < 0.5:
        print(f"[Warning] Low confidence from Naive Bayes ({confidence:.2f}). Falling back to semantic classification.")
        top_topic = classify_content_semantic(text)[0]
        return f"{top_topic['topic']} (semantic fallback, score={top_topic['similarity_score']:.2f})"

    return f"{predicted_label} (confidence={confidence:.2f})"


def classify_content_semantic(text: str, top_k: int = 3) -> List[dict]:
    """
    Classify the input text using semantic similarity to a predefined list of topics.
    Returns top-k topics and their similarity scores.
    """
    if not text.strip():
        return []

    # Compute embeddings
    text_embedding = sbert_model.encode(text, convert_to_tensor=True)
    topic_embeddings = sbert_model.encode(TOPIC_LABELS, convert_to_tensor=True)

    # Compute similarity
    similarities = util.cos_sim(text_embedding, topic_embeddings)[0]
    top_results = similarities.topk(k=top_k)

    results = []
    for score, idx in zip(top_results.values, top_results.indices):
        results.append({
            "topic": TOPIC_LABELS[int(idx)],
            "similarity_score": float(score)
        })

    return results
