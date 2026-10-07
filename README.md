# Policy Assistant

![CI](https://github.com/henfredpietersen/policy-assistant/actions/workflows/ci.yml/badge.svg)

A small **retrieval-augmented generation (RAG)** service that answers life-insurance policy questions (claims, premiums, beneficiaries, cancellations) from a knowledge base, with a **scikit-learn intent classifier**, a **FastAPI** endpoint, **Docker** packaging and **GitHub Actions CI**.

It runs free with no API key. Set `GEMINI_API_KEY` and the answer step switches from extractive to an LLM-generated answer grounded in the retrieved sections.

> The knowledge base is a generic, fictional example written for this project. It is not any insurer's real policy wording.

## Why I built it

I've built and shipped a commercial RAG chatbot for WordPress (PHP) at [Outview](https://outview.co.za). This project rebuilds the core ideas in Python and adds the pieces a production ML pipeline needs: evaluation metrics, hyperparameter tuning, tests, containerisation and CI.

## How it works

```
question
   │
   ├─► IntentClassifier (TF-IDF + LogisticRegression, GridSearchCV)  → topic + confidence
   │
   ├─► TfidfRetriever (char n-gram TF-IDF, cosine similarity)       → top-k sections + scores
   │
   └─► Generator ── GEMINI_API_KEY set? ── yes → Gemini, prompt grounded in retrieved sections
                                        └─ no  → extractive answer (best-matching section)
                    (if the LLM call fails, it falls back to extractive instead of erroring)
```

| Module | Responsibility |
|---|---|
| `documents.py` | Loads markdown files and splits them into one chunk per `##` section |
| `retriever.py` | Vectorises chunks and returns the most similar ones to a question |
| `intent.py` | Trains, tunes, evaluates, saves and loads the intent classifier |
| `generator.py` | Builds the grounded prompt; Gemini or extractive answer |
| `pipeline.py` | Wires the pieces together, with LLM-failure fallback |
| `evaluation.py` | Offline retrieval metrics: Hit@1, Hit@3, MRR |
| `api.py` | FastAPI app with `/health` and `/ask` |

## Results

Retrieval, on 15 labelled questions (`data/retrieval_eval.csv`):

| Metric | Score |
|---|---|
| Hit@1 | 0.80 |
| Hit@3 | 0.87 |
| MRR | 0.83 |

Intent classifier, 60 labelled questions, 75/25 stratified split, 3-fold grid search:

| Metric | Score |
|---|---|
| Best CV accuracy | 0.82 |
| Held-out test accuracy | 0.73 |

**What the misses show.** The two retrieval misses ("Who gets the money if I never named anyone?", "Can I split the payout between my two kids?") share almost no words with the right section. That's the limit of lexical (TF-IDF) search. A dense embedding model would match them by meaning; the retriever's `fit`/`search` interface is built so one can be swapped in. The classifier's test set is only 15 questions, so its accuracy is noisy; more labelled data would matter more than more tuning.

An early version used word-level TF-IDF and failed "How do I change my **beneficiary**?" because the document says "**beneficiaries**". Switching to character n-grams fixed it without adding a stemmer.

## Run it

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
export PYTHONPATH=src              # Windows PowerShell: $env:PYTHONPATH="src"

python scripts/train_intent.py           # train + tune the classifier, prints metrics
python scripts/evaluate_retrieval.py     # retrieval Hit@k / MRR
python scripts/ask.py "Can my child be a beneficiary?"
pytest -v                                # 18 tests
uvicorn policy_assistant.api:app --reload
```

Then open http://localhost:8000/docs to try `/ask` in the browser.

### With Docker

```bash
docker build -t policy-assistant .
docker run -p 8000:8000 policy-assistant
# optional LLM answers:
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key policy-assistant
```

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What happens if I miss a premium?"}'
```

## CI

Every push runs `.github/workflows/ci.yml`:

1. **Lint** with ruff
2. **Test** with pytest, including a retrieval-quality guard that fails the build if Hit@3 drops below 0.8
3. **Build** the Docker image (which trains the model during the build) and **smoke-test** `/health` and `/ask` against the running container

## Next steps

- Swap TF-IDF for dense embeddings (e.g. sentence-transformers) and compare on the same eval set
- Store vectors in a vector database (pgvector, OpenSearch) instead of in memory
- Deploy to AWS: image in ECR, served from Lambda (via Mangum) or ECS, docs in S3
- Log questions, retrieved sources and latency to monitor quality over time
