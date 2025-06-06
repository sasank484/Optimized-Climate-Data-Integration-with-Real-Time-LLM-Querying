import sqlite3
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any
import datetime
import sys

# === Configuration ===
DB_PATH = "disaster_fema_hud.db"
TABLE_NAME = "disaster_dollar_db"
LOG_FILE = "mcp_debug.log"

# === Track Tools Registered ===
REGISTERED_TOOLS = set()

# === Logger ===
def log(message: str):
    with open(LOG_FILE, "a") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

log(" File loaded - this is the REAL disastermcp.py")
log(f" Running as: {sys.argv}")

# === Create MCP Server ===
mcp = FastMCP("FemaDisasterServer", dependencies=["mcp"])

# === SQL Helper ===
def query_database(query: str) -> List[Dict]:
    log(f" Executing SQL Query:\n{query}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    log(f" Rows fetched: {len(rows)}")
    return [dict(zip(columns, row)) for row in rows]


@REGISTERED_TOOLS.add("advanced_query") or mcp.tool()
def advanced_query(filters: Dict[str, Any]) -> List[Dict]:
    log(" advanced_query was called")
    log(f"🧪 Filters received: {filters}")

    try:
        flat_filters = {}
        for k, v in filters.items():
            # Convert ['>=', 2009] to tuple
            if isinstance(v, list) and len(v) == 2 and isinstance(v[0], str):
                flat_filters[k] = tuple(v)
            else:
                flat_filters[k] = v

        log(f" Flattened Filters: {flat_filters}")

        conditions = []
        VALID_FIELDS = {
            "state", "incident_type", "year", "event", "incident_number",
            "valid_ihp_applications", "eligible_ihp_applications",
            "ihp_total", "pa_total", "pa_projects_count", "cdbg_dr_allocation"
        }

        def format_condition(col: str, condition: tuple) -> str:
            op, val = condition
            return f"{col} {op} {val}" if not isinstance(val, str) else f"{col} {op} '{val}'"

        for key, val in flat_filters.items():
            if key not in VALID_FIELDS:
                continue

            if isinstance(val, list):
                # Multiple conditions (e.g. [['>=', 2005], ['<=', 2010]])
                sub_conditions = [
                    format_condition(key, tuple(cond))
                    for cond in val
                    if isinstance(cond, (list, tuple)) and len(cond) == 2
                ]
                if sub_conditions:
                    conditions.append("(" + " AND ".join(sub_conditions) + ")")

            elif isinstance(val, (list, tuple)) and len(val) == 2:
                # Single condition in tuple or list
                conditions.append(format_condition(key, tuple(val)))

            else:
                # Simple equality
                conditions.append(f"{key} = '{val}'")

        unknown = [k for k in flat_filters if k not in VALID_FIELDS]
        if unknown:
            log(f" Ignored unknown filters: {unknown}")

        where_clause = " AND ".join(conditions)
        query = f"SELECT * FROM {TABLE_NAME}"
        if where_clause:
            query += f" WHERE {where_clause}"

        log(f" Final SQL Query: {query}")
        return query_database(query)

    except Exception as e:
        log(f" Error in advanced_query: {e}")
        return []


@REGISTERED_TOOLS.add("ping") or mcp.tool()
def ping() -> str:
    log(" ping was called.")
    return "pong"


# === Start the MCP Server ===
if __name__ == "__main__":
    log(" MCP Server started")
    log(f" Registered Tools: {sorted(REGISTERED_TOOLS)}")
    mcp.run()
