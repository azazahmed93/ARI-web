"""
Maps ARI session-state data to OpenX OpenAudience API parameters.

Uses a TaxonomyIndex with keyword-based matching instead of fuzzy matching.
Handles segment catalog loading from the OpenXSelect Taxonomy CSV,
structured matching for demographics/interests/psychographics, and audience
definition building.
"""

import csv
import json
import os
import re
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from core.openx_service import OpenXService, OPENX_PROVIDER_ID

logger = logging.getLogger(__name__)

# ---------- Constants ----------

# Path to the OpenXSelect Taxonomy CSV (downloaded from OpenX UI)
TAXONOMY_CSV_PATH = Path("data/openx_taxonomy.csv")

# ARI segment labels in display order
ARI_SEGMENT_LABELS = [
    "Core Audience",
    "Primary Growth",
    "Secondary Growth",
    "Emerging Audience",
]

# Categories whose segments feed the keyword index for interest matching
INTEREST_INDEX_CATEGORIES = {
    "Activities/Interests",
    "Sports",
    "Technology & Computing",
    "Hobbies & Interests",
    "Enthusiast",
    "Lifestyle",
    "Food and Beverage",
    "Travel",
    "Education",  # interest-type Education, not Advanced Demographics
}

# Categories used for taxonomy / industry matching
INDUSTRY_CATEGORIES = {
    "Activities/Interests",
    "Sports",
    "Technology & Computing",
    "Hobbies & Interests",
    "Food and Beverage",
    "Travel",
    "Education",
    "Auto",
    "Retailer",
    "Lifestyle",
    "Property/Realty",
    "Occupation",
}

# Words to exclude when building the keyword index
_STOP_WORDS = frozenset({
    "the", "a", "an", "and", "or", "of", "in", "for", "to", "with",
    "by", "on", "at", "is", "are", "was", "were", "has", "have", "had",
    "been", "being", "be", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "than",
    "less", "more", "not", "no", "very", "most", "also", "but",
})

# Quality/confidence level words to strip from keywords
_QUALITY_WORDS = frozenset({
    "high", "low", "medium", "likely", "extremely", "unlikely",
    "accepted", "preferred", "known", "modeled",
})

INTEREST_MATCH_THRESHOLD = 0.40


# ---------- TaxonomyIndex ----------


class TaxonomyIndex:
    """Pre-computed indexes over the OpenXSelect taxonomy for O(1) lookups."""

    def __init__(self):
        self.all_rows: List[dict] = []

        # Exact-lookup dicts
        self.age_by_value: Dict[int, dict] = {}
        self.gender_by_name: Dict[str, dict] = {}
        self.state_by_name: Dict[str, dict] = {}

        # Small-category lists
        self.education_segments: List[dict] = []   # ~10 rows (Advanced Demographics)
        self.income_segments: List[dict] = []      # ~12 rows
        self.lifestage_segments: List[dict] = []   # ~24 rows (includes Marital Status)
        self.children_segments: List[dict] = []    # ~46 rows
        self.language_segments: List[dict] = []    # ~2 rows
        self.area_segments: List[dict] = []        # ~12 rows
        self.mosaic_persona_segments: List[dict] = []  # ~81 rows
        self.attitude_segments: List[dict] = []    # ~15 rows (Tech/Health/Mobile)

        # Keyword inverted index for interest matching
        self.keyword_index: Dict[str, List[dict]] = {}

        # Industry segments (flat list)
        self.industry_segments: List[dict] = []

    @property
    def loaded(self) -> bool:
        return bool(self.all_rows)


def _tokenize(text: str) -> Set[str]:
    """Split text into lowercase keyword tokens, filtering stop/quality words."""
    tokens = set(re.split(r"[\s&/,>:;()\-–]+", text.lower()))
    tokens -= _STOP_WORDS
    tokens -= _QUALITY_WORDS
    tokens.discard("")
    # Filter single-char tokens and pure numbers
    return {t for t in tokens if len(t) > 1 and not t.isdigit()}


def _build_index(rows: List[dict]) -> TaxonomyIndex:
    """Build a TaxonomyIndex from raw taxonomy rows."""
    idx = TaxonomyIndex()
    idx.all_rows = rows

    # Attitude sub-categories we want
    attitude_categories = {"Tech Adoption", "Health and Well Being", "Mobile Usage"}

    for row in rows:
        category = row.get("category", "")
        seg_type = row.get("type", "")
        name = row.get("name", "")

        # --- Exact-lookup indexes ---

        if category == "Age":
            try:
                age_val = int(name.strip())
                idx.age_by_value[age_val] = row
            except (ValueError, TypeError):
                pass

        elif category == "Gender":
            idx.gender_by_name[name] = row

        elif category == "State":
            idx.state_by_name[name] = row

        # --- Small-category lists ---

        # Education demographics (type=Advanced Demographics, not interest)
        elif category == "Education" and seg_type == "Advanced Demographics":
            idx.education_segments.append(row)

        elif category == "Estimated Home Income (EHI)":
            idx.income_segments.append(row)

        elif category == "Lifestage":
            idx.lifestage_segments.append(row)

        elif category == "Presence of Children":
            idx.children_segments.append(row)

        elif category == "Browser Language":
            idx.language_segments.append(row)

        elif category == "Area":
            idx.area_segments.append(row)

        elif category == "Mosaic Persona":
            idx.mosaic_persona_segments.append(row)

        elif category in attitude_categories:
            idx.attitude_segments.append(row)

        # --- Keyword index for interests ---
        # Include interest categories BUT exclude education rows that are demographics
        if category in INTEREST_INDEX_CATEGORIES:
            if category == "Education" and seg_type == "Advanced Demographics":
                pass  # Skip demographic education rows from interest index
            else:
                tokens = _tokenize(name)
                sub_cat = row.get("sub_category", "")
                if sub_cat:
                    tokens |= _tokenize(sub_cat)
                for token in tokens:
                    if token not in idx.keyword_index:
                        idx.keyword_index[token] = []
                    idx.keyword_index[token].append(row)

        # Industry segments
        if category in INDUSTRY_CATEGORIES:
            idx.industry_segments.append(row)

    logger.info(
        "TaxonomyIndex built: %d rows, %d age, %d gender, %d state, "
        "%d education, %d income, %d lifestage, %d children, %d language, "
        "%d area, %d mosaic, %d attitude, %d keywords",
        len(rows), len(idx.age_by_value), len(idx.gender_by_name),
        len(idx.state_by_name), len(idx.education_segments),
        len(idx.income_segments), len(idx.lifestage_segments),
        len(idx.children_segments), len(idx.language_segments),
        len(idx.area_segments), len(idx.mosaic_persona_segments),
        len(idx.attitude_segments), len(idx.keyword_index),
    )
    return idx


