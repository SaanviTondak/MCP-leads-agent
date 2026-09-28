# Leads Agent: MCP-powered lead qualification & outreach

An agent that automates a manual B2B lead-generation workflow for a water and wastewater treatment company (World Technologies, Singapore). It finds real industrial facilities, qualifies each one against an ideal-customer profile (ICP), drafts outreach for the good ones, critiques and rewrites its own drafts, and logs every decision.

Built on the **Model Context Protocol (MCP)** with a custom Python server; **Claude Code** is the agent runtime.

> Outreach is **drafted for human review, never sent.** There is no mail transport in this codebase, by design.

## How it works

```
/run-leads  (Claude Code slash command)
   |
   |-- 1. GENERATE  fetch_leads -> OpenStreetMap Overpass API: named industrial sites in Singapore
   |-- 2. QUALIFY   qualify_lead prompt + ICP -> QUALIFIED / REJECTED, logged via log_decision
   |-- 3. DRAFT     <90-word email per qualified lead -> self-critique (personalisation, relevance,
   |                tone, length; 1-5) -> rewrite if any score < 4 -> save_draft
   `-- 4. REPORT    counts generated / qualified / rejected + drafts folder
```

## MCP server (`server.py`)

| Primitive | Name | What it does |
| --- | --- | --- |
| Tool | `fetch_leads` | Queries OpenStreetMap for named industrial facilities likely to produce wastewater |
| Tool | `log_decision` | Stores each qualify/reject decision and a one-line reason in SQLite |
| Tool | `save_draft` | Saves an outreach draft to `drafts/` for a human to review |
| Tool | `search_leads` | Filters the seeded sample leads by industry and size |
| Resource | `leads://all`, `leads://{id}` | Sample leads as readable context |
| Prompt | `qualify_lead` | Reusable ICP qualification template |

The agent workflow itself lives in [`.claude/commands/run-leads.md`](.claude/commands/run-leads.md).

## Run it

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python seed_data.py        # creates leads.db (sample leads + decisions table)
mcp dev server.py          # optional: inspect the server in MCP Inspector
```

Then register the server with Claude Code (`claude mcp add leads -- python server.py`) and run `/run-leads`.

## Design choices

- **Human in the loop by construction:** drafts land in files; nothing can send email.
- **Auditable:** every qualification decision is stored with its reason, so the ICP can be tuned against real outcomes.
- **Self-critique before save:** each draft is scored on four criteria and rewritten until all score 4 or higher.

## Next

- A hand-labelled evaluation set of facilities to measure qualification precision and recall
- Enrichment (company size, sector) beyond OpenStreetMap tags
- Rate-limited, consent-aware sending behind an explicit human approval step
