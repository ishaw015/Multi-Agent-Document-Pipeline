# ════════════════════════════════════════════════════════════════════════════════
# Stage 1 — Builder
#   Installs all Python dependencies into an isolated prefix so the final
#   image stays lean and doesn't carry pip / build tools into production.
# ════════════════════════════════════════════════════════════════════════════════
FROM python:3.11-slim AS builder

# System libraries required to build / install OpenCV, psycopg2, cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libglib2.0-0 \
        libgl1 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /install

COPY requirements.txt .

# Install into a prefix that we can copy cleanly into the final stage
RUN pip install --upgrade pip \
 && pip install --prefix=/install/deps --no-cache-dir -r requirements.txt


# ════════════════════════════════════════════════════════════════════════════════
# Stage 2 — Runtime
#   Minimal image; only copies compiled site-packages + app source.
# ════════════════════════════════════════════════════════════════════════════════
FROM python:3.11-slim AS runtime

# Runtime shared libraries needed by OpenCV & psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        libglib2.0-0 \
        libgl1 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install/deps /usr/local

# ── App setup ──────────────────────────────────────────────────────────────────
WORKDIR /app

# Copy application source
COPY src/  ./src/
COPY api/  ./api/

# Create a non-root user for security (Cloud Run best practice)
RUN useradd --no-create-home --shell /bin/false appuser \
 && chown -R appuser:appuser /app
USER appuser

# ── Runtime configuration ──────────────────────────────────────────────────────
# Cloud Run injects PORT env var; default to 8080 for local Docker testing
ENV PORT=8080 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Expose the port (documentation only — Cloud Run ignores EXPOSE)
EXPOSE ${PORT}

# ── Healthcheck (used by docker-compose; Cloud Run uses its own probe) ──────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')"

# ── Entrypoint ─────────────────────────────────────────────────────────────────
# Use exec form so SIGTERM reaches uvicorn directly (graceful shutdown)
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT} --workers 1 --timeout-keep-alive 75"]