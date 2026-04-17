"""
Epsilon TSP Data Dictionary mapper — preview-only segment matching.

Mirrors the openx_mapper.py pattern:
- Loads a taxonomy CSV into an EpsilonIndex
- Provides matchers for demographics, interests, psychographics
- Returns identical preview structure so the UI can render both sources
"""

import csv
import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

logger = logging.getLogger(__name__)

EPSILON_CSV_PATH = Path("data/epsilon_taxonomy.csv")

# Reuse from openx_mapper
from core.openx_mapper import ARI_SEGMENT_LABELS, generate_ethnic_keywords

# ---------- Tokenization (copied from openx_mapper — small utility) ----------

_STOP_WORDS = frozenset({
    "the", "a", "an", "and", "or", "of", "in", "for", "to", "with",
    "by", "on", "at", "is", "are", "was", "were", "has", "have", "had",
    "been", "being", "be", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "than",
    "less", "more", "not", "no", "very", "most", "also", "but",
})

_QUALITY_WORDS = frozenset({
    "high", "low", "medium", "likely", "extremely", "unlikely",
    "accepted", "preferred", "known", "modeled",
})

INTEREST_MATCH_THRESHOLD = 0.40

# Dimensions to index for keyword-based interest matching
KEYWORD_INDEX_DIMENSIONS = {"Lifestyle", "Market Trend", "Automotive", "Health"}


def _tokenize(text: str) -> Set[str]:
    tokens = set(re.split(r"[\s&/,>:;()\-–]+", text.lower()))
    tokens -= _STOP_WORDS
    tokens -= _QUALITY_WORDS
    tokens.discard("")
    return {t for t in tokens if len(t) > 1 and not t.isdigit()}


# ---------- EpsilonIndex ----------


class EpsilonIndex:
    def __init__(self):
        self.all_rows: List[dict] = []

        # Exact-lookup dicts
        self.age_ranges: List[dict] = []
        self.gender_by_name: Dict[str, dict] = {}

        # Small-category lists
        self.income_segments: List[dict] = []
        self.education_segments: List[dict] = []
        self.marital_segments: List[dict] = []
        self.children_segments: List[dict] = []
        self.ethnicity_segments: List[dict] = []

        # Epsilon-exclusive
        self.automotive_segments: List[dict] = []
        self.health_segments: List[dict] = []
        self.lifestyle_segments: List[dict] = []
        self.market_trend_segments: List[dict] = []
        self.market_indicator_segments: List[dict] = []
        self.trigger_segments: List[dict] = []
        self.prizm_segments: List[dict] = []
        self.neighborhood_segments: List[dict] = []

        # Keyword inverted index
        self.keyword_index: Dict[str, List[dict]] = {}

    @property
    def loaded(self) -> bool:
        return bool(self.all_rows)


def _parse_age_range_from_def(value_def: str) -> Optional[Tuple[int, int]]:
    """Parse '25-34 years old' → (25, 34) or '75+ years old' → (75, 99)."""
    m = re.search(r"(\d{1,2})\s*[-–]\s*(\d{1,2})", value_def)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"(\d{1,2})\+", value_def)
    if m:
        return int(m.group(1)), 99
    m = re.match(r"Under\s+(\d{1,2})", value_def, re.IGNORECASE)
    if m:
        return 0, int(m.group(1)) - 1
    return None


