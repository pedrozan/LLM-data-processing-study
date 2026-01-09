FROM python:3.11-slim

WORKDIR /dbt

# Install dbt with compatible protobuf version
# TODO: fix protobuf error message after dbt run
RUN pip install --no-cache-dir dbt-postgres==1.7.0 'protobuf<4'

# Copy dbt project
COPY . .

# Default command - can be overridden
ENTRYPOINT ["dbt"]
CMD ["run"]
