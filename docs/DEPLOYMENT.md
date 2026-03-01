# Production Deployment

## Cloud Deployment (Recommended)

Deploy the full stack for free using managed cloud services — no server management required.

### Services Used

| Component | Service | URL |
|---|---|---|
| Web (Next.js) | Vercel | https://vercel.com |
| API (FastAPI) | Railway | https://railway.app |
| Database | Neon (PostgreSQL + pgvector) | https://neon.tech |
| Redis | Upstash | https://upstash.com |
| Object Storage | Cloudflare R2 or AWS S3 | |

### 1. Database — Neon

1. Sign up at [neon.tech](https://neon.tech) and create a project.
2. Copy the **Connection String** from the dashboard.
3. Enable pgvector in the Neon SQL editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### 2. Redis — Upstash

1. Sign up at [upstash.com](https://upstash.com).
2. Create a **Redis** database.
3. Copy the **Redis URL** (e.g. `rediss://default:password@host:port`).

### 3. API — Railway

1. Sign up at [railway.app](https://railway.app).
2. **New Project → Deploy from GitHub repo**, select this repository.
3. Set **Root Directory** to `apps/api`.
4. Set environment variables:

   ```env
   DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
   REDIS_URL=rediss://default:pass@host:port
   SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_hex(32))">
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   OPENAI_API_KEY=sk-...
   MINIO_ENDPOINT=<s3-endpoint>
   MINIO_ACCESS_KEY=<access-key>
   MINIO_SECRET_KEY=<secret-key>
   MINIO_BUCKET=fpconnect
   ```

5. Deploy, then run migrations from the Railway shell:
   ```bash
   alembic upgrade head
   ```
6. Note your Railway public URL (e.g. `https://fpconnect-api.up.railway.app`).

### 4. Web — Vercel

1. Sign up at [vercel.com](https://vercel.com).
2. **Add New → Project**, import this GitHub repository.
3. Vercel automatically detects `apps/web` as the root directory via `vercel.json`.
4. Set environment variables:

   ```env
   NEXT_PUBLIC_API_URL=https://fpconnect-api.up.railway.app
   NEXT_PUBLIC_APP_NAME=FPConnect
   NEXT_PUBLIC_APP_VERSION=1.0.0
   ```

5. Click **Deploy**. The app goes live at `https://<project>.vercel.app`.

### 5. CI/CD — GitHub Actions

Add these secrets to your GitHub repo (**Settings → Secrets and variables → Actions**):

| Secret | Where to find it |
|---|---|
| `VERCEL_TOKEN` | Vercel → Settings → Tokens |
| `RAILWAY_TOKEN` | Railway → Account → Tokens |

The `.github/workflows/deploy.yml` workflow will automatically test and redeploy both services on every push to `main`.

---

## Self-Hosted Deployment (VPS / Docker)

Use this if you prefer to manage your own server.

### Prerequisites

- Ubuntu 22.04 VPS (or any Linux server)
- Docker and Docker Compose installed
- A domain name pointing to your server's IP

### Steps

#### 1. Clone and configure

```bash
git clone https://github.com/ElhombreX21th/fpconnect-rca-copilot.git
cd fpconnect-rca-copilot
cp .env.example .env
# Edit .env with production values
```

#### 2. Build and start

```bash
docker-compose up -d --build
```

#### 3. Run migrations

```bash
docker-compose exec api alembic upgrade head
```

#### 4. Reverse proxy (Nginx)

```nginx
server {
    listen 80;
    server_name api.yourapp.com;
    location / {
        proxy_pass http://localhost:8000;
    }
}
server {
    listen 80;
    server_name yourapp.com;
    location / {
        proxy_pass http://localhost:3000;
    }
}
```

#### 5. SSL with Certbot

```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d api.yourapp.com -d yourapp.com
```

### Monitoring

- API logs: `docker-compose logs -f api`
- Database: `docker-compose exec db psql -U fpconnect`
- All logs: `make logs`

