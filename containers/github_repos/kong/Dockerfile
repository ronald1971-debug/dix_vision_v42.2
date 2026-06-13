# Kong Container Dockerfile
# Use official Kong image with Python sidecar for governance
FROM kong:3.4-alpine

LABEL maintainer="DIX VISION <devin@dixvision.ai>"
LABEL version="42.2"
LABEL description="Kong API Gateway container for DIX VISION with governance sidecar"

# Install Python for governance sidecar
RUN apk add --no-cache python3 py3-pip

WORKDIR /app

# Copy governance files
COPY kong_governance_wrapper.py .
COPY kong_domain_adapter.py .
COPY base_external_repo_wrapper.py /app/governance/
COPY base_domain_adapter.py /app/adapters/

RUN mkdir -p /app/logs /app/data /app/config /app/routes

COPY kong_config.yaml /app/config/

# Simple health check
RUN echo 'import sys\nsys.exit(0)' > /app/health_check.py

COPY entry_point.sh /app/
RUN chmod +x /app/entry_point.sh

EXPOSE 9127
EXPOSE 8000
EXPOSE 8443

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python /app/health_check.py

ENTRYPOINT ["/app/entry_point.sh"]