# ---------- Module-level state ----------

_index: Optional[TaxonomyIndex] = None


# ---------- Catalog loading ----------


def _load_taxonomy_csv(csv_path: Path = None) -> List[dict]:
    """Load the OpenXSelect Taxonomy CSV into a list of dicts."""
    path = csv_path or TAXONOMY_CSV_PATH
    if not path.exists():
        logger.warning("Taxonomy CSV not found at %s", path)
        return []

    rows = []
    try:
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append({
                    "name": row.get("Segment", "").strip(),
                    "full_name": row.get("Segment Full Name", "").strip(),
                    "description": row.get("Segment Description", "").strip(),
                    "sub_category": row.get("Segment Sub Category", "").strip(),
                    "category": row.get("Segment Category", "").strip(),
                    "type": row.get("Segment Type", "").strip(),
                    "source": row.get("Segment Source", "").strip(),
                })
    except Exception as exc:
        logger.error("Failed to load taxonomy CSV: %s", exc)

    logger.info("Loaded %d segments from taxonomy CSV", len(rows))
    return rows


def load_taxonomy(csv_path: Path = None) -> List[dict]:
    """Load taxonomy and build index. Call once at startup or on first use."""
    global _index

    if _index and _index.loaded:
        return _index.all_rows

    rows = _load_taxonomy_csv(csv_path)
    _index = _build_index(rows)
    return rows


def _get_index() -> TaxonomyIndex:
    """Return the current TaxonomyIndex, loading if needed."""
    global _index
    if not _index or not _index.loaded:
        load_taxonomy()
    return _index


# ---------- Matching helpers ----------


def _parse_age_range(age_str: str) -> Optional[Tuple[int, int]]:
    """Extract (min_age, max_age) from strings like '25-34' or '18-45'."""
    m = re.search(r"(\d{1,2})\s*[-–]\s*(\d{1,2})", age_str)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"(\d{1,2})\+", age_str)
    if m:
        return int(m.group(1)), 99
    return None


# ---------- Core matchers (existing, improved) ----------


def match_age_range(age_str: str) -> List[dict]:
    """Find OpenX age segments covering the ARI age range.

    Uses O(1) dict lookups instead of scanning all age segments.
    Returns boundary segments (min, max) with all_segments_in_range for the
    definition builder.
    """
    target = _parse_age_range(age_str)
    if not target:
        return []

    idx = _get_index()
    in_range = []
    for age_val in range(target[0], target[1] + 1):
        seg = idx.age_by_value.get(age_val)
        if seg:
            in_range.append((age_val, seg))

    if not in_range:
        return []

    in_range.sort(key=lambda x: x[0])

    results = []
    if len(in_range) == 1:
        results.append({"segment": in_range[0][1], "confidence": 1.0})
    else:
        results.append({"segment": in_range[0][1], "confidence": 1.0})
        results.append({"segment": in_range[-1][1], "confidence": 1.0})
        results[0]["all_segments_in_range"] = [s for _, s in in_range]

    return results


def match_gender(gender_str: str) -> List[dict]:
    """Match ARI gender targeting to OpenX gender segments.

    Uses O(1) dict lookup.
    ARI values: 'All', 'Male dominant (93%)', 'Female dominant (68%)'
    """
    idx = _get_index()
    lower = gender_str.lower()

    if "all" in lower:
        return [{"segment": {"name": "All Genders", "full_name": "No gender restriction"},
                 "confidence": 1.0, "note": "No gender filter applied"}]

    # Check "female" before "male" since "female" contains "male"
    if "female" in lower:
        target = "Female"
    elif "male" in lower:
        target = "Male"
    else:
        return [{"segment": {"name": "All Genders", "full_name": "No gender restriction"},
                 "confidence": 1.0, "note": "No gender filter applied"}]

    seg = idx.gender_by_name.get(target)
    if seg:
        return [{"segment": seg, "confidence": 0.95}]

    return [{
        "segment": {"name": f"{target} (inferred)", "full_name": f"Gender > {target}"},
        "confidence": 0.70,
        "note": f"No exact gender segment found; {target} targeting inferred",
    }]


def match_location(state_name: str) -> List[dict]:
    """Match a US state name against the taxonomy State index (O(1) lookup)."""
    if not state_name or state_name == "N/A":
        return []

    idx = _get_index()

    # Try exact match first
    seg = idx.state_by_name.get(state_name)
    if seg:
        return [{"segment": seg, "confidence": 1.0}]

    # Case-insensitive fallback
    for name, s in idx.state_by_name.items():
        if name.lower() == state_name.lower():
            return [{"segment": s, "confidence": 0.95}]

    return []


# ---------- New matchers ----------


