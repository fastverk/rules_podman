#!/usr/bin/env bash
# Smoke check: the given podman client exits 0 on `--version` and prints
# a version string. `--version` is handled client-side before any
# connection, so this stays hermetic — no Podman service required.
set -euo pipefail

BIN="$1"
WANT="${2:-}"

if [[ ! -x "$BIN" ]]; then
  echo "version_smoke: binary not executable: $BIN" >&2
  exit 2
fi

out="$("$BIN" --version)"
echo "$out"
[[ -n "$out" ]] || { echo "version_smoke: empty --version output" >&2; exit 3; }

if [[ -n "$WANT" ]]; then
  case "$out" in
    *"$WANT"*) ;;
    *)
      echo "version_smoke: expected version '$WANT' in: $out" >&2
      exit 4
      ;;
  esac
fi