def _build_index(rows: List[dict]) -> EpsilonIndex:
    idx = EpsilonIndex()
    idx.all_rows = rows

    for row in rows:
        dimension = row.get("category", "")  # mapped from CSV Dimension column
        category = row.get("sub_category", "")
        field_name = row.get("epsilon_field_name", "")
        value_def = row.get("name", "")
        name_field = row.get("epsilon_name", "")

        name_lower = name_field.lower()
        field_lower = field_name.lower()

        # Each row can only sit in one specialized bucket; filters use the Name
        # column (Epsilon attribute name) rather than Field Name to disambiguate
        # rows like "Presence of Children age 00-17" from true age-range rows.

        if dimension == "Demographic":
            # --- Age: only rows whose Name is about HH/individual age AND
            #     whose Value Definition parses as an age range.
            #     Match "age" as a whole word (not substring of "Advantage"). ---
            name_tokens = re.split(r"[\s\-_()]+", name_lower)
            if (
                "age" in name_tokens
                and "children" not in name_lower
                and "birth" not in name_lower
            ):
                parsed = _parse_age_range_from_def(value_def)
                if parsed:
                    row["_age_range"] = parsed
                    idx.age_ranges.append(row)
                    continue

            # --- Gender ---
            if field_lower == "gender" and value_def.lower() in ("female", "male"):
                idx.gender_by_name[value_def] = row
                continue

            # --- Education ---
            if "education" in name_lower:
                # Skip metadata values (Household Inferred/Specific)
                if value_def.lower() not in ("household inferred", "household specific"):
                    idx.education_segments.append(row)
                continue

            # --- Marital ---
            if "marital" in name_lower and value_def.lower() in ("married", "single"):
                idx.marital_segments.append(row)
                continue

            # --- Children / Presence of Children ---
            if "children" in name_lower or "presence of children" in name_lower:
                idx.children_segments.append(row)
                continue

            # --- Ethnicity ---
            if category == "Ethnicity and Religion":
                idx.ethnicity_segments.append(row)
                continue

        elif dimension == "Financial":
            # --- Income tiers ---
            if "income" in name_lower:
                idx.income_segments.append(row)
                continue

        elif dimension == "Lifestyle":
            # PRIZM is a subset of Lifestyle
            if "prizm" in name_lower:
                idx.prizm_segments.append(row)
            else:
                idx.lifestyle_segments.append(row)

        elif dimension == "Automotive":
            idx.automotive_segments.append(row)

        elif dimension == "Health":
            idx.health_segments.append(row)

        elif dimension == "Trigger":
            idx.trigger_segments.append(row)

        elif dimension == "Market Trend":
            idx.market_trend_segments.append(row)

        elif dimension == "Market Indicators":
            idx.market_indicator_segments.append(row)

        elif dimension == "Neighborhood Attributes":
            idx.neighborhood_segments.append(row)

        # --- Keyword index for interest matching ---
        # Use epsilon_name (the attribute name, e.g. "Books - Fiction")
        # rather than value_def which is often just "Yes"/"No".
        # Only index affirmative values (Yes, Present, Y, or numeric scores).
        if dimension in KEYWORD_INDEX_DIMENSIONS:
            vd_lower = value_def.lower()
            if vd_lower in ("no", "blank", "unknown", "absent"):
                pass  # skip negative/empty values
            else:
                tokens = _tokenize(name_field) if name_field else _tokenize(value_def)
                for token in tokens:
                    if token not in idx.keyword_index:
                        idx.keyword_index[token] = []
                    idx.keyword_index[token].append(row)

    logger.info(
        "EpsilonIndex built: %d rows, %d age, %d gender, %d income, "
        "%d education, %d marital, %d children, %d prizm, %d auto, "
        "%d health, %d lifestyle, %d market_trend, %d trigger, %d keywords",
        len(rows), len(idx.age_ranges), len(idx.gender_by_name),
        len(idx.income_segments), len(idx.education_segments),
        len(idx.marital_segments), len(idx.children_segments),
        len(idx.prizm_segments), len(idx.automotive_segments),
        len(idx.health_segments), len(idx.lifestyle_segments),
        len(idx.market_trend_segments), len(idx.trigger_segments),
        len(idx.keyword_index),
    )
    return idx


# ---------- Module-level state ----------

_index: Optional[EpsilonIndex] = None


# ---------- Catalog loading ----------


