from pathlib import Path
import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def recommend_projects(project, conn: sqlite3.Connection, limit=3):
    """Recommend similar projects using TF-IDF text vectors and cosine similarity."""
    rows = conn.execute(
        "SELECT * FROM projects WHERE id != ? ORDER BY created_at DESC",
        (project["id"],),
    ).fetchall()

    if not rows:
        return []

    frame = pd.DataFrame([dict(r) for r in rows])
    target_text = f"{project['title']} {project['description']} {project['domain']} {project['technologies']}"
    frame["ml_text"] = (
        frame["title"].fillna("") + " " + frame["description"].fillna("") + " " +
        frame["domain"].fillna("") + " " + frame["technologies"].fillna("")
    )

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform([target_text] + frame["ml_text"].tolist())
    similarities = cosine_similarity(matrix[0:1], matrix[1:]).ravel()
    frame["similarity"] = similarities

    # Prefer meaningful matches, then higher similarity.
    frame = frame.sort_values("similarity", ascending=False)
    selected = frame[frame["similarity"] > 0].head(limit)
    return [sqlite3.Row(dict(row)) if False else row.to_dict() for _, row in selected.iterrows()]
