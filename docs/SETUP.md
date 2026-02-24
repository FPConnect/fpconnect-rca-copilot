# Local Development Setup

## Prerequisites

- Docker 24+ and Docker Compose v2
- Python 3.11+
- Node.js 20+
- Git

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/ElhombreX21th/fpconnect-rca-copilot.git
cd fpconnect-rca-copilot

# 2. Copy environment variables
cp .env.example .env
# Edit .env with your values (especially OpenAI and Clerk keys)

# 3. Start all services
make up

# 4. Run migrations
make migrate

# 5. Open the app
# Web: http://localhost:3000
# API: http://localhost:8000/docs
# MinIO: http://localhost:9001
```

## Backend Development

```bash
make install-api
make dev-api
```

## Frontend Development

```bash
make install-web
make dev-web
```

## Running Tests

```bash
make test-api
make test-web
```

## Troubleshooting

### Database connection refused
Ensure the `db` container is healthy: `docker-compose ps`

### Port already in use
Change the port in docker-compose.yml or stop the conflicting service.

### Alembic migration errors
```bash
cd apps/api
alembic downgrade base
alembic upgrade head
```
