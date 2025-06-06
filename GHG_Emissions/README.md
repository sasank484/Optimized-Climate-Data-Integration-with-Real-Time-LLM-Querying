# 🌍 EDGAR GHG Emissions Module

A containerized MCP-based emissions query system that allows users to retrieve greenhouse gas (GHG) emissions data from preprocessed EDGAR datasets. The system supports natural language questions and delivers human-like responses by integrating with the **ClimateGPT** API.

---

## 🚀 Features

- **Multi-Gas Emissions Access**: Query emissions for CO₂, CH₄, N₂O, and Fluorinated gases from over 200 countries.
- **Natural Language Question Parsing**: Parses country names, gas types, and years from questions (e.g., “What is the methane emission in India in 2020?”).
- **ClimateGPT Integration**: Converts structured emissions data into user-friendly explanations using the ClimateGPT LLM.
- **Model Context Protocol (MCP)**: Connects client and server using lightweight `stdio`-based protocol.
- **Dockerized Setup**: Easily deployable in any environment via Docker and Docker Compose.

---

## 📁 Repository Structure

```
GHG_Emissions/
├── Data Preprocessing/
│   ├── CO2_Emissions_-2.ipynb
│   ├── CH4_Emissions_-2.ipynb
│   ├── N2O_emissions.ipynb
│   ├── flourinated_emissions_.ipynb
│   └── [Raw Excel files for each gas]
├── co2_emissions.db
├── methane_emissions.db
├── N2o_emissions.db
├── Flourinated_gas_emissions.db
├── emissions_mcp.py          ← MCP server
├── EDGARclient.py            ← MCP client
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 🧱 MCP Modules

| File | Role |
|------|------|
| `emissions_mcp.py` | MCP server: handles gas-specific queries and routes them to the correct database |
| `EDGARclient.py`   | MCP client: parses question, queries the server, and integrates with ClimateGPT |
| `requirements.txt` | Lists all necessary Python packages |
| `Dockerfile`       | Sets up the server container |
| `docker-compose.yml` | Optional: coordinates multi-container setup |

---

## 🧪 Supported Emissions Gases

| Gas | Database | Description |
|-----|----------|-------------|
| CO₂ | `co2_emissions.db` | Carbon Dioxide |
| CH₄ | `methane_emissions.db` | Methane |
| N₂O | `N2o_emissions.db` | Nitrous Oxide |
| F-gases | `Flourinated_gas_emissions.db` | Fluorinated gases |

---

## 📊 Data Columns

Each database contains an `emissions` table with:

- `Name`: Country name
- `Substance`: Gas type
- `IPCC_Annex`, `Country_code_A3`
- `1970–2023`: Annual emissions values (in kilotons)

---

## ⚙️ Setup & Usage

### 🐳 Using Docker

```bash
docker-compose up --build
```

Then run the client:
```bash
python EDGARclient.py
```

### 💻 Without Docker

1. Start the server:
```bash
python emissions_mcp.py
```

2. Open a second terminal and run:
```bash
python EDGARclient.py
```

3. Ask a question:
```bash
What is the CO2 emission in Brazil in 2020?
```

---

## 🧠 ClimateGPT Integration

All responses are passed to [ClimateGPT](https://erasmus.ai/models/climategpt_8b_latest) with context, allowing natural, conversational answers backed by database facts.

---

## 🧪 Testing (Optional)

This module can be extended to support tests using `pytest` for functions like:

- `extract_inputs(question)`
- `query_table(database, table, sql)`

---

## 🔐 API Credentials (Optional)

If you're using secure API calls, include:
```env
API_USER=your_user
API_KEY=your_key
```
in a `.env` or `auth.env` file.

---

## 📜 License

This module is part of the ClimateGPT suite. Licensed under MIT.

---

## 🧑‍💻 Maintainers

For help, raise an issue or contact the maintainers on GitHub.
