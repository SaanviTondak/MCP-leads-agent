# CLAUDE.md — Leads Agent Project

## What this project is

An **MCP-powered agentic AI system** that automates a manual lead-generation and
outreach workflow. Built on the Model Context Protocol with a custom Python server,
with **Claude Code as the agent runtime**.

### The real business (premise — important)
This is for **World Technologies** (worldtechnologies.sg), a **water & wastewater
treatment company** in Singapore (also Indonesia, India, USA). They sell water/wastewater
treatment products & services (ETP/STP, DAF, sludge dewatering, RO/UF, zero liquid
discharge, water audits, chemicals, etc.) to **industrial and municipal clients**.

- **A "lead" = an industrial facility that generates wastewater / needs water treatment.**
  Sectors: pharma, semiconductor, oil & gas / petrochemical, food & beverage / breweries,
  textile & dyeing, distilleries, pulp & paper, power, oleochemical, municipal.
- **Decision-makers** = Facility Managers, Utility Managers, Plant/Operations Managers.
- **Lead source = OpenStreetMap (Overpass API)** — free, no key. We query real industrial
  facilities in Singapore (factories, works, breweries, industrial sites) with names and
  sometimes website/phone.
- **Outreach** = draft an email pitching a RELEVANT WT service matched to the facility's
  likely wastewater problem, addressed to the Facility/Operations Manager, for human review.
- Honest limitation to state openly: OSM gives the facility + maybe website/phone, NOT a
  named decision-maker email. Prototype drafts to the role; real contact lookup is a
  human/next step.

## Timeline / constraints

- Hard-ish deadline: this needs to be portfolio-ready as a GitHub project soon
  (NUS Overseas Colleges Silicon Valley applications; CVs circulate in August 2026).
- Scope is deliberately capped at a **2–3 day build**. Prioritize a working,
  well-understood, agentic system over feature breadth.

## Key design decisions (don't silently change these)

1. **Expose all three MCP primitives** — tool, resource, AND prompt. Most people only
   build tools; doing all three is the differentiator and I need to be able to explain
   the difference between them.
   - Tool = a model-controlled *action* with side effects (`search_leads`)
   - Resource = read-only *context* the app loads (`leads://all`, `leads://{id}`)
   - Prompt = a reusable *instruction template* the user invokes (`qualify_lead`,
     which holds the ICP so qualification stays consistent across runs)
2. **Outreach is DRAFTED for human review, never auto-sent.** Deliberate choice for a
   prototype touching real-world contacts. This is a feature, not a limitation.
3. **Leads come from a seeded sample database**, standing in for a real lead source.
   Be honest about this — no implying live web scraping.
4. **Claude Code is the agent runtime.** We don't hand-write the agent loop; Claude
   Code discovers the MCP primitives and orchestrates them. This is what makes
   "built with Claude Code" literally true.

## Tech stack

Python · MCP Python SDK (`FastMCP`, installed via `mcp[cli]`) · SQLite · Claude Code ·
`uv` (used by `mcp dev` to launch the Inspector)

## Project structure

```
leads-agent/
├── venv/            # virtualenv (gitignored)
├── seed_data.py     # builds leads.db from sample lead data
├── server.py        # the MCP server: tool + resources + prompt
├── leads.db         # generated SQLite DB (gitignored — rebuild via seed_data.py)
├── README.md        # public-facing project readme (portfolio artifact)
├── CLAUDE.md        # this file
└── .gitignore       # ignores venv/, leads.db, __pycache__, *.pyc, .env
```

## Environment / how to run

```bash
source venv/bin/activate          # always activate first; prompt should show (venv)
python seed_data.py               # (re)build leads.db
python server.py                  # should hang quietly = healthy (Ctrl+C to stop)
mcp dev server.py                 # opens MCP Inspector to test the server manually
```

MCP Inspector gotcha: in the Inspector's left panel, set Command to the venv python
and Arguments to the absolute path of server.py, e.g.
`/Users/saanvitondak/leads-agent/venv/bin/python` + `/Users/saanvitondak/leads-agent/server.py`.
(`uv` must be installed for the default `mcp dev` launch command to work: `pip install uv`.)

