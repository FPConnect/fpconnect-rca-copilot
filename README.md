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

## Environment Variables

Copy `apps/web/.env.example` to `apps/web/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=FPConnect
NEXT_PUBLIC_APP_VERSION=1.0.0
```

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | FastAPI backend URL |
| `NEXT_PUBLIC_APP_NAME` | `FPConnect` | Application name |
| `NEXT_PUBLIC_APP_VERSION` | `1.0.0` | Application version |

## Deploy to Vercel

1. Push your code to GitHub
2. Import the repository in [Vercel](https://vercel.com)
3. Set the **Root Directory** to `apps/web`
4. Add environment variables:
   - `NEXT_PUBLIC_API_URL` → your backend URL
   - `NEXT_PUBLIC_APP_NAME` → `FPConnect`
   - `NEXT_PUBLIC_APP_VERSION` → `1.0.0`
5. Click **Deploy**

The app will be live at your Vercel URL with no authentication required.

## Docker (Full Stack)

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
