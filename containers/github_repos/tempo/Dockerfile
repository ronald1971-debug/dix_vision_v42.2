# Tempo Container Dockerfile
# Use official Tempo image with Python sidecar for governance
FROM grafana/tempo:latest

LABEL maintainer="DIX VISION <devin@dixvision.ai>"
LABEL version="42.2"
LABEL description="Tempo metrics backend container for DIX VISION with governance sidecar"

# Install Python for governance sidecar
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy governance files
COPY tempo_governance_wrapper.py .
COPY tempo_domain_adapter.py .
COPY base_external_repo_wrapper.py /app/governance/
COPY base_domain_adapter.py /app/adapters/

RUN mkdir -p /app/logs /app/data /app/config /app/metrics

COPY tempo_config.yaml /app/config/

# Simple health check
RUN echo 'import sys\nsys.exit(0)' > /app/health_check.py

COPY entry_point.sh /app/
RUN chmod +x /app/entry_point.sh

EXPOSE 9132
EXPOSE 3200
EXPOSE 4317
EXPOSE 4318

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python /app/health_check.py

ENTRYPOINT ["/app/entry_point.sh"]
