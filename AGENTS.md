# Agent Operating Guide

## HubSpot Agent CLI environment policy

- Use `hubspot-sb` for sandbox work and `hubspot-prod` for production work.
- Do not use bare `hubspot` for routine repo workflows.
- Default to sandbox unless the task explicitly requires production.
- Always run `whoami` before using the HubSpot Agent CLI in a meaningful way.
- Current repo policy is read-only when using the HubSpot Agent CLI.

## Local command surfaces

- Sandbox wrapper: `~/.local/bin/hubspot-sb`
- Production wrapper: `~/.local/bin/hubspot-prod`
- Underlying binary: `/Users/oliver.jobson/.hubspot/bin/hubspot`

Each wrapper should set an isolated `HOME` so auth state stays separate:

- Sandbox auth home: `~/.hubspot-agent/sandbox`
- Production auth home: `~/.hubspot-agent/prod`

## Required session checks

At the start of a HubSpot task, run:

```bash
hubspot-sb whoami
hubspot-prod whoami
```

Use the output to confirm the target portal before any CRM or workflow command.

If the requested environment is ambiguous, stop and ask.

## Skill bundle guidance

HubSpot Agent CLI operating guidance is available in `.agents/skills/` when installed locally from:

```bash
npx skills add hubspot/agent-cli-skills
```

Relevant playbooks include:

- `crm-lookup`
- `bulk-operations`
- `workflow-automation`
- `crm-data-quality`
- `sales-execution`

These skill files are local operating instructions, not guaranteed first-class Codex skills in every app session. Read the relevant `SKILL.md` before specialized HubSpot Agent CLI work.

## Task note expectations

When using the HubSpot Agent CLI, note:

- which wrapper was used: `hubspot-sb` or `hubspot-prod`
- the result of `whoami`
- that the task was read-only
- which skill file informed the workflow, if applicable
