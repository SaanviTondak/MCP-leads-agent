import sqlite3

#fake data to test out lead scraping

leads = [
    # (company, industry, employees, funding, signal, status)
    ("Nimbus AI",       "SaaS",        45,  "Series A", "Hiring 3 ML engineers",        "new"),
    ("GreenLeaf Foods", "Food",        200, "Series C", "Opened 2 new warehouses",      "new"),
    ("Coblt",           "Fintech",     12,  "Seed",     "Launched public beta",         "new"),
    ("Harborview",      "Real Estate", 500, "Public",   "No recent signals",            "new"),
    ("Pixula",          "SaaS",        30,  "Series A", "Posted about scaling infra",   "new"),
    ("MediSync",        "Healthtech",  80,  "Series B", "New FDA clearance",            "new"),
    ("BrewBox",         "Retail",      8,   "Seed",     "First hire in growth",         "new"),
    ("Aeronix",         "Aerospace",   1200,"Public",   "Government contract won",       "new"),
    ("Talize",          "SaaS",        22,  "Seed",     "Hiring first sales rep",       "new"),
    ("Fernpath",        "Consulting",  60,  "Bootstrap","No funding, steady growth",     "new"),
]

conn = sqlite3.connect("leads.db")
c = conn.cursor()
c.execute(
    """CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY, 
    company TEXT,
    industry TEXT, employees INTEGER,
    funding TEXT,
    signal TEXT,
    status TEXT)""")

c.execute("DELETE FROM leads")  # Clear existing data

c.executemany(
    "INSERT INTO leads (company, industry, employees, funding, signal, status) VALUES (?, ?, ?, ?, ?, ?)",
    leads
    )
conn.commit()
conn.close()

print(f"Seeded {len(leads)} leads into leads.db")

