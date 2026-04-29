"""
TransUnion (TruAudience AdAdvisor) taxonomy mapper, preview only.

Mirrors the epsilon_mapper.py pattern but for TransUnion's flat
"Category | Audience Name | Description" CSV. Each row is one direct segment
with the path encoded in Audience Name (already stripped of the "AdAdvisor by
TransUnion > " prefix at conversion time).
"""

import csv
import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

logger = logging.getLogger(__name__)

TRANSUNION_CSV_PATH = Path("data/transunion_taxonomy.csv")

# Reuse from openx_mapper
from core.openx_mapper import ARI_SEGMENT_LABELS, generate_ethnic_keywords

# ---------- Tokenization (small utility, copied from openx_mapper) ----------

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

# Categories whose segment names are fed into the keyword index for
# interest/lifestyle/industry matching.
KEYWORD_INDEX_CATEGORIES = {
    "Propensity & Interests",
    "Automotive",
    "Consumer Finance",
    "Home Ownership / Property",
}

# US state name → 2-letter abbreviation (TU stores both, e.g. "Alabama - AL").
_STATE_NAMES = {
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado",
    "connecticut", "delaware", "district of columbia", "florida", "georgia",
    "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky",
    "louisiana", "maine", "maryland", "massachusetts", "michigan", "minnesota",
    "mississippi", "missouri", "montana", "nebraska", "nevada", "new hampshire",
    "new jersey", "new mexico", "new york", "north carolina", "north dakota",
    "ohio", "oklahoma", "oregon", "pennsylvania", "rhode island",
    "south carolina", "south dakota", "tennessee", "texas", "utah", "vermont",
    "virginia", "washington", "west virginia", "wisconsin", "wyoming",
}


def _tokenize(text: str) -> Set[str]:
    tokens = set(re.split(r"[\s&/,>:;()\-–]+", text.lower()))
    tokens -= _STOP_WORDS
    tokens -= _QUALITY_WORDS
    tokens.discard("")
    return {t for t in tokens if len(t) > 1 and not t.isdigit()}


# ---------- TransUnionIndex ----------


class TransUnionIndex:
    def __init__(self):
        self.all_rows: List[dict] = []

        # Demographics buckets
        self.age_segments: List[dict] = []
        self.gender_segments: List[dict] = []
        self.income_segments: List[dict] = []
        self.education_segments: List[dict] = []
        self.marital_segments: List[dict] = []
        self.children_segments: List[dict] = []
        self.language_segments: List[dict] = []
        self.political_segments: List[dict] = []
        self.life_events_segments: List[dict] = []

        # Geographic
        self.state_by_name: Dict[str, dict] = {}

        # Persona analog (TruAudience Segments + Strategic Groups)
        self.truaudience_segments: List[dict] = []

        # TU-exclusive category buckets
        self.automotive_segments: List[dict] = []
        self.consumer_finance_segments: List[dict] = []
        self.home_property_segments: List[dict] = []

        # Keyword inverted index (Propensity & Interests, etc.)
        self.keyword_index: Dict[str, List[dict]] = {}

    @property
    def loaded(self) -> bool:
        return bool(self.all_rows)


def _parse_age_range_from_def(value_def: str) -> Optional[Tuple[int, int]]:
    """Parse '25-34', '25 - 34', '75+' from segment leaf names."""
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


def _state_name_from_segment(leaf: str) -> Optional[str]:
    """Pull state name from a TU state leaf like 'Alabama - AL'."""
    if not leaf:
        return None
    head = leaf.split(" - ")[0].strip()
    if head.lower() in _STATE_NAMES:
        return head
    return None


