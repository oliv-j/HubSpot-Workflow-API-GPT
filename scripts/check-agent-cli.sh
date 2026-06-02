#!/usr/bin/env bash

set -euo pipefail

HUBSPOT_ENV="${HUBSPOT_ENV:-sb}"
case "$HUBSPOT_ENV" in
  sb) HUBSPOT_CMD="${HUBSPOT_CMD:-hubspot-sb}" ;;
  prod) HUBSPOT_CMD="${HUBSPOT_CMD:-hubspot-prod}" ;;
  *) echo "error: HUBSPOT_ENV must be 'sb' or 'prod'" >&2; exit 1 ;;
esac

if ! command -v "$HUBSPOT_CMD" >/dev/null 2>&1; then
  echo "error: $HUBSPOT_CMD was not found on PATH" >&2
  echo "hint: install the wrapper command under ~/.local/bin and ensure it is available to Codex sessions" >&2
  exit 1
fi

echo "hubspot environment: $HUBSPOT_ENV"
echo "hubspot command: $(command -v "$HUBSPOT_CMD")"
echo "hubspot version: $("$HUBSPOT_CMD" --version)"
echo
echo "auth probe:"
"$HUBSPOT_CMD" whoami
echo
echo "workflow probe:"

workflow_probe="$("$HUBSPOT_CMD" workflows list --limit 1 --format json 2>&1 || true)"

if printf '%s' "$workflow_probe" | grep -q '"ok":false'; then
  echo "$workflow_probe"
  echo
  echo "workflow access is not currently available for this auth context." >&2
  echo "Re-authenticate with '$HUBSPOT_CMD auth login' or use HUBSPOT_ACCESS_TOKEN with the required workflow scopes." >&2
  exit 2
fi

echo "$workflow_probe"
echo
echo "workflow access looks available."
