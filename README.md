# YouTube ELT Data Pipeline

> An end-to-end ELT (Extract, Load, Transform) data pipeline built with Apache Airflow. This project extracts YouTube channel video analytics via YouTube Data API v3, loads raw JSON data into a staging PostgreSQL database, transforms and models the data into a core warehouse layer, executes automated data quality checks via Soda Core, and incorporates CI/CD and pytest automated testing.

---

## 🏗️ Project Architecture & Pipeline Workflow

The pipeline is modularized into three decoupled DAGs triggered in sequence using `TriggerDagRunOperator`:

```text
┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐
│   DAG 1: produce_json  │ ───► │    DAG 2: update_db    │ ───► │  DAG 3: data_quality   │
└────────────────────────┘      └────────────────────────┘      └────────────────────────┘
```

*   **`produce_json` (Extraction)**
    *   Fetches channel upload playlist ID and video IDs from **YouTube Data API v3**.
    *   Extracts metrics (title, publish date, view count, like count, comment count, duration).
    *   Saves raw payload locally as `./data/YT_data_{date}.json`.
    *   Triggers `update_db`.

*   **`update_db` (Data Warehouse Loading & Transformation)**
    *   **Staging Layer (`staging` schema):** Reads JSON payload and bulk inserts raw records into PostgreSQL.
    *   **Core Layer (`core` schema):** Transforms raw data (date parsing, duration formatting, metrics casting) and upserts/updates dimensional and fact tables.
    *   Triggers `data_quality`.

*   **`data_quality` (Data Validation)**
    *   Runs **Soda Core** (`soda scan`) tests against both `staging` and `core` schemas using predefined YAML check rules (`checks.yml`).

---

## 📁 Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── ci-cd_yt-elt.yaml    # CI/CD Pipeline (Linting, Testing, Build Check)
├── dags/
│   ├── api/
│   │   └── video_stats.py       # Tasks for fetching data via YouTube API
│   ├── dataquality/
│   │   └── soda.py              # Soda data quality validation tasks
│   ├── datawarehouse/
│   │   ├── data_loading.py      # Staging layer database ingestion
│   │   ├── data_modification.py # Data mutation & upsert utilities
│   │   ├── data_transformation.py # Business transformation logic
│   │   ├── data_utils.py        # Database connection & SQL helper utilities
│   │   └── dwh.py               # DW tasks wrapper
│   └── main.py                  # Airflow DAG definitions & dependencies
├── data/                        # Extracted raw JSON files storage
├── docker/
│   └── postgres/
│       └── init-multiple-databases.sh # Database initialization script
├── include/
│   └── soda/
│       ├── checks.yml           # Soda data quality rules
│       └── configuration.yml    # Soda datasource connection configuration
├── tests/
│   ├── conftest.py              # Pytest fixtures & mock environment setup
│   ├── integration_test.py      # Integration tests for end-to-end pipeline
│   └── unit_test.py             # Unit tests for API extraction & transformation
├── docker-compose.yaml          # Local environment deployment (Airflow + Postgres)
├── Dockerfile                   # Custom Airflow image definition
├── requirements.txt             # Python dependencies
└── video_stats.json             # Sample raw data payload
```

---

## 🛠️ Tech Stack & Tools

*   **Orchestration:** Apache Airflow 2.x (TaskFlow API + Operators)
*   **Database / Data Warehouse:** PostgreSQL (Multi-schema: `staging`, `core`)
*   **Data Quality:** Soda Core (`soda-core-postgres`)
*   **Testing:** Pytest, Unittest Mock
*   **CI/CD:** GitHub Actions
*   **Containerization:** Docker & Docker Compose

---

## 🚀 Getting Started (Local Setup)

### Prerequisites

*   Docker Engine and Docker Compose installed.
*   A valid YouTube Data API Key.

### 1. Environment Configuration

Create a `.env` file or configure Airflow Variables via UI/CLI:

```env
API_KEY=your_youtube_api_key_here
CHANNEL_HANDLE=@your_target_channel_handle
```

### 2. Launch Environment via Docker Compose

Build and spin up the Airflow scheduler, webserver, and Postgres database:

```bash
docker-compose up -d --build
```

Access the Airflow Web UI at `http://localhost:8080` (Default credentials: `airflow` / `airflow`).

### 3. Set Up Airflow Variables

Navigate to **Admin -> Variables** in the Airflow UI and add:

*   **`API_KEY`**: Your YouTube API Key
*   **`CHANNEL_HANDLE`**: Target YouTube Handle (e.g., `@mkbhd`)

---

## 🧪 Testing & Data Quality

### Running Unit & Integration Tests

To run pytest locally inside your virtual environment or docker container:

```bash
pytest tests/
```

*   `unit_test.py`: Mocks YouTube API responses and verifies data parsing/transformation functions.
*   `integration_test.py`: Validates schema creation and database insertion logic.

### Data Quality Checks (Soda Core)

Soda Core scans the database automatically in the `data_quality` DAG. You can also manually run a scan using CLI:

```bash
soda scan -d pg_datasource -c include/soda/configuration.yml -v SCHEMA=core include/soda/checks.yml
```

---

## 🔄 CI/CD Pipeline

The repository includes a GitHub Actions workflow (`.github/workflows/ci-cd_yt-elt.yaml`) that triggers on `push` or `pull_request` to `main` branches:

*   **Code Linting:** Checks Python code quality using `flake8` / `black`.
*   **Automated Testing:** Runs `pytest` suite with mocked external calls to prevent breaking changes.
*   **Build Check:** Ensures Docker environment builds cleanly without missing packages.
