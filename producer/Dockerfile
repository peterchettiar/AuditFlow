# producer/Dockerfile
FROM python:3.11-slim

# System deps for netcat (wait loop) and certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# App workspace
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install producer deps directly (adjust versions as you like)
# RUN pip install --no-cache-dir confluent-kafka==2.5.0

# Copy your producer code
COPY producer.py /app/producer.py

# Simple wait-for script so we don’t start before Kafka is reachable
# It waits for $KAFKA_BOOTSTRAP host:port then runs the python script.
# Note: KAFKA_BOOTSTRAP is like "kafka:29092"
RUN printf '%s\n' \
  '#!/usr/bin/env bash' \
  'set -euo pipefail' \
  'hostport=${KAFKA_BOOTSTRAP:-kafka:29092}' \
  'host="${hostport%%:*}"' \
  'port="${hostport##*:}"' \
  'echo "Waiting for Kafka at ${host}:${port} ..."' \
  'for i in {1..60}; do' \
  '  if nc -z "$host" "$port" >/dev/null 2>&1; then' \
  '    echo "Kafka is up"; break' \
  '  fi' \
  '  sleep 1' \
  'done' \
  'exec python /app/producer.py' \
  > /usr/local/bin/entrypoint.sh && chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]