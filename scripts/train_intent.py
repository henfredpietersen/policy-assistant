"""Train the intent classifier, print evaluation metrics and save the model.

Usage: python scripts/train_intent.py
"""

from pathlib import Path

import pandas as pd

from policy_assistant.intent import IntentClassifier

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    df = pd.read_csv(ROOT / "data" / "intents.csv")
    print(f"Loaded {len(df)} examples across {df['intent'].nunique()} intents")
    clf = IntentClassifier()
    report = clf.train(df)
    print(f"Best params:   {report.best_params}")
    print(f"CV accuracy:   {report.cv_accuracy:.2f}")
    print(f"Test accuracy: {report.test_accuracy:.2f}\n")
    print(report.report)
    out = ROOT / "models" / "intent.joblib"
    clf.save(out)
    print(f"Saved model to {out}")


if __name__ == "__main__":
    main()
