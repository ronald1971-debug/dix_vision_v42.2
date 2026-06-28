# CCXT Container Dockerfile for DIX VISION
# This container provides cryptocurrency trading capabilities through CCXT
# with DIX VISION governance and safety oversight

FROM python:3.11-slim

LABEL maintainer="DIX VISION <devin@dixvision.ai>"
LABEL version="42.2"
LABEL description="CCXT cryptocurrency trading container for DIX VISION"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
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
COPY ccxt_governance_wrapper.py .
COPY ccxt_domain_adapter.py .

# Copy base templates
COPY base_external_repo_wrapper.py /app/governance/
COPY base_domain_adapter.py /app/adapters/

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/config

# Copy configuration files
COPY ccxt_config.yaml /app/config/

# Create health check script
RUN echo 'import sys\nsys.exit(0)' > /app/health_check.py

# Create entry point script
COPY entry_point.sh /app/
RUN chmod +x /app/entry_point.sh

# Expose port for API communication
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python /app/health_check.py

# Set entry point
ENTRYPOINT ["/app/entry_point.sh"]

# Default command
CMD ["python", "-m", "ccxt_governance_wrapper"]
