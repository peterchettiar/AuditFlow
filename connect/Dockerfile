FROM confluentinc/cp-kafka-connect:7.6.1

# Install the legacy, self-hosted BigQuery sink from Confluent Hub
# (works with self-managed Connect)
RUN confluent-hub install --no-prompt wepay/kafka-connect-bigquery:2.5.7

# (Optional) list installed connectors
RUN ls -la /usr/share/confluent-hub-components

EXPOSE 8083

# CMD ["/bin/bash", "-c", "while true; do sleep 3600000; done"]