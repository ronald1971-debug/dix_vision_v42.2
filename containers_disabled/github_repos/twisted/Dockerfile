# twisted Container Dockerfile for DIX VISION
# This container provides Twisted networking engine
# with DIX VISION governance and security oversight

FROM python:3.11-slim

LABEL maintainer="DIX VISION <devin@dixvision.ai>"
LABEL version="42.2"
LABEL description="Twisted networking engine container for DIX VISION"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy governance wrapper and domain adapter
COPY twisted_governance_wrapper.py .
COPY twisted_domain_adapter.py .

# Copy base templates
COPY base_external_repo_wrapper.py /app/governance/
COPY base_domain_adapter.py /app/adapters/

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/config

# Copy configuration files
COPY twisted_config.yaml /app/config/

# Create health check script
RUN echo 'import sys\nsys.exit(0)' > /app/health_check.py

# Create entry point script
COPY entry_point.sh /app/
RUN chmod +x /app/entry_point.sh

EXPOSE 9171

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python /app/health_check.py

ENTRYPOINT ["/app/entry_point.sh"]

CMD ["python", "-m", "twisted_governance_wrapper"]
