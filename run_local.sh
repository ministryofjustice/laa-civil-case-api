#!/bin/bash

if [ -z ${SECRET_KEY} ]; then
    echo "SECRET_KEY is unset."
    exit 1
fi

docker compose down --remove-orphans
docker compose up -d --build
docker compose wait migrations
docker compose logs migrations
docker compose rm --force
docker compose logs api
docker compose exec api python3 bin/add_users.py
