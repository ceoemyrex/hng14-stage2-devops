# Job Processing System — Stage 2 DevOps

A containerized microservices application with a full CI/CD pipeline.

## Services
- **Frontend** (Node.js) — Job submission UI on port 3000
- **API** (Python/FastAPI) — REST API for job management
- **Worker** (Python) — Background job processor
- **Redis** — Job queue (internal only, not exposed)

## Prerequisites
- Docker Engine >= 24.x
- Docker Compose plugin >= 2.x
- Git

## Quick Start (Clean Machine)

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/hng14-stage2-devops.git
cd hng14-stage2-devops
```

### 2. Set up environment
```bash
cp .env.example .env
# .env is pre-filled with sane defaults — no changes needed for local dev
```

### 3. Start the stack
```bash
docker compose up -d --build
```

### 4. Verify all services are healthy
```bash
docker compose ps
# Wait ~60 seconds — all 4 services should show: running (healthy)
```

### 5. Access the app
Open your browser to: http://localhost:3000

## Successful Startup Output
