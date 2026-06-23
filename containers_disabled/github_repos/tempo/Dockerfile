# Tempo Container Dockerfile
# Use official Tempo image, governance will be external for now
FROM grafana/tempo:latest

LABEL maintainer="DIX VISION <devin@dixvision.ai>"
LABEL version="42.2"
LABEL description="Tempo metrics backend container for DIX VISION"

# Copy configuration
COPY tempo_config.yaml /etc/tempo/

# Standard Tempo ports
EXPOSE 9132
EXPOSE 3200
EXPOSE 4317
EXPOSE 4318

# Use Tempo's built-in entrypoint
ENTRYPOINT ["/tempo"]
