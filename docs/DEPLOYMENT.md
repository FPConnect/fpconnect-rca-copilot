# Production Deployment

## Cloud Deployment (Recommended)

Deploy the full stack for free using managed cloud services — no server management required.

### Services Used

| Component | Service | URL |
|---|---|---|
| Web (Next.js) | Vercel | https://vercel.com |
| API (FastAPI) | Vercel | https://vercel.com |
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

### 3. API — Vercel

1. Import this repository into a dedicated Vercel project for the API.
2. Set **Root Directory** to `apps/api` and **Framework Preset** to FastAPI.
3. Set production environment variables:

   ```env
   DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
   REDIS_URL=rediss://default:pass@host:port
   APP_ENV=production
   SEED_TEST_ACCOUNTS=false
   PUBLIC_REGISTRATION_ENABLED=false
   REGISTRATION_ALLOWED_EMAILS=[]
   CORS_ORIGINS=["https://fpconnect.tec.br","https://www.fpconnect.tec.br"]
   SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_hex(32))">
   REFRESH_SECRET_KEY=<generate a separate secret with at least 32 characters>
   ALGORITHM=HS256
   JWT_ISSUER=opspecta-api
   JWT_AUDIENCE=opspecta-app
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   OPENAI_API_KEY=sk-...
   S3_ENDPOINT_URL=<s3-endpoint>
   S3_ACCESS_KEY_ID=<access-key>
   S3_SECRET_ACCESS_KEY=<secret-key>
   S3_BUCKET_NAME=fpconnect-ticket-attachments
   ```

4. Reconcile the idempotent legacy schema and then run the full migration chain before promotion:
   ```bash
   vercel env run --environment=production -- python apps/api/scripts/migrate_auth_schema.py --reconcile-alembic
   vercel env run --environment=production -- sh -c 'cd apps/api && alembic upgrade head'
   ```
5. Add `api.fpconnect.tec.br` to the API project. Verify `/health` and that an unknown `/auth/login` request returns `401` before updating the public alias.

When self-registration is needed, set `PUBLIC_REGISTRATION_ENABLED=true`,
populate `REGISTRATION_ALLOWED_EMAILS` with the authorized addresses, set
`NEXT_PUBLIC_REGISTRATION_ENABLED=true` in the web project and rebuild both
deployments. Keep the API allowlist restricted even when the web form is visible.

### 4. Web — Vercel

1. Sign up at [vercel.com](https://vercel.com).
2. **Add New → Project**, import this GitHub repository.
3. Set **Root Directory** to `apps/web` in the Vercel project settings.
4. Set environment variables:

   ```env
   NEXT_PUBLIC_API_URL=https://api.fpconnect.tec.br
   NEXT_PUBLIC_APP_NAME=OPSPECTA
   NEXT_PUBLIC_APP_VERSION=1.0.0
   NEXT_PUBLIC_SITE_URL=https://fpconnect.tec.br
   NEXT_PUBLIC_REGISTRATION_ENABLED=false
   NEXT_PUBLIC_PREVIEW_MODE=false
   ```

5. Add the production domain `fpconnect.tec.br` in **Vercel → Project → Settings → Domains**.
6. Configure DNS with the records shown by Vercel. See `docs/DOMAIN_MIGRATION.md` for the complete migration and validation checklist.
7. Click **Deploy**. The app goes live at `https://fpconnect.tec.br` after DNS validation.

### 5. CI/CD — GitHub Actions

Add this secret to your GitHub repo (**Settings → Secrets and variables → Actions**):

| Secret | Where to find it |
|---|---|
| `VERCEL_TOKEN` | Vercel → Settings → Tokens |

Add these repository variables:

| Variable | Value |
|---|---|
| `VERCEL_ORG_ID` | Vercel team ID |
| `VERCEL_PROJECT_ID` | Web project ID |
| `VERCEL_API_PROJECT_ID` | API project ID |

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
