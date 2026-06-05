"""
Aristotle Digital Taxonomy mapper, preview only.

Mirrors the transunion_mapper.py pattern. Reads the unified
data/aristotle_taxonomy.csv (9 marketing sheets + Top Segments + Mobile &
Cookie Reach) and exposes the standard preview_all_segments() entry point.
"""

import csv
import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from core.generations import resolve_generation_age_range

logger = logging.getLogger(__name__)

ARISTOTLE_CSV_PATH = Path("data/aristotle_taxonomy.csv")

# Reuse from openx_mapper
from core.openx_mapper import ARI_SEGMENT_LABELS, generate_ethnic_keywords

# ---------- Tokenization ----------

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

# Sheets fed into the keyword index for free-text interest/industry matching
KEYWORD_INDEX_SHEETS = {
    "Consumer", "Affluent", "Auto", "Medical", "Holiday",
    "Top Segments", "Mobile & Cookie Reach",
}


def _tokenize(text: str) -> Set[str]:
    tokens = set(re.split(r"[\s&/,>:;()\-–]+", text.lower()))
    tokens -= _STOP_WORDS
    tokens -= _QUALITY_WORDS
    tokens.discard("")
    return {t for t in tokens if len(t) > 1 and not t.isdigit()}


# ---------- AristotleIndex ----------


class AristotleIndex:
    def __init__(self):
        self.all_rows: List[dict] = []

        # Demographics
        self.age_segments: List[dict] = []
        self.gender_segments: List[dict] = []
        self.education_segments: List[dict] = []
        self.marital_segments: List[dict] = []
        self.ethnicity_segments: List[dict] = []
        self.children_segments: List[dict] = []

        # Sheet-specific buckets
        self.automotive_segments: List[dict] = []
        self.medical_segments: List[dict] = []
        self.political_segments: List[dict] = []
        self.donor_segments: List[dict] = []
        self.holiday_segments: List[dict] = []
        self.business_segments: List[dict] = []
        self.government_segments: List[dict] = []
        self.education_alumni_segments: List[dict] = []
        self.financial_segments: List[dict] = []
        self.top_segments: List[dict] = []

        # Keyword inverted index for interest / industry matching
        self.keyword_index: Dict[str, List[dict]] = {}

    @property
    def loaded(self) -> bool:
        return bool(self.all_rows)


def _parse_age_range_from_segment(name: str) -> Optional[Tuple[int, int]]:
    """Parse age ranges from segment names like:
    "Age - Adult 25-34", "Age - Female 35-44", "Age - Adult 75+", "Age - Boomers".
    Returns (min, max) or None for non-range segments.
    """
    m = re.search(r"(\d{1,2})\s*[-–]\s*(\d{1,2})", name)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"(\d{1,2})\s*\+", name)
    if m:
        return int(m.group(1)), 99
    gen_range = resolve_generation_age_range(name)
    if gen_range:
        return gen_range
    if "traditionalist" in name.lower():
        return 80, 99
    return None


_ETHNICITY_KEY_MAP = {
    # detect_target_race output → Aristotle leaf substring (lowercase contains)
    "Asian": "asian",
    "Hispanic or Latino": "hispanic",
    "Black or African American": "african american",
    "White": "caucasian",
}


