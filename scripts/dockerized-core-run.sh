#!/usr/bin/env bash

set -e

RUN_MANAGE_PY='poetry run python -m core.manage'

# We need to collect static files to make WhiteNoise work (and we need to do it here)
# TODO(dmu) LOW: Collect static once, not on every run (we need to have named volume for it)
echo 'Collecting static files...'
$RUN_MANAGE_PY collectstatic --no-input

echo 'Running migrations...'
$RUN_MANAGE_PY migrate --no-input

echo 'Starting the Core API...'
poetry run daphne -b 0.0.0.0 -p 8000 core.project.asgi:application
