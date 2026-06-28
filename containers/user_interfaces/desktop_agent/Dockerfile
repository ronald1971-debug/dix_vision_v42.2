# DIX VISION v42.2+ Desktop Agent Dockerfile
FROM python:3.11-slim

LABEL maintainer="DIX VISION <devin@dixvision.ai>"
LABEL version="42.2.0"
LABEL description="Desktop Agent container for DIX VISION - Governed interaction layer"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies (minimal for Phase 1 foundation layer)
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Desktop Agent components
COPY engine.py .
COPY orchestrator.py .
COPY authority_router.py .
COPY session_manager.py .
COPY activity_tracker.py .
COPY __init__.py .

# Copy layer directories (Phase 1 placeholders)
COPY voice/ ./voice/
COPY browser/ ./browser/
COPY desktop/ ./desktop/
COPY documents/ ./documents/
COPY research/ ./research/
COPY notifications/ ./notifications/
COPY presence/ ./presence/
COPY automation/ ./automation/
COPY learning/ ./learning/
COPY security/ ./security/
COPY memory/ ./memory/
COPY integrations/ ./integrations/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/config /app/learning

# Create health check script
RUN echo 'import sys\nimport requests\nsys.exit(0 if requests.get("http://localhost:9186/health").status_code == 200 else 1)' > /app/health_check.py

# Copy entry point script
COPY entry_point.sh /app/
RUN chmod +x /app/entry_point.sh

EXPOSE 9186

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python /app/health_check.py

ENTRYPOINT ["/app/entry_point.sh"]

CMD ["python", "engine.py"]
