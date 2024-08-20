#!/bin/bash
docker compose down --remove-orphans
docker compose up -d --build
docker compose wait migrations
docker compose logs migrations
docker compose rm --force
docker compose logs api
# Adds in a local user
container_id=$(docker ps --filter "ancestor=postgres:16" --format "{{.ID}}")
docker cp "insert_local_user.sql" "${container_id}:/tmp/insert_local_user.sql"
docker exec -it ${container_id} psql -U postgres -d case_api -f /tmp/insert_local_user.sql