FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

# Serve only the FastAPI admin panel. `python -m app` would also start
# Telegram long-polling, which fails with the placeholder bot token —
# for the admin-only demo container we serve the web app directly.
CMD ["uvicorn", "app.web:app", "--host", "0.0.0.0", "--port", "8000"]
