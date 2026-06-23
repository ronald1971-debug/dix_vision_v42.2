# timescaledb Container Dockerfile for DIX VISION
# Use official TimescaleDB image, governance will be external for now
FROM timescale/timescaledb:latest-pg15

LABEL maintainer="DIX VISION <devin@dixvision.ai>"
LABEL version="42.2"
LABEL description="TimescaleDB time-series database container for DIX VISION"

# Copy configuration
COPY timescaledb_config.yaml /etc/postgresql/

# Standard PostgreSQL ports plus TimescaleDB monitoring
EXPOSE 9148
EXPOSE 5432

# Use standard PostgreSQL entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]
