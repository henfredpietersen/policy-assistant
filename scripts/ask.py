"""Ask a question from the command line.

Usage: python scripts/ask.py "How do I change my beneficiary?"
"""

import sys
from pathlib import Path

from policy_assistant.pipeline import RAGPipeline

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "How long does a claim take?"
    pipe = RAGPipeline.from_paths(ROOT / "data" / "docs", ROOT / "models" / "intent.joblib")
    ans = pipe.ask(question)
    print(f"Q: {ans.question}")
    print(f"Intent: {ans.intent} ({ans.intent_confidence})")
    print(f"A: {ans.answer}")
    print("Sources:", ", ".join(s["id"] for s in ans.sources))
