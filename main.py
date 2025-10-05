import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

# LangChain / OpenAI (swap model or provider if you want)
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

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
# Data Models
# ------------------------------------------------------------------------------

class SWOTItem(BaseModel):
    text: str
    impact: int = Field(ge=1, le=10, description="Business impact 1-10")
    sentiment: float = Field(ge=-1.0, le=1.0, description="Sentiment -1..1")


class LayerOutput(BaseModel):
    layer: str
    company: str
    desired_outcomes: str
    strengths: List[SWOTItem] = []
    weaknesses: List[SWOTItem] = []
    opportunities: List[SWOTItem] = []
    threats: List[SWOTItem] = []


class RunSummary(BaseModel):
    run_id: str
    timestamp: str
    company: str
    desired_outcomes: str
    canonical: LayerOutput
    corpus: LayerOutput
    transactional: LayerOutput
    priorities: Dict[str, Any]  # computed gap × impact per dimension


# ------------------------------------------------------------------------------
# HTML (Form + Results)
# ------------------------------------------------------------------------------

FORM_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>SWOT DCIF Engine (v2)</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 980px; margin: 0 auto; padding: 24px; background:#f7f7f7;}
    h1 { color:#222; }
    h2 { color:#444; margin-top:28px; }
    .card { background:#fff; border-radius:8px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.06); margin-bottom:20px; }
    label { display:block; font-weight:bold; margin:10px 0 6px; color:#333;}
    input[type=text], textarea { width:100%; padding:10px; border:1px solid #ddd; border-radius:6px; box-sizing:border-box; }
    textarea { min-height:90px; }
    .grid { display:grid; gap:12px; grid-template-columns: 1fr 1fr; }
    .btn { background:#2d7a46; color:#fff; border:none; padding:12px 18px; border-radius:6px; cursor:pointer; font-size:16px; }
    .btn:hover { background:#25663a; }
    .muted { color:#666; font-size:14px;}
    .small { font-size:12px; color:#777;}
    .status { display:none; margin-top:12px; padding:10px; border-radius:6px;}
    .loading { display:block; background:#fff3cd; color:#856404;}
    .error { display:block; background:#f8d7da; color:#721c24;}
  </style>
  <script>
    function onSubmit(evt){
      evt.preventDefault();
      const form = evt.target;
      const status = document.getElementById('status');
      status.className = 'status loading';
      status.textContent = 'Running DCIF analysis with AI…';
      const btn = document.getElementById('submitBtn');
      btn.disabled = true; btn.textContent = 'Analyzing…';

      const fd = new FormData(form);
      fetch('/analyze', { method:'POST', body: fd })
        .then(r => { if(!r.ok) throw new Error('Network error'); return r.text(); })
        .then(html => { document.open(); document.write(html); document.close(); })
        .catch(err => {
          status.className = 'status error';
          status.textContent = 'Error: ' + err.message;
          btn.disabled = false; btn.textContent = 'Analyze';
        });
    }
  </script>
</head>
<body>
  <h1>SWOT DCIF Engine (v2)</h1>
  <div class="card">
    <p class="muted">This version adds Canonical / Corpus / Transactional layers, structured JSON from the LLM, and a Gap × Impact priority model. It also exposes a JSON API for downstream dashboards.</p>
  </div>

  <form class="card" onsubmit="onSubmit(event)">
    <h2>Company</h2>
    <label>Company Name</label>
    <input type="text" name="company_name" required>
    <label>Desired Outcomes / KPIs</label>
    <textarea name="desired_outcomes" required placeholder="e.g., 30% YoY revenue growth, +10% forecast accuracy"></textarea>

    <h2>Three-Layer Inputs (free text)</h2>
    <div class="small">Provide short summaries for each layer (paste notes, bullet points, extracts). You can start with Canonical only—Corpus/Transactional are optional placeholders you can wire up later.</div>
    <label>Canonical (Internal Truth)</label>
    <textarea name="layer_canonical" placeholder="Playbooks, strategy docs, positioning…"></textarea>
    <label>Corpus (External Truth)</label>
    <textarea name="layer_corpus" placeholder="Market chatter, analyst notes, reviews, competitor messaging…"></textarea>
    <label>Transactional (Internal Reality)</label>
    <textarea name="layer_transactional" placeholder="Sales call patterns, objections, win/loss insights…"></textarea>

    <h2>(Optional) Canonical Quadrant Seed Inputs</h2>
    <div class="grid">
      <div>
        <label>Strengths (one per line)</label>
        <textarea name="strengths"></textarea>
      </div>
      <div>
        <label>Weaknesses (one per line)</label>
        <textarea name="weaknesses"></textarea>
      </div>
    </div>
    <div class="grid">
      <div>
        <label>Opportunities (one per line)</label>
        <textarea name="opportunities"></textarea>
      </div>
      <div>
        <label>Threats (one per line)</label>
        <textarea name="threats"></textarea>
      </div>
    </div>

    <div id="status" class="status"></div>
    <br>
    <button id="submitBtn" class="btn" type="submit">Analyze</button>
  </form>

  <div class="card">
    <p class="small">Tip: After a run, your JSON will be available at <code>/api/result?id=&lt;run_id&gt;</code> for visualization.</p>
  </div>
</body>
</html>
"""


# ------------------------------------------------------------------------------
# LLM Helpers
# ------------------------------------------------------------------------------

def prompt_layer_to_json(layer: str, company: str, desired_outcomes: str, raw_text: str,
                         canonical_seed: Dict[str, List[str]]) -> LayerOutput:
    """
    Ask the LLM to produce structured JSON for the given layer.
    The model should return concise SWOT items with impact (1-10) and sentiment (-1..1).
    """
    seed_note = ""
    if layer.lower() == "canonical" and any(canonical_seed.values()):
        seed_note = (
            "\nUse these optional seed items (from form quadrants) only if helpful, "
            "but do not exceed 6 items per quadrant:\n"
            f"- strengths_seed: {canonical_seed.get('strengths', [])}\n"
            f"- weaknesses_seed: {canonical_seed.get('weaknesses', [])}\n"
            f"- opportunities_seed: {canonical_seed.get('opportunities', [])}\n"
            f"- threats_seed: {canonical_seed.get('threats', [])}\n"
        )

    system = f"""
You are a strategy analyst. Convert raw notes for the '{layer}' layer of a company's SWOT into a compact JSON object.

Rules:
- For each quadrant (strengths, weaknesses, opportunities, threats), return 1-6 items max.
- Each item: concise 'text' (<= 60 words), integer 'impact' 1-10 (business leverage toward desired outcomes),
  and 'sentiment' between -1 and 1 (positive=good, negative=bad as appropriate for the quadrant).
- Stay grounded in the provided notes; no hallucination. If a quadrant has no evidence, return [].

Return ONLY valid JSON with keys: layer, company, desired_outcomes, strengths, weaknesses, opportunities, threats.
"""

    user = f"""
Company: {company}
Desired Outcomes: {desired_outcomes}

Layer: {layer}
Raw Notes:
{raw_text}

{seed_note}
"""
    # Log prompt (server console)
    print("\n" + "="*70)
    print(f"[LLM] Layer JSON → {layer}")
    print("="*70)
    print(user[:2000] + ("...\n" if len(user) > 2000 else "\n"))

    resp = llm.invoke([HumanMessage(content=system.strip()), HumanMessage(content=user.strip())])
    content = resp.content.strip()

    # Guard: try to coerce to JSON
    try:
        data = json.loads(content)
    except Exception:
        # If the model returned text, do a light salvage attempt by extracting json block
        try:
            start = content.index("{")
            end = content.rindex("}") + 1
            data = json.loads(content[start:end])
        except Exception as e:
            print("[LLM PARSE ERROR]", e)
            raise ValueError("LLM did not return valid JSON for layer " + layer)

    # Validate with Pydantic
    def coerce_items(items: Optional[List[Dict[str, Any]]]) -> List[SWOTItem]:
        if not items:
            return []
        fixed = []
        for it in items:
            # Defensive coercions
            impact = int(max(1, min(10, round(float(it.get("impact", 5))))))
            sentiment = float(max(-1.0, min(1.0, float(it.get("sentiment", 0)))))
            text = str(it.get("text", "")).strip()
            if text:
                fixed.append(SWOTItem(text=text, impact=impact, sentiment=sentiment))
        return fixed

    out = LayerOutput(
        layer=str(data.get("layer", layer)),
        company=company,
        desired_outcomes=desired_outcomes,
        strengths=coerce_items(data.get("strengths")),
        weaknesses=coerce_items(data.get("weaknesses")),
        opportunities=coerce_items(data.get("opportunities")),
        threats=coerce_items(data.get("threats")),
    )
    return out


# ------------------------------------------------------------------------------
# Scoring (Gap × Impact)
# ------------------------------------------------------------------------------

DIMENSIONS = ["strengths", "weaknesses", "opportunities", "threats"]


def _avg_impact(items: List[SWOTItem]) -> float:
    return float(sum(i.impact for i in items) / len(items)) if items else 0.0


def _avg_sentiment(items: List[SWOTItem]) -> float:
    return float(sum(i.sentiment for i in items) / len(items)) if items else 0.0


def compute_priorities(canonical: LayerOutput, corpus: LayerOutput, transactional: LayerOutput) -> Dict[str, Any]:
    """
    For each dimension:
        - Compute per-layer average impact and sentiment
        - GAP = max difference between any two layer average impacts
        - IMPACT = mean of the three layer impacts
        - PRIORITY = round(GAP * IMPACT, 2)
    Returns a dict with per-dimension detail and a sorted list of priorities.
    """
    layers = {
        "canonical": canonical,
        "corpus": corpus,
        "transactional": transactional
    }

    dim_results = {}
    for dim in DIMENSIONS:
        layer_impacts = {}
        layer_sents = {}
        for lname, lval in layers.items():
            items = getattr(lval, dim)
            layer_impacts[lname] = _avg_impact(items)
            layer_sents[lname] = _avg_sentiment(items)

        impacts = list(layer_impacts.values())
        gap = float(max(impacts) - min(impacts)) if impacts else 0.0
        impact_mean = float(sum(impacts) / len(impacts)) if impacts else 0.0
        priority = round(gap * impact_mean, 2)

        dim_results[dim] = {
            "layer_impacts": layer_impacts,
            "layer_sentiments": layer_sents,
            "gap": round(gap, 3),
            "impact_mean": round(impact_mean, 3),
            "priority": priority
        }

    # Sorted priorities high→low
    ranked = sorted(
        [{"dimension": d, **v} for d, v in dim_results.items()],
        key=lambda x: x["priority"],
        reverse=True
    )
    return {"by_dimension": dim_results, "ranked": ranked}


# ------------------------------------------------------------------------------
# Persistence
# ------------------------------------------------------------------------------

def persist_run(summary: RunSummary) -> None:
    run_path = DATA_DIR / f"{summary.run_id}.json"
    with open(run_path, "w", encoding="utf-8") as f:
        json.dump(summary.model_dump(), f, indent=2)

    row = {
        "timestamp": summary.timestamp,
        "run_id": summary.run_id,
        "company": summary.company,
        "desired_outcomes": summary.desired_outcomes,
        "top_priority_dimension": summary.priorities["ranked"][0]["dimension"] if summary.priorities["ranked"] else "",
        "top_priority_score": summary.priorities["ranked"][0]["priority"] if summary.priorities["ranked"] else 0.0,
    }
    if CSV_FILE.exists():
        df = pd.read_csv(CSV_FILE)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
    else:
        pd.DataFrame([row]).to_csv(CSV_FILE, index=False)


def load_run(run_id: str) -> Optional[RunSummary]:
    path = DATA_DIR / f"{run_id}.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return RunSummary(**data)


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
        "Canonical", company_name, desired_outcomes,
        safe_text(layer_canonical, "No canonical notes provided."),
        canonical_seed
    )
    corpus_out = prompt_layer_to_json(
        "Corpus", company_name, desired_outcomes,
        safe_text(layer_corpus, "No corpus notes provided."),
        canonical_seed={}
    )
    transactional_out = prompt_layer_to_json(
        "Transactional", company_name, desired_outcomes,
        safe_text(layer_transactional, "No transactional notes provided."),
        canonical_seed={}
    )

    priorities = compute_priorities(canonical_out, corpus_out, transactional_out)

    run_id = f"{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}_{company_name.replace(' ', '_')}"
    summary = RunSummary(
        run_id=run_id,
        timestamp=datetime.utcnow().isoformat(),
        company=company_name,
        desired_outcomes=desired_outcomes,
        canonical=canonical_out,
        corpus=corpus_out,
        transactional=transactional_out,
        priorities=priorities
    )
    persist_run(summary)

    # Pretty JSON for display
    pretty_json = json.dumps(summary.model_dump(), indent=2)

    html = f"""
<!DOCTYPE html>
<html>
<head>
  <title>SWOT DCIF Results – {company_name}</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 980px; margin: 0 auto; padding: 24px; background:#f5f5f5; }}
    .card {{ background:#fff; border-radius:8px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.06); margin-bottom:20px; }}
    pre {{ background:#0f172a; color:#e2e8f0; padding:16px; border-radius:8px; overflow:auto; }}
    a.btn {{ display:inline-block; background:#2d7a46; color:#fff; padding:10px 14px; border-radius:6px; text-decoration:none; }}
    a.btn:hover {{ background:#25663a; }}
    .pill {{ display:inline-block; padding:4px 10px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-left:6px; }}
    table {{ width:100%; border-collapse: collapse; }}
    th, td {{ text-align:left; padding:8px; border-bottom:1px solid #eee; }}
  </style>
</head>
<body>
  <h1>SWOT DCIF Results – {company_name}</h1>
  <div class="card">
    <p><strong>Run ID:</strong> <code>{run_id}</code></p>
    <p>
      <a class="btn" href="/">← New Analysis</a>
      &nbsp;&nbsp;
      <a class="btn" href="/api/result?id={run_id}">View JSON API</a>
    </p>
  </div>

  <div class="card">
    <h2>Top Priorities <span class="pill">Gap × Impact</span></h2>
    <table>
      <tr><th>Dimension</th><th>Priority</th><th>Gap</th><th>Impact Mean</th></tr>
      {''.join([
        f"<tr><td>{r['dimension'].title()}</td><td><b>{r['priority']}</b></td><td>{r['gap']}</td><td>{r['impact_mean']}</td></tr>"
        for r in priorities['ranked']
      ])}
    </table>
  </div>

  <div class="card">
    <h2>Full JSON Payload</h2>
    <pre>{pretty_json}</pre>
  </div>

  <div class="card">
    <p class="small">Use the JSON at <code>/api/result?id={run_id}</code> for dashboards (e.g., 3D SWOT map) or to diff runs over time.</p>
  </div>
</body>
</html>
"""
    return HTMLResponse(html)


@app.get("/api/result", response_class=JSONResponse)
def api_result(id: str = Query(..., description="Run ID of the analysis")):
    run = load_run(id)
    if not run:
        return JSONResponse({"error": "Run ID not found."}, status_code=404)
    return JSONResponse(run.model_dump())


# ------------------------------------------------------------------------------
# Local Dev Entrypoint
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Starting SWOT DCIF Engine (v2)")
    print("-> http://localhost:8000")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
