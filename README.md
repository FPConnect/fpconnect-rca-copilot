# fpconnect-rca-copilot
RCA Copilot & Availability Engine for Healthcare/MedTech Operations

> **No authentication required** — the app is fully open access. Just clone, install, and run.

## Quick Start

```bash
git clone <repo-url>
cd fpconnect-rca-copilot/apps/web
cp .env.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) — the app redirects to `/dashboard` automatically. No login needed.

> To run on port 3001: `npm run dev -- -p 3001`

## Mobile App (React Native / Expo)

The project includes a full React Native mobile app under `apps/mobile`.

### Prerequisites

- [Node.js 18+](https://nodejs.org)
- [Expo Go](https://expo.dev/client) installed on your iOS or Android device, **or** an Android/iOS simulator

### Run on your device or simulator

```bash
cd apps/mobile
npm install
npm start          # opens Expo Dev Tools — scan the QR code with Expo Go
```

Or use the Makefile from the repository root:

```bash
make install-mobile   # install dependencies
make dev-mobile       # start the Expo dev server
```

To target a specific platform:

```bash
npm run android   # open in Android emulator / connected device
npm run ios       # open in iOS simulator (macOS only)
npm run web       # open in browser (Expo Web)
```

### Mobile screens

| Screen | Description |
|---|---|
| Dashboard | Summary metrics and recent activity feed |
| Machines | Live list of medical equipment with status badges |
| Tickets | Create and search maintenance tickets |
| Settings | User profile, appearance, and notification preferences |

## Environment Variables

Copy `apps/web/.env.example` to `apps/web/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=FPConnect
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_SITE_URL=https://fpconnect.tec.br
```

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | FastAPI backend URL |
| `NEXT_PUBLIC_APP_NAME` | `FPConnect` | Application name |
| `NEXT_PUBLIC_APP_VERSION` | `1.0.0` | Application version |
| `NEXT_PUBLIC_SITE_URL` | `https://fpconnect.tec.br` | Canonical production URL used by metadata and domain redirects |

## Deploy to Production (Cloud)

### Architecture

| Component | Platform | Notes |
|---|---|---|
| Web (Next.js) | [Vercel](https://vercel.com) | Free tier available |
| API (FastAPI) | [Railway](https://railway.app) | Free trial available |
| Database (PostgreSQL + pgvector) | [Neon](https://neon.tech) | Free tier, supports pgvector |
| Redis | [Upstash](https://upstash.com) | Free tier |
| Storage | [Cloudflare R2](https://cloudflare.com/r2) or AWS S3 | |

### Step 1 — Database (Neon)

1. Create a free account at [neon.tech](https://neon.tech)
2. Create a new project and copy the **Connection String** (it looks like `postgresql://user:pass@host/db?sslmode=require`)
3. Enable the `pgvector` extension in the Neon SQL editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### Step 2 — Redis (Upstash)

1. Create a free account at [upstash.com](https://upstash.com)
2. Create a new **Redis** database (choose the region closest to your API)
3. Copy the **Redis URL** (e.g. `rediss://default:password@host:port`)

### Step 3 — API (Railway)

1. Create an account at [railway.app](https://railway.app)
2. Click **New Project → Deploy from GitHub repo** and select this repository
3. Set the **Root Directory** to `apps/api`
4. Add the following environment variables in Railway's dashboard:

   ```
   DATABASE_URL=<your Neon connection string>
   REDIS_URL=<your Upstash Redis URL>
   SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
   OPENAI_API_KEY=<your OpenAI key>
   MINIO_ENDPOINT=<your S3/R2 endpoint>
   MINIO_ACCESS_KEY=<your access key>
   MINIO_SECRET_KEY=<your secret key>
   MINIO_BUCKET=fpconnect
   ```

5. After deploying, run the database migrations from the Railway shell:
   ```bash
   alembic upgrade head
   ```
6. Copy the public Railway URL (e.g. `https://fpconnect-api.up.railway.app`)

### Step 4 — Web (Vercel)

1. Create an account at [vercel.com](https://vercel.com)
2. Click **Add New → Project** and import this GitHub repository
3. The **Root Directory** is pre-configured via `vercel.json` — Vercel will detect `apps/web` automatically
4. Add the following environment variables:

   ```
   NEXT_PUBLIC_API_URL=<your Railway API URL from Step 3>
   NEXT_PUBLIC_APP_NAME=FPConnect
   NEXT_PUBLIC_APP_VERSION=1.0.0
   NEXT_PUBLIC_SITE_URL=https://fpconnect.tec.br
   ```

5. Add `fpconnect.tec.br` in **Vercel → Project → Settings → Domains** and point DNS according to Vercel. See `docs/DOMAIN_MIGRATION.md` for the full domain migration checklist.
6. Click **Deploy** — your app will be live at `https://<your-project>.vercel.app`

### Step 5 — Automated CI/CD (GitHub Actions)

Push to `main` automatically tests and deploys both services. Add these secrets to your GitHub repository (**Settings → Secrets and variables → Actions**):

| Secret | How to get it |
|---|---|
| `VERCEL_TOKEN` | Vercel dashboard → Settings → Tokens |
| `RAILWAY_TOKEN` | Railway dashboard → Account → Tokens |

Once the secrets are set, every push to `main` will:
1. Run all tests
2. Deploy the web app to Vercel
3. Deploy the API to Railway

---

## Docker (Full Stack — Local)

```bash
make up        # Start all services
make logs      # View logs
make migrate   # Run database migrations
make down      # Stop all services
```

Or run only the frontend:

```bash
cd apps/web
docker build -t fpconnect-web .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8000 fpconnect-web
```

## Development

```bash
make dev-web   # Start frontend (port 3000)
make dev-api   # Start backend (port 8000)
make lint-web  # Lint frontend
make lint-api  # Lint backend
make test-api  # Run backend tests
```
