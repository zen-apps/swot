"""Data models for SWOT DCIF Engine."""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


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
