from pathlib import Path
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "project_dataset.csv"
MODEL_PATH = BASE_DIR / "project_classifier.joblib"


def main():
    df = pd.read_csv(DATA_PATH)
    df["text"] = df["title"].fillna("") + " " + df["description"].fillna("") + " " + df["technologies"].fillna("")

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["domain"], test_size=0.25, random_state=42, stratify=df["domain"]
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)),
        ("classifier", LogisticRegression(max_iter=2000, random_state=42)),
    ])
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"Test accuracy: {accuracy:.2%}")
    print(classification_report(y_test, predictions, zero_division=0))

    # Retrain on all available examples before saving the final model used by the app.
    model.fit(df["text"], df["domain"])
    joblib.dump(model, MODEL_PATH)
    print(f"Saved model to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
