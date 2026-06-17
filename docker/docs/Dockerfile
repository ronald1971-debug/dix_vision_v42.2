# DIX VISION v42.2 - Documentation Server Dockerfile
# Serves all documentation and reports via nginx

FROM nginx:alpine

# Install additional tools if needed
RUN apk add --no-cache curl

# Create directory for docs
RUN mkdir -p /usr/share/nginx/html/docs

# Copy custom nginx configuration (if you have one)
# COPY nginx.conf /etc/nginx/nginx.conf

# Create health check endpoint
RUN echo 'OK' > /usr/share/nginx/html/health

# Default: docs will be mounted as volume
# Documentation content is mounted from host ./docs directory

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]