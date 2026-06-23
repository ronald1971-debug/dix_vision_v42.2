# DIX VISION v42.2 - Development Environment Dockerfile
# Complete development environment with all tools

FROM python:3.11-slim

# Set working directory
WORKDIR /workspace

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEV_MODE=true

# Install system dependencies and dev tools
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    vim \
    nano \
    htop \
    net-tools \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Install Python development tools
RUN pip install --upgrade pip && \
    pip install \
    pytest \
    pytest-cov \
    pytest-asyncio \
    black \
    flake8 \
    mypy \
    pylint \
    ipython \
    jupyter \
    jupyterlab

# Install main application dependencies
COPY requirements.txt* /workspace/
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Install additional dev dependencies
RUN pip install \
    docker \
    docker-compose \
    pre-commit \
    bandit \
    safety

# Create non-root user for development
RUN useradd -m -u 1000 developer && \
    chown -R developer:developer /workspace

# Switch to non-root user
USER developer

# Set up Jupyter for notebook access
RUN jupyter notebook --generate-config && \
    echo "c.NotebookApp.allow_root = True" >> ~/.jupyter/jupyter_notebook_config.py

# Expose Jupyter port
EXPOSE 8888

# Default command (interactive shell for development)
CMD ["/bin/bash"]