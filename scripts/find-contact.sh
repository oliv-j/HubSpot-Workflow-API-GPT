#!/usr/bin/env bash

set -euo pipefail

if [ "${1:-}" = "" ]; then
  echo "usage: $0 <email>" >&2
  exit 1
fi

if ! command -v hubspot >/dev/null 2>&1; then
  echo "error: hubspot was not found on PATH" >&2
  exit 1
fi

hubspot objects search \
  --type contacts \
  --filter "email=$1" \
  --properties email,firstname,lastname
