# Production Deployment

## Prerequisites

- A VPS or cloud VM (Ubuntu 22.04 recommended)
- Docker and Docker Compose installed
- A domain name with DNS configured

## Steps

### 1. Clone and configure

```bash
git clone https://github.com/ElhombreX21th/fpconnect-rca-copilot.git
cd fpconnect-rca-copilot
cp .env.example .env
# Fill in production values
```

### 2. Build and start

```bash
docker-compose -f docker-compose.yml up -d --build
```

### 3. Run migrations

```bash
docker-compose exec api alembic upgrade head
```

### 4. Set up reverse proxy (Nginx example)

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

### 5. SSL with Certbot

```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d api.yourapp.com -d yourapp.com
```

## Environment Variables

See `.env.example` for all required variables.

## Monitoring

- API logs: `docker-compose logs -f api`
- Database: Connect via `docker-compose exec db psql -U fpconnect`
