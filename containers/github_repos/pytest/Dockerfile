# pytest Container Dockerfile
FROM python:3.11-slim

LABEL maintainer="DIX VISION <devin@dixvision.ai>"
LABEL version="42.2"
LABEL description="pytest testing container for DIX VISION"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pytest_governance_wrapper.py .
COPY pytest_domain_adapter.py .
COPY base_external_repo_wrapper.py /app/governance/
COPY base_domain_adapter.py /app/adapters/

RUN mkdir -p /app/logs /app/data /app/config /app/tests

COPY pytest_config.yaml /app/config/

RUN echo 'import sys\nsys.exit(0)' > /app/health_check.py

COPY entry_point.sh /app/
RUN chmod +x /app/entry_point.sh

EXPOSE 9123

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python /app/health_check.py

ENTRYPOINT ["/app/entry_point.sh"]

CMD ["python", "-m", "pytest_governance_wrapper"]