def _build_index(rows: List[dict]) -> TransUnionIndex:
    idx = TransUnionIndex()
    idx.all_rows = rows

    for row in rows:
        category = row.get("category", "")
        path_parts = row.get("tu_path_parts", [])
        # Path looks like ["Demographics", "Individual", "Marital Status", "Married"]
        sub_2 = path_parts[1] if len(path_parts) > 1 else ""
        sub_3 = path_parts[2] if len(path_parts) > 2 else ""
        sub_3_lower = sub_3.lower()
        leaf = path_parts[-1] if path_parts else row.get("name", "")

        # --- Geographic (states only) ---
        if category == "Geographic":
            if sub_2 == "State":
                state = _state_name_from_segment(leaf)
                if state:
                    idx.state_by_name[state] = row
            # DMA / Congressional District skipped per plan
            continue

        # --- Demographics breakdown ---
        if category == "Demographics":
            # Match "age" as a whole word, not substring of "language", "marriage" etc.
            sub_3_tokens = re.split(r"[\s\-_/()]+", sub_3_lower)
            is_age_only = "age" in sub_3_tokens and "gender" not in sub_3_tokens
            if is_age_only:
                # Pure age segments (Demographics > Individual > Age, Age Ranges)
                parsed = _parse_age_range_from_def(leaf)
                if parsed:
                    row["_age_range"] = parsed
                    idx.age_segments.append(row)
                continue
            if sub_3_lower == "gender":
                if leaf.lower() in ("female", "male"):
                    idx.gender_segments.append(row)
                continue
            if sub_3_lower == "estimated household income":
                idx.income_segments.append(row)
                continue
            if sub_3_lower == "education":
                # Only keep top-level education segments
                # ("Highest Education Achieved - High School", etc.).
                # Skip "Recent Graduates" major-specific subsegments.
                if "highest education" in leaf.lower():
                    idx.education_segments.append(row)
                continue
            if sub_3_lower == "marital status":
                idx.marital_segments.append(row)
                continue
            if sub_3_lower == "household composition" and "children" in (
                path_parts[3].lower() if len(path_parts) > 3 else ""
            ):
                idx.children_segments.append(row)
                continue
            if sub_3_lower in ("language spoken", "spanish-language media"):
                idx.language_segments.append(row)
                continue
            if "political" in sub_3_lower:
                idx.political_segments.append(row)
                continue
            if sub_3_lower == "life events":
                idx.life_events_segments.append(row)
                continue
            # Other demographics (Employment Status, Time at Address, etc.)
            # left out of any specific bucket; still indexed by keyword below.

        # --- TruAudience persona-style segments ---
        if category in ("TruAudience Segments", "TruAudience Strategic Groups"):
            idx.truaudience_segments.append(row)
            continue

        # --- TU-exclusive category buckets ---
        if category == "Automotive":
            idx.automotive_segments.append(row)
        elif category == "Consumer Finance":
            idx.consumer_finance_segments.append(row)
        elif category == "Home Ownership / Property":
            idx.home_property_segments.append(row)
        # Business intentionally not indexed (B2B, not consumer ARI)

        # --- Keyword index for interest/industry matching ---
        if category in KEYWORD_INDEX_CATEGORIES:
            tokens = _tokenize(leaf)
            for token in tokens:
                idx.keyword_index.setdefault(token, []).append(row)

    logger.info(
        "TransUnionIndex: %d rows, %d age, %d gender, %d state, %d income, "
        "%d edu, %d marital, %d children, %d lang, %d political, %d life_events, "
        "%d truaudience, %d auto, %d finance, %d home, %d keywords",
        len(rows), len(idx.age_segments), len(idx.gender_segments),
        len(idx.state_by_name), len(idx.income_segments),
        len(idx.education_segments), len(idx.marital_segments),
        len(idx.children_segments), len(idx.language_segments),
        len(idx.political_segments), len(idx.life_events_segments),
        len(idx.truaudience_segments), len(idx.automotive_segments),
        len(idx.consumer_finance_segments), len(idx.home_property_segments),
        len(idx.keyword_index),
    )
    return idx


# ---------- Module-level state ----------

_index: Optional[TransUnionIndex] = None


# ---------- Catalog loading ----------


