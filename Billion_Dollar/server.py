import sqlite3
import logging
import os
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Database Path (Update this to reflect the correct path inside the Docker container)
#DB_PATH = "/Users/maneesha/Documents/Noaa_docker_file/disaster_data.db"
DB_PATH = os.environ.get("DB_PATH", "/app/disaster_data.db")

# Create the MCP server instance - don't specify port in constructor
mcp = FastMCP("Disaster Database Server")

@mcp.resource("schema://main")
def get_schema() -> str:
    """Provide the database schema as a resource."""
    logger.info("Fetching database schema")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            schema = cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall()
            result = "\n".join(sql[0] for sql in schema if sql[0])
            logger.info(f"Schema fetch successful, found {len(schema)} tables")
            return result
    except sqlite3.Error as e:
        logger.error(f"Error fetching schema: {e}")
        return "Error retrieving schema."

@mcp.tool()
def query_data(sql: str) -> str:
    """Execute a SQL query on the Disaster database."""
    logger.info(f"Executing SQL query: {sql}")
    try:
        if not sql.strip().lower().startswith(("select", "pragma")):
            logger.warning(f"Rejected non-SELECT/PRAGMA query: {sql}")
            return "Only SELECT and PRAGMA queries are allowed."

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            result = cursor.execute(sql).fetchall()
        
        if result:
            formatted_result = "\n".join(map(str, result))
            logger.info(f"Query returned {len(result)} rows")
            return formatted_result
        else:
            logger.info("Query returned no results")
            return "No data found for the query."
    except sqlite3.Error as e:
        logger.error(f"Query execution failed: {e}")
        return f"Database query error: {str(e)}"

@mcp.tool()
def get_table_names() -> str:
    """Get all table names from the disaster database."""
    logger.info("Fetching table names")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        
        if tables:
            table_names = [table[0] for table in tables]
            logger.info(f"Found tables: {', '.join(table_names)}")
            return "\n".join(table_names)
        else:
            logger.warning("No tables found in database")
            return "No tables found."
    except sqlite3.Error as e:
        logger.error(f"Error fetching table names: {e}")
        return f"Error fetching table names: {str(e)}"

@mcp.tool()
def get_disaster_types() -> str:
    """Get all unique disaster types from the database."""
    logger.info("Fetching disaster types")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # First, check if disasters table exists and has disaster_type column
            table_info = cursor.execute("PRAGMA table_info(disasters)").fetchall()
            has_disaster_type = any(col[1] == 'disaster_type' for col in table_info)
            
            if has_disaster_type:
                logger.info("Found disaster_type column in disasters table")
                types = cursor.execute("SELECT DISTINCT disaster_type FROM disasters").fetchall()
                if types:
                    disaster_types = [dtype[0] for dtype in types]
                    logger.info(f"Found disaster types: {', '.join(disaster_types)}")
                    return "\n".join(disaster_types)
                else:
                    logger.warning("No disaster types found in database")
                    return "No disaster types found."
            else:
                logger.warning("No disaster_type column found in disasters table")
                return "No disaster_type column found in disasters table."
    except sqlite3.Error as e:
        logger.error(f"Error fetching disaster types: {e}")
        return f"Error fetching disaster types: {str(e)}"

if __name__ == "__main__":
    print("\n" + "="*50)
    print("STARTING DISASTER DATABASE MCP SERVER")
    print("="*50)
    logger.info("Starting MCP server...")
    
    # Check if database exists before starting
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            table_names = [table[0] for table in tables]
            print(f"Database connected successfully. Found tables: {', '.join(table_names)}")
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        print(f"WARNING: Could not connect to database at {DB_PATH}")
        print(f"Error: {str(e)}")
    
    print("\nServer is now running. Press Ctrl+C to stop.")
    print("="*50 + "\n")
    
    # Run the MCP server
    mcp.run()