def _build_index(rows: List[dict]) -> AristotleIndex:
    idx = AristotleIndex()
    idx.all_rows = rows

    for row in rows:
        sheet = row.get("category", "")  # CSV "Sheet" → row "category"
        sub_cat = (row.get("sub_category", "") or "").strip()
        leaf = row.get("name", "")
        leaf_lower = leaf.lower()
        sub_lower = sub_cat.lower()

        # --- Top Segments: curated highlights ---
        if sheet == "Top Segments":
            idx.top_segments.append(row)

        # --- Consumer Demographics: split into age/gender/education/marital/ethnicity ---
        if sheet == "Consumer" and sub_lower == "demographics":
            if leaf_lower.startswith("age - "):
                parsed = _parse_age_range_from_segment(leaf)
                if parsed:
                    row["_age_range"] = parsed
                    idx.age_segments.append(row)
                if "female" in leaf_lower or " male " in (" " + leaf_lower + " "):
                    idx.gender_segments.append(row)
                continue
            if leaf_lower.startswith("ethnicity - "):
                idx.ethnicity_segments.append(row)
                continue
            if leaf_lower.startswith("education - "):
                idx.education_segments.append(row)
                continue
            if leaf_lower.startswith("marital status - "):
                idx.marital_segments.append(row)
                continue

        # --- Consumer Family ---
        if sheet == "Consumer" and sub_lower == "family":
            idx.children_segments.append(row)

        # --- Consumer Financial / Affluent Financial ---
        if sheet in ("Consumer", "Affluent") and sub_lower == "financial":
            idx.financial_segments.append(row)

        # --- Sheet-level buckets ---
        if sheet == "Auto":
            idx.automotive_segments.append(row)
        elif sheet == "Medical":
            idx.medical_segments.append(row)
        elif sheet == "Political":
            idx.political_segments.append(row)
        elif sheet == "Holiday":
            idx.holiday_segments.append(row)
        elif sheet == "Business":
            idx.business_segments.append(row)
        elif sheet == "Government":
            idx.government_segments.append(row)
        elif sheet == "Education":
            idx.education_alumni_segments.append(row)
        elif sheet == "Affluent" and "donor" in sub_lower:
            idx.donor_segments.append(row)

        # --- Keyword index ---
        if sheet in KEYWORD_INDEX_SHEETS:
            tokens = _tokenize(leaf)
            for tok in tokens:
                idx.keyword_index.setdefault(tok, []).append(row)

    logger.info(
        "AristotleIndex: %d rows, %d age, %d gender, %d edu, %d marital, "
        "%d ethnicity, %d children, %d auto, %d medical, %d political, "
        "%d donors, %d holiday, %d business, %d gov, %d edu_alumni, "
        "%d financial, %d top, %d keywords",
        len(rows), len(idx.age_segments), len(idx.gender_segments),
        len(idx.education_segments), len(idx.marital_segments),
        len(idx.ethnicity_segments), len(idx.children_segments),
        len(idx.automotive_segments), len(idx.medical_segments),
        len(idx.political_segments), len(idx.donor_segments),
        len(idx.holiday_segments), len(idx.business_segments),
        len(idx.government_segments), len(idx.education_alumni_segments),
        len(idx.financial_segments), len(idx.top_segments),
        len(idx.keyword_index),
    )
    return idx


# ---------- Module-level state ----------

_index: Optional[AristotleIndex] = None


# ---------- Catalog loading ----------


def _load_aristotle_csv(csv_path: Path = None) -> List[dict]:
    path = csv_path or ARISTOTLE_CSV_PATH
    if not path.exists():
        logger.warning("Aristotle CSV not found at %s", path)
        return []

    rows = []
    seen_full = set()
    try:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for csv_row in reader:
                sheet = (csv_row.get("Sheet") or "").strip()
                category = (csv_row.get("Category") or "").strip()
                segment = (csv_row.get("Segment") or "").strip()
                description = (csv_row.get("Description") or "").strip()
                dd_name = (csv_row.get("Data Dictionary Naming") or "").strip()

                if not sheet or not segment:
                    continue

                full_name = f"{sheet} > {category} > {segment}" if category else f"{sheet} > {segment}"
                # Dedupe by (sheet, category, segment, dd_name)
                key = (sheet, category, segment, dd_name)
                if key in seen_full:
                    continue
                seen_full.add(key)

                rows.append({
                    "name": segment,
                    "full_name": full_name,
                    "description": description,
                    "sub_category": category,
                    "category": sheet,
                    "type": "Aristotle",
                    "source": "Aristotle",
                    "aristotle_dd_name": dd_name,
                })
    except Exception as exc:
        logger.error("Failed to load Aristotle CSV: %s", exc)

    logger.info("Loaded %d segments from Aristotle CSV", len(rows))
    return rows


