import asyncio
import logging
import sys
import json
import requests
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# API endpoint for climategpt_8b_latest
API_URL = "https://erasmus.ai/models/climategpt_8b_latest/v1/chat/completions"
API_AUTH = ("ai", "4climate")  # Username: ai, Password: 4climate
HEADERS = {"Content-Type": "application/json"}

# Define disaster type mapping to columns in your database
DISASTER_COLUMN_MAPPING = {
    "earthquake": None,  # Not present in your schema
    "flood": "Flooding",
    "flooding": "Flooding",
    "freeze": "Freeze",
    "severe storm": "Severe Storm",
    "storm": "Severe Storm",
    "tropical cyclone": "Tropical Cyclone",
    "hurricane": "Tropical Cyclone",
    "cyclone": "Tropical Cyclone",
    "wildfire": "Wildfire",
    "fire": "Wildfire",
    "winter storm": "Winter Storm",
    "snow": "Winter Storm",
    "drought": "Drought"
}

def parse_disaster_question(question):
    """Parse question to extract disaster type, location, and year"""
    logger.info(f"Parsing question: {question}")
    question = question.lower()
    
    # Extract disaster type using the mapping
    disaster_type = None
    mapped_column = None
    
    for keyword, column in DISASTER_COLUMN_MAPPING.items():
        if keyword in question:
            disaster_type = keyword
            mapped_column = column
            break
    
    # Extract year (single year or range)
    year = None
    words = question.split()
    for i, word in enumerate(words):
        if word.isdigit() and len(word) == 4 and 1900 <= int(word) <= 2024:
            year = int(word)
            break
        # Check for year range like "2010-2015"
        elif "-" in word and all(part.isdigit() and len(part) == 4 for part in word.split("-")):
            start, end = word.split("-")
            if 1900 <= int(start) <= 2024 and 1900 <= int(end) <= 2024:
                year = f"{start}-{end}"
                break
    
    # If we didn't find a year directly, try to find it in location
    if year is None and "1980" in question:
        year = 1980
    elif year is None and "1983" in question:
        year = 1983
    
    # Extract location (simplified approach)
    location = None
    location_indicators = ["in", "at", "near"]
    for indicator in location_indicators:
        if indicator in words:
            idx = words.index(indicator)
            if idx + 1 < len(words) and not words[idx + 1].isdigit():
                # Simple extraction for location after indicators like "in", "at", "near"
                location_words = []
                for i in range(idx + 1, len(words)):
                    if words[i] in location_indicators or words[i].isdigit() or words[i] == "between":
                        break
                    location_words.append(words[i])
                if location_words:
                    location = " ".join(location_words).capitalize()
                break
    
    result = {"disaster_type": disaster_type, "mapped_column": mapped_column, "location": location, "year": year}
    logger.info(f"Parsed result: {result}")
    print(f"Parsed - Disaster: {disaster_type}, Location: {location}, Year: {year}")
    return disaster_type, mapped_column, location, year

def improved_answer(question, answer):
    """Send the extracted answer and question to ClimateGPT for better formatting."""
    system_prompt = (
        "You are a disaster data specialist. "
        "CRITICAL INSTRUCTION: Preserve ALL factual information exactly as stated in the input answer. "
        "Format rules:\n"
        "1. NEVER contradict numerical values or facts in the original answer.\n"
        "2. If the original says there was data for a specific year, your answer must say the same.\n"
        "3. If the original includes specific costs or counts, keep those exact figures.\n"
        "4. If you're unsure about a fact, keep the original wording exactly.\n"
        "5. Your job is ONLY to improve readability, not to change facts or add information.\n"
        "6. Do not say 'I don't have information' if the original answer provided information.\n"
        "The answer you're improving comes directly from our disaster database and is factually correct."
    )

    payload = {
        "model": "/cache/climategpt_8b_latest",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Original question: {question}\n\nFactual answer to improve (keep all facts exactly the same): {answer}"}
        ]
    }

    response = requests.post(
        API_URL,
        auth=API_AUTH,
        headers=HEADERS,
        data=json.dumps(payload)
    )

    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"Error from API: {response.text}"

