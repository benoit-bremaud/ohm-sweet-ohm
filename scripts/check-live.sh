#!/bin/sh
# Liveness of the public site (#111), run by `just nightly`: the site was down for days before
# anyone noticed. The root must redirect to the troubleshooting guides; the LED block page and its
# schematic must answer 200, which proves the Worker reaches the catalogue database through
# Hyperdrive for both reads (ADR-0005). Each URL gets a second try after LIVE_RETRY_DELAY seconds
# (a network blip on the laptop, a cold Neon compute), then the script fails. Exit 0 when every
# URL answers as expected, 1 otherwise.
#
#   LIVE_BASE_URL     site origin (default: the production Worker on its custom domain)
#   LIVE_RETRY_DELAY  seconds before the second try (default 10)
set -u

base=${LIVE_BASE_URL:-https://ohm.benoitbremaud.fr}
delay=${LIVE_RETRY_DELAY:-10}
rc=0

answer() { # answer <url>: "<status> <redirect target>", 000 when nothing answered; not followed
  curl -s -o /dev/null -m 20 -w '%{http_code} %{redirect_url}' "$1" 2> /dev/null || true
}

# expect <path> <expected answer>: one retry, then report.
expect() {
  url="$base$1"
  got=$(answer "$url")
  [ "$got" = "$2" ] || { sleep "$delay"; got=$(answer "$url"); }
  if [ "$got" = "$2" ]; then
    echo "live: $url $got"
  else
    echo "live: FAIL $url answered '${got:-000}' twice, expected '$2'" >&2
    rc=1
  fi
}

expect / "302 $base/depannage/"
expect /blocks/led-resistor-basic "200 "
expect /blocks/led-resistor-basic/schematic.svg "200 "
exit "$rc"
