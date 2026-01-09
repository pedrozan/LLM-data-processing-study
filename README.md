# LLM-data-processing-study
A study on the use of LLMs to process customer support tickets

## Setup

### Prerequisites
- Docker
- Docker Compose

### Install Git Hooks

This repository uses git hooks to enforce Conventional Commits for commit messages. After cloning the repository, run the setup script:

```bash
bash scripts/setup-hooks.sh
```

This will install the `commit-msg` hook that validates your commits. For more details, see [COMMIT_CONVENTIONS.md](COMMIT_CONVENTIONS.md).

## Docker Setup

This project uses Docker Compose to manage two services:
- **postgres**: A PostgreSQL database instance
- **app**: A Python application that reads customer support tickets from CSV and loads them into the database

### Configuration

Create a `.env` file based on the example:

```bash
cp .env.example .env
```

You can customize the database credentials in `.env`.

### Running the Application

To build and run the containers:

```bash
docker-compose up --build
```

The app will automatically:
1. Wait for the PostgreSQL container to be healthy
2. Create the `raw_support_tickets` table
3. Load data from `files/customer_support_tickets.csv`
4. Exit when complete

To run in detached mode:

```bash
docker-compose up --build -d
```

### Useful Commands

**View logs:**
```bash
docker-compose logs -f app
docker-compose logs -f postgres
```

**Access the PostgreSQL CLI:**
```bash
docker-compose exec postgres psql -U postgres -d llm_data
```

**Verify data was loaded:**
```bash
docker-compose exec postgres psql -U postgres -d llm_data -c "SELECT COUNT(*) FROM raw_support_tickets;"
```

**Stop and remove containers:**
```bash
docker-compose down
```

**Remove containers and database volume:**
```bash
docker-compose down -v
```

## Project Structure

```
src/ingest/
  └── load_raw_tickets.py    # Script to load CSV data into PostgreSQL

files/
  └── customer_support_tickets.csv  # Source data

Dockerfile                    # Python app container definition
docker-compose.yml           # Multi-container orchestration
requirements.txt             # Python dependencies
.env.example                 # Environment variables template
```