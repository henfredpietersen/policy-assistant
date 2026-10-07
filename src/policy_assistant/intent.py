"""Intent classifier: routes a question to a topic (claims, premiums, ...)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline


@dataclass
class TrainingReport:
    best_params: dict
    cv_accuracy: float
    test_accuracy: float
    report: str


class IntentClassifier:
    """TF-IDF + logistic regression, tuned with cross-validated grid search."""

    PARAM_GRID: ClassVar[dict] = {
        "tfidf__ngram_range": [(1, 1), (1, 2)],
        "tfidf__sublinear_tf": [True, False],
        "clf__C": [0.1, 1.0, 10.0],
    }

    def __init__(self, random_state: int = 42) -> None:
        self.random_state = random_state
        self.model: Pipeline | None = None

    def _base_pipeline(self) -> Pipeline:
        return Pipeline(
            [
                ("tfidf", TfidfVectorizer()),
                ("clf", LogisticRegression(max_iter=1000, random_state=self.random_state)),
            ]
        )

    def train(self, df: pd.DataFrame, test_size: float = 0.25) -> TrainingReport:
        x_train, x_test, y_train, y_test = train_test_split(
            df["text"], df["intent"], test_size=test_size,
            stratify=df["intent"], random_state=self.random_state,
        )
        search = GridSearchCV(self._base_pipeline(), self.PARAM_GRID, cv=3, scoring="accuracy")
        search.fit(x_train, y_train)
        self.model = search.best_estimator_
        preds = self.model.predict(x_test)
        return TrainingReport(
            best_params=search.best_params_,
            cv_accuracy=float(search.best_score_),
            test_accuracy=float(accuracy_score(y_test, preds)),
            report=classification_report(y_test, preds, zero_division=0),
        )

    def predict(self, text: str) -> tuple[str, float]:
        if self.model is None:
            raise RuntimeError("Model is not trained or loaded")
        probs = self.model.predict_proba([text])[0]
        best = probs.argmax()
        return str(self.model.classes_[best]), float(probs[best])

    def save(self, path: str | Path) -> None:
        if self.model is None:
            raise RuntimeError("Nothing to save")
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)

    @classmethod
    def load(cls, path: str | Path) -> IntentClassifier:
        obj = cls()
        obj.model = joblib.load(path)
        return obj