def match_income(income_str: str) -> List[dict]:
    """Match ARI income targeting (e.g. '$50K-$100K') to EHI segments.

    Mapping: <$50K → Low, $50K-$100K → Medium, >$100K → High
    Prefers Income Percentile (National), also includes County EHI Index.
    """
    if not income_str:
        return []

    idx = _get_index()
    lower = income_str.lower().replace(",", "")

    # Parse dollar amounts (e.g. "$50K-$100K" → [50, 100])
    amounts = [int(x) for x in re.findall(r"(\d+)k", lower)]
    if not amounts:
        # Try raw dollar amounts like "$50000"
        amounts = [int(x) // 1000 for x in re.findall(r"\$(\d+)", lower)]

    if not amounts:
        return []

    # Determine target income level(s)
    levels = set()
    min_val = min(amounts)
    max_val = max(amounts) if len(amounts) > 1 else min_val

    if "+" in income_str:
        # Open-ended range like "$100K+"
        if min_val >= 100:
            levels.add("High")
        elif min_val >= 50:
            levels.update(["Medium", "High"])
        else:
            levels.update(["Low", "Medium", "High"])
    else:
        if min_val < 50:
            levels.add("Low")
        if (min_val <= 100 and max_val >= 50) or (50 <= min_val <= 100):
            levels.add("Medium")
        if max_val > 100:
            levels.add("High")

    results = []
    for seg in idx.income_segments:
        name = seg["name"]
        for level in levels:
            if level in name and "Income Percentile (National)" in name:
                results.append({"segment": seg, "confidence": 0.90})
                break
            elif level in name and "County EHI Index" in name and "Percentile" not in name:
                results.append({"segment": seg, "confidence": 0.75})
                break

    return results


def match_education(edu_str: str) -> List[dict]:
    """Match ARI education targeting to demographic Education segments.

    Segments: Bachelor's Degree, Graduate Degree, High School Diploma,
    Less than High School Diploma, Some College — each with Extremely Likely/Likely.
    """
    if not edu_str:
        return []

    idx = _get_index()
    lower = edu_str.lower()

    target_keywords = []
    include_above = "or above" in lower or "or higher" in lower or "+" in lower

    if "graduate" in lower or "master" in lower or "advanced" in lower:
        target_keywords.append("Graduate Degree")
    elif "bachelor" in lower or "college degree" in lower:
        target_keywords.append("Bachelor's Degree")
        if include_above:
            target_keywords.append("Graduate Degree")
    elif "some college" in lower:
        target_keywords.append("Some College")
        if include_above:
            target_keywords.extend(["Bachelor's Degree", "Graduate Degree"])
    elif "college" in lower:
        # Generic "college" without "some" → Bachelor's
        target_keywords.append("Bachelor's Degree")
        if include_above:
            target_keywords.append("Graduate Degree")
    elif "high school" in lower:
        target_keywords.append("High School Diploma")
        if include_above:
            target_keywords.extend(["Some College", "Bachelor's Degree", "Graduate Degree"])
    else:
        return []

    results = []
    for seg in idx.education_segments:
        seg_name = seg["name"]
        for kw in target_keywords:
            if kw in seg_name and "Extremely Likely" in seg_name:
                results.append({"segment": seg, "confidence": 0.90})
                break
            elif kw in seg_name and "Likely" in seg_name:
                results.append({"segment": seg, "confidence": 0.75})
                break

    return results


def match_language(language_recs: list) -> List[dict]:
    """Match languageRecommendations to Browser Language segments.

    Adds Spanish Speaking segments if Spanish >= 20% in any demographic group.
    """
    if not language_recs:
        return []

    idx = _get_index()
    found_spanish = False
    spanish_pct = 0

    for rec in language_recs:
        for lang in rec.get("languages", []):
            if lang.get("language", "").lower() == "spanish" and lang.get("percentage", 0) >= 20:
                found_spanish = True
                spanish_pct = max(spanish_pct, lang["percentage"])

    if not found_spanish:
        return []

    results = []
    conf = 0.90 if spanish_pct >= 50 else 0.80
    for seg in idx.language_segments:
        if "spanish" in seg["name"].lower():
            results.append({"segment": seg, "confidence": conf})

    return results


def match_children(demographics_list: list) -> List[dict]:
    """Match children presence from audience_insights.demographics strings.

    Parses statements like "49% do not have Children Under Age 18" and
    matches against Presence of Children taxonomy segments.
    """
    if not demographics_list:
        return []

    idx = _get_index()

    has_children = False
    no_children = False

    for demo in demographics_list:
        lower = demo.lower()
        if "children" not in lower:
            continue

        pct_match = re.search(r"(\d+)%", demo)
        pct = int(pct_match.group(1)) if pct_match else 0

        if pct < 30:
            continue

        if "do not" in lower or "no children" in lower or "without" in lower:
            no_children = True
        else:
            has_children = True

    if not has_children and not no_children:
        return []

    results = []
    for seg in idx.children_segments:
        seg_name = seg["name"]
        # Only match the broadest age range (0-18)
        if "Age 0-18" not in seg_name:
            continue

        if has_children:
            if "Known data" in seg_name:
                results.append({"segment": seg, "confidence": 0.90})
            elif "Modeled likely" == seg_name.split(": ")[-1].strip():
                results.append({"segment": seg, "confidence": 0.80})
        elif no_children:
            if "Not likely" in seg_name:
                results.append({"segment": seg, "confidence": 0.85})
            elif "Modeled not as likely" in seg_name:
                results.append({"segment": seg, "confidence": 0.75})

    return results[:3]


def match_marital(demographics_list: list) -> List[dict]:
    """Match marital status from audience_insights.demographics strings.

    Parses "36% are Single", "40% are Married" etc.
    Matches against Lifestage > Marital Status segments.
    """
    if not demographics_list:
        return []

    idx = _get_index()

    married = False
    single = False

    for demo in demographics_list:
        lower = demo.lower()
        pct_match = re.search(r"(\d+)%", demo)
        pct = int(pct_match.group(1)) if pct_match else 0

        if pct < 30:
            continue

        if "married" in lower:
            married = True
        elif "single" in lower:
            single = True

    if not married and not single:
        return []

    results = []
    for seg in idx.lifestage_segments:
        seg_name = seg["name"]
        if "Marital Status" not in seg_name:
            continue

        if married and seg_name.startswith("Marital Status: Married"):
            conf = 0.90 if "Extremely Likely" in seg_name else 0.75
            results.append({"segment": seg, "confidence": conf})
        elif single and "Single" in seg_name:
            results.append({"segment": seg, "confidence": 0.85})

    return results


def match_interests_via_index(interest_list: List[str]) -> List[dict]:
    """Match ARI interest categories using the keyword inverted index.

    For each interest:
    1. Normalize to keywords
    2. Look up each keyword in index -> get candidate segments
    3. Score by keyword hit ratio + exact name containment bonus
    4. Return top 3 matches per interest above threshold
    """
    if not interest_list:
        return []

    idx = _get_index()
    results = []

    for interest in interest_list:
        interest_keywords = _tokenize(interest)
        if not interest_keywords:
            results.append({"input": interest, "matched": False, "confidence": 0.0})
            continue

        # Collect candidate segments and count keyword hits
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

        # Score candidates
        scored = []
        interest_lower = interest.lower()
        for key, (hits, seg) in candidate_hits.items():
            # Hit ratio: fraction of input keywords that matched
            hit_ratio = hits / len(interest_keywords)

            # Exact name containment bonus
            seg_name_lower = seg.get("name", "").lower()
            # Strip quality suffixes for comparison
            seg_name_clean = re.sub(
                r":\s*(high|low|medium|likely|extremely likely)\s*$",
                "", seg_name_lower, flags=re.IGNORECASE,
            ).strip()

            bonus = 0.0
            if interest_lower in seg_name_clean or seg_name_clean in interest_lower:
                bonus = 0.30
            elif interest_lower in seg.get("full_name", "").lower():
                bonus = 0.15

            score = min(hit_ratio * 0.80 + bonus, 1.0)
            scored.append((score, seg))

        scored.sort(key=lambda x: x[0], reverse=True)

        # Take top 3 above threshold
        matched_any = False
        for score, seg in scored[:3]:
            if score >= INTEREST_MATCH_THRESHOLD:
                results.append({
                    "input": interest,
                    "matched": True,
                    "confidence": round(score, 2),
                    "segment": seg,
                })
                matched_any = True

        if not matched_any:
            best_score = scored[0][0] if scored else 0.0
            results.append({
                "input": interest,
                "matched": False,
                "confidence": round(best_score, 2),
            })

    return results


def _match_traits_via_index(traits_list: list) -> List[dict]:
    """Match a list of {trait, qvi} items through the keyword index.

    Shared implementation for match_activities and match_daily_routines.
    Weight results by QVI.
    """
    if not traits_list:
        return []

    idx = _get_index()
    results = []

    for item in traits_list:
        trait = item.get("trait", "")
        qvi = item.get("qvi", 100)
        if not trait:
            continue

        trait_keywords = _tokenize(trait)
        if not trait_keywords:
            continue

        # Collect candidates via keyword index
        candidate_hits: Dict[str, Tuple[int, dict]] = {}
        for kw in trait_keywords:
            for seg in idx.keyword_index.get(kw, []):
                key = seg.get("full_name", seg.get("name"))
                if key in candidate_hits:
                    candidate_hits[key] = (candidate_hits[key][0] + 1, seg)
                else:
                    candidate_hits[key] = (1, seg)

        if not candidate_hits:
            continue

        # Find best match
        trait_lower = trait.lower()
        best_score = 0.0
        best_seg = None

        for key, (hits, seg) in candidate_hits.items():
            hit_ratio = hits / len(trait_keywords)

            seg_name_lower = seg.get("name", "").lower()
            seg_name_clean = re.sub(
                r":\s*(high|low|medium)\s*$", "", seg_name_lower,
            ).strip()

            bonus = 0.0
            if trait_lower in seg_name_clean or seg_name_clean in trait_lower:
                bonus = 0.30
            elif trait_lower in seg.get("full_name", "").lower():
                bonus = 0.15

            score = min(hit_ratio * 0.80 + bonus, 1.0)

            # QVI weight: boost high-QVI traits
            qvi_factor = min(qvi / 200.0, 1.5)
            weighted = score * (0.7 + 0.3 * qvi_factor)
            weighted = min(weighted, 1.0)

            if weighted > best_score:
                best_score = weighted
                best_seg = seg

        if best_seg and best_score >= INTEREST_MATCH_THRESHOLD:
            results.append({
                "segment": best_seg,
                "confidence": round(best_score, 2),
                "source_trait": trait,
                "qvi": qvi,
            })

    return results


def match_activities(activities_list: list) -> List[dict]:
    """Match audience_insights.activities traits through keyword index.

    Each item: {"trait": "Exercising Regularly", "qvi": 131}
    """
    return _match_traits_via_index(activities_list)


def match_daily_routines(routines_list: list) -> List[dict]:
    """Match audience_insights.daily_routines traits through keyword index.

    Same mechanism as activities but tracked separately in match results.
    """
    return _match_traits_via_index(routines_list)


def match_area_type(location_targeting: str) -> List[dict]:
    """Match ARI location_targeting text to Area segments.

    Parses for Urban/Suburban/Rural keywords and maps to specific Area segments.
    """
    if not location_targeting:
        return []

    idx = _get_index()
    lower = location_targeting.lower()
    results = []

    # Map location keywords to preferred Area segment names
    area_keywords = {
        "urban": [
            "Urban pop 20,000+ metro adjacent",
            "Metro Counties pop 1,000,000+",
            "Metropolitan",
        ],
        "suburban": [
            "Metro Counties pop 250,000-1,000,000",
            "Metro Counties pop less than 250,000",
            "Metropolitan",
        ],
        "rural": [
            "Rural",
            "Town",
        ],
    }

    matched_names = set()
    for keyword, target_names in area_keywords.items():
        if keyword in lower:
            for seg in idx.area_segments:
                if seg["name"] in target_names and seg["name"] not in matched_names:
                    matched_names.add(seg["name"])
                    results.append({"segment": seg, "confidence": 0.80})

    return results


def match_mosaic_persona(values_list: list, psych_drivers_list: list) -> List[dict]:
    """Map audience_insights values and psychological_drivers to Mosaic Persona segments.

    Uses keyword overlap between ARI trait text and Mosaic persona names
    (e.g. "Achievement and Success" -> "Wired for Success", "Cosmopolitan Achievers").
    Weights by QVI for confidence scoring.
    """
    all_traits = list(values_list or []) + list(psych_drivers_list or [])
    if not all_traits:
        return []

    idx = _get_index()
    results = []
    seen_personas = set()

    for item in all_traits:
        trait = item.get("trait", "")
        qvi = item.get("qvi", 100)
        if not trait:
            continue

        trait_keywords = _tokenize(trait)
        if not trait_keywords:
            continue

        for seg in idx.mosaic_persona_segments:
            seg_name = seg.get("name", "")
            if seg_name in seen_personas:
                continue

            seg_keywords = _tokenize(seg_name)
            if not seg_keywords:
                continue

            # Count keyword overlap
            overlap = trait_keywords & seg_keywords
            if not overlap:
                continue

            # Score based on overlap ratio (relative to smaller set for generosity)
            score = len(overlap) / min(len(trait_keywords), len(seg_keywords))

            # QVI weight
            qvi_factor = min(qvi / 200.0, 1.5)
            weighted = score * (0.7 + 0.3 * qvi_factor)
            weighted = min(weighted, 1.0)

            if weighted >= 0.30:
                seen_personas.add(seg_name)
                results.append({
                    "segment": seg,
                    "confidence": round(weighted, 2),
                    "source_trait": trait,
                    "qvi": qvi,
                })

    results.sort(key=lambda r: r["confidence"], reverse=True)
    return results[:5]


def match_attitudes(psych_drivers_list: list, activities_list: list) -> List[dict]:
    """Map psychological drivers and activities to Attitudes segments.

    Attitude categories: Tech Adoption, Health and Well Being, Mobile Usage.
    Uses keyword matching to determine which attitude category a trait maps to,
    then includes matching segments.
    """
    idx = _get_index()
    if not idx.attitude_segments:
        return []

    all_traits = list(psych_drivers_list or []) + list(activities_list or [])
    if not all_traits:
        return []

    # Keyword sets for each attitude category
    tech_keywords = {
        "technology", "tech", "innovation", "digital", "computing",
        "software", "gadget", "adoption", "internet", "online",
    }
    health_keywords = {
        "health", "wellness", "fitness", "healthy", "wellbeing",
        "nutrition", "exercise", "holistic", "weight", "diet",
    }
    mobile_keywords = {
        "mobile", "phone", "smartphone", "app", "connected", "device",
    }

    results = []
    seen = set()

    for item in all_traits:
        trait = item.get("trait", "")
        qvi = item.get("qvi", 100)
        if not trait:
            continue

        trait_keywords = _tokenize(trait)

        # Determine which attitude categories this trait maps to
        matched_categories = set()
        if trait_keywords & tech_keywords:
            matched_categories.add("Tech Adoption")
        if trait_keywords & health_keywords:
            matched_categories.add("Health and Well Being")
        if trait_keywords & mobile_keywords:
            matched_categories.add("Mobile Usage")

        if not matched_categories:
            continue

        for seg in idx.attitude_segments:
            seg_category = seg.get("category", "")
            if seg_category not in matched_categories:
                continue

            seg_name = seg.get("name", "")
            if seg_name in seen:
                continue

            # Score: base from category match + bonus for keyword overlap
            seg_keywords = _tokenize(seg_name)
            overlap = trait_keywords & seg_keywords

            base_conf = 0.70
            if overlap:
                base_conf = 0.85

            qvi_factor = min(qvi / 200.0, 1.5)
            weighted = base_conf * (0.7 + 0.3 * qvi_factor)
            weighted = min(weighted, 1.0)

            seen.add(seg_name)
            results.append({
                "segment": seg,
                "confidence": round(weighted, 2),
                "source_trait": trait,
                "qvi": qvi,
            })

    results.sort(key=lambda r: r["confidence"], reverse=True)
    return results


def match_taxonomy(industry: str) -> List[dict]:
    """Match an ARI industry name using the keyword index.

    Replaces fuzzy matching with keyword-based scoring against interest
    category segments.
    """
    if not industry:
        return []

    idx = _get_index()
    industry_keywords = _tokenize(industry)
    if not industry_keywords:
        return []

    # Collect candidates via keyword index
    candidate_hits: Dict[str, Tuple[int, dict]] = {}
    for kw in industry_keywords:
        for seg in idx.keyword_index.get(kw, []):
            key = seg.get("full_name", seg.get("name"))
            if key in candidate_hits:
                candidate_hits[key] = (candidate_hits[key][0] + 1, seg)
            else:
                candidate_hits[key] = (1, seg)

    scored = []
    industry_lower = industry.lower()

    for key, (hits, seg) in candidate_hits.items():
        hit_ratio = hits / len(industry_keywords)

        # Category exact match bonus
        category = seg.get("category", "").lower()
        cat_bonus = 0.0
        if industry_lower == category:
            cat_bonus = 0.30
        elif any(w == category for w in industry_keywords):
            cat_bonus = 0.25

        # Name containment bonus
        name_bonus = 0.0
        seg_name_lower = seg.get("name", "").lower()
        if industry_lower in seg_name_lower or seg_name_lower in industry_lower:
            name_bonus = 0.20

        score = min(hit_ratio * 0.50 + cat_bonus + name_bonus, 1.0)
        if score >= 0.35:
            scored.append({"segment": seg, "confidence": round(score, 2)})

    scored.sort(key=lambda r: r["confidence"], reverse=True)
    return scored[:10]


# ---------- Audience definition builder ----------


# Map CSV Segment Category → API category for querying segmentsByCategory.
# The API has only: demographic_age, demographic_gender, location, predefined, direct.
_CSV_CAT_TO_API_CAT = {
    "Age": "demographic_age",
    "Gender": "demographic_gender",
    "State": "location",
    "Area": "location",
    "Congressional District": "location",
    "DMA": "location",
    "Zip Code": "location",
}


def _api_cat_for(csv_category: str) -> str:
    """Return the API category name for a CSV Segment Category."""
    return _CSV_CAT_TO_API_CAT.get(csv_category, "predefined")


# The same mapping doubles as the normalized_definition key.
_def_key_for = _api_cat_for


def _collect_matched_segments(match_results: dict) -> List[dict]:
    """Collect all unique segment dicts (with full_name) from match results."""
    seen = set()
    segments = []

    for key, matches in match_results.items():
        for m in matches:
            # Age may have all_segments_in_range
            if "all_segments_in_range" in m:
                for seg in m["all_segments_in_range"]:
                    fn = seg.get("full_name", "")
                    if fn and fn not in seen:
                        seen.add(fn)
                        segments.append(seg)
                continue

            seg = m.get("segment", {})
            fn = seg.get("full_name", "")
            # Skip synthetic entries (e.g. "All Genders")
            if not fn or "No gender restriction" in fn:
                continue
            if fn not in seen:
                seen.add(fn)
                segments.append(seg)

    return segments


def resolve_segment_ids(
    match_results: dict,
    service: "OpenXService",
) -> Dict[str, str]:
    """Resolve matched segment full_names to UUIDs via the OpenX API.

    The API uses 5 categories: ``demographic_age``, ``demographic_gender``,
    ``location``, ``predefined``, ``direct``.  We map CSV categories to these,
    query each, and match by joining the API ``path`` array with ``" > "``
    against the CSV ``full_name``.

    Returns a dict mapping ``full_name → UUID``.
    """
    matched = _collect_matched_segments(match_results)
    if not matched:
        return {}

    # Build the set of full_names we need, grouped by API category
    needed_by_api_cat: Dict[str, Set[str]] = {}
    for seg in matched:
        fn = seg.get("full_name", "")
        if not fn:
            continue
        api_cat = _api_cat_for(seg.get("category", ""))
        needed_by_api_cat.setdefault(api_cat, set()).add(fn)

    id_map: Dict[str, str] = {}

    for api_cat, needed_fns in needed_by_api_cat.items():
        remaining = set(needed_fns)
        logger.info(
            "Resolving %d segment IDs from API category %r ...",
            len(remaining), api_cat,
        )

        offset = 0
        batch = 1000
        while remaining:
            page = service.get_segments_by_category(api_cat, limit=batch, offset=offset)
            if not page:
                break

            for api_seg in page:
                api_path = api_seg.get("path", [])
                api_fn = " > ".join(api_path)
                if api_fn in remaining:
                    id_map[api_fn] = api_seg["id"]
                    remaining.discard(api_fn)

            # Stop early if all found, or no more pages
            if not remaining or len(page) < batch:
                break
            offset += batch

        if remaining:
            logger.warning(
                "Could not resolve %d segment(s) in %r: %s",
                len(remaining), api_cat,
                ", ".join(list(remaining)[:5]),
            )

    resolved = len(id_map)
    total = len(matched)
    logger.info("Resolved %d/%d segment IDs", resolved, total)
    return id_map


def build_audience_definition(match_results: dict, id_map: Dict[str, str]) -> dict:
    """Build the ``normalized_definition`` JSON for audienceCreate.

    Uses the OpenX format::

        {
          "includes": {
            "operator": "INTERSECT",
            "groups": [{
              "demographic_age": {"operator": "UNION", "segments": [{"id": "uuid"}, ...]},
              "location":        {"operator": "UNION", "segments": [{"id": "uuid"}, ...]},
              "predefined":      {"operator": "UNION", "segments": [{"id": "uuid"}, ...]}
            }]
          },
          "excludes": {}
        }
    """
    # Collect segments into definition-key buckets
    buckets: Dict[str, List[str]] = {}  # def_key → [uuid, ...]

    def _add(seg: dict):
        fn = seg.get("full_name", "")
        uid = id_map.get(fn)
        if not uid:
            return
        cat = seg.get("category", "")
        dk = _def_key_for(cat)
        buckets.setdefault(dk, []).append(uid)

    # --- Age (include all in range) ---
    for r in match_results.get("age", []):
        if "all_segments_in_range" in r:
            for seg in r["all_segments_in_range"]:
                _add(seg)
        elif r.get("segment", {}).get("name", "").isdigit():
            _add(r["segment"])

    # --- Gender (skip "All Genders") ---
    for r in match_results.get("gender", []):
        seg = r.get("segment", {})
        if seg.get("full_name") and "No gender restriction" not in seg.get("full_name", ""):
            _add(seg)

    # --- Location + Area ---
    for key in ("location", "area_type"):
        for r in match_results.get(key, []):
            _add(r.get("segment", {}))

    # --- Advanced demographics (income, education, marital, children) ---
    for key in ("income", "education", "marital", "children"):
        for r in match_results.get(key, []):
            _add(r.get("segment", {}))

    # --- Language ---
    for r in match_results.get("language", []):
        _add(r.get("segment", {}))

    # --- Interests + Activities + Routines + Taxonomy ---
    for r in match_results.get("interests", []):
        if r.get("matched"):
            _add(r.get("segment", {}))
    for key in ("activities", "daily_routines", "taxonomy"):
        for r in match_results.get(key, []):
            _add(r.get("segment", {}))

    # --- Psychographic (mosaic + attitudes) ---
    for key in ("mosaic_persona", "attitudes"):
        for r in match_results.get(key, []):
            _add(r.get("segment", {}))

    # Build the group object — must include "operator" at group level
    group = {"operator": "INTERSECT"}
    for dk, uids in buckets.items():
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for uid in uids:
            if uid not in seen:
                seen.add(uid)
                unique.append({"id": uid})
        group[dk] = {"operator": "UNION", "segments": unique}

    return {
        "includes": {
            "operator": "INTERSECT",
            "groups": [group] if group else [],
        },
        "excludes": {},
    }


def build_audience_params(
    ari_segment: dict,
    match_results: dict,
    id_map: Dict[str, str],
    export_type: str = "oa_match",
    export_targets: List[str] = None,
    provider_id: str = None,
) -> dict:
    """Build the full ``audienceCreate`` input from an ARI segment."""
    if export_targets is None:
        export_targets = ["user", "ctv"]

    segment_name = ari_segment.get("name", "Unnamed Segment")
    timestamp_suffix = datetime.now(timezone.utc).strftime("%m%d%H%M%S")
    definition = build_audience_definition(match_results, id_map)

    return {
        "name": f"{OPENX_AUDIENCE_NAME_PREFIX} - {segment_name} {timestamp_suffix}",
        "export_type": export_type,
        "export_targets": export_targets,
        "direct_audience_provider": provider_id or OPENX_PROVIDER_ID,
        "normalized_definition": definition,
    }


# ---------- Ethnic affinity keywords ----------


def generate_ethnic_keywords(
    segment: dict,
    language_recs: list = None,
) -> dict:
    """Generate contextual targeting keywords for ethnic affinity using GPT-4o.

    Analyzes the segment's name, interests, demographics, and language to
    produce 20 contextual keywords for OpenX metacategory targeting.

    Keywords must be alphabetic characters and hyphens only (OpenX constraint).

    Returns ``{"keywords": [...], "ethnicity": "...", "sources": [...]}``
    """
    from core.behavioral_adjustments import detect_target_race
    from core.ai_utils import make_openai_request

    ethnicity = detect_target_race(segment)

    # If no ethnic affinity detected, return empty
    if not ethnicity:
        return {"keywords": [], "ethnicity": None, "sources": []}

    # Gather context for the prompt
    seg_name = segment.get("name", "")
    interests = segment.get("interest_categories", [])
    targeting = segment.get("targeting_params", {})
    description = segment.get("description", "")

    lang_context = ""
    if language_recs:
        for rec in language_recs:
            for lang in rec.get("languages", []):
                if lang.get("percentage", 0) >= 20:
                    lang_context += f"{lang.get('language', '')}: {lang.get('percentage')}%, "

    prompt = f"""You are an expert in multicultural advertising and programmatic media buying on OpenX.

Generate exactly 20 contextual targeting keywords for an OpenX deal.

These keywords are matched by OpenX's URL Categorizer against page-level content tags. Pages are tagged with SHORT, SIMPLE terms like "black", "hispanic", "hiphop", "gospel", "afrobeats", "latino", "reggaeton", "soul", "urban". The categorizer does NOT use long compound phrases.

AUDIENCE SEGMENT:
- Name: {seg_name}
- Detected Ethnicity: {ethnicity}
- Interests: {', '.join(interests) if interests else 'N/A'}
- Description: {description or 'N/A'}
- Age Range: {targeting.get('age_range', 'N/A')}
- Location: {targeting.get('location_targeting', 'N/A')}
- Language Affinity: {lang_context or 'N/A'}

KEYWORD RULES:
- Each keyword must be SHORT — one word or at most two words hyphenated (e.g. "hip-hop", "k-pop")
- NEVER use long hyphenated phrases like "african-american-family-travel" — these match nothing
- Lowercase alphabetic characters and hyphens ONLY (no spaces, numbers, special characters)
- Good examples: "black", "hispanic", "hiphop", "gospel", "afrobeats", "soul", "urban", "latino", "reggaeton", "r-and-b", "latin", "anime", "bollywood", "k-pop"
- Bad examples: "african-american-road-trips", "black-family-vacations", "family-safety-protection"
- Include a mix of ethnic/cultural identity terms AND cultural media/entertainment/lifestyle terms
- Do NOT include generic terms like "music", "food", "news", "sports" alone
- Do NOT include geographic terms
- Produce exactly 20 keywords, ordered by relevance

Return JSON: {{"keywords": ["keyword-one", "keyword-two", ...]}}"""

    result = make_openai_request(
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.4,
        max_tokens=500,
    )

    if not result or "keywords" not in result:
        logger.warning("AI keyword generation failed, returning empty")
        return {"keywords": [], "ethnicity": ethnicity, "sources": ["AI generation failed"]}

    # Validate: only allow alphabetic + hyphens, lowercase
    raw_keywords = result.get("keywords", [])
    valid = []
    for kw in raw_keywords:
        if not isinstance(kw, str):
            continue
        cleaned = kw.lower().strip()
        if cleaned and all(c.isalpha() or c == "-" for c in cleaned):
            if cleaned not in valid:
                valid.append(cleaned)

    return {
        "keywords": valid[:20],
        "ethnicity": ethnicity,
        "sources": [f"AI-generated for {ethnicity}"],
    }


# ---------- Deal creation ----------

# Deal config from env vars (defaults from existing DCG deal)
OPENX_AUDIENCE_NAME_PREFIX = os.environ.get("OPENX_AUDIENCE_NAME_PREFIX", "Digital Culture Group")
OPENX_DEAL_ID_PREFIX = os.environ.get("OPENX_DEAL_ID_PREFIX", "DCG-")
OPENX_DEAL_CURRENCY = os.environ.get("OPENX_DEAL_CURRENCY", "USD")
OPENX_DEAL_PRICE = os.environ.get("OPENX_DEAL_PRICE", "0.01")
OPENX_DEAL_PMP_TYPE = os.environ.get("OPENX_DEAL_PMP_TYPE", "3")
OPENX_DEAL_DEMAND_PARTNER = os.environ.get("OPENX_DEAL_DEMAND_PARTNER", "537073301")
OPENX_DEAL_FEES_PARTNER_ID = os.environ.get("OPENX_DEAL_FEES_PARTNER_ID", "561460270")
OPENX_DEAL_FEES_SHARE = os.environ.get("OPENX_DEAL_FEES_SHARE", "0.300")


def _build_metacategory(keywords: List[str] = None) -> dict:
    """Build the metacategory targeting block, optionally with ethnic keywords."""
    meta: dict = {
        "exclude_mfa": True,
        "inter_dimension_operator": "AND",
    }
    if keywords:
        meta["keywords"] = {
            "includes": keywords,
            "excludes": [],
        }
    return meta


def build_deal_params(
    audience_id: str,
    audience_name: str,
    ethnic_keywords: List[str] = None,
) -> dict:
    """Build the ``dealCreate`` input from an activated audience UUID.

    Replicates the targeting structure from existing DCG deals:
    - rendering_context: Banner + WEB/APP + desktop/phone/tablet
    - viewability: >= 0.70
    - metacategory: exclude MFA + ethnic affinity keywords
    - audience: openaudience-<UUID>
    """
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

    deal_params: dict = {
        "name": audience_name,
        "currency": OPENX_DEAL_CURRENCY,
        "deal_price": OPENX_DEAL_PRICE,
        "pmp_deal_type": OPENX_DEAL_PMP_TYPE,
        "start_date": now_iso,
        "deal_participants": [
            {
                "demand_partner": OPENX_DEAL_DEMAND_PARTNER,
                "buyer_ids": [],
                "brand_ids": [],
            }
        ],
        "third_party_fees_config": [
            {
                "revenue_method": "PoM",
                "gross_share": OPENX_DEAL_FEES_SHARE,
                "partner_id": OPENX_DEAL_FEES_PARTNER_ID,
            }
        ],
        "package": {
            "name": f"Package for {audience_name}",
            "targeting": {
                "inter_dimension_operator": "AND",
                "audience": {
                    "openaudience_custom": {
                        "op": "INTERSECTS",
                        "val": f"openaudience-{audience_id}",
                    }
                },
                "rendering_context": {
                    "op": "AND",
                    "ad_placement": {
                        "op": "==",
                        "val": "BANNER",
                    },
                    "distribution_channel": {
                        "op": "INTERSECTS",
                        "val": "WEB,APP",
                    },
                    "device_type": {
                        "op": "INTERSECTS",
                        "desktop_devices": "desktop",
                        "mobile_devices": "phone,tablet",
                    },
                },
                "viewability": {
                    "viewability_score": {
                        "op": ">=",
                        "val": "0.70",
                    }
                },
                "metacategory": _build_metacategory(ethnic_keywords),
            },
        },
    }

    return deal_params


# ---------- High-level preview ----------


def _match_single_segment(
    segment: dict,
    industry: str,
    audience_insights: dict,
    language_recs: list,
) -> dict:
    """Run all matchers for a single ARI segment and return results + summary."""
    targeting = segment.get("targeting_params", {})

    # Demographics from audience_insights
    demographics = audience_insights.get("demographics", [])
    values = audience_insights.get("values", [])
    psych_drivers = audience_insights.get("psychological_drivers", [])
    activities = audience_insights.get("activities", [])
    daily_routines = audience_insights.get("daily_routines", [])

    # Core matches (existing, improved with O(1) lookups)
    age_results = match_age_range(targeting.get("age_range", ""))
    gender_results = match_gender(targeting.get("gender_targeting", "All"))
    location_results = match_location(segment.get("primary_state", ""))

    # Interest matching via keyword index (replaces fuzzy matching)
    interest_results = match_interests_via_index(
        segment.get("interest_categories", []),
    )
    taxonomy_results = match_taxonomy(industry)

    # New matchers
    income_results = match_income(targeting.get("income_targeting", ""))
    education_results = match_education(targeting.get("education_targeting", ""))
    language_results = match_language(language_recs)
    area_results = match_area_type(targeting.get("location_targeting", ""))
    children_results = match_children(demographics)
    marital_results = match_marital(demographics)
    activities_results = match_activities(activities)
    routines_results = match_daily_routines(daily_routines)
    mosaic_results = match_mosaic_persona(values, psych_drivers)
    attitude_results = match_attitudes(psych_drivers, activities)

    # Ethnic affinity keywords
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
        "area_type": area_results,
        "children": children_results,
        "marital": marital_results,
        "activities": activities_results,
        "daily_routines": routines_results,
        "mosaic_persona": mosaic_results,
        "attitudes": attitude_results,
        "ethnic_keywords": ethnic_kw,
    }

    # Summary statistics
    matched_interests = sum(1 for r in interest_results if r.get("matched"))
    total_interests = len(interest_results)
    unmatched = [r["input"] for r in interest_results if not r.get("matched")]

    warnings = []
    if not age_results:
        warnings.append("No matching age segments found")
    if not gender_results:
        warnings.append("No matching gender segments found")
    if not location_results:
        state = segment.get("primary_state", "N/A")
        if state and state != "N/A":
            warnings.append(f"Could not match location: {state}")
    if unmatched:
        warnings.append(f"Unmatched interests: {', '.join(unmatched)}")
    if not taxonomy_results:
        warnings.append(f"No taxonomy match for industry: {industry}")

    return {
        "segment_name": segment.get("name", "Unnamed"),
        "segment_data": segment,
        "matches": match_data,
        "summary": {
            "age_matches": len(age_results),
            "gender_matches": len(gender_results),
            "location_matches": len(location_results),
            "interest_matches": matched_interests,
            "interest_total": total_interests,
            "taxonomy_matches": len(taxonomy_results),
            "income_matches": len(income_results),
            "education_matches": len(education_results),
            "language_matches": len(language_results),
            "area_matches": len(area_results),
            "children_matches": len(children_results),
            "marital_matches": len(marital_results),
            "activities_matches": len(activities_results),
            "routines_matches": len(routines_results),
            "mosaic_matches": len(mosaic_results),
            "attitude_matches": len(attitude_results),
            "ethnic_keyword_count": len(ethnic_kw.get("keywords", [])),
        },
        "warnings": warnings,
    }


def preview_all_segments(
    session_state: Dict[str, Any],
) -> List[dict]:
    """Generate mapping previews for all ARI audience segments.

    Loads the taxonomy CSV on first call, then runs all matchers
    (demographics, interests, psychographics, attitudes).
    Returns a list (up to 4 entries) with match details and warnings.
    """
    load_taxonomy()

    idx = _get_index()
    if not idx.loaded:
        logger.error("No taxonomy data loaded — cannot generate previews")
        return []

    industry = session_state.get("industry", "")

    # Get audience_insights (may be dict or JSON string)
    audience_insights = session_state.get("audience_insights", {})
    if isinstance(audience_insights, str):
        try:
            audience_insights = json.loads(audience_insights)
        except (json.JSONDecodeError, TypeError):
            audience_insights = {}

    # Get language recommendations (may be list or JSON string)
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
