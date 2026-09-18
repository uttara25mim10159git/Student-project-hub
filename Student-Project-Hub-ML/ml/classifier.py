from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "project_classifier.joblib"

_model = None


def _load_model():
    global _model
    if _model is None and MODEL_PATH.exists():
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_project(text: str):
    """Predict the project domain and confidence using the trained TF-IDF + Logistic Regression model."""
    model = _load_model()
    if model is None:
        return "Other", 0.0

    cleaned = " ".join((text or "").split())
    if not cleaned:
        return "Other", 0.0

    probabilities = model.predict_proba([cleaned])[0]
    index = probabilities.argmax()
    label = model.classes_[index]
    confidence = float(probabilities[index])
    return label, confidence
