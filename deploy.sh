#!/bin/bash

set -e

cd /opt/star-burger/

git pull

. .env

DOCKER_BUILDKIT=1 docker-compose -f docker-compose.prod.yml up --build --force-recreate --no-deps -d server
docker cp starburger-backend:/app/staticfiles/ ./frontend/

DOCKER_BUILDKIT=1 docker-compose -f docker-compose.prod.yml up --build --force-recreate --no-deps -d parcel
docker cp starburger-parcel:/app/bundles-src/ ./frontend/

docker cp ./frontend/. starburger-nginx:/app/frontend/

docker-compose exec server python3 ./manage.py migrate --noinput
docker-compose exec server http POST https://api.rollbar.com/api/1/deploy/ access_token=$ROLLBAR_ACCESS_TOKEN environment=$ROLLBAR_ENVIRONMENT revision=$REVISION

echo
echo "Project deployed successfully"