def load_aristotle_taxonomy(csv_path: Path = None) -> List[dict]:
    global _index
    if _index and _index.loaded:
        return _index.all_rows
    rows = _load_aristotle_csv(csv_path)
    _index = _build_index(rows)
    return rows


def _get_index() -> AristotleIndex:
    global _index
    if not _index or not _index.loaded:
        load_aristotle_taxonomy()
    return _index


# ---------- Matchers ----------


def match_age_range(age_str: str) -> List[dict]:
    """Match ARI age range against Aristotle Age - Adult/Female/Male X-Y segments."""
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
    return results[:20]


def match_gender(gender_str: str) -> List[dict]:
    """Return gender-specific Aristotle Age segments when a gender is specified."""
    if not gender_str:
        return []
    idx = _get_index()
    lower = gender_str.lower()
    if "female" in lower:
        target = "female"
    elif "male" in lower and "female" not in lower:
        target = "male"
    else:
        return []

    results = []
    for row in idx.gender_segments:
        if target in row.get("name", "").lower():
            results.append({"segment": row, "confidence": 1.0})
    return results[:10]


def match_education(edu_str: str) -> List[dict]:
    """Match ARI education targeting against Aristotle Education - * segments."""
    if not edu_str:
        return []
    idx = _get_index()
    lower = edu_str.lower()
    include_above = "or above" in lower or "or higher" in lower or "+" in lower

    # (label, input_keywords, segment_match_keywords)
    edu_levels = [
        ("high school", ["high school"], ["high school"]),
        ("vocational", ["vocational", "technical"], ["vocational"]),
        ("college", ["college", "bachelor"], ["college graduate"]),
        ("graduate", ["graduate", "master", "doctorate", "phd"], ["graduate school"]),
    ]

    target_seg_kws = []
    for i, (label, input_kws, seg_kws) in enumerate(edu_levels):
        if any(kw in lower for kw in input_kws):
            if include_above:
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
        if "married" in leaf_lower and "married" in text:
            results.append({"segment": row, "confidence": 0.80})
        elif "single" in leaf_lower and "single" in text:
            results.append({"segment": row, "confidence": 0.70})
    return results


def match_children(demographics_list: list) -> List[dict]:
    """Match presence of children → Families with Children sub-segments."""
    if not demographics_list:
        return []
    idx = _get_index()
    has_children = False
    for demo in demographics_list:
        if not isinstance(demo, str):
            continue
        lower = demo.lower()
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


def match_ethnicity(segment: dict) -> List[dict]:
    """Use detect_target_race to map ARI's ethnic affinity to ETHNIC_* segments."""
    from core.behavioral_adjustments import detect_target_race

    idx = _get_index()
    race = detect_target_race(segment)
    if not race:
        return []
    target_kw = _ETHNICITY_KEY_MAP.get(race)
    if not target_kw:
        return []
    target_kw = target_kw.lower()
    results = []
    for row in idx.ethnicity_segments:
        leaf_lower = row.get("name", "").lower()
        if target_kw in leaf_lower:
            results.append({"segment": row, "confidence": 1.0})
    return results


def match_income(income_str: str) -> List[dict]:
    """Aristotle's Financial segments are descriptive labels, not dollar tiers.
    Use keyword overlap with the income range string as a soft match."""
    if not income_str:
        return []
    idx = _get_index()
    lower = income_str.lower()
    is_high = (
        "$100" in lower or "$150" in lower or "$200" in lower or "100k" in lower
        or "150k" in lower or "200k" in lower or "+ " in lower
    )

    results = []
    seen = set()
    for row in idx.financial_segments:
        leaf_lower = row.get("name", "").lower()
        if is_high and ("affluent" in leaf_lower or "premium" in leaf_lower
                        or "wealth" in leaf_lower or "high" in leaf_lower):
            fn = row.get("full_name", "")
            if fn not in seen:
                seen.add(fn)
                results.append({"segment": row, "confidence": 0.65})
    return results[:10]