def _load_epsilon_csv(csv_path: Path = None) -> List[dict]:
    path = csv_path or EPSILON_CSV_PATH
    if not path.exists():
        logger.warning("Epsilon CSV not found at %s", path)
        return []

    rows = []
    seen_signatures: Set[Tuple[str, str, str, str]] = set()
    try:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                dimension = (row.get("Dimension") or "").strip()
                category_col = (row.get("Category") or "").strip()
                name_col = (row.get("Name") or "").strip()
                field_name = (row.get("Field Name") or "").strip()
                value = (row.get("Value") or "").strip()
                value_def = (row.get("Value Definition") or "").strip()
                description = (row.get("Description") or "").strip()

                if not value or not value_def:
                    continue

                # Choose a concise display name:
                # - Affirmative flag values (Value in Y/Yes/Present) → use Name column
                #   (avoids "Condition likely for individual" etc.)
                # - Propensity-score values (e.g. "01-99, Blank") → use the Name column
                # - Long descriptive sentences → use the Name column
                # - Otherwise keep the Value Definition (e.g. "25-34 years old", "$50K-$75K")
                display_name = value_def
                value_lower = value.lower()
                vd_lower = value_def.lower()
                if value_lower in ("yes", "y", "present") and name_col:
                    display_name = name_col
                elif re.match(r"^\d+\s*[-–]\s*\d+", value_lower) and name_col:
                    # Score range value like "01-99" or "1-99"
                    display_name = name_col
                elif len(value_def) > 60 and name_col:
                    # Long descriptive sentences
                    display_name = name_col

                # Dedupe on (Dimension, Name, Value, display_name).
                # Epsilon sometimes has multiple source variants (Self Reported
                # vs All) with the same Name+Value — collapse them.
                sig = (dimension, name_col, value, display_name)
                if sig in seen_signatures:
                    continue
                seen_signatures.add(sig)

                rows.append({
                    "name": display_name,
                    "full_name": f"{dimension} > {category_col} > {name_col} > {display_name}",
                    "description": description,
                    "sub_category": category_col,
                    "category": dimension,
                    "type": "Epsilon",
                    "source": "Epsilon",
                    "epsilon_value": value,
                    "epsilon_field_name": field_name,
                    "epsilon_name": name_col,
                })
    except Exception as exc:
        logger.error("Failed to load Epsilon CSV: %s", exc)

    logger.info("Loaded %d segments from Epsilon CSV", len(rows))
    return rows


def load_epsilon_taxonomy(csv_path: Path = None) -> List[dict]:
    global _index
    if _index and _index.loaded:
        return _index.all_rows
    rows = _load_epsilon_csv(csv_path)
    _index = _build_index(rows)
    return rows


def _get_index() -> EpsilonIndex:
    global _index
    if not _index or not _index.loaded:
        load_epsilon_taxonomy()
    return _index


# ---------- Matchers ----------


def match_age_range(age_str: str) -> List[dict]:
    """Match ARI age range (e.g. '25-40') against Epsilon age bands."""
    m = re.search(r"(\d{1,2})\s*[-–]\s*(\d{1,2})", age_str)
    if not m:
        m_plus = re.search(r"(\d{1,2})\+", age_str)
        if m_plus:
            target_min, target_max = int(m_plus.group(1)), 99
        else:
            return []
    else:
        target_min, target_max = int(m.group(1)), int(m.group(2))

    idx = _get_index()
    results = []
    for row in idx.age_ranges:
        seg_range = row.get("_age_range")
        if not seg_range:
            continue
        seg_min, seg_max = seg_range
        if seg_min <= target_max and seg_max >= target_min:
            results.append({"segment": row, "confidence": 1.0})
    return results


def match_gender(gender_str: str) -> List[dict]:
    if not gender_str:
        return []
    idx = _get_index()
    lower = gender_str.lower()
    results = []
    if "female" in lower:
        seg = idx.gender_by_name.get("Female")
        if seg:
            results.append({"segment": seg, "confidence": 1.0})
    if "male" in lower and "female" not in lower:
        seg = idx.gender_by_name.get("Male")
        if seg:
            results.append({"segment": seg, "confidence": 1.0})
    if not results and "all" not in lower:
        for name, seg in idx.gender_by_name.items():
            results.append({"segment": seg, "confidence": 0.50})
    return results


def match_income(income_str: str) -> List[dict]:
    """Parse '$50K-$100K' and find overlapping Epsilon income tiers."""
    if not income_str:
        return []
    idx = _get_index()

    m = re.search(r"\$\s*([\d,.]+)\s*[kK]?\s*[-–]\s*\$\s*([\d,.]+)\s*[kK]?", income_str)
    if not m:
        return []

    def parse_amount(s: str) -> float:
        s = s.replace(",", "")
        val = float(s)
        if val < 1000:
            val *= 1000
        return val

    target_min = parse_amount(m.group(1))
    target_max = parse_amount(m.group(2))

    results = []
    seen = set()
    for seg in idx.income_segments:
        vd = seg.get("name", "")
        if vd in seen:
            continue
        inc_match = re.findall(r"\$\s*([\d,]+)", vd)
        if len(inc_match) >= 2:
            seg_min = float(inc_match[0].replace(",", ""))
            seg_max = float(inc_match[1].replace(",", ""))
            if seg_min <= target_max and seg_max >= target_min:
                seen.add(vd)
                results.append({"segment": seg, "confidence": 0.85})
        elif len(inc_match) == 1:
            seg_val = float(inc_match[0].replace(",", ""))
            if target_min <= seg_val <= target_max:
                seen.add(vd)
                results.append({"segment": seg, "confidence": 0.70})
    return results[:10]


