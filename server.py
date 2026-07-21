from mcp.server.fastmcp import FastMCP
import sqlite3

#fastmcp helper creates and names mcp server 

mcp = FastMCP("leads") #server name 


def db():
    conn = sqlite3.connect("leads.db")
    conn.row_factory = sqlite3.Row
    return conn 


@mcp.tool() #decorator to register the function as a tool in the mcp server

def search_leads(industry: str = "", min_employees: int = 0) -> list[dict]:
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


if __name__ == "__main__":
    mcp_run() #start server and listen for client req 

#client(claude code) connects -> discovers what server can do -> sends req to server -> server executes function -> return results to client 


