# Production Multi-Stage Dockerfile for GENIUS MCP Server
# Spec 2025-11-25 Streamable HTTP & SSE Server

FROM python:3.12-slim-bookworm AS base

# Install system dependencies for audio processing (libsndfile) and health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY server/ ./server/
COPY graph/ ./graph/
COPY beepdb/ ./beepdb/
COPY audio/ ./audio/
COPY tools/ ./tools/
COPY proactive/ ./proactive/
COPY ui/ ./ui/
COPY client/ ./client/
COPY tests/clips/ ./tests/clips/

# Create unprivileged user for security compliance
RUN useradd -m -u 1001 genius && \
    chown -R genius:genius /app

USER genius

# Expose Streamable HTTP & SSE port
EXPOSE 8000

# Health check against inspection endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/api/config || exit 1

# Launch uvicorn production server
CMD ["python", "-m", "uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
