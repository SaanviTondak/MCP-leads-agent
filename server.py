from mcp.server.fastmcp import FastMCP
import sqlite3

mcp = FastMCP("leads") #server name 

def db():
    conn = sqlite3.connect("leads.db")
    conn.row_factory = sqlite3.Row
    return conn 


@mcp.tool()

def search_leads(industry: str = "", min_employees: int = 0) -> list[dict]:
    """
    Search leads, optionally filtering by industry and minimum employee count.
    Returns a list of leads with all their fields.
    """

    conn = db()
    rows = conn.execute(
        "SELECT * FROM leads WHERE industry LIKE ? AND employees >= ?",
        (f"%{industry}%", min_employees)

    ).fetchall()
    conn.close()
    return [ dict(r) for r in rows ]



