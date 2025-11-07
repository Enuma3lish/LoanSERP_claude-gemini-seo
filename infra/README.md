# Infrastructure Directory

This directory contains the Docker infrastructure configuration for the LoanSERP application.

## Files

- `docker-compose.yml` - Main orchestration file for all services
- `db/init-db.sql` - PostgreSQL initialization script with pgvector extension

## Quick Commands

All commands below should be run from this directory (`infra/`).

### Start the stack
```bash
docker-compose up -d
```

### Stop the stack
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f [service-name]
```

### Rebuild after code changes
```bash
docker-compose up -d --build [service-name]
```

### Run Django commands
```bash
docker-compose exec backend python manage.py [command]
```

## Services

- **postgres** - PostgreSQL 16 with pgvector (port 5432)
- **redis** - Redis 7 (port 6379)
- **backend** - Django application (port 8000)
- **celery-worker** - Background task processor
- **celery-beat** - Scheduled task manager
- **llm-broker** - FastAPI LLM service (port 9001)

## Environment Variables

Make sure you have a `.env` file in the project root with all required variables. See `../.env.example` for the template.

## More Information

For detailed documentation, see: `../DOCKER_README.md`
