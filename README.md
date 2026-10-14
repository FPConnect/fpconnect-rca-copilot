# OPSPECTA
Assistive data organization for MedTech technical service operations

OPSPECTA is the working display name under validation. FPConnect remains the
historical project and technical compatibility identifier; no trademark
registration or legal clearance is claimed.

> **Web preview:** local demonstration data is available only when `NEXT_PUBLIC_PREVIEW_MODE=true`. Keep it disabled in production. API-backed workflows require authentication tokens from `/auth/login`.

## Quick Start

```bash
git clone <repo-url>
cd fpconnect-rca-copilot/apps/web
cp .env.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the landing page.
The authenticated workspace requires a working API and a valid account; local
preview data is not an authentication mechanism.

Production self-registration is limited to email addresses explicitly listed
in `REGISTRATION_ALLOWED_EMAILS`. New accounts always receive the regular
`user` role and cannot select their own access level.

### Run the API locally

```bash
cd apps/api
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Install `requirements-ml.txt` instead when local semantic-search embeddings are
required. The Vercel runtime uses the smaller production dependency set and
falls back to the documented non-semantic RCA response when that optional model
is unavailable.

To seed demo data and development test users, explicitly set
`SEED_TEST_ACCOUNTS=true` and a unique `TEST_ACCOUNT_PASSWORD` of at least 12
characters in `apps/api/.env`, then run `python scripts/seed_clinical.py`.
Seeding replaces the password for the listed development accounts, so never
enable it outside a disposable local development database.

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
NEXT_PUBLIC_APP_NAME=OPSPECTA
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_SITE_URL=https://fpconnect.tec.br
```

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | FastAPI backend URL |
| `NEXT_PUBLIC_APP_NAME` | `OPSPECTA` | Application display name |
| `NEXT_PUBLIC_APP_VERSION` | `1.0.0` | Application version |
| `NEXT_PUBLIC_SITE_URL` | `https://fpconnect.tec.br` | Canonical production URL used by metadata and domain redirects |

`NEXT_PUBLIC_APP_NAME` controls the Web display name at build time and defaults
to `OPSPECTA`. For the Expo app, update only `expo.name` in
`apps/mobile/app.json` when a display-name change is approved. Keep the Expo
`slug`, `scheme`, bundle/package identifiers, API contracts, and existing
`fpconnect_*` storage keys unchanged unless a separate migration is planned.

## Commercial scope and evidence

Public offer descriptions are planning references, not guarantees. Confirm data
availability, access, deliverables, acceptance criteria, and schedule with the
customer before contracting. The current reference scopes are:

| Offer | Reference scope | Target timeline |
|---|---|---|
| Support diagnosis | Up to 100 service orders, one source, interview, bottlenecks, and action plan | 5 business days |
| Metrics pilot | Up to 300 service orders, one source/team/service line, dashboard, and triage | 10 business days |
| Metrics pilot + assisted automation | Metrics pilot scope, one workflow, and one integration after technical validation | 15 business days |

Public pages and documentation do not publish prices. Commercial proposals are
sized after the technical scope, integrations, security requirements, support
level, and acceptance criteria are confirmed.

Recurring service is a hypothesis to validate after paid pilots, not an
established offer. Describe product capabilities as assistive unless verified
in the current implementation. Demonstrations use illustrative data; report
outcomes as measured only when the period, sample, calculation, and permission
to disclose are documented.

The Strategic Moats calculator is an arithmetic scenario using user-entered
premises. Its values are not measured product impact, realized savings,
downtime reduction, or a guaranteed return. Do not reuse its outputs as
customer evidence or performance claims.

## Deploy to Production (Cloud)

### Architecture

| Component | Platform | Notes |
|---|---|---|
| Web (Next.js) | [Vercel](https://vercel.com) | Free tier available |
| API (FastAPI) | [Vercel](https://vercel.com) | Existing `fpconnect-rca-copilot-main` project |
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

### Step 3 — API (Vercel)

1. Import this repository into a dedicated Vercel project for the API.
2. Set **Root Directory** to `apps/api` and **Framework Preset** to FastAPI.
3. Add the following production environment variables in Vercel:

   ```
   APP_ENV=production
   PUBLIC_REGISTRATION_ENABLED=false
   REGISTRATION_ALLOWED_EMAILS=[]
   CORS_ORIGINS=["https://fpconnect.tec.br","https://www.fpconnect.tec.br"]
   DATABASE_URL=<your Neon connection string>
   REDIS_URL=<your Upstash Redis URL>
   SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
   REFRESH_SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
   ACCESS_TOKEN_EXPIRE_MINUTES=15
   REFRESH_TOKEN_EXPIRE_DAYS=7
   OPENAI_API_KEY=<your OpenAI key>
   S3_ENDPOINT_URL=<your S3/R2 endpoint>
   S3_ACCESS_KEY_ID=<your access key>
   S3_SECRET_ACCESS_KEY=<your secret key>
   S3_BUCKET_NAME=fpconnect-ticket-attachments
   ```

4. Apply the authentication schema repair before promoting a deployment:
   ```bash
   vercel env run --environment=production -- python apps/api/scripts/migrate_auth_schema.py
   ```
5. Add `api.fpconnect.tec.br` to this API project and verify `/health` and `/auth/login` before updating the alias.

To enable allowlisted self-registration, set `PUBLIC_REGISTRATION_ENABLED=true`
and list the authorized addresses in `REGISTRATION_ALLOWED_EMAILS`.

### Step 4 — Web (Vercel)

1. Create an account at [vercel.com](https://vercel.com)
2. Click **Add New → Project** and import this GitHub repository
3. Set **Root Directory** to `apps/web` in the Vercel project settings.
4. Add the following environment variables:

   ```
   NEXT_PUBLIC_API_URL=https://api.fpconnect.tec.br
   NEXT_PUBLIC_APP_NAME=OPSPECTA
   NEXT_PUBLIC_APP_VERSION=1.0.0
   NEXT_PUBLIC_SITE_URL=https://fpconnect.tec.br
   ```

5. Add `fpconnect.tec.br` in **Vercel → Project → Settings → Domains** and point DNS according to Vercel. See `docs/DOMAIN_MIGRATION.md` for the full domain migration checklist.
6. Click **Deploy** — your app will be live at `https://<your-project>.vercel.app`

### Step 5 — Automated CI/CD (GitHub Actions)

Push to `main` automatically tests and deploys both services. Add this secret to your GitHub repository (**Settings → Secrets and variables → Actions**):

| Secret | How to get it |
|---|---|
| `VERCEL_TOKEN` | Vercel dashboard → Settings → Tokens |

Add these repository variables in the same Actions settings:

| Variable | Value |
|---|---|
| `VERCEL_ORG_ID` | Vercel team ID |
| `VERCEL_PROJECT_ID` | Web project ID |
| `VERCEL_API_PROJECT_ID` | API project ID |

Once the secrets are set, every push to `main` will:
1. Run all tests
2. Deploy the web app to Vercel
3. Deploy the API to Vercel and promote it only after health and authentication probes pass

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
