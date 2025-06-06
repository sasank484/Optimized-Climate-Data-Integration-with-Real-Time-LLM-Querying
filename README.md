# Optimized-Climate-Data-Integration-with-Real-Time-LLM-Querying

This project is a comprehensive suite of Python-based, containerized applications designed to analyze climate and disaster-related data using structured SQLite databases, natural language processing (NLP), and integration with the **ClimateGPT API**. The suite includes four modules: **NOAA Billion Dollar**, **Disaster Dollar**, **ERA5 Monthly Means**, and **EDGAR GHG Emissions**. Each module supports querying specific datasets, processing natural language questions, and delivering human-like responses through a Model Context Protocol (MCP) framework. The system is fully Dockerized for seamless setup, deployment, and scalability.

---

## 🚀 Features

- **Disaster Data Analysis**:
  - Query historical U.S. disaster data (NOAA) including disaster types, dates, locations, and economic impacts.
  - Analyze FEMA and HUD financial assistance metrics (e.g., IHP totals, PA totals, CDBG-DR allocations).
  - Access time-series disaster cost per capita data (1980–2024).

- **Climate Data Access**:
  - Retrieve environmental data (e.g., temperature, ozone, precipitation) for South Asian countries (India, Pakistan, Bangladesh, Nepal, Afghanistan, Sri Lanka, Bhutan).
  - Query greenhouse gas (GHG) emissions (CO₂, CH₄, N₂O, F-gases) for over 200 countries from the EDGAR dataset.

- **Natural Language Processing**:
  - Parse user queries for filters like years, locations, incident types, or metrics using SpaCy, regex, fuzzy matching, and Geopy.
  - Generate human-readable responses via ClimateGPT integration.

- **Dockerized Architecture**:
  - Fully containerized with Docker and Docker Compose for consistent setup and deployment.
  - Includes health checks to ensure database readiness.

- **Extensible Design**:
  - Modular MCP-based server-client architecture for easy integration of new datasets or NLP modules.
  - Testing suites (e.g., pytest) for robust development.

---

## 🧱 Modules Overview

### 1. NOAA Billion Dollar
Analyzes historical U.S. disaster data from NOAA, including disaster types, economic impacts, and cost per capita (1980–2024).

- **Key Components**:
  - MCP server for querying the disaster database.
  - MCP client for user interaction.
  - Jupyter Notebook for data preprocessing and visualization.
  - SQLite database with disaster records.
  - CSV file with cost per capita time series.

- **Example Queries**:
  - "Number of disaster events in 2015."
  - "Economic impact of hurricanes in Texas."

### 2. Disaster Dollar
Queries FEMA and HUD financial assistance data for U.S. disasters, supporting filters like state, incident type, and year.

- **Key Components**:
  - MCP server for querying the financial assistance database.
  - NLP-based client with ClimateGPT integration.
  - SQLite database with financial metrics.

- **Example Queries**:
  - "What was the IHP total for Texas hurricanes in 2012?"
  - "List tornado incidents in Florida from 2005 to 2010."

### 3. ERA5 Monthly Means
Retrieves climate data (e.g., temperature, precipitation) for South Asian countries, with fuzzy matching for city names.

- **Key Components**:
  - MCP server for querying the climate database.
  - MCP client with NLP and ClimateGPT integration.
  - Pytest suite for testing.
  - SQLite database with climate data.
  - Preprocessing notebook for raw `.nc` files.

- **Example Queries**:
  - "Skin temperature in Delhi in April 2022."
  - "Total precipitation in Kathmandu in 2020."

### 4. EDGAR GHG Emissions
Queries GHG emissions (CO₂, CH₄, N₂O, F-gases) for over 200 countries from the EDGAR dataset.

- **Key Components**:
  - MCP server for querying gas-specific databases.
  - MCP client with ClimateGPT integration.
  - SQLite databases for emissions data.

- **Example Queries**:
  - "CO₂ emissions in Brazil in 2020."
  - "Methane emissions in India in 2015."

---

## 📊 Database Schemas

### NOAA Billion Dollar
- **Disaster Database**:
  - Columns: `event_type` (TEXT), `year` (INTEGER), `location` (TEXT), `economic_impact` (REAL), etc.
- **Cost Per Capita CSV**:
  - Columns: `year` (INTEGER), `cost_per_capita` (REAL).

### Disaster Dollar
- **Financial Assistance Database** (table: `disaster_dollar_db`):
  - Columns: `state` (TEXT), `incident_type` (TEXT), `year` (INTEGER), `event` (TEXT), `incident_number` (TEXT), `valid_ihp_applications` (INTEGER), `eligible_ihp_applications` (INTEGER), `ihp_total` (REAL), `pa_total` (REAL), `pa_projects_count` (INTEGER), `cdbg_dr_allocation` (REAL).

