#!/bin/bash

# ============================================
# Deployment Scripts for local dev environment
# ============================================

set -e

# Color codes
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

info "Starting deployment of services..."

info "Step 1: Starting Docker containers..."
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
success "Docker containers started."

info "Step 2: Waiting for Airflow to be healthy..."

MAX_WAIT=180
INTERVAL=5
ELAPSED=0

while ! curl -sSf http://localhost:8080/health >/dev/null; do
  if [ "$ELAPSED" -ge "$MAX_WAIT" ]; then
    error "Timeout waiting for Airflow. Exiting."
    exit 1
  fi
  warn "Airflow not ready yet, waiting ${INTERVAL}s..."
  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))
done

success "Airflow is healthy!"

info "Step 3: Initializing Airflow DB..."
docker exec airflow bash -c "airflow db init" >/dev/null 2>&1
success "Airflow DB initialized."

info "Step 4: Setting up Airflow connections..."

info "  4.1: Configuring MongoDB connection..."
(docker exec airflow airflow connections delete mongo_default || true) >/dev/null 2>&1
(docker exec airflow airflow connections add mongo_default \
  --conn-type mongo \
  --conn-host mongodb \
  --conn-port 27017 \
  --conn-login admin \
  --conn-password admin \
  --conn-schema raw_papers) >/dev/null 2>&1
success "MongoDB connection configured."

info "  4.2: Configuring PostgreSQL connection..."
(docker exec airflow airflow connections delete postgres_default || true) >/dev/null 2>&1
(docker exec airflow airflow connections add postgres_default \
  --conn-type postgres \
  --conn-host postgres \
  --conn-port 5432 \
  --conn-login admin@admin.com \
  --conn-password admin \
  --conn-schema test) >/dev/null 2>&1
success "PostgreSQL connection configured."

echo ""
success "All services are up and running!"
echo -e "${YELLOW}🔗 Service URLs:${NC}"
echo -e "  MongoDB UI:      ${GREEN}http://localhost:8081${NC}  (user: admin / pass: admin)"
echo -e "  PostgreSQL UI:   ${GREEN}http://localhost:5050${NC}  (user: admin@admin.com / pass: admin)"
echo -e "  Airflow Web UI:  ${GREEN}http://localhost:8080${NC}  (user: admin / pass: admin)"
echo ""
