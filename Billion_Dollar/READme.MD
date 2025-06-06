# NOAA Billion Dollar

This project leverages historical disaster data provided by the National Oceanic and Atmospheric Administration (NOAA) to analyze the impact of natural disasters across the United States. The data includes information on disaster types, dates, locations, and economic impact, and is complemented by a separate time series of cost per capita for disasters from 1980 to 2024. This system is built for querying and understanding disaster patterns.

## Features

- **Disaster Data Access**: Query historical disaster data (e.g., disaster type, date, location, economic impact) across the United States from an organized SQLite database.

- **Time Series Analysis**: Analyze trends in disaster-related costs per capita from 1980 to 2024 with easy-to-use CSV integration.
Natural Language-Ready Architecture: Designed to easily extend with NLP modules for user-friendly disaster-related queries.

- **Dockerized Workflow**: Fully containerized using Docker and Docker Compose to ensure seamless setup, deployment, and scaling across environments.

- **Health Check Monitoring**: Docker Compose health checks ensure that the database is ready before the client interacts with the server.

## Repository Structure

- `Dockerfile`: Defines the Docker image using Python 3.11-slim, installing MCP libraries and disaster data dependencies.

- `docker-compose.yml`: Configures two services (server and client), sets environment variables, maps volumes, and manages service health.

- `requirements.txt`: Lists Python dependencies (mcp, fastmcp, requests, spacy).

- `server.py`: MCP server that handles disaster data queries by interacting with the SQLite database (disaster_data.db).

- `new_disaster_c.py`: MCP client that connects to the server, sends disaster-related queries, and displays the received responses.

- `noaa_disaster_db.ipynb`: Jupyter Notebook for preprocessing, exploratory data analysis, and visualization of disaster trends and cost per capita.

- `disaster_data.db`: SQLite database containing structured U.S. disaster data records including event type, year, and economic impact.

- `time-series-US-cost-per-capita-1980-2024.csv`: CSV file providing yearly U.S. disaster cost per capita data from 1980 to 2024.

## Prerequisites

- Docker and Docker Compose
- Python 3.11 (optional, for local development without Docker)
- SQLite3 (included in the Docker image)
- Access to the ClimateGPT API (requires API credentials)

## Setup

1. Cloning Billion_Dollar folder from the repository: 
  ```bash
  git init noaa-disaster-analysis
  cd noaa-disaster-analysis
  git remote add origin https://github.com/your-username/noaa-disaster-analysis.git
  git pull origin main

  ```

2. Obtain the Database: The `disaster_data.db` file contains preprocessed historical U.S. disaster records.

You need to:

   - Ensure disaster_data.db is placed in the project root directory.
   - This file is included in the project repository. No additional download is needed.

3. Install Dependencies (Optional, for Local Development): If running without Docker, install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Using Docker

1. Build and run the Docker container:

   ```bash
   docker-compose up --build
   ```

2. The chatbot will start, and you can interact with it via the terminal.

3. To stop, press `Ctrl+C` and clean up:

   ```bash
   docker-compose down
   ```

### Without Docker

1. Start the MCP server:

   ```bash
   python server.py
   ```

2. In a separate terminal, run the client:

   ```bash
   python new_disaster_c.py
   ```

3. Enter questions in the client terminal and type `exit` to quit.

## Usage

- **Example use cases**:

- Query the number of disaster events in a given year or range of years.
- Retrieve total and per-capita economic impact of disasters over time.
- Analyze types of disasters (e.g., floods, hurricanes) and their frequency.
- Comparision of different disasters in a particular year or in different years.

