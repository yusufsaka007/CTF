#!/bin/bash

NETWORK="latrosec_network"
N8N_CONTAINER="n8n-container"
DEHASHED_CONTAINER="dehashed_service"

echo "[*] Creating docker network: $NETWORK"
docker network inspect "$NETWORK" >/dev/null 2>&1 || docker network create "$NETWORK"

# --- n8n ---
if ! docker ps --format '{{.Names}}' | grep -q "^${N8N_CONTAINER}$"; then
  # container not running, start it
  echo "[*] Starting n8n container..."
  if docker ps -a --format '{{.Names}}' | grep -q "^${N8N_CONTAINER}$"; then
    # container exists but stopped, start it
    docker start "$N8N_CONTAINER" >/dev/null
  else
    # container doesn't exist, create it
    docker run -d \
      --name "$N8N_CONTAINER" \
      --network "$NETWORK" \
      -p 5678:5678 \
      -v /home/viv4ldi/LatroSec/n8n-data:/home/node/.n8n \
      n8nio/n8n
  fi
else
  echo "[*] n8n container already running, skipping"
fi

# --- dehashed_service ---
if ! docker ps --format '{{.Names}}' | grep -q "^${DEHASHED_CONTAINER}$"; then
  echo "[*] Starting dehashed_service container..."
  docker run -it --rm -d \
    --name "$DEHASHED_CONTAINER" \
    --network "$NETWORK" \
    -p 8000:8000 \
    -v /home/viv4ldi/LatroSec/dehashed_service:/app \
    -w /app \
    python:3.11-slim \
    bash -c "pip install fastapi uvicorn colorama requests && uvicorn dehashed_service:app --host 0.0.0.0 --port 8000 --reload"
else
  echo "[*] dehashed_service container already running"
fi

echo
echo "[+] Containers running:"
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"

echo
echo "n8n → http://localhost:5678"
echo "dehashed_service → http://localhost:8000"
echo
echo "[*] Tailing logs for dehashed_service (Ctrl+C to stop)..."
docker logs -f "$DEHASHED_CONTAINER"

