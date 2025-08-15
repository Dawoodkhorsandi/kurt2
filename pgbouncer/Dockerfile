FROM bitnami/pgbouncer:1.22.0

USER root

# Install the PostgreSQL client, which provides the 'pg_isready' utility.
# We use --no-install-recommends to keep the image lean and clean up afterwards.
RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to the non-root user that the Bitnami image uses for better security.
USER 1001