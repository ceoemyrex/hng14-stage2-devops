# syntax=docker/dockerfile:1

FROM python:3.11-slim as builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --upgrade pip==26.0.1 && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

RUN useradd -m -u 1001 -s /sbin/nologin appuser

COPY --from=builder /install /usr/local
COPY . .

RUN rm -f .env .env.* && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
