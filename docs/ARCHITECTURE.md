# FPConnect Architecture

## Overview

FPConnect is a monorepo containing:
- **Backend API** (`apps/api/`) — FastAPI + PostgreSQL + Redis
- **Web Frontend** (`apps/web/`) — Next.js 14 + Tailwind CSS + Clerk
- **Mobile App** (`apps/mobile/`) — Expo React Native
- **Infrastructure** (`infra/`) — Docker, SQL migrations

## System Design

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Web (Next)  │────▶│  FastAPI     │────▶│  PostgreSQL  │
│  Mobile(Expo)│     │  (REST API)  │     │  + pgvector  │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                     ┌──────▼───────┐
                     │    Redis     │
                     │  (Cache)     │
                     └──────────────┘
```

## Data Flow: RCA Analysis

1. Technician creates a ticket via Web or Mobile
2. API stores ticket in PostgreSQL
3. `/analyze` endpoint is called with the ticket ID
4. `analyze_service.py` queries historical tickets and KB articles
5. RCA suggestions are stored and returned to the client

## Authentication

- JWT-based auth with HS256 signing
- Passwords hashed with bcrypt
- Clerk (optional) for frontend social login

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md).
