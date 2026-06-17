# DIX VISION v42.2 - Core Application Dockerfile
# Optimized container for the main application

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file (if exists)
COPY requirements.txt* /app/

# Install Python dependencies
RUN pip install --upgrade pip && \
    if [ -f requirements.txt ]; then pip install -r requirements.txt; else pip install numpy pandas torch scikit-learn; fi

# Copy core application code
COPY cognitive_os/ /app/cognitive_os/
COPY execution_unified/ /app/execution_unified/
COPY evolution_engine/ /app/evolution_engine/
COPY world_model/ /app/world_model/
COPY adapters/ /app/adapters/
COPY cognitive_control_center/ /app/cognitive_control_center/
COPY state/ /app/state/
COPY governance_unified/ /app/governance_unified/
COPY tests/ /app/tests/

# Copy main entry points
COPY dix_vision_unified.py /app/
COPY LAUNCH_DIX_VISION_DESKTOP.py /app/  # if used

# Create necessary directories
RUN mkdir -p /app/data /app/checkpoints /app/logs /app/models

# Set up data directories as volumes
VOLUME ["/app/data", "/app/checkpoints", "/app/logs"]

# Create non-root user for security
RUN useradd -m -u 1000 dixvision && \
    chown -R dixvision:dixvision /app

# Switch to non-root user
USER dixvision

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app'); import dix_vision_unified; print('OK')" || exit 1

# Default command
CMD ["python", "dix_vision_unified.py"]

# Expose ports if needed (adjust as per your application)
# EXPOSE 8000