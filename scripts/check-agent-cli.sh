#!/usr/bin/env bash

set -euo pipefail

if ! command -v hubspot >/dev/null 2>&1; then
  echo "error: hubspot was not found on PATH" >&2
  echo "hint: add ~/.hubspot/bin to PATH for Codex sessions" >&2
  exit 1
fi

echo "hubspot binary: $(command -v hubspot)"
echo "hubspot version: $(hubspot --version)"
echo
echo "auth probe:"
hubspot whoami
echo
echo "workflow probe:"

workflow_probe="$(hubspot workflows list --limit 1 --format json 2>&1 || true)"

if printf '%s' "$workflow_probe" | grep -q '"ok":false'; then
  echo "$workflow_probe"
  echo
  echo "workflow access is not currently available for this auth context." >&2
  echo "Re-authenticate with 'hubspot auth login' or use HUBSPOT_ACCESS_TOKEN with the required workflow scopes." >&2
  exit 2
fi

echo "$workflow_probe"
echo
echo "workflow access looks available."