def match_education(edu_str: str) -> List[dict]:
    if not edu_str:
        return []
    idx = _get_index()
    lower = edu_str.lower()
    include_above = "or above" in lower or "or higher" in lower or "+" in lower

    edu_hierarchy = [
        ("some high school", ["some high school"]),
        ("high school", ["high school"]),
        ("some college", ["some college"]),
        ("college", ["college", "completed college"]),
        ("graduate", ["graduate school", "graduate"]),
    ]

    target_levels = []
    for label, keywords in edu_hierarchy:
        if any(kw in lower for kw in keywords):
            idx_pos = [i for i, (l, _) in enumerate(edu_hierarchy) if l == label][0]
            if include_above:
                target_levels = [l for i, (l, _) in enumerate(edu_hierarchy) if i >= idx_pos]
            else:
                target_levels = [label]
            break

    if not target_levels:
        return []

    results = []
    for seg in idx.education_segments:
        seg_name = seg.get("name", "").lower()
        for level in target_levels:
            if level in seg_name:
                results.append({"segment": seg, "confidence": 0.90})
                break
    return results


def match_marital(demographics_list: list) -> List[dict]:
    if not demographics_list:
        return []
    idx = _get_index()
    results = []
    for demo in demographics_list:
        lower = demo.lower() if isinstance(demo, str) else ""
        for seg in idx.marital_segments:
            seg_name = seg.get("name", "").lower()
            if seg_name in lower:
                pct = re.search(r"(\d+)%", demo)
                conf = 0.80 if pct and int(pct.group(1)) >= 30 else 0.60
                results.append({"segment": seg, "confidence": conf})
    return results


def match_children(demographics_list: list) -> List[dict]:
    if not demographics_list:
        return []
    idx = _get_index()
    has_children = False
    no_children = False
    for demo in demographics_list:
        lower = demo.lower() if isinstance(demo, str) else ""
        if "children" not in lower:
            continue
        pct = re.search(r"(\d+)%", demo)
        if not pct:
            continue
        pct_val = int(pct.group(1))
        if "do not" in lower or "no children" in lower:
            if pct_val >= 50:
                no_children = True
        else:
            if pct_val >= 30:
                has_children = True

    results = []
    if not has_children:
        return results

    seen = set()
    for seg in idx.children_segments:
        # Only include affirmative "Yes" presence-of-children segments
        if seg.get("epsilon_value", "").lower() not in ("yes", "y"):
            continue
        key = seg.get("epsilon_name", "")
        if key in seen:
            continue
        seen.add(key)
        results.append({"segment": seg, "confidence": 0.80})
    return results


def match_interests_via_index(interest_list: List[str]) -> List[dict]:
    """Match ARI interest categories against Epsilon keyword index."""
    if not interest_list:
        return []
    idx = _get_index()
    results = []
    seen_segments = set()

    for interest in interest_list:
        interest_keywords = _tokenize(interest)
        if not interest_keywords:
            results.append({"input": interest, "matched": False, "confidence": 0.0})
            continue

        candidate_hits: Dict[str, Tuple[int, dict]] = {}
        for kw in interest_keywords:
            for seg in idx.keyword_index.get(kw, []):
                key = seg.get("full_name", seg.get("name"))
                if key in candidate_hits:
                    candidate_hits[key] = (candidate_hits[key][0] + 1, seg)
                else:
                    candidate_hits[key] = (1, seg)

        if not candidate_hits:
            results.append({"input": interest, "matched": False, "confidence": 0.0})
            continue

        interest_lower = interest.lower()
        interest_had_match = False
        for key, (hits, seg) in candidate_hits.items():
            if key in seen_segments:
                continue
            hit_ratio = min(hits / len(interest_keywords), 1.0)
            seg_name_lower = seg.get("name", "").lower()
            containment_bonus = 0.20 if interest_lower in seg_name_lower else 0.0
            score = min(hit_ratio + containment_bonus, 1.0)

            if score >= INTEREST_MATCH_THRESHOLD:
                seen_segments.add(key)
                interest_had_match = True
                results.append({
                    "segment": seg,
                    "confidence": round(score, 2),
                    "input": interest,
                    "matched": True,
                })

        if not interest_had_match:
            results.append({"input": interest, "matched": False, "confidence": 0.0})

    matched = [r for r in results if r.get("matched")]
    matched.sort(key=lambda x: x["confidence"], reverse=True)
    # Preserve unmatched entries so the UI can show them as "no match"
    unmatched = [r for r in results if not r.get("matched")]
    return matched[:15] + unmatched


