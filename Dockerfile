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
CMD ["uvicorn", "policy_assistant.api:app", "--host", "0.0.0.0", "--port", "8000"]
