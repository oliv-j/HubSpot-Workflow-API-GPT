# HubSpot Workflow API GPT

## Overview

This repository is now organized around the **HubSpot agent CLI** (`hubspot`) as the primary way to inspect HubSpot CRM data and automation workflows.

The goal is to create a repeatable workflow for:

- verifying HubSpot agent CLI access
- snapshotting workflow data from a portal
- generating analysis-ready local artifacts
- handing those artifacts to Codex or a custom GPT for workflow analysis

The existing Python exporter remains in the repo as a fallback path, but the default workflow is now CLI-first.

## Which CLI is Which?

There are two different HubSpot CLIs that may exist on the same machine:

- `hubspot`: the newer **HubSpot agent CLI**
- `hs`: the older HubSpot developer CLI

This repo uses **`hubspot`** as the main interface.

## Current Status

In this environment, the HubSpot agent CLI is installed and can be used for CRM lookups. For example, `hubspot objects search` works for contact search.

Workflow access is a separate permission boundary. A portal session can authenticate successfully and still fail `hubspot workflows list` with `403` if the auth context does not include the required scopes.

That means this repo now assumes:

- the agent CLI is present
- read-only operations are preferred
- workflow snapshotting depends on the authenticated user or token having workflow access

## Prerequisites

- macOS or another environment where the HubSpot agent CLI is installed
- `hubspot` on `PATH`
- Python 3.12 recommended
- Git
- HubSpot access with the read scopes needed for the commands you intend to run

## Quick Start

### 1. Verify the agent CLI

Run the preflight script:

```bash
./scripts/check-agent-cli.sh
```

This checks:

- `hubspot` is installed
- the CLI can respond to `--version`
- `hubspot whoami` works
- workflow read access is available

If workflow access is missing, the script will tell you instead of failing silently.

### 2. Find a contact

```bash
./scripts/find-contact.sh oj@bson.uk
```

This uses the agent CLI directly and prints the matching contact record.

### 3. Snapshot workflows

```bash
./scripts/snapshot-workflows.sh
```

This command:

- pages through `hubspot workflows list`
- stores the workflow inventory as JSONL
- fetches detailed workflow JSON for each workflow ID

Generated outputs:

- `flows/raw/workflows.jsonl`
- `flows/raw/workflow-details/<flow-id>.json`

If the authenticated session lacks workflow scopes, the script exits with a clear error and guidance.

### 4. Build analysis reports

```bash
python3 ./scripts/build-workflow-report.py
```

This reads the saved workflow detail files and produces:

- `flows/reports/workflow-summary.csv`
- `flows/reports/workflow-findings.md`

These outputs are designed to be easier for Codex or a custom GPT to reason over than raw workflow JSON alone.

## Recommended Codex Workflow

The intended workflow for this repo is:

1. Run `./scripts/check-agent-cli.sh`
2. Confirm workflow access is available
3. Run `./scripts/snapshot-workflows.sh`
4. Run `python3 ./scripts/build-workflow-report.py`
5. Ask Codex questions against the local artifacts

Examples:

- Which workflows send marketing emails?
- Which workflows reference a given property?
- Which workflows contain branches or delays?
- Which workflows create tasks or records?

## Repo Structure

```bash
HubSpot-Workflow-API-GPT/
├── README.md
├── export_flows_to_csv.py
├── requirements.txt
├── config/
│   └── customGPT_config.txt
├── scripts/
│   ├── build-workflow-report.py
│   ├── check-agent-cli.sh
│   ├── find-contact.sh
│   └── snapshot-workflows.sh
├── flows/
│   ├── all_flows.txt
│   ├── all_flow_content.csv
│   ├── raw/
│   │   ├── workflows.jsonl
│   │   └── workflow-details/
│   └── reports/
│       ├── workflow-findings.md
│       └── workflow-summary.csv
└── gpt-training-files/
```

## Fallback Python Exporter

The legacy exporter is still available:

```bash
python3 export_flows_to_csv.py
```

Use it only if you specifically want the original Python-based export flow. The preferred path for this repo is the HubSpot agent CLI.

## Custom GPT / Codex Context

The files in `gpt-training-files/` remain useful as reference material for workflow structure and HubSpot automation concepts.

For day-to-day analysis, the higher-value inputs are now:

- `flows/raw/workflows.jsonl`
- `flows/raw/workflow-details/*.json`
- `flows/reports/workflow-summary.csv`
- `flows/reports/workflow-findings.md`

The config in `config/customGPT_config.txt` can be used as a starting point for a custom GPT, but it should be paired with the current CLI-generated artifacts rather than only the static training files.
