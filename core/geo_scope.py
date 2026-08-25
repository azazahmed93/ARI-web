"""
Campaign geographic scope — where the brief says media should run / the
target audience lives — used to restrict the Top-DMA ranking (an Arizona RFP
must not surface nationwide markets).

Python port of ari-api's geo-scope.ts (deterministic resolver; the LLM
extraction lives in core/geo_scope_extract.py so this module stays free of
OpenAI dependencies). Keep the two in sync.
"""
import re

from core.dma_targeting_data import load_dma_dataset

NATIONAL_SCOPE = {"type": "national", "label": "National", "states": [], "dma_codes": []}

STATE_NAME_TO_CODE = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
    "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
    "virginia": "VA", "washington": "WA", "west virginia": "WV", "wisconsin": "WI",
    "wyoming": "WY", "district of columbia": "DC", "washington dc": "DC", "washington d.c.": "DC",
}
STATE_CODES = set(STATE_NAME_TO_CODE.values())
STATE_CODE_TO_NAME = {
    code: re.sub(r"\b\w", lambda m: m.group(0).upper(), name).replace("Of", "of")
    for name, code in STATE_NAME_TO_CODE.items()
    if not name.startswith("washington d")
}

REGION_TO_STATES = {
    "new england": ["CT", "ME", "MA", "NH", "RI", "VT"],
    "northeast": ["CT", "ME", "MA", "NH", "RI", "VT", "NJ", "NY", "PA"],
    "mid-atlantic": ["NJ", "NY", "PA", "DE", "MD", "DC"],
    "mid atlantic": ["NJ", "NY", "PA", "DE", "MD", "DC"],
    "tri-state": ["NY", "NJ", "CT"],
    "tri state": ["NY", "NJ", "CT"],
    "dmv": ["DC", "MD", "VA"],
    "southeast": ["AL", "FL", "GA", "KY", "MS", "NC", "SC", "TN", "VA", "WV"],
    "south": ["AL", "AR", "FL", "GA", "KY", "LA", "MS", "NC", "OK", "SC", "TN", "TX", "VA", "WV"],
    "deep south": ["AL", "GA", "LA", "MS", "SC"],
    "gulf coast": ["TX", "LA", "MS", "AL", "FL"],
    "midwest": ["IL", "IN", "IA", "KS", "MI", "MN", "MO", "NE", "ND", "OH", "SD", "WI"],
    "great lakes": ["IL", "IN", "MI", "MN", "OH", "WI"],
    "great plains": ["KS", "NE", "ND", "SD", "OK"],
    "plains": ["KS", "NE", "ND", "SD", "OK"],
    "southwest": ["AZ", "NM", "NV", "TX", "OK"],
    "mountain west": ["CO", "ID", "MT", "NV", "UT", "WY"],
    "rocky mountain": ["CO", "ID", "MT", "NV", "UT", "WY"],
    "rockies": ["CO", "ID", "MT", "NV", "UT", "WY"],
    "west": ["AZ", "CA", "CO", "ID", "MT", "NV", "NM", "OR", "UT", "WA", "WY", "AK", "HI"],
    "west coast": ["CA", "OR", "WA"],
    "pacific northwest": ["WA", "OR", "ID"],
    "sun belt": ["AZ", "CA", "FL", "GA", "NV", "NM", "NC", "SC", "TX", "AL", "LA", "MS"],
    "sunbelt": ["AZ", "CA", "FL", "GA", "NV", "NM", "NC", "SC", "TX", "AL", "LA", "MS"],
}


def _as_string_list(value):
    return [v for v in value if isinstance(v, str)] if isinstance(value, list) else []


