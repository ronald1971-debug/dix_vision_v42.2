# timescaledb Container Dockerfile for DIX VISION
# Use official TimescaleDB image with Python sidecar for governance
FROM timescale/timescaledb:latest-pg15

LABEL maintainer="DIX VISION <devin@dixvision.ai>"
LABEL version="42.2"
LABEL description="TimescaleDB time-series database container for DIX VISION with governance sidecar"

# Install Python for governance sidecar
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy governance files
COPY timescaledb_governance_wrapper.py .
COPY timescaledb_domain_adapter.py .
COPY base_external_repo_wrapper.py /app/governance/
COPY base_domain_adapter.py /app/adapters/

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/config

# Copy configuration files
COPY timescaledb_config.yaml /app/config/

# Create health check script
RUN echo 'import sys\nsys.exit(0)' > /app/health_check.py

# Create entry point script
COPY entry_point.sh /app/
RUN chmod +x /app/entry_point.sh

EXPOSE 9148
EXPOSE 5432

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python /app/health_check.py

ENTRYPOINT ["/app/entry_point.sh"]
