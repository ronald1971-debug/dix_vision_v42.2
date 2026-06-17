# DIX VISION v42.2 - Backup and Archive Dockerfile
# Container for managing backups and archival of old reports

FROM alpine:latest

# Install necessary tools
RUN apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    rsync \
    gzip \
    tar \
    zip

# Create backup directory
RUN mkdir -p /backup

# Copy backup scripts (if you have any)
# COPY backup_scripts/ /app/

# Set working directory
WORKDIR /app

# Create a simple backup script
RUN echo '#!/bin/sh' > /app/backup.sh && \
    echo 'echo "Backup container running"' >> /app/backup.sh && \
    echo 'echo "Backup directory: /backup"' >> /app/backup.sh && \
    chmod +x /app/backup.sh

# Default command
CMD ["/app/backup.sh"]