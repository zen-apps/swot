"""Priority scoring logic for SWOT analysis."""

from typing import Dict, List, Any
from .models import LayerOutput, SWOTItem


DIMENSIONS = ["strengths", "weaknesses", "opportunities", "threats"]


def _avg_impact(items: List[SWOTItem]) -> float:
    return float(sum(i.impact for i in items) / len(items)) if items else 0.0


def _avg_sentiment(items: List[SWOTItem]) -> float:
    return float(sum(i.sentiment for i in items) / len(items)) if items else 0.0


def compute_priorities(
    canonical: LayerOutput,
    corpus: LayerOutput,
    transactional: LayerOutput
) -> Dict[str, Any]:
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