def match_taxonomy(industry: str) -> List[dict]:
    if not industry:
        return []
    idx = _get_index()
    industry_keywords = _tokenize(industry)
    if not industry_keywords:
        return []

    candidate_hits: Dict[str, Tuple[int, dict]] = {}
    for kw in industry_keywords:
        for seg in idx.keyword_index.get(kw, []):
            key = seg.get("full_name", seg.get("name"))
            if key in candidate_hits:
                candidate_hits[key] = (candidate_hits[key][0] + 1, seg)
            else:
                candidate_hits[key] = (1, seg)

    results = []
    for key, (hits, seg) in candidate_hits.items():
        hit_ratio = min(hits / len(industry_keywords), 1.0)
        if hit_ratio >= INTEREST_MATCH_THRESHOLD:
            results.append({"segment": seg, "confidence": round(hit_ratio, 2)})

    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results[:10]


def match_activities(activities_list: list) -> List[dict]:
    """Match audience_insights.activities via keyword index."""
    if not activities_list:
        return []
    idx = _get_index()
    results = []
    seen = set()
    for item in activities_list:
        trait = item.get("trait", "") if isinstance(item, dict) else str(item)
        qvi = item.get("qvi", 100) if isinstance(item, dict) else 100
        if not trait:
            continue
        trait_keywords = _tokenize(trait)
        if not trait_keywords:
            continue

        candidate_hits: Dict[str, Tuple[int, dict]] = {}
        for kw in trait_keywords:
            for seg in idx.keyword_index.get(kw, []):
                key = seg.get("full_name", seg.get("name"))
                if key in candidate_hits:
                    candidate_hits[key] = (candidate_hits[key][0] + 1, seg)
                else:
                    candidate_hits[key] = (1, seg)

        for key, (hits, seg) in candidate_hits.items():
            if key in seen:
                continue
            hit_ratio = min(hits / len(trait_keywords), 1.0)
            qvi_boost = min((qvi - 100) / 400, 0.15) if qvi > 100 else 0
            score = min(hit_ratio + qvi_boost, 1.0)
            if score >= INTEREST_MATCH_THRESHOLD:
                seen.add(key)
                results.append({
                    "segment": seg,
                    "confidence": round(score, 2),
                    "source_trait": trait,
                })

    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results[:10]


def match_daily_routines(routines_list: list) -> List[dict]:
    return match_activities(routines_list)


def match_prizm_persona(values_list: list, psych_drivers_list: list) -> List[dict]:
    """Match ARI values/psychographic drivers to Epsilon PRIZM clusters."""
    idx = _get_index()
    if not idx.prizm_segments:
        return []

    traits = []
    for item in (values_list or []):
        if isinstance(item, dict):
            traits.append((item.get("trait", ""), item.get("qvi", 100)))
    for item in (psych_drivers_list or []):
        if isinstance(item, dict):
            traits.append((item.get("trait", ""), item.get("qvi", 100)))

    if not traits:
        return []

    results = []
    seen = set()
    for trait, qvi in traits:
        if not trait:
            continue
        trait_keywords = _tokenize(trait)
        if not trait_keywords:
            continue

        for seg in idx.prizm_segments:
            seg_name = seg.get("name", "")
            if not seg_name or seg_name in seen:
                continue
            seg_keywords = _tokenize(seg_name)
            if not seg_keywords:
                continue
            overlap = trait_keywords & seg_keywords
            if not overlap:
                continue
            score = len(overlap) / min(len(trait_keywords), len(seg_keywords))
            qvi_boost = min((qvi - 100) / 400, 0.15) if qvi > 100 else 0
            final = min(score + qvi_boost, 1.0)
            if final >= INTEREST_MATCH_THRESHOLD:
                seen.add(seg_name)
                results.append({
                    "segment": seg,
                    "confidence": round(final, 2),
                    "source_trait": trait,
                })

    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results[:10]