def _keyword_match(traits: List[str], segments: List[dict],
                   conf_floor: float = INTEREST_MATCH_THRESHOLD) -> List[dict]:
    """Score segments by keyword overlap with trait strings; deduped + sorted."""
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
            if score >= conf_floor:
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
    kws = _tokenize(industry)
    if not kws:
        return []

    candidate_hits: Dict[str, Tuple[int, dict]] = {}
    for kw in kws:
        for seg in idx.keyword_index.get(kw, []):
            key = seg.get("full_name", seg.get("name"))
            if key in candidate_hits:
                candidate_hits[key] = (candidate_hits[key][0] + 1, seg)
            else:
                candidate_hits[key] = (1, seg)

    results = []
    for key, (hits, seg) in candidate_hits.items():
        ratio = min(hits / len(kws), 1.0)
        if ratio >= INTEREST_MATCH_THRESHOLD:
            results.append({"segment": seg, "confidence": round(ratio, 2)})
    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results[:10]


def match_activities(activities_list: list) -> List[dict]:
    if not activities_list:
        return []
    idx = _get_index()
    traits = []
    for item in activities_list:
        if isinstance(item, dict):
            traits.append((item.get("trait", ""), item.get("qvi", 100)))
        elif isinstance(item, str):
            traits.append((item, 100))

    results = []
    seen = set()
    for trait, qvi in traits:
        if not trait:
            continue
        trait_kws = _tokenize(trait)
        if not trait_kws:
            continue
        candidate_hits: Dict[str, Tuple[int, dict]] = {}
        for kw in trait_kws:
            for seg in idx.keyword_index.get(kw, []):
                key = seg.get("full_name")
                if key in candidate_hits:
                    candidate_hits[key] = (candidate_hits[key][0] + 1, seg)
                else:
                    candidate_hits[key] = (1, seg)
        for key, (hits, seg) in candidate_hits.items():
            if key in seen:
                continue
            ratio = min(hits / len(trait_kws), 1.0)
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


def match_top_segments_persona(values_list: list, psych_drivers_list: list) -> List[dict]:
    """Match values + psych drivers against the curated Top Segments list."""
    idx = _get_index()
    if not idx.top_segments:
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
    return _keyword_match(traits, idx.top_segments)[:10]


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


def match_medical(psych_drivers_list: list, activities_list: list) -> List[dict]:
    """Match health/wellness psychographic drivers to Medical sheet segments."""
    idx = _get_index()
    if not idx.medical_segments:
        return []
    traits = []
    for item in (psych_drivers_list or []):
        if isinstance(item, dict) and item.get("trait"):
            traits.append(item["trait"])
    for item in (activities_list or []):
        if isinstance(item, dict) and item.get("trait"):
            traits.append(item["trait"])
    return _keyword_match(traits, idx.medical_segments)[:10]


def match_political(demographics: list, audience_insights: dict) -> List[dict]:
    """Gated political matcher — only fires when brief signals politics."""
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


def match_donors(audience_insights: dict, demographics: list) -> List[dict]:
    """Donor segments — fire when affluence/charity signals present."""
    idx = _get_index()
    if not idx.donor_segments:
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
    affluence_signals = ("donor", "charit", "philanthrop", "affluent",
                         "wealth", "high income", "luxury", "premium")
    if not any(sig in full_text for sig in affluence_signals):
        return []
    return _keyword_match(text_blobs, idx.donor_segments)[:10]


def match_holiday(industry: str, interest_list: List[str]) -> List[dict]:
    """Match seasonal/holiday traits."""
    idx = _get_index()
    if not idx.holiday_segments:
        return []
    text_blobs: List[str] = list(interest_list or [])
    if industry:
        text_blobs.append(industry)
    full_text = " ".join(text_blobs).lower()
    holiday_signals = ("holiday", "season", "gift", "halloween", "christmas",
                       "easter", "valentine", "thanksgiving", "back to school",
                       "graduation", "celebration")
    if not any(sig in full_text for sig in holiday_signals):
        return []
    return _keyword_match(text_blobs, idx.holiday_segments)[:10]


