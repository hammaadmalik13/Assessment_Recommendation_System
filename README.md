<<<<<<< HEAD
# SHL Conversational Assessment Recommender

FastAPI service implementing a stateless conversational recommender for SHL assessments.

## Endpoints

- `GET /health` -> `{"status":"ok"}`
- `POST /chat` -> strict schema:
  - `reply: string`
  - `recommendations: [] or 1..10 items`
  - `end_of_conversation: boolean`

## Quick Start

1. Create and activate virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Run API:
   - `uvicorn app.main:app --reload`
4. Run tests:
   - `pytest -q`

## Chat Request Example

```json
{
  "messages": [
    {"role":"user","content":"Hiring a Java developer"},
    {"role":"assistant","content":"What seniority level?"},
    {"role":"user","content":"Mid-level with 4 years"}
  ]
}
```

## Local Evaluation

Use:

- `python scripts/eval_local.py --trace-file path/to/traces.json --base-url http://127.0.0.1:8000`

## Catalog Data

- Current runtime catalog file: `data/processed/catalog.json`
- Optional scraper:
  - `python scripts/scrape_catalog.py`

> Note: scraper output may need manual enrichment (description/tags/levels) for better recommendation quality.

=======
# Assessment_Recommendation_System
>>>>>>> dd6b111f4fc4eb76528be3a0d86aa0c064e552c3