def _load_transunion_csv(csv_path: Path = None) -> List[dict]:
    path = csv_path or TRANSUNION_CSV_PATH
    if not path.exists():
        logger.warning("TransUnion CSV not found at %s", path)
        return []

    rows = []
    seen_full_names = set()
    try:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for csv_row in reader:
                category = (csv_row.get("Category") or "").strip()
                full_name = (csv_row.get("Audience Name") or "").strip()
                description = (csv_row.get("Description") or "").strip()

                if not category or not full_name:
                    continue
                # Dedupe identical (Category, Audience Name) pairs
                if full_name in seen_full_names:
                    continue
                seen_full_names.add(full_name)

                path_parts = [p.strip() for p in full_name.split(" > ") if p.strip()]
                leaf = path_parts[-1] if path_parts else full_name
                sub_category = path_parts[1] if len(path_parts) > 1 else ""

                rows.append({
                    "name": leaf,
                    "full_name": full_name,
                    "description": description,
                    "sub_category": sub_category,
                    "category": category,
                    "type": "TransUnion",
                    "source": "TransUnion",
                    "tu_path_parts": path_parts,
                })
    except Exception as exc:
        logger.error("Failed to load TransUnion CSV: %s", exc)

    logger.info("Loaded %d segments from TransUnion CSV", len(rows))
    return rows


def load_transunion_taxonomy(csv_path: Path = None) -> List[dict]:
    global _index
    if _index and _index.loaded:
        return _index.all_rows
    rows = _load_transunion_csv(csv_path)
    _index = _build_index(rows)
    return rows


def _get_index() -> TransUnionIndex:
    global _index
    if not _index or not _index.loaded:
        load_transunion_taxonomy()
    return _index


# ---------- Matchers ----------


def match_age_range(age_str: str) -> List[dict]:
    """Match ARI age range (e.g. '25-40') against TU age segments."""
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
    seen = set()
    for row in idx.age_segments:
        seg_range = row.get("_age_range")
        if not seg_range:
            continue
        seg_min, seg_max = seg_range
        if seg_min <= target_max and seg_max >= target_min:
            fn = row.get("full_name", "")
            if fn in seen:
                continue
            seen.add(fn)
            results.append({"segment": row, "confidence": 1.0})
    return results[:15]


def match_gender(gender_str: str) -> List[dict]:
    if not gender_str:
        return []
    idx = _get_index()
    lower = gender_str.lower()
    results = []
    target = None
    if "female" in lower:
        target = "female"
    elif "male" in lower and "female" not in lower:
        target = "male"

    for row in idx.gender_segments:
        leaf = row.get("name", "").lower()
        if target and leaf == target:
            results.append({"segment": row, "confidence": 1.0})
        elif target is None and "all" not in lower:
            results.append({"segment": row, "confidence": 0.50})
    return results


def match_location(state_name: str) -> List[dict]:
    """Match ARI primary_state to TU state segments."""
    if not state_name:
        return []
    idx = _get_index()
    state_lower = state_name.strip().lower()
    for full, row in idx.state_by_name.items():
        if full.lower() == state_lower:
            return [{"segment": row, "confidence": 1.0}]
    return []


def match_income(income_str: str) -> List[dict]:
    """Parse ARI income range and find overlapping TU income tiers."""
    if not income_str:
        return []
    idx = _get_index()

    m = re.search(r"\$\s*([\d,.]+)\s*[kK]?\s*[-–]\s*\$\s*([\d,.]+)\s*[kK]?", income_str)
    if not m:
        # Single-sided like "$100K+"
        m_plus = re.search(r"\$\s*([\d,.]+)\s*[kK]?\s*\+", income_str)
        if not m_plus:
            return []
        target_min = _parse_dollar(m_plus.group(1))
        target_max = float("inf")
    else:
        target_min = _parse_dollar(m.group(1))
        target_max = _parse_dollar(m.group(2))

    results = []
    seen = set()
    for row in idx.income_segments:
        leaf = row.get("name", "")
        if leaf in seen:
            continue
        # Parse "$100,000 - $124,999" or "$200,000+"
        nums = re.findall(r"\$\s*([\d,]+)", leaf)
        if not nums:
            continue
        if "+" in leaf:
            seg_min = float(nums[0].replace(",", ""))
            seg_max = float("inf")
        elif len(nums) >= 2:
            seg_min = float(nums[0].replace(",", ""))
            seg_max = float(nums[1].replace(",", ""))
        else:
            continue
        if seg_min <= target_max and seg_max >= target_min:
            seen.add(leaf)
            results.append({"segment": row, "confidence": 0.90})
    return results[:10]