def match_automotive(interest_list: List[str], activities_list: list) -> List[dict]:
    """Match interests/activities against Epsilon Automotive dimension."""
    idx = _get_index()
    if not idx.automotive_segments:
        return []

    all_traits = list(interest_list or [])
    for item in (activities_list or []):
        if isinstance(item, dict):
            all_traits.append(item.get("trait", ""))
        elif isinstance(item, str):
            all_traits.append(item)

    results = []
    seen = set()
    for trait in all_traits:
        if not trait:
            continue
        trait_keywords = _tokenize(trait)
        if not trait_keywords:
            continue

        for seg in idx.automotive_segments:
            seg_name = seg.get("name", "")
            if not seg_name or seg_name in seen:
                continue
            seg_keywords = _tokenize(seg_name)
            if not seg_keywords:
                continue
            overlap = trait_keywords & seg_keywords
            if not overlap:
                continue
            score = len(overlap) / min(len(trait_keywords), len(seg_keywords))
            if score >= INTEREST_MATCH_THRESHOLD:
                seen.add(seg_name)
                results.append({
                    "segment": seg,
                    "confidence": round(score, 2),
                    "source_trait": trait,
                })

    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results[:10]


def match_health(psych_drivers_list: list, activities_list: list) -> List[dict]:
    """Match psychographic/activity traits against Epsilon Health dimension."""
    idx = _get_index()
    if not idx.health_segments:
        return []

    all_traits = []
    for item in (psych_drivers_list or []):
        if isinstance(item, dict):
            all_traits.append(item.get("trait", ""))
    for item in (activities_list or []):
        if isinstance(item, dict):
            all_traits.append(item.get("trait", ""))

    results = []
    seen = set()
    for trait in all_traits:
        if not trait:
            continue
        trait_keywords = _tokenize(trait)
        if not trait_keywords:
            continue

        for seg in idx.health_segments:
            seg_name = seg.get("name", "")
            if not seg_name or seg_name in seen:
                continue
            seg_keywords = _tokenize(seg_name)
            if not seg_keywords:
                continue
            overlap = trait_keywords & seg_keywords
            if not overlap:
                continue
            score = len(overlap) / min(len(trait_keywords), len(seg_keywords))
            if score >= INTEREST_MATCH_THRESHOLD:
                seen.add(seg_name)
                results.append({
                    "segment": seg,
                    "confidence": round(score, 2),
                    "source_trait": trait,
                })

    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results[:10]


def match_trigger_events(demographics_list: list) -> List[dict]:
    """Match demographic signals to Epsilon Trigger (life events) segments."""
    idx = _get_index()
    if not idx.trigger_segments or not demographics_list:
        return []

    results = []
    all_text = " ".join(
        d.lower() for d in demographics_list if isinstance(d, str)
    )

    trigger_keywords = {
        "new mover": ["move", "moving", "relocated", "new home"],
        "new parent": ["children", "newborn", "baby", "parent"],
        "new driver": ["driver", "driving", "license"],
    }

    seen = set()
    for seg in idx.trigger_segments:
        seg_name = seg.get("name", "").lower()
        if seg_name in seen:
            continue
        for trigger_type, keywords in trigger_keywords.items():
            if any(kw in all_text for kw in keywords):
                seg_kw = _tokenize(seg.get("epsilon_name", ""))
                trigger_kw = set(trigger_type.split())
                if seg_kw & trigger_kw:
                    seen.add(seg_name)
                    results.append({"segment": seg, "confidence": 0.60})
                    break

    return results[:5]


# ---------- High-level preview ----------


