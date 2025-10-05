import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse

# LangChain / OpenAI (swap model or provider if you want)
from langchain_openai import ChatOpenAI

# Import from helpers
from helpers import (
    FORM_HTML,
    RunSummary,
    compute_priorities,
    generate_results_html,
    generate_visualization_html,
    load_run,
    persist_run,
    prompt_layer_to_json,
)

# ------------------------------------------------------------------------------
# Config & Setup
# ------------------------------------------------------------------------------
load_dotenv(override=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY env var.")

llm = ChatOpenAI(model=MODEL, api_key=OPENAI_API_KEY, temperature=0)

app = FastAPI(title="SWOT DCIF Engine (v2)")

DATA_DIR = Path("swot_data")
DATA_DIR.mkdir(exist_ok=True)

CSV_FILE = DATA_DIR / "swot_runs.csv"


# ------------------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home():
    return FORM_HTML


@app.post("/analyze", response_class=HTMLResponse)
def analyze(
    company_name: str = Form(...),
    desired_outcomes: str = Form(...),
    layer_canonical: str = Form(""),
    layer_corpus: str = Form(""),
    layer_transactional: str = Form(""),
    strengths: str = Form(""),
    weaknesses: str = Form(""),
    opportunities: str = Form(""),
    threats: str = Form(""),
):
    # Parse canonical quadrant seeds (optional)
    canonical_seed = {
        "strengths": [s.strip() for s in strengths.splitlines() if s.strip()],
        "weaknesses": [s.strip() for s in weaknesses.splitlines() if s.strip()],
        "opportunities": [s.strip() for s in opportunities.splitlines() if s.strip()],
        "threats": [s.strip() for s in threats.splitlines() if s.strip()],
    }

    # If a layer is empty, provide a minimal nudge so the LLM returns []
    def safe_text(txt: str, fallback: str) -> str:
        return txt.strip() if txt.strip() else fallback

    canonical_out = prompt_layer_to_json(
        llm,
        "Canonical", company_name, desired_outcomes,
        safe_text(layer_canonical, "No canonical notes provided."),
        canonical_seed
    )
    corpus_out = prompt_layer_to_json(
        llm,
        "Corpus", company_name, desired_outcomes,
        safe_text(layer_corpus, "No corpus notes provided."),
        canonical_seed={}
    )
    transactional_out = prompt_layer_to_json(
        llm,
        "Transactional", company_name, desired_outcomes,
        safe_text(layer_transactional, "No transactional notes provided."),
        canonical_seed={}
    )

    priorities = compute_priorities(canonical_out, corpus_out, transactional_out)

    run_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}_{company_name.replace(' ', '_')}"
    summary = RunSummary(
        run_id=run_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        company=company_name,
        desired_outcomes=desired_outcomes,
        canonical=canonical_out,
        corpus=corpus_out,
        transactional=transactional_out,
        priorities=priorities
    )
    persist_run(summary, DATA_DIR, CSV_FILE)

    # Generate visualization
    viz_html = generate_visualization_html(summary)

    # Generate complete results page
    html = generate_results_html(summary, viz_html)
    return HTMLResponse(html)


@app.get("/api/result", response_class=JSONResponse)
def api_result(id: str = Query(..., description="Run ID of the analysis")):
    run = load_run(id, DATA_DIR)
    if not run:
        return JSONResponse({"error": "Run ID not found."}, status_code=404)
    return JSONResponse(run.model_dump())


# ------------------------------------------------------------------------------
# Local Dev Entrypoint
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Starting SWOT DCIF Engine (v2) with Enhanced Visualization")
    print("-> http://localhost:8000")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
