# InsightBoard AI Executive Performance Narrator

Production-grade starter repository for turning structured KPI data into executive-ready business narratives.

## Current phase

The project is now through:

- **Phase 1: System Architecture & Data Modeling**
- **Phase 2: Data Ingestion & Preprocessing (Pandas)**
- **Phase 6: Multimodal LLM Integration**
- **Phase 10: Frontend Implementation**
- **Phase 11: Deployment & Containerization**

The repository now enforces a canonical long-format CSV contract and preprocesses real-world KPI time series before analytics and narrative generation.

- Canonical CSV shape: `date`, `metric_name`, `value`
- Workflow: `Ingestion -> Processing -> Visualization -> Prompt Assembly -> LLM Inference -> Output`
- Cleaning: datetime normalization, exact duplicate removal, missing-value imputation, weekly/monthly bucketing

## What this project is for

Business analytics teams often spend hours every month turning dashboards into leadership commentary. This repository provides the starting point for an application that:

- accepts structured KPI CSV uploads,
- detects trend shifts and anomalies,
- generates executive summaries,
- prepares chart-to-text explanation hooks for multimodal workflows,
- recommends concrete follow-up actions.

## Current repository scope

This first version gives you a strong backend scaffold rather than a finished AI product. It includes:

- FastAPI service with health and report-generation endpoints,
- contract endpoints for input schema and workflow inspection,
- CSV ingestion, preprocessing, and KPI profiling,
- heuristic anomaly detection,
- trend-based narrative generation,
- chart explanation placeholder for future multimodal model support,
- optional OpenAI Responses API and Gemini SDK adapters for multimodal narration,
- vanilla HTML/CSS/JS frontend served directly by FastAPI,
- test fixtures and baseline pytest coverage,
- Docker-ready packaging.

## Repository structure

```text
app/
  api/            FastAPI routes
  core/           settings and logging
  models/         response schemas
  services/       ingestion, analytics, anomaly detection, narrative pipeline
  prompts/        prompt artifacts for future LLM adapters
docs/             architecture notes
tests/            fixtures and baseline tests
scripts/          local development helpers
```

## Quick start

### 1. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -e .[dev,llm]
```

### 3. Run the API

```powershell
python -m uvicorn app.main:app --reload
```

Or use:

```powershell
.\scripts\run_dev.ps1
```

### 4. Run tests

```powershell
pytest
```

## API endpoints

### Health

`GET /api/v1/health`

### Generate report

`POST /api/v1/reports/generate`

Also available as:

`POST /api/v1/generate-report`

Multipart form fields:

- `csv_file`: required CSV upload
- `report_title`: optional string
- `aggregation_granularity`: `weekly` or `monthly`
- `missing_value_strategy`: `drop`, `forward_fill`, or `interpolate`
- `chart_image`: optional image upload for multimodal chart explanation workflows
- `persona`: optional executive framing (`cfo`, `coo`, `cro`, `analyst`, `operations`)

Expected CSV header:

```text
date,metric_name,value
```

### Input contract

`GET /api/v1/contracts/input-schema`

### Workflow definition

`GET /api/v1/contracts/workflow`

## Example response shape

```json
{
  "report_title": "Monthly Executive Performance Summary",
  "records_analyzed": 36,
  "periods_analyzed": 6,
  "date_column": "date",
  "preprocessing_summary": {
    "aggregation_granularity": "monthly",
    "missing_value_strategy": "forward_fill",
    "rows_received": 36,
    "exact_duplicate_rows_removed": 0,
    "date_metric_duplicates_collapsed": 0,
    "missing_values_detected": 0,
    "missing_values_imputed": 0,
    "output_periods_generated": 6
  },
  "executive_summary": "Monthly Executive Performance Summary covers 6 KPI(s)...",
  "trend_narrative": [
    "revenue closed at 520000.00..."
  ],
  "anomaly_commentary": [
    "revenue is flagged as medium severity..."
  ],
  "recommended_actions": [
    "Investigate the drivers behind the flagged anomalies before the next reporting cycle."
  ]
}
```

## Suggested next milestones

1. Add authentication, audit logging, and request tracing.
2. Persist generated reports and user feedback for iteration loops.
3. Add background job execution for long-running report requests.
4. Expand evaluation datasets and regression tests for narrative quality.
5. Add production infrastructure manifests for your target cloud environment.

## Frontend

The app now serves a lightweight frontend at:

```text
GET /
```

It provides:

- CSV upload and optional chart upload
- persona, aggregation, and missing-value controls
- loading and error states
- dynamic rendering of executive summary, anomalies, actions, and trend narrative
- direct display of returned Base64 chart images

## Multimodal providers

Set one of these in `.env` to enable live model calls:

```text
INSIGHTBOARD_DEFAULT_LLM_PROVIDER=openai
INSIGHTBOARD_OPENAI_API_KEY=...
INSIGHTBOARD_OPENAI_MODEL=gpt-4.1-mini
```

or

```text
INSIGHTBOARD_DEFAULT_LLM_PROVIDER=gemini
INSIGHTBOARD_GEMINI_API_KEY=...
INSIGHTBOARD_GEMINI_MODEL=gemini-2.5-flash
```

When a chart image is available, the app now forwards it with the prompt:

- OpenAI: as an `input_image` part using a `data:image/...;base64,...` URL
- Gemini: as an image part using inline Base64-backed bytes

## Deployment

### Environment file

Create a real `.env` from the example:

```powershell
Copy-Item .env.example .env
```

Populate the provider secrets you want to use:

```text
INSIGHTBOARD_DEFAULT_LLM_PROVIDER=openai
INSIGHTBOARD_OPENAI_API_KEY=your_real_key
```

or

```text
INSIGHTBOARD_DEFAULT_LLM_PROVIDER=gemini
INSIGHTBOARD_GEMINI_API_KEY=your_real_key
```

### Docker build

```powershell
docker build -t insightboard-ai .
```

### Docker run

```powershell
docker run --env-file .env -p 8000:8000 insightboard-ai
```

The production container uses:

- a multi-stage `Dockerfile`
- `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- non-root runtime user
- runtime image system libraries for Matplotlib and Pillow-backed image handling

### Docker Compose

```powershell
docker compose up --build
```

Then open:

```text
http://localhost:8000/
```

## Tech stack

- Python
- FastAPI
- Pandas
- Matplotlib-ready workflow
- LLM integration abstraction
- Pytest