def _parse_dollar(s: str) -> float:
    s = s.replace(",", "")
    val = float(s)
    if val < 1000:
        val *= 1000
    return val


def match_education(edu_str: str) -> List[dict]:
    if not edu_str:
        return []
    idx = _get_index()
    lower = edu_str.lower()
    include_above = "or above" in lower or "or higher" in lower or "+" in lower

    # TU level segments (leaf names):
    #   "Highest Education Achieved - High School"
    #   "Highest Education Achieved - Some College"
    #   "Highest Education Achieved - College Graduates"
    #   "Highest Education Achieved - Graduate School Graduates"
    # (label, input_keywords, segment_match_keywords)
    edu_levels = [
        ("high school", ["high school"], ["high school"]),
        ("some college", ["some college"], ["some college"]),
        ("college", ["college", "bachelor"], ["college graduates"]),
        ("graduate", ["graduate", "master", "doctorate", "phd"], ["graduate school"]),
    ]

    target_seg_kws = []
    for i, (label, input_kws, seg_kws) in enumerate(edu_levels):
        if any(kw in lower for kw in input_kws):
            if include_above:
                # Take seg_kws of this level and all higher levels
                for j in range(i, len(edu_levels)):
                    target_seg_kws.extend(edu_levels[j][2])
            else:
                target_seg_kws.extend(seg_kws)
            break

    if not target_seg_kws:
        return []

    results = []
    seen = set()
    for row in idx.education_segments:
        leaf_lower = row.get("name", "").lower()
        for kw in target_seg_kws:
            if kw in leaf_lower:
                fn = row.get("full_name", "")
                if fn not in seen:
                    seen.add(fn)
                    results.append({"segment": row, "confidence": 0.85})
                break
    return results[:10]


def match_marital(demographics_list: list) -> List[dict]:
    if not demographics_list:
        return []
    idx = _get_index()
    text = " ".join(d for d in demographics_list if isinstance(d, str)).lower()

    results = []
    for row in idx.marital_segments:
        leaf_lower = row.get("name", "").lower()
        if leaf_lower in text:
            pct_match = re.search(r"(\d+)%[^%]*?" + re.escape(leaf_lower), text)
            conf = 0.80 if (pct_match and int(pct_match.group(1)) >= 30) else 0.60
            results.append({"segment": row, "confidence": conf})
    return results


def match_children(demographics_list: list) -> List[dict]:
    if not demographics_list:
        return []
    idx = _get_index()
    has_children = False
    for demo in demographics_list:
        lower = demo.lower() if isinstance(demo, str) else ""
        if "children" not in lower:
            continue
        pct = re.search(r"(\d+)%", demo)
        if not pct:
            continue
        if "do not" in lower or "no children" in lower:
            continue
        if int(pct.group(1)) >= 30:
            has_children = True
            break

    if not has_children:
        return []

    # Pick "Children in Household" presence-style segments. The granular
    # age/gender breakdowns are noisy, so cap at 10.
    results = []
    seen = set()
    for row in idx.children_segments:
        fn = row.get("full_name", "")
        if fn in seen:
            continue
        seen.add(fn)
        results.append({"segment": row, "confidence": 0.70})
        if len(results) >= 10:
            break
    return results


def match_language(language_recs: list) -> List[dict]:
    """Match ARI language recs to TU Language Spoken / Spanish-Language Media."""
    if not language_recs:
        return []
    idx = _get_index()

    spanish_pct = 0
    for rec in language_recs:
        if not isinstance(rec, dict):
            continue
        for lang in rec.get("languages", []) or []:
            if not isinstance(lang, dict):
                continue
            if (lang.get("language", "") or "").lower().startswith("spanish"):
                spanish_pct = max(spanish_pct, int(lang.get("percentage", 0) or 0))

    if spanish_pct < 20:
        return []

    results = []
    seen = set()
    for row in idx.language_segments:
        fn = row.get("full_name", "")
        if fn in seen:
            continue
        leaf_lower = row.get("name", "").lower()
        if "spanish" in leaf_lower or "spanish" in fn.lower():
            seen.add(fn)
            results.append({"segment": row, "confidence": 0.80})
    return results[:10]


