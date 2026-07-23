from mcp.server.fastmcp import FastMCP
import sqlite3
import requests 
import os

#fastmcp helper creates and names mcp server 

mcp = FastMCP("leads") #server name 


def db():
    conn = sqlite3.connect("leads.db")
    conn.row_factory = sqlite3.Row
    return conn 
OVERPASS = "https://overpass-api.de/api/interpreter"

@mcp.tool()
def fetch_leads(limit: int = 20) -> list[dict]:
    """Generate REAL potential customers for World Technologies (water & wastewater
    treatment). Finds industrial facilities in Singapore that likely produce wastewater
    using OpenStreetMap. Returns each site's name, type, and any website/phone."""
    query = """
    [out:json][timeout:60];
    (
      nwr["man_made"="works"]["name"](1.15,103.6,1.47,104.1);
      nwr["man_made"="wastewater_plant"]["name"](1.15,103.6,1.47,104.1);
      nwr["man_made"="water_works"]["name"](1.15,103.6,1.47,104.1);
      nwr["building"="industrial"]["name"](1.15,103.6,1.47,104.1);
      nwr["building"="manufacture"]["name"](1.15,103.6,1.47,104.1);
      nwr["building"="warehouse"]["name"](1.15,103.6,1.47,104.1);
      nwr["landuse"="industrial"]["name"](1.15,103.6,1.47,104.1);
      nwr["industrial"]["name"](1.15,103.6,1.47,104.1);
      nwr["craft"="brewery"]["name"](1.15,103.6,1.47,104.1);
      nwr["craft"="distillery"]["name"](1.15,103.6,1.47,104.1);
      nwr["office"="company"]["name"](1.15,103.6,1.47,104.1);
    );
    out center tags 150;
    """
    r = requests.post(
        OVERPASS,
        data={"data": query},
        headers={"User-Agent": "leads-agent/0.1 (learning project)"},
        timeout=60,
    )
    # surface the real problem instead of a cryptic JSON error
    if r.status_code != 200 or not r.text.lstrip().startswith("{"):
        raise RuntimeError(f"Overpass error {r.status_code}: {r.text[:200]}")

    elements = r.json().get("elements", [])
    leads = []
    for el in elements:
        t = el.get("tags", {})
        leads.append({
            "osm_id": el.get("id"),
            "company": t.get("name"),
            "site_type": t.get("man_made") or t.get("craft") or t.get("building") or t.get("landuse") or "industrial",
            "industry_hint": t.get("product") or t.get("industrial") or t.get("craft") or "",
            "website": t.get("website") or t.get("contact:website") or "",
            "phone": t.get("phone") or t.get("contact:phone") or "",
            "address": t.get("addr:street") or t.get("addr:full") or "",
        })
        if len(leads) >= limit:
            break
    return leads



@mcp.tool()
def log_decision(lead_id: int, company: str, decision: str, reason: str) -> str:
    """Record a qualification decision for a lead. Call this after deciding whether a
    lead is qualified or rejected. `decision` must be 'qualified' or 'rejected';
    `reason` is one sentence citing the ICP criteria that drove the call."""
    conn = db()
    conn.execute(
        "INSERT INTO decisions (lead_id, company, decision, reason) VALUES (?,?,?,?)",
        (lead_id, company, decision, reason)
    )
    conn.commit()
    conn.close()
    return f"Logged {decision} for {company}."

#def search_leads(industry: str = "", min_employees: int = 0) -> list[dict]:
    """
    Search leads, optionally filtering by industry and minimum employee count.
    Returns a list of leads with all their fields.
    """
    #instruction for LLM

    conn = db()
    rows = conn.execute(
        "SELECT * FROM leads WHERE industry LIKE ? AND employees >= ?",
        (f"%{industry}%", min_employees)

    ).fetchall()
    conn.close()
    return [ dict(r) for r in rows ] #


#resource is data AI can read for context 
@mcp.resource("leads://all")
def all_leads() -> str:
    """
    The full list of leads in the database, as readable text
    """
    conn = db()
    rows = conn.execute("SELECT * FROM leads").fetchall()
    conn.close() 

    lines = [
        f"#{r['id']} {r['company']} | {r['industry']} | "
          f"{r['employees']} employees | {r['funding']} | signal: {r['signal']} | status: {r['status']}"
        for r in rows
    ]

    return "\n".join(lines)



@mcp.resource("leads://{lead_id}")
def one_lead(lead_id: str) -> str:
    """
    A single lead, by ID, as readable text
    """
    conn = db()
    r = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
    conn.close()

    if r is None:
        return f"Lead with ID {lead_id} not found."

    return (f"{r['company']} — {r['industry']}, {r['employees']} employees, "
            f"{r['funding_stage']}. Signal: {r['signal']}. Status: {r['status']}.")



#reuasable template that LLM can use 

@mcp.prompt()
def qualify_lead(lead_info:str) -> str: 
    """
    A reusable prompt that asks the model to qualify a lead against our ICP
    """
    return f""" You are qualifying a sales lead against our Ideal Customer Profile (ICP). Here is the lead information:
    OOur ICP — a strong lead meets MOST of these:
- An industrial or municipal facility that generates wastewater or needs water treatment
- Operates in a sector we serve: pharmaceutical, semiconductor, oil & gas / petrochemical,
  food & beverage / breweries, textile & dyeing, distilleries, pulp & paper, power,
  oleochemical, or municipal water/sewage
- Located in a region we service (Singapore, Indonesia, India, wider APAC)
- Large enough to have meaningful effluent volumes and a treatment budget
Reject: retail, offices, pure logistics/warehousing, or anything with no plausible
wastewater/water-treatment need.

Here is the lead:
{lead_info}

Decide: QUALIFIED or NOT QUALIFIED. Give one sentence of reasoning citing the ICP criteria."""


#client passes in qualiy lead prompt passes in lead 

DRAFTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drafts")

@mcp.tool()
def save_draft(company:str, contact_role: str, subject: str, body: str) -> str:
    """
    Save an outreach email draft to a file for human review.
    Use this after writing outreach for a qualified lead.
    Drafts are NEVER sent - they are saved for a human to review and send. 'contact_role is who it's addressed to (e.g., "Head of Operations").
    Returns the path to the saved draft file.
    """

    os.makedirs(DRAFTS_DIR, exist_ok=True)

    safe = "".join(ch for ch in company if ch.isalnum() or ch in " -_").strip()
    safe = safe.replace(" ", "_") or "lead"
    path = os.path.join(DRAFTS_DIR, f"{safe}.md")
    with open(path, "w") as f:
        f.write(f"To: {contact_role}, {company}\n")
        f.write(f"Subject: {subject}\n")
        f.write(f"\n")
        f.write(body.strip() + "\n")
    return f"Saved draft for {company} to drafts/{safe}.md"


if __name__ == "__main__":
    mcp.run() #start server and listen for client req

#client(claude code) connects -> discovers what server can do -> sends req to server -> server executes function -> return results to client