def _match_single_segment(
    segment: dict,
    industry: str,
    audience_insights: dict,
    language_recs: list,
) -> dict:
    targeting = segment.get("targeting_params", {})
    demographics = audience_insights.get("demographics", [])
    values = audience_insights.get("values", [])
    psych_drivers = audience_insights.get("psychological_drivers", [])
    activities = audience_insights.get("activities", [])
    daily_routines = audience_insights.get("daily_routines", [])

    age_results = match_age_range(targeting.get("age_range", ""))
    gender_results = match_gender(targeting.get("gender_targeting", "All"))
    income_results = match_income(targeting.get("income_targeting", ""))
    education_results = match_education(targeting.get("education_targeting", ""))
    marital_results = match_marital(demographics)
    children_results = match_children(demographics)

    interest_results = match_interests_via_index(
        segment.get("interest_categories", []),
    )
    taxonomy_results = match_taxonomy(industry)
    activities_results = match_activities(activities)
    routines_results = match_daily_routines(daily_routines)
    prizm_results = match_prizm_persona(values, psych_drivers)

    # Epsilon-exclusive
    automotive_results = match_automotive(
        segment.get("interest_categories", []), activities
    )
    health_results = match_health(psych_drivers, activities)
    trigger_results = match_trigger_events(demographics)

    # Ethnic keywords (reused from openx_mapper)
    ethnic_kw = generate_ethnic_keywords(segment, language_recs)

    match_data = {
        "age": age_results,
        "gender": gender_results,
        "location": [],  # Epsilon has no US state segments
        "interests": interest_results,
        "taxonomy": taxonomy_results,
        "income": income_results,
        "education": education_results,
        "language": [],  # Epsilon has no language segments
        "area_type": [],  # Epsilon has no area type
        "children": children_results,
        "marital": marital_results,
        "activities": activities_results,
        "daily_routines": routines_results,
        "mosaic_persona": prizm_results,  # PRIZM replaces Mosaic
        "attitudes": [],  # Epsilon has no attitudes segments
        "ethnic_keywords": ethnic_kw,
        # Epsilon-exclusive
        "automotive": automotive_results,
        "health": health_results,
        "trigger_events": trigger_results,
    }

    all_matches = []
    for val in match_data.values():
        if isinstance(val, list):
            all_matches.extend(val)

    warnings = []
    unmatched_interests = [
        r.get("input", "?") for r in interest_results
        if isinstance(r, dict) and not r.get("matched")
    ]
    if unmatched_interests:
        warnings.append(f"Unmatched interests: {', '.join(unmatched_interests)}")

    return {
        "segment_name": segment.get("name", "Unnamed"),
        "segment_data": segment,
        "matches": match_data,
        "summary": {
            "age_matches": len(age_results),
            "gender_matches": len(gender_results),
            "location_matches": 0,
            "interest_matches": len([r for r in interest_results if r.get("matched")]),
            "interest_total": len(segment.get("interest_categories", []) or []),
            "taxonomy_matches": len(taxonomy_results),
            "income_matches": len(income_results),
            "education_matches": len(education_results),
            "language_matches": 0,
            "area_matches": 0,
            "children_matches": len(children_results),
            "marital_matches": len(marital_results),
            "activities_matches": len(activities_results),
            "routines_matches": len(routines_results),
            "mosaic_matches": len(prizm_results),
            "attitude_matches": 0,
            "ethnic_keyword_count": len(ethnic_kw.get("keywords", [])),
            # Epsilon-exclusive
            "automotive_matches": len(automotive_results),
            "health_matches": len(health_results),
            "trigger_matches": len(trigger_results),
        },
        "warnings": warnings,
    }


def preview_all_segments(
    session_state: Dict[str, Any],
) -> List[dict]:
    """Generate Epsilon mapping previews for all ARI audience segments."""
    load_epsilon_taxonomy()

    idx = _get_index()
    if not idx.loaded:
        logger.error("No Epsilon taxonomy loaded")
        return []

    industry = session_state.get("industry", "")

    audience_insights = session_state.get("audience_insights", {})
    if isinstance(audience_insights, str):
        try:
            audience_insights = json.loads(audience_insights)
        except (json.JSONDecodeError, TypeError):
            audience_insights = {}

    language_recs = session_state.get("languageRecommendations", [])
    if isinstance(language_recs, str):
        try:
            language_recs = json.loads(language_recs)
        except (json.JSONDecodeError, TypeError):
            language_recs = []

    segments = []
    audience_segments = session_state.get("audience_segments", {})
    if isinstance(audience_segments, dict):
        segments = audience_segments.get("segments", [])

    previews = []
    for seg_idx, seg in enumerate(segments[:4]):
        label = (
            ARI_SEGMENT_LABELS[seg_idx]
            if seg_idx < len(ARI_SEGMENT_LABELS)
            else f"Segment {seg_idx + 1}"
        )
        preview = _match_single_segment(seg, industry, audience_insights, language_recs)
        preview["label"] = label
        preview["index"] = seg_idx
        previews.append(preview)

    return previews
