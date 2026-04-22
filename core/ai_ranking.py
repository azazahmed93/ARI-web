"""
AI-based relevance ranking for user-added custom taxonomy segments.

Given an ARI audience segment and a set of user-added taxonomy segments,
asks GPT-4o to score each segment's relevance to the audience.
"""

import json
import logging
from typing import List, Dict, Any

from core.ai_utils import make_openai_request

logger = logging.getLogger(__name__)


def _summarize_ari_segment(ari_segment: dict, audience_insights: dict) -> str:
    """Compact text description of the ARI audience for the prompt."""
    parts = []
    if ari_segment.get("name"):
        parts.append(f"Name: {ari_segment['name']}")
    if ari_segment.get("description"):
        parts.append(f"Description: {ari_segment['description']}")

    tp = ari_segment.get("targeting_params", {}) or {}
    for key, label in [
        ("age_range", "Age"),
        ("gender_targeting", "Gender"),
        ("income_targeting", "Income"),
        ("education_targeting", "Education"),
        ("location_targeting", "Location"),
    ]:
        if tp.get(key):
            parts.append(f"{label}: {tp[key]}")

    interests = ari_segment.get("interest_categories", []) or []
    if interests:
        parts.append(f"Interests: {', '.join(interests)}")

    demographics = audience_insights.get("demographics", []) or []
    if demographics:
        parts.append("Demographics: " + "; ".join(
            d for d in demographics if isinstance(d, str)
        )[:400])

    values = audience_insights.get("values", []) or []
    if values:
        parts.append("Values: " + ", ".join(
            v.get("trait", "") for v in values if isinstance(v, dict)
        )[:200])

    drivers = audience_insights.get("psychological_drivers", []) or []
    if drivers:
        parts.append("Drivers: " + ", ".join(
            d.get("trait", "") for d in drivers if isinstance(d, dict)
        )[:200])

    return "\n".join(parts)


def _describe_segment(seg: dict, index: int) -> str:
    """Produce a one-line description of a taxonomy segment for the prompt."""
    full_name = seg.get("full_name") or seg.get("name") or ""
    desc = seg.get("description", "")
    line = f"{index}. {full_name}"
    if desc:
        line += f" — {desc[:150]}"
    return line


def rank_custom_picks(
    ari_segment: dict,
    audience_insights: dict,
    segments: List[dict],
) -> Dict[str, dict]:
    """Score each taxonomy segment's relevance (0.0-1.0) to the ARI audience.

    Returns a dict mapping segment `full_name` → ``{"confidence": float, "reasoning": str}``.
    On failure returns an empty dict.
    """
    if not segments:
        return {}

    audience_text = _summarize_ari_segment(ari_segment, audience_insights)
    seg_lines = [_describe_segment(s, i + 1) for i, s in enumerate(segments)]

    prompt = f"""You are scoring how relevant each taxonomy segment is to a specific audience.

AUDIENCE:
{audience_text}

SEGMENTS TO SCORE:
{chr(10).join(seg_lines)}

For each segment, return a relevance score from 0.00 to 1.00:
- 1.00: highly relevant, strong semantic fit
- 0.70-0.90: clearly relevant
- 0.50-0.69: marginally relevant
- 0.30-0.49: weak fit
- 0.00-0.29: not relevant

Consider the audience's interests, demographics, values, and psychographic drivers.
Be honest — if a segment is a poor fit, score it low.

Return JSON exactly in this format:
{{"rankings": [
  {{"index": 1, "confidence": 0.85, "reasoning": "short 1-sentence rationale"}},
  {{"index": 2, "confidence": 0.40, "reasoning": "short 1-sentence rationale"}}
]}}"""

    result = make_openai_request(
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3,
        max_tokens=min(100 + 80 * len(segments), 2000),
    )

    if not result or "rankings" not in result:
        logger.warning("AI ranking failed, no rankings returned")
        return {}

    out: Dict[str, dict] = {}
    for entry in result.get("rankings", []):
        if not isinstance(entry, dict):
            continue
        idx = entry.get("index")
        if not isinstance(idx, int) or idx < 1 or idx > len(segments):
            continue
        seg = segments[idx - 1]
        fn = seg.get("full_name") or seg.get("name") or ""
        conf = entry.get("confidence", 0)
        try:
            conf = float(conf)
        except (TypeError, ValueError):
            conf = 0.0
        conf = max(0.0, min(conf, 1.0))
        out[fn] = {
            "confidence": round(conf, 2),
            "reasoning": str(entry.get("reasoning", ""))[:300],
        }

    return out
