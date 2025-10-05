"""LLM interaction helpers for SWOT analysis."""

from typing import Dict, List
from langchain_core.messages import HumanMessage, SystemMessage

from .models import LayerOutput


def prompt_layer_to_json(
    llm,
    layer: str,
    company: str,
    desired_outcomes: str,
    raw_text: str,
    canonical_seed: Dict[str, List[str]]
) -> LayerOutput:
    """
    Ask the LLM to produce structured JSON for the given layer using with_structured_output.
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

    system_msg = f"""You are a strategy analyst. Convert raw notes for the '{layer}' layer of a company's SWOT into a structured output.

Rules:
- For each quadrant (strengths, weaknesses, opportunities, threats), return 1-6 items max.
- Each item: concise 'text' (<= 60 words), integer 'impact' 1-10 (business leverage toward desired outcomes),
  and 'sentiment' between -1 and 1 (positive=good, negative=bad as appropriate for the quadrant).
- Stay grounded in the provided notes; no hallucination. If a quadrant has no evidence, return empty list.
"""

    user_msg = f"""Company: {company}
Desired Outcomes: {desired_outcomes}

Layer: {layer}
Raw Notes:
{raw_text}

{seed_note}
"""

    # Log prompt (server console)
    print("\n" + "="*70)
    print(f"[LLM] Layer Analysis → {layer}")
    print("="*70)
    print(user_msg[:2000] + ("...\n" if len(user_msg) > 2000 else "\n"))

    # Use with_structured_output for reliable parsing
    structured_llm = llm.with_structured_output(LayerOutput)

    result = structured_llm.invoke([
        SystemMessage(content=system_msg.strip()),
        HumanMessage(content=user_msg.strip())
    ])

    # Ensure layer, company, and desired_outcomes are set correctly
    result.layer = layer
    result.company = company
    result.desired_outcomes = desired_outcomes

    return result
