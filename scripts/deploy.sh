#!/usr/bin/env bash

set -e

DOCKER_REGISTRY_HOST=ghcr.io

# TODO(dmu) MEDIUM: Figure out a way to pass environment variables from github actions to
#                   this script instead of using positional arguments
GITHUB_USERNAME="${GITHUB_USERNAME:-$1}"
GITHUB_PASSWORD="${GITHUB_PASSWORD:-$2}"

RUN_MANAGE_PY='poetry run python -m core.manage'
DOCKER_COMPOSE_RUN_MANAGE_PY="docker compose run --rm core $RUN_MANAGE_PY"

docker logout $DOCKER_REGISTRY_HOST

# Support github actions deploy as well as manual deploy
if [[ -z "$GITHUB_USERNAME" || -z "$GITHUB_PASSWORD" ]]; then
  echo "Interactive docker registry login (username=github username; password=github personal access token (not github password)"
  docker login $DOCKER_REGISTRY_HOST
else
  echo "Automated docker registry login"
  # TODO(dmu) LOW: Implement a defensive technique to avoid printing password in case of `set -x`
  docker login --username "$GITHUB_USERNAME" --password "$GITHUB_PASSWORD" $DOCKER_REGISTRY_HOST
fi

echo 'Getting docker-compose.yml'
wget https://raw.githubusercontent.com/thenewboston-developers/Core/master/docker-compose.yml -O docker-compose.yml

echo 'Creating/updating .env file...'
grep -q -o CORESETTING_SECRET_KEY .env 2> /dev/null || echo "CORESETTING_SECRET_KEY=$$(xxd -c 48 -l 48 -p /dev/urandom)" >> .env

docker compose pull  # Ensure latest image is downloaded locally (even if tag did not change)

docker compose run -it --rm certbot certificates | grep -q 'No certificates found' && (echo 'Installing certificates..'; docker compose run -it --rm certbot certonly --non-interactive --domain thenewboston.network --standalone)

echo 'Starting the Core API...'
docker compose up -d --force-recreate
docker logout $DOCKER_REGISTRY_HOST

echo 'Core API is up and running'
