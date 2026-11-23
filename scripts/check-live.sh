#!/bin/sh
# Liveness of the public site (#111), run by `just nightly`: the site was down for days before
# anyone noticed. Checks the root (a redirect counts) and one block page, which proves the Worker
# reaches the catalogue database through Hyperdrive (ADR-0005). Each URL gets a second try after
# LIVE_RETRY_DELAY seconds (a network blip on the laptop, a cold Neon compute), then the script
# fails. Exit 0 when every URL answers 2xx or 3xx, 1 otherwise.
#
#   LIVE_BASE_URL     site origin (default: the production Worker on its custom domain)
#   LIVE_RETRY_DELAY  seconds before the second try (default 10)
set -u

base=${LIVE_BASE_URL:-https://ohm.benoitbremaud.fr}
delay=${LIVE_RETRY_DELAY:-10}
rc=0

status() { # status <url>: the HTTP status, 000 when nothing answered; redirects are not followed
  curl -s -o /dev/null -m 20 -w '%{http_code}' "$1" 2> /dev/null || true
}

for path in / /blocks/led-resistor-basic; do
  url="$base$path"
  code=$(status "$url")
  case "$code" in
    2?? | 3??) ;;
    *) sleep "$delay"; code=$(status "$url") ;;
  esac
  case "$code" in
    2?? | 3??) echo "live: $url $code" ;;
    *) echo "live: FAIL $url answered ${code:-000} twice" >&2; rc=1 ;;
  esac
done
exit "$rc"