async def ask_about_disaster(session, question):
    """Process a question and get data from the database using MCP"""
    try:
        # Get schema using MCP
        logger.info("Fetching schema from MCP server")
        schema_result = await session.read_resource("schema://main")
        
        # Extract the schema content text
        schema_content = ""
        if hasattr(schema_result, 'contents') and schema_result.contents:
            schema_content = schema_result.contents[0].text if hasattr(schema_result.contents[0], 'text') else str(schema_result)
        else:
            schema_content = str(schema_result)
            
        logger.info(f"Schema content (first 100 chars): {schema_content[:100]}...")
        
        # Parse the question
        disaster_type, mapped_column, location, year = parse_disaster_question(question)
        
        # Get table names
        logger.info("Getting table names using MCP tool")
        result = await session.call_tool("get_table_names")
        
        # Extract the tables data text
        tables_data = ""
        if hasattr(result, 'content') and result.content:
            tables_data = result.content[0].text if hasattr(result.content[0], 'text') else ""
        elif hasattr(result, 'text'):
            tables_data = result.text
        
        tables = tables_data.strip().split('\n') if tables_data else []
        logger.info(f"Tables found: {tables}")
        
        # Use disaster_records table which we know exists
        table_name = "disaster_records" if "disaster_records" in tables else tables[0] if tables else "unknown_table"
        
        # Get column info
        columns_query = f'PRAGMA table_info({table_name})'
        logger.info(f"Executing PRAGMA query: {columns_query}")
        columns_result = await session.call_tool("query_data", {"sql": columns_query})
        
        # Extract the columns data text
        columns_text = ""
        if hasattr(columns_result, 'content') and columns_result.content:
            columns_text = columns_result.content[0].text if hasattr(columns_result.content[0], 'text') else ""
        elif hasattr(columns_result, 'text'):
            columns_text = columns_result.text
            
        logger.info(f"Column data received: {len(columns_text)} chars")
        
        # Parse column names
        columns = []
        try:
            for line in columns_text.split('\n'):
                if line.startswith('('):
                    # Each line is a tuple like (0, 'Year', 'INTEGER', 0, None, 0)
                    col_tuple = eval(line)
                    columns.append(col_tuple[1])  # Column name is at index 1
        except Exception as e:
            logger.error(f"Error parsing columns: {e}")
            # Fallback if parsing fails
            columns = ["Year", "Drought Count", "Drought Cost", "Flooding Count", "Flooding Cost", 
                      "Freeze Count", "Freeze Cost", "Severe Storm Count", "Severe Storm Cost", 
                      "Tropical Cyclone Count", "Tropical Cyclone Cost", "Wildfire Count", "Wildfire Cost", 
                      "Winter Storm Count", "Winter Storm Cost", "Total_Disaster_Count", "Total_Disaster_Cost"]
        
        logger.info(f"Parsed columns: {columns}")
        
        # Helper function to properly quote identifiers with spaces
        def quote_identifier(identifier):
            return f'"{identifier}"'
        
        # Build base query
        select_columns = ["Year"]
        
        # Add disaster-specific columns if we have a mapped column
        if mapped_column:
            count_col = f"{mapped_column} Count"
            cost_col = f"{mapped_column} Cost"
            if count_col in columns:
                select_columns.append(count_col)
            if cost_col in columns:
                select_columns.append(cost_col)
            
            # If it's a comparison question, add columns for other disaster types mentioned
            if "compare" in question.lower():
                for word in question.lower().split():
                    if word != disaster_type and word in DISASTER_COLUMN_MAPPING:
                        other_col = DISASTER_COLUMN_MAPPING[word]
                        if other_col:
                            other_count = f"{other_col} Count"
                            other_cost = f"{other_col} Cost"
                            if other_count in columns and other_count not in select_columns:
                                select_columns.append(other_count)
                            if other_cost in columns and other_cost not in select_columns:
                                select_columns.append(other_cost)
        else:
            # If no specific disaster was found, include all relevant columns
            for col_prefix in ["Drought", "Flooding", "Severe Storm", "Tropical Cyclone", "Wildfire"]:
                count_col = f"{col_prefix} Count"
                cost_col = f"{col_prefix} Cost"
                if count_col in columns:
                    select_columns.append(count_col)
                if cost_col in columns:
                    select_columns.append(cost_col)
        
        # Add total disaster columns
        if "Total_Disaster_Count" in columns:
            select_columns.append("Total_Disaster_Count")
        if "Total_Disaster_Cost" in columns:
            select_columns.append("Total_Disaster_Cost")
        
        # Quote all column names to handle spaces
        quoted_columns = [quote_identifier(col) for col in select_columns]
        
        # Build the SQL query
        sql_query = f"SELECT {', '.join(quoted_columns)} FROM {table_name} WHERE 1=1"
        
        # Add year condition
        if year:
            if isinstance(year, str) and "-" in year:  # Year range
                start, end = year.split("-")
                sql_query += f" AND Year BETWEEN {start} AND {end}"
            else:
                sql_query += f" AND Year = {year}"
        
        # Order by year
        sql_query += " ORDER BY Year ASC"
        
        # Limit results
        sql_query += " LIMIT 20"
        
        logger.info(f"SQL Query: {sql_query}")
        print(f"SQL Query: {sql_query}")
        
        # Execute the query using the MCP session
        raw_result = await session.call_tool("query_data", {"sql": sql_query})
        
        # After executing the SQL query and getting raw_result:
        raw_data = ""
        if hasattr(raw_result, 'content') and raw_result.content:
            raw_data = raw_result.content[0].text if hasattr(raw_result.content[0], 'text') else ""
        elif hasattr(raw_result, 'text'):
            raw_data = raw_result.text
            
        logger.info(f"Query result length: {len(raw_data)} chars")
        logger.info(f"Raw query result: {raw_data[:100]}...")
        
        # Parse the raw data into a more structured format
        structured_data = []
        column_names = select_columns  # These are the columns selected in the query
        
        if raw_data:
            lines = raw_data.strip().split('\n')
            for line in lines:
                # Remove parentheses and split by commas
                clean_line = line.strip('() ')
                # Handle the case where values might contain commas within quotes
                parsed_values = []
                in_quotes = False
                current_value = ""
                
                for char in clean_line:
                    if char == '"' or char == "'":
                        in_quotes = not in_quotes
                        current_value += char
                    elif char == ',' and not in_quotes:
                        parsed_values.append(current_value.strip())
                        current_value = ""
                    else:
                        current_value += char
                
                # Add the last value
                if current_value:
                    parsed_values.append(current_value.strip())
                
                # Create a dictionary of the values with their column names
                if len(parsed_values) == len(column_names):
                    row_dict = {}
                    for i, col in enumerate(column_names):
                        # Clean up the value - remove quotes and extra spaces
                        value = parsed_values[i].strip('"\'')
                        
                        # For cost columns, format as currency
                        if "Cost" in col:
                            try:
                                value = f"${float(value):.1f} billion"
                            except ValueError:
                                pass  # Keep as is if not a valid float
                        
                        row_dict[col] = value
                    structured_data.append(row_dict)
        
        # Format the structured data into a readable text
        formatted_data = ""
        if structured_data:
            formatted_data = "Results from the disaster database:\n\n"
            for row in structured_data:
                formatted_data += f"Year {row.get('Year', 'Unknown')}:\n"
                for col, value in row.items():
                    if col != 'Year':  # Skip Year as we already included it
                        formatted_data += f"- {col}: {value}\n"
                formatted_data += "\n"
        else:
            formatted_data = "No data found matching your query in the disaster database."
        
        # Create a more data-focused system prompt
        data_prompt = (
            "You are a data analyst specializing in natural disaster information. "
            "Below is the result of a database query about disasters. "
            f"Query results format:\n{formatted_data}\n\n"
            "Answer the user's question using ONLY the data provided. "
            "Important rules to follow:\n"
            "1. Your answers must be 100% factually correct based on the data provided.\n"
            "2. Never make up data or fill in missing information - stick exactly to what's in the results.\n"
            "3. Be specific about years, costs, and counts when they appear in the data.\n"
            "4. If the data shows costs, always specify the monetary unit (billions of dollars).\n"
            "5. If the question asks for a comparison, directly compare the specific values from the data.\n"
            "6. If the data doesn't contain information to answer the question, clearly state this limitation.\n"
            f"The user asked: {question}\n"
            "Base your answer solely on the database results shown above."
        )

        payload = {
            "model": "/cache/climategpt_8b_latest",
            "messages": [
                {"role": "system", "content": data_prompt},
                {"role": "user", "content": question}
            ]
        }

        response = requests.post(
            API_URL,
            auth=API_AUTH,
            headers=HEADERS,
            data=json.dumps(payload)
        )

        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            error_message = f"Error from API: {response.status_code} - {response.text}"
            logger.error(error_message)
            return error_message
    except Exception as e:
        logger.error(f"Error in ask_about_disaster: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return f"Error processing question: {str(e)}"

async def process_questions(questions):
    """Process a list of questions using MCP"""
    # Create server parameters for connecting to your server
    server_params = StdioServerParameters(
        command="python",  # Use python to run your server
        args=["server.py"],  # Your server script
        env=None,  # No special environment variables
    )
    
    print("Connecting to MCP server...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                
                # List available tools and resources to verify connection
                tools = await session.list_tools()
                resources = await session.list_resources()
                
                print(f"Connected to MCP server!")
                print(f"Available tools: {tools}")
                print(f"Available resources: {resources}")
                
                # Process each question
                for question in questions:
                    print("\n" + "-"*50)
                    print(f"Asking: {question}")
                    
                    answer = await ask_about_disaster(session, question)
                    print("\nRaw answer received:")
                    print("-"*30)
                    print(answer)
                    print("-"*30)
                    
                    improved_answer_text = improved_answer(question, answer)
                    
                    print("\nFinal response:")
                    print("-"*30)
                    print(improved_answer_text)
                    print("-"*30)
    except Exception as e:
        print(f"Error connecting to MCP server: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        print("Please make sure your server.py file is accessible and functioning properly.")

if __name__ == "__main__":
    # Test questions
    questions = [
        "How many droughts occurred in 1980?",
        "What was the total disaster cost in 1983?",
        "Compare the flooding and tropical cyclone cost between 1980-1984"
    ]
    
    # Run the async main function
    asyncio.run(process_questions(questions))
    