def match_education_alumni(audience_insights: dict, interest_list: List[str]) -> List[dict]:
    """Match audience traits against Education & Alumni segments
    (alumni associations, sports fans, education groups)."""
    idx = _get_index()
    if not idx.education_alumni_segments:
        return []
    text_blobs: List[str] = list(interest_list or [])
    for item in (audience_insights.get("activities") or []):
        if isinstance(item, dict) and item.get("trait"):
            text_blobs.append(item["trait"])
    for item in (audience_insights.get("daily_routines") or []):
        if isinstance(item, dict) and item.get("trait"):
            text_blobs.append(item["trait"])
    return _keyword_match(text_blobs, idx.education_alumni_segments)[:10]


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
    interest_list = segment.get("interest_categories", []) or []

    age_results = match_age_range(targeting.get("age_range", ""))
    gender_results = match_gender(targeting.get("gender_targeting", "All"))
    income_results = match_income(targeting.get("income_targeting", ""))
    education_results = match_education(targeting.get("education_targeting", ""))
    marital_results = match_marital(demographics)
    children_results = match_children(demographics)
    ethnicity_results = match_ethnicity(segment)

    interest_results = match_interests_via_index(interest_list)
    taxonomy_results = match_taxonomy(industry)
    activities_results = match_activities(activities)
    routines_results = match_daily_routines(daily_routines)
    top_results = match_top_segments_persona(values, psych_drivers)

    automotive_results = match_automotive(interest_list, activities)
    medical_results = match_medical(psych_drivers, activities)
    political_results = match_political(demographics, audience_insights)
    donor_results = match_donors(audience_insights, demographics)
    holiday_results = match_holiday(industry, interest_list)
    education_alumni_results = match_education_alumni(audience_insights, interest_list)

    ethnic_kw = generate_ethnic_keywords(segment, language_recs)

    match_data = {
        "age": age_results,
        "gender": gender_results,
        "location": [],
        "area_type": [],
        "interests": interest_results,
        "taxonomy": taxonomy_results,
        "income": income_results,
        "education": education_results,
        "language": [],
        "children": children_results,
        "marital": marital_results,
        "activities": activities_results,
        "daily_routines": routines_results,
        "mosaic_persona": top_results,  # surfaced via shared key (label is "Aristotle Top Segments")
        "attitudes": [],
        "ethnic_keywords": ethnic_kw,
        # Shared with other preview sources
        "automotive": automotive_results,
        "health": [],
        "trigger_events": [],
        "political": political_results,
        # Aristotle-exclusive
        "ethnicity": ethnicity_results,
        "medical": medical_results,
        "donors": donor_results,
        "holiday": holiday_results,
        "education_alumni": education_alumni_results,
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
            "location_matches": 0,
            "interest_matches": len([r for r in interest_results if r.get("matched")]),
            "interest_total": len(interest_list),
            "taxonomy_matches": len(taxonomy_results),
            "income_matches": len(income_results),
            "education_matches": len(education_results),
            "language_matches": 0,
            "area_matches": 0,
            "children_matches": len(children_results),
            "marital_matches": len(marital_results),
            "activities_matches": len(activities_results),
            "routines_matches": len(routines_results),
            "mosaic_matches": len(top_results),
            "attitude_matches": 0,
            "ethnic_keyword_count": len(ethnic_kw.get("keywords", [])),
            "automotive_matches": len(automotive_results),
            "health_matches": 0,
            "trigger_matches": 0,
            "political_matches": len(political_results),
            "ethnicity_matches": len(ethnicity_results),
            "medical_matches": len(medical_results),
            "donor_matches": len(donor_results),
            "holiday_matches": len(holiday_results),
            "education_alumni_matches": len(education_alumni_results),
        },
        "warnings": warnings,
    }


def preview_all_segments(session_state: Dict[str, Any]) -> List[dict]:
    """Generate Aristotle mapping previews for ARI audience segments."""
    load_aristotle_taxonomy()
    idx = _get_index()
    if not idx.loaded:
        logger.error("No Aristotle taxonomy loaded")
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