def _keyword_match(traits: List[str], segments: List[dict]) -> List[dict]:
    """Score segments by keyword overlap with a list of trait/interest strings.

    Returns deduplicated matches sorted by confidence descending.
    """
    results = []
    seen = set()
    for trait in traits:
        if not trait:
            continue
        trait_kws = _tokenize(trait)
        if not trait_kws:
            continue
        for seg in segments:
            fn = seg.get("full_name", "")
            if fn in seen:
                continue
            leaf = seg.get("name", "")
            seg_kws = _tokenize(leaf)
            if not seg_kws:
                continue
            overlap = trait_kws & seg_kws
            if not overlap:
                continue
            score = min(len(overlap) / min(len(trait_kws), len(seg_kws)), 1.0)
            if score >= INTEREST_MATCH_THRESHOLD:
                seen.add(fn)
                results.append({
                    "segment": seg,
                    "confidence": round(score, 2),
                    "source_trait": trait,
                })
    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results


def match_interests_via_index(interest_list: List[str]) -> List[dict]:
    if not interest_list:
        return []
    idx = _get_index()
    results = []
    seen_segments = set()

    for interest in interest_list:
        kws = _tokenize(interest)
        if not kws:
            results.append({"input": interest, "matched": False, "confidence": 0.0})
            continue

        candidate_hits: Dict[str, Tuple[int, dict]] = {}
        for kw in kws:
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
        had_match = False
        for key, (hits, seg) in candidate_hits.items():
            if key in seen_segments:
                continue
            hit_ratio = min(hits / len(kws), 1.0)
            seg_name_lower = seg.get("name", "").lower()
            bonus = 0.20 if interest_lower in seg_name_lower else 0.0
            score = min(hit_ratio + bonus, 1.0)
            if score >= INTEREST_MATCH_THRESHOLD:
                seen_segments.add(key)
                had_match = True
                results.append({
                    "segment": seg,
                    "confidence": round(score, 2),
                    "input": interest,
                    "matched": True,
                })

        if not had_match:
            results.append({"input": interest, "matched": False, "confidence": 0.0})

    matched = [r for r in results if r.get("matched")]
    matched.sort(key=lambda x: x["confidence"], reverse=True)
    unmatched = [r for r in results if not r.get("matched")]
    return matched[:15] + unmatched


def match_taxonomy(industry: str) -> List[dict]:
    if not industry:
        return []
    idx = _get_index()
    industry_kws = _tokenize(industry)
    if not industry_kws:
        return []

    candidate_hits: Dict[str, Tuple[int, dict]] = {}
    for kw in industry_kws:
        for seg in idx.keyword_index.get(kw, []):
            key = seg.get("full_name", seg.get("name"))
            if key in candidate_hits:
                candidate_hits[key] = (candidate_hits[key][0] + 1, seg)
            else:
                candidate_hits[key] = (1, seg)

    results = []
    for key, (hits, seg) in candidate_hits.items():
        ratio = min(hits / len(industry_kws), 1.0)
        if ratio >= INTEREST_MATCH_THRESHOLD:
            results.append({"segment": seg, "confidence": round(ratio, 2)})
    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results[:10]


def match_activities(activities_list: list) -> List[dict]:
    if not activities_list:
        return []
    idx = _get_index()
    traits_by_qvi = []
    for item in activities_list:
        if isinstance(item, dict):
            traits_by_qvi.append((item.get("trait", ""), item.get("qvi", 100)))
        elif isinstance(item, str):
            traits_by_qvi.append((item, 100))

    results = []
    seen = set()
    for trait, qvi in traits_by_qvi:
        if not trait:
            continue
        kws = _tokenize(trait)
        if not kws:
            continue
        candidate_hits: Dict[str, Tuple[int, dict]] = {}
        for kw in kws:
            for seg in idx.keyword_index.get(kw, []):
                key = seg.get("full_name")
                if key in candidate_hits:
                    candidate_hits[key] = (candidate_hits[key][0] + 1, seg)
                else:
                    candidate_hits[key] = (1, seg)
        for key, (hits, seg) in candidate_hits.items():
            if key in seen:
                continue
            ratio = min(hits / len(kws), 1.0)
            qvi_boost = min((qvi - 100) / 400, 0.15) if qvi > 100 else 0
            score = min(ratio + qvi_boost, 1.0)
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