### ERA5 Monthly Means
- **Climate Database**:
  - **df0_tables** (e.g., `india_df0`): `City` (TEXT), `date` (TEXT), `latitude` (REAL), `longitude` (REAL), `high_vegetation_cover` (REAL), `surface_pressure` (REAL), `total_ozone` (REAL), `wind_speed` (REAL), `skin_temperature` (REAL).
  - **df1_tables** (e.g., `india_df1`): `City` (TEXT), `date` (TEXT), `latitude` (REAL), `longitude` (REAL), `uv_radiation` (REAL), `snowfall` (REAL), `net_thermal_radiation` (REAL), `total_precipitation` (REAL), `convective_rain_rate` (REAL), `mean_evaporation_rate` (REAL), `mean_moisture_divergence` (REAL), `mean_precipitation_rate` (REAL).

### EDGAR GHG Emissions
- **Emissions Databases** (table: `emissions`):
  - Columns: `Name` (TEXT), `Substance` (TEXT), `IPCC_Annex` (TEXT), `Country_code_A3` (TEXT), `1970–2023` (REAL, annual emissions in kilotons).

---

## ⚙️ Prerequisites

- **Docker and Docker Compose**: Required for containerized deployment.
- **Python 3.11 or 3.12**: Optional for local development without Docker.
- **SQLite3**: Included in Docker images.
- **ClimateGPT API Access**: Requires API credentials from Erasmus.AI.

---

## 🛠️ Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/newsconsole/GMU_DAEN_2025_01_C.git
   cd GMU_DAEN_2025_01_C
   ```

2. **Create `auth.env` for Each Module**:
   Create an `auth.env` file in the root of each module directory (`NOAA_Billion_Dollar`, `Disaster_Dollar`, `ERA5_Monthly_Means`, `GHG_Emissions`) with:
   ```env
   CLIMATEGPT_USERNAME=your_username
   CLIMATEGPT_PASSWORD=your_password
   ```
   or for ERA5 and GHG:
   ```env
   API_USER=your_api_user
   API_KEY=your_api_key
   ```
   Replace placeholders with your ClimateGPT API credentials. These files are gitignored.

3. **Obtain Databases**:
   - Ensure the following SQLite databases are placed in their respective module directories:
     - `NOAA_Billion_Dollar/disaster_data.db`
     - `Disaster_Dollar/disaster_fema_hud.db`
     - `ERA5_Monthly_Means/south_asia_monthly_new.db`
     - `GHG_Emissions/co2_emissions.db`, `methane_emissions.db`, `N2o_emissions.db`, `Flourinated_gas_emissions.db`
   - These may be included in the repository or require download (contact the project maintainer).

4. **Install Dependencies (Optional, for Local Development)**:
   Navigate to each module directory and run:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Running the Application

### Using Docker (Recommended)

For each module, navigate to its directory and run:
```bash
docker-compose up --build
```
Then, for client interaction (except NOAA Billion Dollar):
```bash
python client.py  # or era5client.py, EDGARclient.py
```
For NOAA Billion Dollar:
```bash
python new_disaster_c.py
```
To stop:
```bash
docker-compose down
```

### Without Docker

1. Start the MCP server for the desired module:
   ```bash
   cd NOAA_Billion_Dollar && python server.py
   # or
   cd Disaster_Dollar && python server.py
   # or
   cd ERA5_Monthly_Means && python era5server.py
   # or
   cd GHG_Emissions && python emissions_mcp.py
   ```

2. In a separate terminal, run the client:
   ```bash
   python new_disaster_c.py  # NOAA Billion Dollar
   # or
   python client.py          # Disaster Dollar
   # or
   python era5client.py      # ERA5 Monthly Means
   # or
   python EDGARclient.py     # EDGAR GHG Emissions
   ```

3. Interact via the terminal. Type `exit` to quit.

---

## 💡 Example Queries

- **NOAA Billion Dollar**:
  - "How many floods occurred in 2010?"
  - "What was the economic impact of hurricanes in Florida?"

- **Disaster Dollar**:
  - "What was the IHP total for California earthquakes in 2019?"
  - "Show tornado incidents in Texas between 2000 and 2010."

- **ERA5 Monthly Means**:
  - "What was the wind speed in Mumbai in June 2021?"
  - "Compare precipitation in Dhaka and Colombo in 2020."

- **EDGAR GHG Emissions**:
  - "What were the CO₂ emissions in China in 2018?"
  - "Methane emissions in Brazil from 2015 to 2020."

---

## 🧪 Testing

For the ERA5 Monthly Means module, run:
```bash
cd ERA5_Monthly_Means
pytest era5test.py -v
```
Tests cover server and client functions like query generation and NLP parsing. Other modules can be extended with similar pytest suites.

---

## 🔐 Security Notes

- **API Credentials**: Store ClimateGPT credentials in `auth.env` files and ensure they are not committed to the repository.
- **Database Access**: Databases may contain sensitive data; handle them securely and follow project maintainer instructions for access.

---
