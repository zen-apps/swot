"""Data persistence helpers for SWOT analysis."""

import json
from pathlib import Path
from typing import Optional
import pandas as pd

from .models import RunSummary


def persist_run(summary: RunSummary, data_dir: Path, csv_file: Path) -> None:
    """Save run summary to JSON file and append to CSV."""
    run_path = data_dir / f"{summary.run_id}.json"
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
    if csv_file.exists():
        df = pd.read_csv(csv_file)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        df.to_csv(csv_file, index=False)
    else:
        pd.DataFrame([row]).to_csv(csv_file, index=False)


def load_run(run_id: str, data_dir: Path) -> Optional[RunSummary]:
    """Load run summary from JSON file."""
    path = data_dir / f"{run_id}.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return RunSummary(**data)