def match_truaudience_persona(values_list: list, psych_drivers_list: list) -> List[dict]:
    """Match values + psychographic drivers against TruAudience persona names."""
    idx = _get_index()
    if not idx.truaudience_segments:
        return []
    traits = []
    for item in (values_list or []):
        if isinstance(item, dict) and item.get("trait"):
            traits.append(item["trait"])
    for item in (psych_drivers_list or []):
        if isinstance(item, dict) and item.get("trait"):
            traits.append(item["trait"])
    if not traits:
        return []

    matches = _keyword_match(traits, idx.truaudience_segments)
    return matches[:10]


def match_automotive(interest_list: List[str], activities_list: list) -> List[dict]:
    idx = _get_index()
    if not idx.automotive_segments:
        return []
    traits = list(interest_list or [])
    for item in (activities_list or []):
        if isinstance(item, dict) and item.get("trait"):
            traits.append(item["trait"])
        elif isinstance(item, str):
            traits.append(item)
    return _keyword_match(traits, idx.automotive_segments)[:10]


def match_consumer_finance(industry: str, audience_insights: dict) -> List[dict]:
    idx = _get_index()
    if not idx.consumer_finance_segments:
        return []
    traits: List[str] = []
    if industry:
        traits.append(industry)
    for item in (audience_insights.get("values") or []):
        if isinstance(item, dict) and item.get("trait"):
            traits.append(item["trait"])
    for item in (audience_insights.get("psychological_drivers") or []):
        if isinstance(item, dict) and item.get("trait"):
            traits.append(item["trait"])
    return _keyword_match(traits, idx.consumer_finance_segments)[:10]


def match_home_property(audience_insights: dict, demographics: list) -> List[dict]:
    idx = _get_index()
    if not idx.home_property_segments:
        return []
    traits: List[str] = []
    for item in (audience_insights.get("activities") or []):
        if isinstance(item, dict) and item.get("trait"):
            traits.append(item["trait"])
    for item in (audience_insights.get("daily_routines") or []):
        if isinstance(item, dict) and item.get("trait"):
            traits.append(item["trait"])
    for d in demographics or []:
        if isinstance(d, str):
            traits.append(d)
    return _keyword_match(traits, idx.home_property_segments)[:10]


def match_political(demographics: list, audience_insights: dict) -> List[dict]:
    """Only fires when politically-related signals are present in the brief."""
    idx = _get_index()
    if not idx.political_segments:
        return []
    text_blobs: List[str] = []
    for d in demographics or []:
        if isinstance(d, str):
            text_blobs.append(d)
    for item in (audience_insights.get("values") or []):
        if isinstance(item, dict) and item.get("trait"):
            text_blobs.append(item["trait"])
    for item in (audience_insights.get("psychological_drivers") or []):
        if isinstance(item, dict) and item.get("trait"):
            text_blobs.append(item["trait"])

    full_text = " ".join(text_blobs).lower()
    political_signals = ("political", "politics", "republican", "democrat",
                         "conservative", "liberal", "civic", "voter")
    if not any(sig in full_text for sig in political_signals):
        return []

    return _keyword_match(text_blobs, idx.political_segments)[:10]


def match_life_events(demographics: list) -> List[dict]:
    idx = _get_index()
    if not idx.life_events_segments or not demographics:
        return []
    traits = [d for d in demographics if isinstance(d, str)]
    return _keyword_match(traits, idx.life_events_segments)[:10]


# ---------- High-level preview ----------


