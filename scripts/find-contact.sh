#!/usr/bin/env bash

set -euo pipefail

HUBSPOT_ENV="${HUBSPOT_ENV:-sb}"
case "$HUBSPOT_ENV" in
  sb) HUBSPOT_CMD="${HUBSPOT_CMD:-hubspot-sb}" ;;
  prod) HUBSPOT_CMD="${HUBSPOT_CMD:-hubspot-prod}" ;;
  *) echo "error: HUBSPOT_ENV must be 'sb' or 'prod'" >&2; exit 1 ;;
esac

if [ "${1:-}" = "" ]; then
  echo "usage: $0 <email>" >&2
  exit 1
fi

if ! command -v "$HUBSPOT_CMD" >/dev/null 2>&1; then
  echo "error: $HUBSPOT_CMD was not found on PATH" >&2
  exit 1
fi

"$HUBSPOT_CMD" whoami >&2

"$HUBSPOT_CMD" objects search \
  --type contacts \
  --filter "email=$1" \
  --properties email,firstname,lastname
