# LoanSERP Docker Deployment Guide

This guide explains how to run the entire LoanSERP application stack using Docker.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Configuration](#environment-configuration)
- [Service Details](#service-details)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)
- [Production Considerations](#production-considerations)

---

## Architecture Overview

The LoanSERP application consists of the following services:

### Application Services

1. **Frontend** (Angular 18 + Nginx)
   - Port: 80
   - Serves the web UI
   - Proxies API requests to backend and LLM broker

2. **Backend** (Django 5 + Gunicorn)
   - Port: 8000
   - REST API server
   - Handles GSC integration, exposure tracking

3. **Celery Worker**
   - Background task processor
   - Handles async jobs (GSC pulls, data processing)

4. **Celery Beat**
   - Periodic task scheduler
   - Triggers scheduled jobs

5. **LLM Broker** (FastAPI)
   - Port: 9001
   - Brokers requests to Claude/Gemini APIs
   - Caches LLM responses

### Infrastructure Services

6. **PostgreSQL 15 + pgvector**
   - Port: 5432
   - Primary database
   - Includes pgvector extension for embeddings

7. **Redis 7**
   - Port: 6379
   - Cache layer
   - Celery message broker
   - LLM response cache

---

## Prerequisites

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- At least **4GB RAM** available for Docker
- At least **10GB disk space** for images and data

Check your installation:

```bash
docker --version
docker compose version
```

---

## Quick Start

### 1. Clone and Setup

```bash
cd LoanSERP_claude-gemini-seo
```

### 2. Configure Environment Variables

Copy the example files and edit with your actual values:

```bash
# Root .env (for backend and infrastructure)
cp .env.example .env
nano .env  # or use your preferred editor

# LLM Broker .env
cp geo_LLM_infra/llm_broker/.env.example geo_LLM_infra/llm_broker/.env
nano geo_LLM_infra/llm_broker/.env
```

**Required configurations:**
- `DJANGO_SECRET_KEY` - Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `CLAUDE_API_KEY` - Get from https://console.anthropic.com/
- `GEMINI_API_KEY` - Get from https://makersuite.google.com/app/apikey
- Database credentials (or use defaults)

### 3. Setup Google Search Console (Optional)

If using GSC integration:

```bash
mkdir -p secrets
# Copy your GSC credentials to secrets/
cp /path/to/client_secrets.json secrets/
```

### 4. Start Services

Using the provided script:

```bash
chmod +x docker-start.sh
./docker-start.sh
```

Or manually:

```bash
docker compose build
docker compose up -d
```

### 5. Access the Application

- **Web UI**: http://localhost
- **Backend API**: http://localhost:8000/admin
- **LLM Broker Docs**: http://localhost:9001/docs

### 6. Create Django Superuser (First Time Only)

```bash
docker compose exec backend python manage.py createsuperuser
```

---

## Environment Configuration

### Root `.env` File

Used by: Backend, Celery, PostgreSQL, Redis

Key variables:

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=false
ALLOWED_HOSTS=localhost,127.0.0.1,backend

# Database
POSTGRES_DB=loanserp
POSTGRES_USER=loan
POSTGRES_PASSWORD=loanpwd

# Redis
REDIS_URL=redis://redis:6379/1

# Business Logic
KEYWORD_TRACK_LIST=loan,mortgage,refinance
GSC_PROPERTY_URI=sc-domain:your-domain.com
```

### LLM Broker `.env` File

Used by: LLM Broker service

```bash
# API Keys
CLAUDE_API_KEY=sk-ant-your-key
GEMINI_API_KEY=your-key

# Behavior
PREFERRED_MODELS=claude-3-sonnet,gemini-1.5-pro
OUTPUT_LANG=zh-tw
LLM_CACHE_TTL_SEC=259200
```

---

## Service Details

### Frontend (Nginx)

- **Built with**: Multi-stage Dockerfile (Node.js build → Nginx serve)
- **Build time**: ~5-10 minutes (first time)
- **Image size**: ~50MB (after build)
- **Configuration**: `frontend/nginx.conf`

Features:
- Gzip compression
- API proxying to backend/llm-broker
- Security headers
- Static asset caching

### Backend (Django)

- **Built with**: Python 3.12 slim
- **Server**: Gunicorn with 4 workers
- **Database**: PostgreSQL via psycopg
- **Commands run on startup**:
  1. Database migrations
  2. Static file collection
  3. Gunicorn start

### Celery Services

**Worker**: Processes async tasks
- Concurrency: 4 workers
- Tasks: GSC pulls, data processing, analysis

**Beat**: Schedules periodic tasks
- Runs cron-like schedules defined in Django

### LLM Broker

- **Built with**: Python 3.12 slim
- **Server**: Uvicorn
- **Caching**: Redis with 3-day TTL
- **APIs**: Anthropic Claude, Google Gemini

---

## Common Tasks

### View Logs

```bash
# All services
./docker-logs.sh

# Specific service
./docker-logs.sh backend
./docker-logs.sh frontend -f  # follow mode

# Or directly
docker compose logs -f backend
```

### Restart a Service

```bash
docker compose restart backend
docker compose restart llm-broker
```

### Run Django Management Commands

```bash
# Django shell
docker compose exec backend python manage.py shell

# Create superuser
docker compose exec backend python manage.py createsuperuser

# Run migrations
docker compose exec backend python manage.py migrate

# Collect static files
docker compose exec backend python manage.py collectstatic
```

### Access Database

```bash
# PostgreSQL shell
docker compose exec postgres psql -U loan -d loanserp

# Or from host (if psql installed)
psql -h localhost -U loan -d loanserp
```

### Access Redis CLI

```bash
docker compose exec redis redis-cli

# Check cache keys
docker compose exec redis redis-cli KEYS "loans:seo:*"
```

### Stop Services

```bash
# Stop (preserve data)
./docker-stop.sh
# or
docker compose down

# Stop and remove all data
./docker-stop.sh --clean
# or
docker compose down -v
```

### Rebuild After Code Changes

```bash
# Rebuild specific service
docker compose build backend
docker compose up -d backend

# Rebuild all services
docker compose build
docker compose up -d
```

### View Service Status

```bash
docker compose ps
```

### Monitor Resource Usage

```bash
docker stats
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker compose logs <service-name>

# Check service status
docker compose ps

# Restart service
docker compose restart <service-name>
```

### Database Connection Errors

1. Ensure PostgreSQL is healthy:
   ```bash
   docker compose ps postgres
   # Should show "healthy"
   ```

2. Check database logs:
   ```bash
   docker compose logs postgres
   ```

3. Verify environment variables in `.env`

### Frontend Shows 502/504 Errors

- Backend might not be ready yet
- Check backend health:
  ```bash
  docker compose ps backend
  curl http://localhost:8000/admin/
  ```

### Celery Tasks Not Running

1. Check worker is running:
   ```bash
   docker compose ps celery-worker
   docker compose logs celery-worker
   ```

2. Check Redis connection:
   ```bash
   docker compose exec redis redis-cli ping
   # Should return "PONG"
   ```

### LLM Broker Errors

1. Verify API keys in `geo_LLM_infra/llm_broker/.env`
2. Check logs:
   ```bash
   docker compose logs llm-broker
   ```
3. Test endpoint:
   ```bash
   curl http://localhost:9001/docs
   ```

### Out of Disk Space

```bash
# Remove unused images/containers
docker system prune -a

# Check disk usage
docker system df
```

### Port Already in Use

If you get "port already allocated" errors:

```bash
# Find process using port (e.g., 8000)
sudo lsof -i :8000
# or
sudo netstat -tlnp | grep 8000

# Kill the process or change port in docker-compose.yml
```

---

## Production Considerations

### Security

1. **Change all default passwords** in `.env`
2. **Use strong DJANGO_SECRET_KEY**
3. **Set DJANGO_DEBUG=false**
4. **Use HTTPS** (add reverse proxy like Nginx or Traefik)
5. **Restrict ALLOWED_HOSTS** to your domain
6. **Never commit .env files** to version control
7. **Use Docker secrets** for sensitive data in production

### Performance

1. **Increase Gunicorn workers** based on CPU:
   ```yaml
   command: gunicorn ... --workers $((2 * $(nproc) + 1))
   ```

2. **Scale Celery workers**:
   ```bash
   docker compose up -d --scale celery-worker=4
   ```

3. **Use external database** (AWS RDS, Google Cloud SQL):
   - Better performance
   - Automatic backups
   - High availability

4. **Use external Redis** (AWS ElastiCache, Redis Cloud):
   - Better reliability
   - Persistence options

### Monitoring

Add monitoring services (Prometheus, Grafana):

```yaml
prometheus:
  image: prom/prometheus
  # ... configuration

grafana:
  image: grafana/grafana
  # ... configuration
```

### Backups

#### Database Backup

```bash
# Backup
docker compose exec postgres pg_dump -U loan loanserp > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20240101.sql | docker compose exec -T postgres psql -U loan -d loanserp
```

#### Redis Backup

```bash
# Backup (copy RDB file)
docker compose exec redis redis-cli SAVE
cp data/redis/dump.rdb backups/redis_$(date +%Y%m%d).rdb
```

### High Availability

For production:

1. **Use managed services**:
   - AWS RDS for PostgreSQL
   - AWS ElastiCache for Redis
   - AWS ECS/EKS for containers

2. **Load balancer** for multiple backend instances

3. **Auto-scaling** for Celery workers

4. **Health checks** and auto-restart

---

## FAQ

### Q: Can I run services individually?

Yes:
```bash
docker compose up -d postgres redis  # Just infrastructure
docker compose up -d backend         # Add backend
```

### Q: How do I update to a new version?

```bash
git pull
docker compose build
docker compose up -d
```

### Q: Can I use a different database?

Yes, but you'll need to modify Django settings and docker-compose.yml.

### Q: How do I enable SSL/HTTPS?

Add a reverse proxy (Nginx, Traefik, Caddy) in front of the services.

### Q: Data persistence - where is data stored?

- PostgreSQL: `./data/postgres/`
- Redis: `./data/redis/`
- Logs: `docker compose logs`

---

## Support

For issues or questions:
1. Check logs: `./docker-logs.sh`
2. Consult this guide
3. Review Docker and service documentation
4. Open an issue in the project repository

---

**Happy Deploying! 🚀**
