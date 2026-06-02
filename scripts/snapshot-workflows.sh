#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAW_DIR="$ROOT_DIR/flows/raw"
DETAIL_DIR="$RAW_DIR/workflow-details"
REPORT_DIR="$ROOT_DIR/flows/reports"
INDEX_JSONL="$RAW_DIR/workflows.jsonl"
LIMIT="${HUBSPOT_WORKFLOW_LIMIT:-100}"

mkdir -p "$RAW_DIR" "$DETAIL_DIR" "$REPORT_DIR"

if ! command -v hubspot >/dev/null 2>&1; then
  echo "error: hubspot was not found on PATH" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required for JSON parsing in this script" >&2
  exit 1
fi

extract_jsonl_and_cursor() {
  local source_file="$1"
  python3 - "$source_file" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text())

if isinstance(data, dict) and data.get("ok") is False:
    message = data.get("error", {}).get("message", "Unknown workflow access error")
    print(message, file=sys.stderr)
    sys.exit(2)

rows = []
if isinstance(data, list):
    rows = data
elif isinstance(data, dict):
    for key in ("results", "items", "data"):
        if isinstance(data.get(key), list):
            rows = data[key]
            break

for row in rows:
    print(json.dumps(row, separators=(",", ":")))

cursor = None
for chain in (
    ("meta", "next", "after"),
    ("paging", "next", "after"),
    ("next", "after"),
):
    current = data
    for key in chain:
        if not isinstance(current, dict):
            current = None
            break
        current = current.get(key)
    if current:
        cursor = current
        break

print(f"__NEXT_AFTER__={cursor or ''}", file=sys.stderr)
PY
}

save_detail_files() {
  local jsonl_file="$1"
  local target_dir="$2"
  python3 - "$jsonl_file" "$target_dir" <<'PY'
import json
import sys
from pathlib import Path

jsonl_path = Path(sys.argv[1])
target_dir = Path(sys.argv[2])
target_dir.mkdir(parents=True, exist_ok=True)

for line in jsonl_path.read_text().splitlines():
    line = line.strip()
    if not line:
        continue
    item = json.loads(line)
    flow_id = str(item.get("id", "")).strip()
    if not flow_id:
        continue
    (target_dir / f"{flow_id}.json").write_text(json.dumps(item, indent=2, sort_keys=True) + "\n")
PY
}

: > "$INDEX_JSONL"

after=""
page=1

while true; do
  page_file="$(mktemp)"
  page_stderr="$(mktemp)"

  if [ -n "$after" ]; then
    hubspot workflows list --limit "$LIMIT" --after "$after" --format json >"$page_file" 2>"$page_stderr" || true
  else
    hubspot workflows list --limit "$LIMIT" --format json >"$page_file" 2>"$page_stderr" || true
  fi

  if [ -s "$page_stderr" ]; then
    cat "$page_stderr" >&2
  fi

  if [ ! -s "$page_file" ]; then
    echo "error: workflow list returned no output" >&2
    exit 1
  fi

  page_output="$(extract_jsonl_and_cursor "$page_file" 2>&1)"
  page_status=$?
  if [ $page_status -ne 0 ]; then
    printf '%s\n' "$page_output" >&2
    echo "hint: run './scripts/check-agent-cli.sh' and verify workflow scopes are present" >&2
    exit $page_status
  fi

  next_after="$(printf '%s\n' "$page_output" | awk -F= '/^__NEXT_AFTER__=/{print $2}' | tail -1)"
  printf '%s\n' "$page_output" | grep -v '^__NEXT_AFTER__=' >> "$INDEX_JSONL" || true
  echo "saved workflow page $page"

  if [ -z "$next_after" ]; then
    break
  fi

  after="$next_after"
  page=$((page + 1))
done

mapfile -t flow_ids < <(python3 - "$INDEX_JSONL" <<'PY'
import json
import sys
from pathlib import Path

for line in Path(sys.argv[1]).read_text().splitlines():
    line = line.strip()
    if not line:
        continue
    item = json.loads(line)
    flow_id = item.get("id")
    if flow_id:
        print(flow_id)
PY
)

if [ "${#flow_ids[@]}" -eq 0 ]; then
  echo "no workflows were returned by the inventory command"
  exit 0
fi

echo "fetching ${#flow_ids[@]} workflow detail record(s)"

chunk_size=50
for ((i = 0; i < ${#flow_ids[@]}; i += chunk_size)); do
  chunk=("${flow_ids[@]:i:chunk_size}")
  detail_file="$(mktemp)"
  hubspot workflows get "${chunk[@]}" --format jsonl >"$detail_file"
  save_detail_files "$detail_file" "$DETAIL_DIR"
done

echo "saved workflow inventory to $INDEX_JSONL"
echo "saved workflow detail files under $DETAIL_DIR"
