# fpconnect-rca-copilot
RCA Copilot & Availability Engine for Healthcare/MedTech Operations

## Quick Start

### Web Frontend

```bash
cd apps/web
cp .env.example .env.local
# Edit .env.local with your API URL
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

### Environment Variables

Copy `apps/web/.env.example` to `apps/web/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Deploy to Vercel

1. Push your code to GitHub
2. Import the repository in [Vercel](https://vercel.com)
3. Set the **Root Directory** to `apps/web`
4. Add the `NEXT_PUBLIC_API_URL` environment variable
5. Deploy

### Docker (Full Stack)

```bash
make up        # Start all services
make logs      # View logs
make migrate   # Run database migrations
make down      # Stop all services
```

## Development

```bash
make dev-web   # Start frontend (port 3000)
make dev-api   # Start backend (port 8000)
make lint-web  # Lint frontend
make lint-api  # Lint backend
make test-api  # Run backend tests
```
