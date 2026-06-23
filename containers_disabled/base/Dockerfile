FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install common Python packages
RUN pip install --no-cache-dir \
    pydantic==2.5.0 \
    requests==2.31.0 \
    httpx==0.25.0 \
    python-dotenv==1.0.0 \
    pyyaml==6.0.1

# Create directories for governance integration
RUN mkdir -p /app/governance /app/shared /app/config

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 8000)); s.close()" || exit 1

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app
