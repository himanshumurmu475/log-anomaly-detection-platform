# Log-Based Anomaly Detection Platform

A backend system for ingesting, storing, analyzing, and detecting anomalies in application and server logs.

The platform provides REST APIs for log ingestion, filtering, analytics, time-based anomaly detection, and system health monitoring.



## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** PostgreSQL (Supabase)
- **ORM:** SQLAlchemy
- **Database Driver:** Psycopg
- **Validation:** Pydantic
- **API Documentation:** Swagger / OpenAPI
- **Anomaly Detection:** Threshold-based detection, moving average, time-bucket analysis


## Features

- Single and bulk log ingestion
- Log storage in PostgreSQL
- Log filtering by level and service
- Time-range filtering
- Pagination for log retrieval
- Log analytics by level and service
- Time-bucket analysis
- Threshold-based anomaly detection
- Moving-average anomaly detection
- Database-backed anomaly analysis
- API health monitoring
- Interactive Swagger/OpenAPI documentation


## Architecture

```text
Client / Log Producer
        |
        v
   FastAPI REST API
        |
        +------------------+
        |                  |
        v                  v
   Log Ingestion      Analytics API
        |                  |
        v                  v
    SQLAlchemy      Anomaly Detection
        |
        v
 PostgreSQL (Supabase)



 ## API Endpoints

### Logs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/logs/` | Create a single log |
| POST | `/logs/bulk` | Create multiple logs |
| GET | `/logs/` | Retrieve logs with filtering and pagination |

### Analytics

| Method | Endpoint | Description |
|---|---|---|
| GET | `/analytics/summary` | Log counts by level |
| GET | `/analytics/by-service` | Log counts by service and level |
| GET | `/analytics/overview` | Overall log statistics |
| GET | `/analytics/anomaly-check` | Threshold-based anomaly detection |
| POST | `/analytics/moving-average-test` | Moving-average anomaly detection |
| GET | `/analytics/bucket-anomaly` | Time-bucket anomaly detection |

### Health

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | API and database health check |

Interactive API documentation is available through Swagger at `/docs`.



## Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd log-anomaly-detection-platform


### 2. Create a virtual environment

python -m venv venv

Activate it on Windows:
venv\Scripts\activate

### 3. Install dependencies

pip install -r requirements.txt


### 4. Configure the database

DATABASE_URL=your_supabase_postgresql_connection_string

### 5. Start the backend

uvicorn app.main:app --reload

     
    API will be available at:  http://127.0.0.1:8000

    Swagger documentation: http://127.0.0.1:8000/docs




## Anomaly Detection

The platform uses multiple approaches to identify unusual log activity.

### 1. Threshold Detection

A log count is considered anomalous when it exceeds a configured threshold.

if current_count > threshold:
    anomaly = true


### 2. Moving Average Detection
The current value is compared with the historical average.

if current_value > historical_average × multiplier:
    anomaly = true


### 3. Time-Bucket Detection
Logs are grouped into fixed time intervals such as 5-minute buckets.
The latest bucket is compared against the average of previous buckets.

For example:
Historical buckets: 1, 1, 1
Average:            1
Multiplier:         2
Threshold:          2
Current bucket:     4

4 > 2 → Anomaly detected