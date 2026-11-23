#!/bin/sh
# Tests for scripts/check-live.sh (#111) with a stub curl first on PATH: no network. The stub
# answers from a script of answers ("<status> <redirect target>"), one line per call, and logs
# each URL it was asked for.
#   sh scripts/test-check-live.sh
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
n=0
fail() { echo "FAIL $1"; exit 1; }

mkdir "$work/bin"
cat > "$work/bin/curl" << 'STUB'
#!/bin/sh
for last; do :; done
echo "$last" >> "$STUB_DIR/calls"
got=$(head -n 1 "$STUB_DIR/answers")
sed -i 1d "$STUB_DIR/answers"
[ "$got" = down ] && exit 7
printf '%s' "$got"
STUB
chmod +x "$work/bin/curl"

root_ok='302 https://site.test/depannage/'
run() { # run <expected-exit> <label> <answers…>: one answer per curl call, `down` = no answer
  want=$1 label=$2; shift 2
  : > "$work/calls"; printf '%s\n' "$@" > "$work/answers"
  rc=0
  PATH="$work/bin:$PATH" STUB_DIR=$work LIVE_BASE_URL=https://site.test LIVE_RETRY_DELAY=0 \
    sh "$root/scripts/check-live.sh" > "$work/out" 2>&1 || rc=$?
  [ "$rc" -eq "$want" ] || { cat "$work/out"; fail "$label: exit $rc, expected $want"; }
  n=$((n + 1))
}

run 0 "everything up" "$root_ok" '200 ' '200 '
[ "$(cat "$work/calls")" = "$(printf 'https://site.test/\nhttps://site.test/blocks/led-resistor-basic\nhttps://site.test/blocks/led-resistor-basic/schematic.svg')" ] \
  || fail "checked the wrong URLs: $(cat "$work/calls")"
n=$((n + 1))

run 0 "second try succeeds" '502 ' "$root_ok" '200 ' '200 '
[ "$(wc -l < "$work/calls")" -eq 4 ] || fail "no second try after a 502"
n=$((n + 1))

run 1 "block page down twice" "$root_ok" '502 ' '502 ' '200 '
grep -q "FAIL https://site.test/blocks/led-resistor-basic answered '502 ' twice" "$work/out" \
  || fail "the failing URL is not named: $(cat "$work/out")"
n=$((n + 1))

run 1 "schematic down twice" "$root_ok" '200 ' '500 ' '500 '
run 1 "no answer at all" down down '200 ' '200 '
grep -q "answered '000' twice" "$work/out" || fail "no answer is not reported as 000: $(cat "$work/out")"
n=$((n + 1))

run 1 "a root redirect elsewhere fails" '302 https://parking.test/' '302 https://parking.test/' '200 ' '200 '
run 1 "a redirected block page fails" "$root_ok" '302 https://site.test/login' '302 https://site.test/login' '200 '
run 1 "a 404 root fails" '404 ' '404 ' '200 ' '200 '

echo "test-check-live: $n cases passed"