def _match_single_segment(
    segment: dict,
    industry: str,
    audience_insights: dict,
    language_recs: list,
) -> dict:
    targeting = segment.get("targeting_params", {})
    demographics = audience_insights.get("demographics", []) or []
    values = audience_insights.get("values", []) or []
    psych_drivers = audience_insights.get("psychological_drivers", []) or []
    activities = audience_insights.get("activities", []) or []
    daily_routines = audience_insights.get("daily_routines", []) or []

    age_results = match_age_range(targeting.get("age_range", ""))
    gender_results = match_gender(targeting.get("gender_targeting", "All"))
    location_results = match_location(segment.get("primary_state", ""))
    income_results = match_income(targeting.get("income_targeting", ""))
    education_results = match_education(targeting.get("education_targeting", ""))
    marital_results = match_marital(demographics)
    children_results = match_children(demographics)
    language_results = match_language(language_recs)
    interest_results = match_interests_via_index(
        segment.get("interest_categories", []) or []
    )
    taxonomy_results = match_taxonomy(industry)
    activities_results = match_activities(activities)
    routines_results = match_daily_routines(daily_routines)
    truaudience_results = match_truaudience_persona(values, psych_drivers)

    automotive_results = match_automotive(
        segment.get("interest_categories", []) or [], activities
    )
    consumer_finance_results = match_consumer_finance(industry, audience_insights)
    home_property_results = match_home_property(audience_insights, demographics)
    political_results = match_political(demographics, audience_insights)
    life_events_results = match_life_events(demographics)

    ethnic_kw = generate_ethnic_keywords(segment, language_recs)

    match_data = {
        "age": age_results,
        "gender": gender_results,
        "location": location_results,
        "interests": interest_results,
        "taxonomy": taxonomy_results,
        "income": income_results,
        "education": education_results,
        "language": language_results,
        "area_type": [],
        "children": children_results,
        "marital": marital_results,
        "activities": activities_results,
        "daily_routines": routines_results,
        "mosaic_persona": truaudience_results,  # surfaced under shared key
        "attitudes": [],
        "ethnic_keywords": ethnic_kw,
        # TU-shared with Epsilon
        "automotive": automotive_results,
        "health": [],
        "trigger_events": [],
        # TU-exclusive
        "consumer_finance": consumer_finance_results,
        "home_property": home_property_results,
        "political": political_results,
        "life_events": life_events_results,
    }

    warnings = []
    unmatched = [
        r.get("input", "?") for r in interest_results
        if isinstance(r, dict) and not r.get("matched")
    ]
    if unmatched:
        warnings.append(f"Unmatched interests: {', '.join(unmatched)}")

    return {
        "segment_name": segment.get("name", "Unnamed"),
        "segment_data": segment,
        "matches": match_data,
        "summary": {
            "age_matches": len(age_results),
            "gender_matches": len(gender_results),
            "location_matches": len(location_results),
            "interest_matches": len([r for r in interest_results if r.get("matched")]),
            "interest_total": len(segment.get("interest_categories", []) or []),
            "taxonomy_matches": len(taxonomy_results),
            "income_matches": len(income_results),
            "education_matches": len(education_results),
            "language_matches": len(language_results),
            "area_matches": 0,
            "children_matches": len(children_results),
            "marital_matches": len(marital_results),
            "activities_matches": len(activities_results),
            "routines_matches": len(routines_results),
            "mosaic_matches": len(truaudience_results),
            "attitude_matches": 0,
            "ethnic_keyword_count": len(ethnic_kw.get("keywords", [])),
            "automotive_matches": len(automotive_results),
            "health_matches": 0,
            "trigger_matches": 0,
            "consumer_finance_matches": len(consumer_finance_results),
            "home_property_matches": len(home_property_results),
            "political_matches": len(political_results),
            "life_events_matches": len(life_events_results),
        },
        "warnings": warnings,
    }


def preview_all_segments(session_state: Dict[str, Any]) -> List[dict]:
    """Generate TransUnion mapping previews for ARI audience segments."""
    load_transunion_taxonomy()
    idx = _get_index()
    if not idx.loaded:
        logger.error("No TransUnion taxonomy loaded")
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
