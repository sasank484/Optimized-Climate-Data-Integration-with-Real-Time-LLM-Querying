import asyncio
import json
import logging
import re
import requests
import spacy
import us
import dateparser
import os
from dotenv import load_dotenv  # Importing dotenv to load environment variables
from collections import defaultdict
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# === CONFIG ===
CLIMATEGPT_API = "https://erasmus.ai/models/climategpt_8b_latest/v1/chat/completions"
USERNAME = os.getenv("CLIMATEGPT_USERNAME")  # Get username from the .env file
PASSWORD = os.getenv("CLIMATEGPT_PASSWORD")  # Get password from the .env file


nlp = spacy.load("en_core_web_sm")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VALID_COLUMNS = {
    "year", "event", "incident_number", "incident_start", "incident_end", "state",
    "incident_type", "valid_ihp_applications", "eligible_ihp_applications",
    "ihp_total", "pa_total", "pa_projects_count", "cdbg_dr_allocation"
}

METRIC_COLUMNS = {
    "valid_ihp_applications", "eligible_ihp_applications", "ihp_total",
    "pa_total", "pa_projects_count", "cdbg_dr_allocation"
}

NON_METRIC_COLUMNS = {
    "year", "event", "incident_number", "incident_start",
    "incident_end", "state", "incident_type"
}

SUPPORTED_INCIDENT_TYPES = [
    "Coastal Storm", "Dam or Levee Break", "Dam/Levee Break", "Earthquake", "Fire", "Flood", "Freezing",
    "Hurricane", "Mud/Landslide", "Other", "Severe Ice Storm", "Severe Storm", "Snowstorm",
    "Straight-Line Winds", "Tornado", "Tropical Storm", "Tsunami", "Typhoon", "Volcanic Eruption", "Winter Storm"
]

COMPARISON_PHRASES = {
    "more than": ">", "greater than": ">", "less than": "<", "under": "<",
    "at least": ">=", "at most": "<="
}

METRIC_UNITS = {
    "valid_ihp_applications": "applications",
    "eligible_ihp_applications": "applications",
    "ihp_total": "$",
    "pa_total": "$",
    "pa_projects_count": "projects",
    "cdbg_dr_allocation": "$"
}

METRIC_ALIASES = {
    "ihp_total": "individual and households program total",
    "pa_total": "public assistance total",
    "pa_projects_count": "public assistance projects count",
    "cdbg_dr_allocation": "community development block grant disaster recovery allocation"
}

# === CLASSIFIER ===
def detect_question_type(question: str) -> str:
    q_lower = question.lower()

    for metric in METRIC_COLUMNS:
        # Build regex patterns for exact matching
        metric_exact = re.compile(rf"\b{re.escape(metric)}\b")
        metric_spaced = re.compile(rf"\b{re.escape(metric.replace('_', ' '))}\b")
        metric_alias = METRIC_ALIASES.get(metric, "")
        metric_alias_exact = re.compile(rf"\b{re.escape(metric_alias)}\b") if metric_alias else None

        if (metric_exact.search(q_lower) or
            metric_spaced.search(q_lower) or
            (metric_alias_exact and metric_alias_exact.search(q_lower))):
            return "metric"

    return "non-metric"



# === SHARED HELPERS ===
def extract_state(doc):
    for ent in doc.ents:
        if ent.label_ == "GPE":
            match = us.states.lookup(ent.text)
            if match:
                return match.abbr
    for token in doc:
        if token.is_upper or token.text.istitle():
            match = us.states.lookup(token.text)
            if match:
                return match.abbr
    return None

def extract_incident_type(doc):
    for token in doc:
        word = token.lemma_.lower()
        for itype in SUPPORTED_INCIDENT_TYPES:
            if word == itype.lower():
                return itype
    return None

def extract_year(doc):
    for ent in doc.ents:
        if ent.label_ == "DATE":
            parsed = dateparser.parse(ent.text)
            if parsed and 1900 <= parsed.year <= 2100:
                return parsed.year
    for token in doc:
        if token.like_num:
            try:
                year = int(token.text)
                if 1900 <= year <= 2100:
                    return year
            except:
                continue
    return None

async def query_mcp(filters):
    server_params = StdioServerParameters(command="python", args=["server.py"])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await session.call_tool("advanced_query", {"filters": filters})

def send_to_climategpt(prompt):
    response = requests.post(
        CLIMATEGPT_API,
        auth=(USERNAME, PASSWORD),
        headers={"Content-Type": "application/json"},
        json={
            "model": "/cache/climategpt_8b_latest",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant. Use only the provided data."},
                {"role": "user", "content": prompt}
            ]
        }
    )
    if response.status_code == 200:
        print("\nClimateGPT's Answer:\n")
        print(response.json()['choices'][0]['message']['content'])
    else:
        print(f"API Error {response.status_code}: {response.text}")

