FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app/src PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY data ./data
COPY scripts ./scripts

# Train the intent model at build time so the image ships ready to serve
RUN python scripts/train_intent.py

EXPOSE 8000
# Render (and most hosts) pass the port in $PORT; default to 8000 locally and in CI
CMD ["sh", "-c", "uvicorn policy_assistant.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
