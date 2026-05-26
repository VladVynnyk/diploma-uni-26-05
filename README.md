# Consulting Marketplace Demo

This repository contains:

- `consulting-backend`: FastAPI, PostgreSQL, SQLAlchemy, Alembic, Redis
- `advicerr-frontend`: Next.js frontend
- `docker-compose.dev.yml`: local development stack with Traefik, frontend, backend, PostgreSQL, and Redis

## Demo Data / Seed Data

The backend now supports idempotent demo-data seeding for diploma/demo runs. The seed uses the existing SQLAlchemy models and the same password hashing helper as normal registration.

What gets created:

- 1 admin user
- 20 consultants with categories, descriptions, prices, and tags
- 25 clients
- 10 consultation tags
- 15 consultation orders with mixed statuses
- 8 reviews tied to consultant-client pairs with completed consultations

### Auto-seed on project startup

The root development stack enables demo seeding by default.

Run:

```bash
docker compose -f docker-compose.dev.yml up --build
```

By default, the backend starts with:

```env
SEED_DEMO_DATA=true
```

If you want to start the project without demo data:

```bash
$env:SEED_DEMO_DATA="false"
docker compose -f docker-compose.dev.yml up --build
```

### Manual seed run

If the containers are already running, you can run the seed manually:

```bash
docker compose -f docker-compose.dev.yml exec backend sh -c "cd /backend/core && python seed.py"
```

You can also run it in the backend-only compose file:

```bash
docker compose -f consulting-backend/docker-compose.dev.yml exec api sh -c "cd /backend/core && python seed.py"
```

### Idempotency

The seed is safe to run repeatedly:

- users are matched by `email`
- tags are matched by `name`
- orders are matched by `client + consultant + topic`
- reviews are matched by `client + consultant + description`

Repeated runs should not create duplicates.

## Demo Users

### Admin

- email: `admin@example.com`
- password: `admin12345`

### Consultant

- email: `consultant.business@example.com`
- password: `password123`

### Client

- email: `client1@example.com`
- password: `password123`

Additional demo users are also created:

- consultants: `consultant.law@example.com`, `consultant.finance@example.com`, `consultant.it@example.com`, `consultant.marketing@example.com`, and others
- clients: `client2@example.com` through `client25@example.com`

All consultant and client demo users use the password:

```text
password123
```

## How To Verify Demo Flow

### Admin dashboard

1. Log in as `admin@example.com`.
2. Open `/dashboard`.
3. Verify the admin sections load:
   `Users`, `Orders`, `Reviews`, `Tags`, `Stats`.

### Consultant dashboard

1. Log in as `consultant.business@example.com`.
2. Open `/dashboard`.
3. Verify the consultant can:
   view own consultations,
   see client contact details for assigned consultations,
   update status only through allowed transitions.

### Client workflow

1. Log in as `client1@example.com`.
2. Open `/dashboard`.
3. Verify the client can:
   view own consultations,
   see created orders,
   browse consultants on the homepage.

### Public marketplace data

After seeding, the homepage should show consultants with:

- tags
- descriptions
- prices
- ratings

Consultant profile views should also show demo reviews.

## Notes

- Demo data is only auto-loaded when `SEED_DEMO_DATA=true`.
- Production should keep `SEED_DEMO_DATA=false` unless demo data is explicitly required.
- The seed does not change the auth flow or create extra tables.