Register the server with Claude Code:
```bash
claude mcp add leads -- /Users/saanvitondak/leads-agent/venv/bin/python /Users/saanvitondak/leads-agent/server.py
claude mcp list       # should show: leads ... ✓
```

## What's DONE so far

- [x] `seed_data.py` — 10 sample leads in SQLite (`leads.db`)
- [x] `server.py` with all three primitives:
  - [x] Tool: `search_leads(industry, min_employees)`
  - [x] Resource: `leads://all` and `leads://{lead_id}`
  - [x] Prompt: `qualify_lead(lead_info)` containing the ICP rubric
- [x] Tested primitives in MCP Inspector
- [x] Git initialized, `.gitignore`, initial commit, starter README
- [x] Fixed startup bug (`mcp_run()` → `mcp.run()`)
- [ ] **IN PROGRESS:** registering server with Claude Code and confirming ✓ connection

### ICP (Ideal Customer Profile) — the qualification rubric
A strong lead meets MOST of:
- An industrial or municipal facility that generates wastewater or needs water treatment
- Operates in a sector WT serves: pharmaceutical, semiconductor, oil & gas / petrochemical,
  food & beverage / breweries, textile & dyeing, distilleries, pulp & paper, power,
  oleochemical, or municipal water/sewage
- Located in a serviceable region (Singapore, Indonesia, India, wider APAC)
- Large enough to have meaningful effluent volumes and a treatment budget
- Reject: retail, offices, pure logistics/warehousing, anything with no wastewater need

## What's NEXT (the remaining build, in order)

1. **Add `fetch_leads` (real lead-gen)** — Overpass/OpenStreetMap tool pulling real
   Singapore industrial facilities. Test in Inspector first. (search_leads over the
   seeded DB stays as a secondary/demo tool.)
2. **Add `save_draft`** — writes review-ready outreach drafts to a `drafts/` folder
   (never sends).
3. **Full agentic run:** give Claude Code the *goal* (not a script): "Generate leads,
   qualify each against our ICP, and draft a personalized outreach email pitching a
   relevant WT service for the qualified ones; save drafts and log decisions."
   Let it decide how to sequence the primitives. This is the core deliverable.
4. **Self-critique loop:** after drafting outreach, have the agent evaluate its own
   draft against a rubric (personalization, tone, length) and revise once before
   finalizing. This is the "reflection" agent pattern — the thing that makes it
   genuinely agentic vs. a one-shot generator.
5. **Decision logging / trajectory trace:** log every decision (which lead, qualified
   or rejected + why, which tools called) to a log file or a `trace` table in SQLite,
   so I can point at a transcript and explain the agent's reasoning. May require a
   `log_decision` tool on the server.
6. **The "~10 hrs/week" number:** help me run an honest timed comparison — time me
   qualifying + drafting a small batch of leads manually vs. agent-assisted (including
   my review time), extrapolate to a weekly volume, and land on a defensible figure.
   If it's not ~10, we adjust the resume bullet to match reality.
7. **README + polish + commits:** keep the README checklist updated, commit
   meaningfully at each milestone (iteration history matters on GitHub), and prep
   talking points for interviews (why Claude Code, why all three primitives, why
   drafts-not-sent, what I'd build next).

### Stretch (only if 1–7 are solid, don't start otherwise)
- Split into sub-agents (a research/enrichment agent + an outreach agent orchestrated
  by a top-level agent). A working 7-step system beats a half-finished stretch.

## Git habits
- Commit at each meaningful milestone with a descriptive message.
- Never commit `venv/`, `leads.db`, or `.env` (they're in `.gitignore`).
- Run `git status` before committing to confirm no junk is staged.

## Interview-prep reminders (keep these answerable as we build)
- Difference between a tool, resource, and prompt in MCP.
- Why Claude Code as the runtime vs. building on the raw Claude API.
- How lead qualification actually works under the hood.
- Why outreach is drafted, not auto-sent.
- Honest limitations + what I'd build next (real email integration w/ rate limiting &
  consent, A/B testing outreach, a formal eval set for qualification accuracy).
