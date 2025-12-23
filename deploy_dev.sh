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

POSTGRES_HOST=postgres
POSTGRES_CONTAINER=postgres
DB_NAME=rcm_papers
DB_USER=admin
DB_PASSWORD=admin
SQL_DIR=./src/warehouse/sql

info "Starting deployment of services..."

info "Step 1: Starting Docker containers..."
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
success "Docker containers started."

#info "Step 2: Waiting for Airflow to be healthy..."
#
#MAX_WAIT=180
#INTERVAL=5
#ELAPSED=0
#
#while ! curl -sSf http://localhost:8080/ >/dev/null; do
#  if [ "$ELAPSED" -ge "$MAX_WAIT" ]; then
#    error "Timeout waiting for Airflow. Exiting."
#    exit 1
#  fi
#  warn "Airflow not ready yet, waiting ${INTERVAL}s..."
#  sleep $INTERVAL
#  ELAPSED=$((ELAPSED + INTERVAL))
#done
#
#success "Airflow is healthy!"
#
#info "Step 4: Setting up Airflow connections..."
#
#info "  4.1: Configuring MongoDB connection..."
#(docker exec airflow airflow connections delete mongo_default || true) >/dev/null 2>&1
#(docker exec airflow airflow connections add mongo_default \
#  --conn-type mongo \
#  --conn-host mongodb \
#  --conn-port 27017 \
#  --conn-login admin \
#  --conn-password admin \
#  --conn-schema raw_papers) >/dev/null 2>&1
#success "MongoDB connection configured."
#
#info "  4.2: Configuring PostgreSQL connection..."
#(docker exec airflow airflow connections delete postgres_default || true) >/dev/null 2>&1
#(docker exec airflow airflow connections add postgres_default \
#  --conn-type postgres \
#  --conn-host postgres \
#  --conn-port 5432 \
#  --conn-login admin \
#  --conn-password admin \
#  --conn-schema rcm_papers) >/dev/null 2>&1
#success "PostgreSQL connection configured."

info "Step 5: Waiting for PostgreSQL to be healthy..."

MAX_WAIT=180
INTERVAL=5
ELAPSED=0

while ! docker exec $POSTGRES_CONTAINER pg_isready -U $DB_USER >/dev/null 2>&1; do
  if [ "$ELAPSED" -ge "$MAX_WAIT" ]; then
    error "Timeout waiting for PostgreSQL. Exiting."
    exit 1
  fi
  warn "PostgreSQL not ready yet, waiting ${INTERVAL}s..."
  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))
done

success "PostgreSQL is ready!"

info "Step 6: Setting up PostgreSQL database, schema and table for dev..."

EXISTS=$(docker exec -i $POSTGRES_CONTAINER \
  psql "postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/postgres" \
  -tA -c "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';")

if [ "$EXISTS" != "1" ]; then
  docker exec -i $POSTGRES_CONTAINER \
    psql "postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/postgres" \
    -c "CREATE DATABASE $DB_NAME;"
  success "Database $DB_NAME created."
else
  info "Database $DB_NAME already exists."
fi

for file in $(ls $SQL_DIR/00_init/*.sql | sort); do
  info "Applying $file..."
  docker exec -i $POSTGRES_CONTAINER \
    psql "postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME" <"$file"
done

for file in "$SQL_DIR"/core/*.sql; do
  info "Applying $file..."
  docker exec -i $POSTGRES_CONTAINER psql \
    "postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME" <"$file"
done

success "Database, schema, and tables are ready for dev."

echo ""
success "All services are up and running!"
echo -e "${YELLOW}🔗 Service URLs:${NC}"
echo -e "  MongoDB UI:      ${GREEN}http://localhost:8081${NC}  (user: admin / pass: admin)"
echo -e "  PostgreSQL UI:   ${GREEN}http://localhost:5050${NC}  (user: admin@admin.com / pass: admin)"
echo -e "  Airflow Web UI:  ${GREEN}http://localhost:8080${NC}  (user: admin / pass: admin)"
echo ""
