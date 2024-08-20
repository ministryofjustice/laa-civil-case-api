#!/bin/bash
docker compose down --remove-orphans
docker compose up -d --build
docker compose wait migrations
docker compose logs migrations
docker compose rm --force
docker compose logs api
python3 add_users.py