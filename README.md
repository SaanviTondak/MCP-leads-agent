# Leads Agent — an MCP-powered lead qualification & outreach system

An agentic AI system that automates a manual lead-generation and outreach
workflow. Built on the **Model Context Protocol (MCP)** with a custom server,
driven by Claude Code as the agent runtime.

## What it does

Given an Ideal Customer Profile (ICP), the agent finds candidate leads,
qualifies each one against the ICP, drafts personalized outreach for the good
ones, and logs every decision — with a self-critique step that reviews and
revises each draft before finalizing.

> Outreach is **drafted for human review, not auto-sent** — a deliberate design
> choice for a prototype handling real-world contacts.

## Architecture

- **MCP server (`server.py`)** exposes all three MCP primitives:
  - **Tool** — `search_leads`: query leads by industry / size
  - **Resource** — `leads://all` and `leads://{id}`: readable lead data
  - **Prompt** — `qualify_lead`: reusable ICP-based qualification template
- **Data (`seed_data.py` → `leads.db`)** — a small SQLite database of sample leads
- **Agent runtime** — Claude Code connects to the MCP server, discovers the
  primitives, and runs the qualify → draft → review loop

## Tech stack

Python · MCP Python SDK (`FastMCP`) · SQLite · Claude Code

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install "mcp[cli]" uv
python seed_data.py          # builds leads.db
mcp dev server.py            # opens the MCP Inspector to test the server
```

## Project status

- [x] MCP server with tool, resource, and prompt primitives
- [x] Sample lead database
- [ ] Wired into Claude Code as an agent
- [ ] Self-critique loop on outreach drafts
- [ ] Decision logging / trajectory trace

## What I'd build next

Real email integration with rate limiting and consent handling, A/B testing of
outreach messaging, and a formal evaluation set to measure qualification accuracy.