# === NON-METRIC FILTER LOGIC ===
def extract_filters_from_question(question: str) -> dict:
    filters = {}
    numeric_conditions = []
    q_lower = question.lower()
    doc = nlp(question)

    incident_type = extract_incident_type(doc)
    if incident_type:
        filters["incident_type"] = incident_type

    state = extract_state(doc)
    if state:
        filters["state"] = state

    YEAR_RANGE_PATTERNS = [
        {
            "pattern": r"\bbetween\s+(?:19|20)\d{2}\s+(?:and|to)\s+(?:19|20)\d{2}",
            "extract": lambda years: [("year", ">=", years[0]), ("year", "<=", years[1])]
        },
        {
            "pattern": r"\bfrom\s+(?:19|20)\d{2}\s+(?:to|until)\s+(?:19|20)\d{2}",
            "extract": lambda years: [("year", ">=", years[0]), ("year", "<=", years[1])]
        }
    ]
    for rule in YEAR_RANGE_PATTERNS:
        match = re.search(rule["pattern"], q_lower)
        if match:
            years = re.findall(r"(?:19|20)\d{2}", match.group(0))
            if len(years) == 2:
                numeric_conditions.extend(rule["extract"](tuple(map(int, years))))
                break

    TIME_DIRECTIONAL_PATTERNS = [
        (r"\bafter\s+(19|20)\d{2}", ">", "year"),
        (r"\bbefore\s+(19|20)\d{2}", "<", "year"),
        (r"\bsince\s+(19|20)\d{2}", ">=", "year")
    ]
    for pattern, op, col in TIME_DIRECTIONAL_PATTERNS:
        match = re.search(pattern, q_lower)
        if match:
            year = int(match.group(0).split()[-1])
            numeric_conditions.append((col, op, year))

    # if not any(cond[0] == "year" for cond in numeric_conditions) and "year" not in filters:
    #     year = extract_year(doc)
    #     if year:
    #         filters["year"] = ("=", year)
    
    if not any(cond[0] == "year" for cond in numeric_conditions) and "year" not in filters:
        year = extract_year(doc)
        if year:
            if "from" in q_lower:
                filters["year"] = (">=", year)
            elif "after" in q_lower:
                filters["year"] = (">", year)
            elif "before" in q_lower:
                filters["year"] = ("<", year)
            elif "since" in q_lower:
                filters["year"] = (">=", year)
            else:
                filters["year"] = ("=", year)


    for column in VALID_COLUMNS:
        if column in METRIC_COLUMNS or column == "event":
            continue
        pattern = fr"{column.replace('_', ' ')}.*?(more than|greater than|less than|under|at least|at most)?\s*\$?([\d,\.]+)"
        match = re.search(pattern, q_lower)
        if match:
            comp = match.group(1)
            val = match.group(2).replace(",", "")
            op = COMPARISON_PHRASES.get(comp, "=")
            try:
                numeric_conditions.append((column, op, float(val)))
            except:
                continue

    grouped_filters = defaultdict(list)
    for col, op, val in numeric_conditions:
        grouped_filters[col].append((op, val))

    for key, conditions in grouped_filters.items():
        filters[key] = conditions[0] if len(conditions) == 1 else conditions

    return filters

# === HANDLER: NON-METRIC ===
async def handle_non_metric_question(question: str):
    filters = extract_filters_from_question(question)
    print("Extracted filters (non-metric):", filters)

    result = await query_mcp(filters)
    data = [json.loads(content.text) for content in result.content if content.text]
    print(f" Rows returned: {len(data)}")

    sample = data[:25]
    prompt = f"Based on the following disaster data, answer the user's question:\n\nData: {json.dumps(sample)}\n\nQuestion: {question}"
    send_to_climategpt(prompt)

    # event_list = "\n".join(
    # f"{row['state']} {row['event']} ({row['year']})"
    # for row in data if 'event' in row)
    
    # prompt = f"The following are the disaster events matching the query:\n\n{event_list}\n\nUser's question: {question}\nPlease summarize based on this data only."


# === HANDLER: METRIC ===
async def handle_metric_question(question: str):
    print("Metric question detected")
    doc = nlp(question)

    metric = next((col for col in METRIC_COLUMNS if col in question.lower() or col.replace("_", " ") in question.lower() or METRIC_ALIASES.get(col, "") in question.lower()), None)
    if not metric:
        print("Could not identify a valid metric column.")
        return

    state = extract_state(doc)
    incident_type = extract_incident_type(doc)
    year = extract_year(doc)

    if not all([state, incident_type, year]):
        print("Missing one or more required filters: year, state, or incident_type.")
        return

    filters = {
        "state": state,
        "incident_type": incident_type,
        "year": ("=", year)
    }

    print("Filters (metric):", filters)
    result = await query_mcp(filters)
    data = [json.loads(content.text) for content in result.content if content.text]
    print(f"Rows returned: {len(data)}")

    if not data:
        prompt = f"No data was found for the question: '{question}'. Please respond based only on this data."
    else:
        row = data[0]
        value = row.get(metric)
        unit = METRIC_UNITS.get(metric, "")
        if value is not None:
            prompt = f"The data retrieved for '{question}' is: {json.dumps(row)}. The requested metric is '{metric}' with a value of {value} {unit}. Please respond based only on this data."
        else:
            prompt = f"The data retrieved for '{question}' is: {json.dumps(row)}. However, the metric '{metric}' was not found in the result."

    send_to_climategpt(prompt)

# === MAIN ROUTER ===
import asyncio

# === MAIN ROUTER ===
async def main():
    while True:  # Keep the loop running to accept multiple questions
        question = input("\n Ask your disaster-related question (or type 'exit' to quit): ").strip()

        if question.lower() == 'exit':  # Exit the loop if the user types 'exit'
            print("Exiting the program.")
            break  # Exit the loop and stop the program

        question_type = detect_question_type(question)

        if question_type == "metric":
            await handle_metric_question(question)
        else:
            await handle_non_metric_question(question)

if __name__ == "__main__":
    asyncio.run(main())

