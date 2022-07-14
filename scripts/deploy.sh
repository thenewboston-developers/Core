#!/usr/bin/env bash

set -e

DOCKER_REGISTRY_HOST=ghcr.io

# TODO(dmu) MEDIUM: Figure out a way to pass environment variables from github actions to
#                   this script instead of using positional arguments
GITHUB_USERNAME="${GITHUB_USERNAME:-$1}"
GITHUB_PASSWORD="${GITHUB_PASSWORD:-$2}"
CORESETTING_CORE_DOMAIN="${CORESETTING_CORE_DOMAIN:-$3}"
CERTBOT_EMAIL="${CERTBOT_EMAIL:-$4}"

RUN_MANAGE_PY='poetry run python -m core.manage'
DOCKER_COMPOSE_RUN_MANAGE_PY="docker compose run --rm core $RUN_MANAGE_PY"

docker logout $DOCKER_REGISTRY_HOST

# Support github actions deploy as well as manual deploy
if [[ -z "$GITHUB_USERNAME" || -z "$GITHUB_PASSWORD" ]]; then
  echo 'Interactive docker registry login (username=github username; password=github personal access token (not github password)'
  docker login $DOCKER_REGISTRY_HOST
else
  echo 'Automated docker registry login'
  # TODO(dmu) LOW: Implement a defensive technique to avoid printing password in case of `set -x`
  docker login --username "$GITHUB_USERNAME" --password "$GITHUB_PASSWORD" $DOCKER_REGISTRY_HOST
fi

echo 'Getting docker-compose.yml'
wget https://raw.githubusercontent.com/thenewboston-developers/Core/master/docker-compose.yml -O docker-compose.yml

echo 'Creating/updating .env file...'
grep -q -o CORESETTING_SECRET_KEY .env 2> /dev/null || echo "CORESETTING_SECRET_KEY=$$(xxd -c 48 -l 48 -p /dev/urandom)" >> .env

if [[ -z "$CORESETTING_CORE_DOMAIN" || -z "$CERTBOT_EMAIL" ]]; then
  echo 'Interactive input mode for domain name and certbot email'

  if grep -q -o CORESETTING_CORE_DOMAIN .env 2> /dev/null; then
    echo 'Domain name is found in .env file'
  else
    read -p 'Domain name: ' CORESETTING_CORE_DOMAIN
    echo "CORESETTING_CORE_DOMAIN=$CORESETTING_CORE_DOMAIN" >> .env
  fi

  if grep -q -o CERTBOT_EMAIL .env 2> /dev/null; then
    echo 'Email address for important certbot ACME notifications is found in .env file'
  else
    read -p "Email address for important certbot ACME notifications (by typing it you agree to the ACME server's Subscriber Agreement): " CERTBOT_EMAIL
    echo "CERTBOT_EMAIL=$CERTBOT_EMAIL" >> .env
  fi
else
  echo 'CI/CD mode for for domain name and certbot email'

  # TODO(dmu) LOW: Update .env file only if a different value is provided
  # TODO(dmu) MEDIUM: Implement automatic revoking the certificate in case of any changes to CORESETTING_CORE_DOMAIN or
  #                   CERTBOT_EMAIL
  sed -i '/CORESETTING_CORE_DOMAIN=/d' ./.env
  echo "CORESETTING_CORE_DOMAIN=$CORESETTING_CORE_DOMAIN" >> .env
  sed -i '/CERTBOT_EMAIL=/d' ./.env
  echo "CERTBOT_EMAIL=$CERTBOT_EMAIL" >> .env
fi

docker compose pull  # Ensure latest image is downloaded locally (even if tag did not change)

echo 'Starting the Core API...'
docker compose up -d --force-recreate
docker logout $DOCKER_REGISTRY_HOST

if docker compose run -it --rm certbot -c 'certbot certificates' | grep -q 'No certificates found'; then
  echo 'Installing certificates...'
  # TODO(dmu) LOW: Do we actually need to stop certbot?
  docker compose stop certbot  # make sure another instance of certbot does not interfere

  set -o allexport
  source .env
  set +o allexport

  docker compose run -it --rm certbot -c "certbot certonly --agree-tos --email $CERTBOT_EMAIL --non-interactive --webroot --webroot-path /usr/share/nginx/html/ --domain $CORESETTING_CORE_DOMAIN --cert-name main"
  docker compose start certbot
fi

echo 'Core API is up and running'