def _normalize(s):
    s = s.lower().replace(".", "")
    s = re.sub(r"[^a-z0-9&\- ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _tokens(s):
    return [t for t in re.split(r"[\s\-&,]+", _normalize(s)) if t]


def _resolve_state_code(raw):
    n = re.sub(r"^state of ", "", _normalize(raw))
    if n in STATE_NAME_TO_CODE:
        return STATE_NAME_TO_CODE[n]
    upper = raw.strip().upper()
    if len(upper) == 2 and upper in STATE_CODES:
        return upper
    return None


def _resolve_region(raw):
    n = _normalize(raw)
    n = re.sub(r"^the ", "", n)
    n = re.sub(r" region$", "", n)
    n = re.sub(r" states?$", "", n)
    return REGION_TO_STATES.get(n)


def _resolve_market(raw, dataset):
    """
    Match a market name ("Phoenix", "Dallas-Fort Worth", "Portland, Oregon")
    to a dataset DMA: every token of the market (minus a trailing state) must
    appear in the DMA name; a named state must hold population in the DMA;
    ties go to the larger market.
    """
    market_tokens = _tokens(raw)
    if not market_tokens:
        return None
    state_filter = None
    for take in (2, 1):
        if len(market_tokens) > take:
            code = _resolve_state_code(" ".join(market_tokens[-take:]))
            if code:
                state_filter = code
                market_tokens = market_tokens[:-take]
                break
    market_tokens = [t for t in market_tokens if t not in ("dma", "market", "metro", "area")]
    if not market_tokens:
        return None
    candidates = []
    for d in dataset["dmas"]:
        name_tokens = set(_tokens(d["name"]))
        if not all(t in name_tokens for t in market_tokens):
            continue
        if state_filter and not d["states"].get(state_filter, 0) > 0:
            continue
        candidates.append(d)
    if not candidates:
        return None
    candidates.sort(key=lambda d: -d["population"])
    return candidates[0]["code"]


def _format_list(items):
    if len(items) <= 3:
        if len(items) <= 1:
            return items[0] if items else ""
        return f"{', '.join(items[:-1])} & {items[-1]}"
    return f"{', '.join(items[:2])} +{len(items) - 2} more"


def _title_case(s):
    return re.sub(r"\b\w", lambda m: m.group(0).upper(), s)


def resolve_geo_scope(raw, dataset=None):
    """Deterministically map an extraction onto state + DMA codes; national on failure."""
    if not raw or str(raw.get("scope", "")).lower() == "national":
        return dict(NATIONAL_SCOPE)
    if dataset is None:
        dataset = load_dma_dataset()

    states = set()
    region_labels = []
    for region in _as_string_list(raw.get("regions")):
        codes = _resolve_region(region)
        if codes:
            states.update(codes)
            region_labels.append(_title_case(_normalize(region)))
        else:
            code = _resolve_state_code(region)  # models sometimes file a state under regions
            if code:
                states.add(code)
    state_labels = []
    for state in _as_string_list(raw.get("states")):
        code = _resolve_state_code(state)
        if code and code not in states:
            state_labels.append(STATE_CODE_TO_NAME[code])
        if code:
            states.add(code)

    dma_codes = []
    market_labels = []
    by_code = {d["code"]: d for d in dataset["dmas"]}
    for market in _as_string_list(raw.get("markets")):
        code = _resolve_market(market, dataset)
        if code is not None and code not in dma_codes:
            dma_codes.append(code)
            market_labels.append(by_code[code]["name"])

    if not states and not dma_codes:
        return dict(NATIONAL_SCOPE)

    if region_labels:
        label = _format_list(region_labels + state_labels)
    elif state_labels:
        label = _format_list(state_labels)
    else:
        label = _format_list(market_labels)

    scope = {"type": "regional", "label": label, "states": sorted(states), "dma_codes": dma_codes}
    evidence = raw.get("evidence")
    if isinstance(evidence, str) and evidence:
        scope["evidence"] = evidence[:300]
    return scope


def dma_in_scope_share(dma, scope):
    """
    Fraction of a DMA's population inside the scope: 1 for national scope or
    an explicitly named market, otherwise the share living in scope states.
    """
    if scope["type"] == "national":
        return 1.0
    if dma["code"] in scope["dma_codes"]:
        return 1.0
    if not scope["states"] or dma["population"] == 0:
        return 0.0
    in_scope = sum(dma["states"].get(s, 0) for s in scope["states"])
    return in_scope / dma["population"]
