# ERA5 Monthly Means Climate Chatbot

A Python-based chatbot that retrieves climate data for South Asian countries from a SQLite database and provides human-like responses using the ClimateGPT API. The application uses the MCP (Model Context Protocol) framework for server-client communication and is containerized with Docker for easy deployment.

## Features

- **Climate Data Access**: Query environmental data (e.g., temperature, ozone, precipitation) for cities in seven South Asian countries: India, Pakistan, Bangladesh, Nepal, Afghanistan, Sri Lanka, and Bhutan.
- **Natural Language Processing**: Extracts metrics, cities, and dates from user questions using fuzzy matching and Geopy for city validation.
- **Humanized Responses**: Integrates with the ClimateGPT API to generate clear, informative, and friendly responses.
- **Dockerized Workflow**: Uses Docker and Docker Compose for consistent setup and deployment.
- **Testing Suite**: Includes unit tests for server and client functionality using pytest.

## Repository Structure

- `Dockerfile`: Defines the Docker image for the application, using Python 3.12-slim and installing dependencies.
- `docker-compose.yml`: Configures the Docker service for the chatbot, mounting the database and setting environment variables.
- `requirements.txt`: Lists Python dependencies (`mcp`, `requests`, `python-dotenv`, `geopy`).
- `era5server.py`: MCP server that handles database queries (list tables, query table, get sample data).
- `era5client.py`: MCP client that processes user questions, generates SQL queries, and integrates with ClimateGPT API.
- `era5test.py`: Test suite for server and client functionality using pytest and unittest.mock.
- `south_asia_monthly_new.db`: Preprocessed SQLite database containing climate data for South Asian countries (not included in the repository; see Setup).
- `auth.env`: Environment file for API credentials (not included in the repository; see Setup).
- `south_asia_monthly_new.db`: Preprocessed database used in the project.
- `Data Preprocessing/data_0.nc`: File contains raw data including city, date, latitude, longitude, high vegetation cover, surface pressure, total ozone, wind speed, and skin temperature, which can be preprocessed for analysis or modeling.
- `Data Preprocessing/data_1.nc`: File contains raw data including city, date, latitude, longitude, UV radiation, snowfall, net thermal radiation, total precipitation, convective rain rate, mean evaporation rate, mean moisture divergence, and mean precipitation rate, suitable for preprocessing and analysis.
- `Data Preprocessing/ERA5_preprocessing.ipynb`: Jupyter Notebook that contains all the steps to convert the raw nc data into structures SQLite DB.
  
**Note**: The `auth.env` file is not included in the repository due to sensitive data. You must create this file locally.

## Prerequisites

- Docker and Docker Compose
- Python 3.12 (optional, for local development without Docker)
- SQLite3 (included in the Docker image)
- Access to the ClimateGPT API (requires API credentials)

## Setup

1. **Cloning only ERA5_Monthly_Means folder from the repository: **

   ```bash
   git init climate-chatbot
   cd climate-chatbot
   git remote add origin https://github.com/newsconsole/GMU_DAEN_2025_01_C.git
   git sparse-checkout init --cone
   git sparse-checkout set ERA5_Monthly_Means
   git pull origin main
   ```

2. **Create** `auth.env`Create a file named `auth.env` in the project root with the following content:

   ```
   API_USER=your_api_user
   API_KEY=your_api_key
   ```

   Replace `your_api_user` and `your_api_key` with your ClimateGPT API credentials. This file is gitignored and should not be pushed to the repository.

3. **Obtain the Database**The `south_asia_monthly_new.db` file contains preprocessed climate data for India, Pakistan, Bangladesh, Nepal, Afghanistan, Sri Lanka, and Bhutan. You need to:

   - Download or generate this database (contact the project maintainer for access or instructions).
   - Place it in the project root directory.

4. **Install Dependencies (Optional, for Local Development**)If running without Docker, install the required Python packages:

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
   python era5server.py
   ```

2. In a separate terminal, run the client:

   ```bash
   python era5client.py
   ```

3. Enter questions in the client terminal and type `exit` to quit.

## Usage

- **Example Questions**:
  - "What was the skin temperature in Delhi in April 2022?"
  - "Compare total ozone and wind speed in Mumbai and Karachi."
  - "What is the total precipitation in Kathmandu in 2020?"
- The chatbot extracts metrics, cities, and dates, queries the database, and returns a response via ClimateGPT.
- Output includes the response and query details (table, metric, city, year, month).

## Database Schema

The `south_asia_monthly_new.db` contains 14 tables:

- **df0_tables** (e.g., `india_df0`, `pakistan_df0`): Columns include `City`, `date`, `latitude`, `longitude`, `high_vegetation_cover`, `surface_pressure`, `total_ozone`, `wind_speed`, `skin_temperature`.
- **df1_tables** (e.g., `india_df1`, `pakistan_df1`): Columns include `City`, `date`, `latitude`, `longitude`, `uv_radiation`, `snowfall`, `net_thermal_radiation`, `total_precipitation`, `convective_rain_rate`, `mean_evaporation_rate`, `mean_moisture_divergence`, `mean_precipitation_rate`.

Each table corresponds to a South Asian country, with monthly climate data.

## Testing

Run the test suite using pytest:

```bash
pytest era5test.py -v
```

The tests cover:

- Server functions (`list_tables`, `query_table`, `get_sample_data`).
- Client functions (`extract_metrics`, `extract_dates`, `find_tables_with_city`, `extract_city_with_geopy`, `generate_query`, `get_climategpt_response`, `process_question`).

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For questions or issues, please open an issue on GitHub or contact the project maintainer.
