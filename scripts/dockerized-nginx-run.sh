#!/usr/bin/env bash

CERTIFICATE_FILE=/etc/letsencrypt/live/main/fullchain.pem

set -e
set -m

_wait_nginx() {
  echo 'Bringing nginx to foreground and waiting it to exit...'
  fg %1 || true  # bring nginx to foreground and fail silently if it already exited
  echo 'nginx has existed'
  # after exiting this script the container should restart and therefore updated certificate reread from storage
}

_stop_nginx() {
  echo 'Gracefully stopping nginx...'
  # TODO(dmu) LOW: Will nginx still close WebSocket connections on SIGQUIT signal?
  kill -SIGQUIT "$NGINX_PID" || true  # fail silently if process not found
  echo 'Gracefully stop signal is sent to nginx'
}

_handle_sigquit() {
  echo 'Forwarding caught SIGQUIT signal to nginx'
  _stop_nginx
  _wait_nginx
  exit
}

echo 'Running nginx in background, so we can watch mtime change later'
nginx -g 'daemon off;' &
NGINX_PID=$!  # save nginx pid
echo 'nginx is running in background'

trap _handle_sigquit SIGQUIT

echo "Waiting certificate file ($CERTIFICATE_FILE) to appear..."
until [ -f "$CERTIFICATE_FILE" ]; do
  sleep 60
done
echo "$CERTIFICATE_FILE has appeared"

# We are not using inotifywait because it does not work well across shared docker volumes
ORIGINAL_MTIME=$(stat -c %Y $CERTIFICATE_FILE)
echo "$CERTIFICATE_FILE mtime: $ORIGINAL_MTIME"
echo "Waiting for $CERTIFICATE_FILE mtime change..."
while [ "$(stat -c %Y $CERTIFICATE_FILE)" == "$ORIGINAL_MTIME" ]; do
  sleep 60
done
echo "$(date): mtime has changed"

_stop_nginx
_wait_nginx
