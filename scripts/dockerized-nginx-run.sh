#!/usr/bin/env bash

CERTIFICATE_FILE=/etc/letsencrypt/live/main/fullchain.pem

set -em

_quit() {
  echo 'Gracefully closing nginx...'
  # TODO(dmu) LOW: Will nginx still close WebSocket connections on SIGQUIT signal?
  kill -SIGQUIT "$NGINX_PID" || true  # fail silently if process not found
  echo 'Signal is sent to nginx'
}

_handle_sigquit() {
  echo 'Forwarding caught SIGQUIT signal to nginx and killing inotifywait'
  quit
  kill "$INOTIFYWAIT_PID" || true  # fail silently if process not found
}

echo 'Running nginx in background, so we can run inotifywait later...'
nginx -g 'daemon off;' &
NGINX_PID=$!  # save nginx pid
echo 'nginx is running in background'

trap _handle_sigquit SIGQUIT  # forward SIGQUIT to nginx and also kill inotifywait

echo "Waiting certificate file ($CERTIFICATE_FILE) to appear..."
# Otherwise inotifywait will exit. This is important on installation from scratch
until [ -f $CERTIFICATE_FILE ]; do
  sleep 60
done
echo "$CERTIFICATE_FILE has to appeared"
echo 'Running inotifywait...'
inotifywait -e modify $CERTIFICATE_FILE &  # in background to be able to grab its pid to kill later
INOTIFYWAIT_PID=$!
echo 'inotifywait is running'
fg %%  # bring last job (inotifywait) to foreground, so we exit only once $CERTIFICATE_FILE is modified

_quit

echo 'Bringing nginx to foreground and waiting it to exit...'
fg %1 || true  # bring nginx to foreground and fail silently if it already exited
echo 'nginx has existed'
# after exiting this script the container should restart and therefore updated certificate reread from storage
