# DIX VISION v42.2 - Configuration Management Dockerfile
# Lightweight container for configuration management

FROM alpine:latest

# Install necessary tools
RUN apk add --no-cache python3 py3-pip curl

# Create config directory
RUN mkdir -p /app/config

# Copy configuration management scripts (if you have any)
# COPY config_manager.py /app/

# Set working directory
WORKDIR /app

# Default command (can be customized based on needs)
CMD ["sh", "-c", "echo 'Configuration container running' && sleep 3600"]