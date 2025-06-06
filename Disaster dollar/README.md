# Disaster Dollar Dataset integration with Climate GPT

A Python-based chatbot that answers disaster-related queries using a structured SQLite database containing FEMA and HUD financial data. It uses the MCP (Model Context Protocol) for server-client communication and integrates with the ClimateGPT API to generate human-like responses.

## Features

- **Disaster Assistance Data**: Query FEMA and HUD financial assistance metrics like IHP totals, PA totals, project counts, and CDBG-DR allocations for disasters across U.S. states.
- **NLP-Based Query Parsing**: Supports natural language queries including incident type, state, and year filters using SpaCy and regex.
- **ClimateGPT Integration**: Uses Erasmus.AI’s ClimateGPT-8B model to transform raw data into summarized, human-readable answers.
- **Advanced SQL Filtering**: Applies rule-based filters to convert year ranges, incident types, and comparison operators into optimized SQL conditions.
- **Dockerized Architecture**: Can be containerized using Docker to allow seamless deployment and consistent local development.

## Repository Structure

- `server.py`: MCP server to query the `disaster_fema_hud.db` SQLite database using custom filters.
- `client.py`: NLP-based client that extracts filters from user queries and forwards data to ClimateGPT.
- `disaster_fema_hud.db`: SQLite database containing disaster incident metadata and associated financial metrics.
- `auth.env`: Environment file containing API credentials (not included; see Setup section).
- `Dockerfile`: For building and running the project in a containerized environment.

## Supported Filters

The chatbot can extract and filter based on the following fields:
- `state`: U.S. state abbreviation (e.g., TX, CA)
- `incident_type`: e.g., Hurricane, Flood, Earthquake
- `year`: single year (e.g., 2020) or range (e.g., between 2010 and 2020)
- Comparison operators for numerical filters such as `ihp_total > 5000000`

## Prerequisites

- Python 3.10 or later
- SQLite3
- ClimateGPT API access (Erasmus.AI)
- Docker (optional for containerized use)

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git init Disaster_Dollar
   cd Disaster_Dollar
   git remote add origin https://github.com/newsconsole/GMU_DAEN_2025_01_C.git
   git sparse-checkout init --cone
   git sparse-checkout set Disaster_Dollar
   git pull origin main


2. **Create** `auth.env`Create a file named `auth.env` in the project root with the following content:

Create a file named `auth.env` in the root of your project directory with the following content:

```env
CLIMATEGPT_USERNAME=your_username
CLIMATEGPT_PASSWORD=your_password
```


## 3. Install Python Dependencies (Optional for Local Development)

```bash
pip install -r requirements.txt
```

---

## 4. Ensure SQLite Database Exists

Make sure `disaster_fema_hud.db` is placed in the root directory.

---

## Running the Application

### Using Docker (Recommended)

**Build and Run**

```bash
docker-compose up --build
```

Then run the client:
```bash
python client.py
```
---

### Without Docker

**Start MCP Server**

```bash
python server.py
```

**Run Client in Separate Terminal**

```bash
python client.py
```

---

## Example Questions

```yaml
What was the ihp_total for Texas hurricane in 2012?
List tornado incidents in Florida from 2005 to 2010
Show all earthquake-related applications after 2010 in California
```

---

## Database Schema

The `disaster_dollar_db` table includes:

- `state` (TEXT)
- `incident_type` (TEXT)
- `year` (INTEGER)
- `event` (TEXT)
- `incident_number` (TEXT)
- `valid_ihp_applications` (INTEGER)
- `eligible_ihp_applications` (INTEGER)
- `ihp_total` (REAL)
- `pa_total` (REAL)
- `pa_projects_count` (INTEGER)
- `cdbg_dr_allocation` (REAL)

This structure enables fine-grained analysis of disaster assistance and spending across time, geography, and incident type.
