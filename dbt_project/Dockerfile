FROM python:3.11-slim

WORKDIR /dbt

# Install dbt
RUN pip install --no-cache-dir dbt-postgres==1.7.0

# Copy dbt project
COPY . .

# Default command - can be overridden
ENTRYPOINT ["dbt"]
CMD ["run"]
