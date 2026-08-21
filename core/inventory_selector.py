"""
AI-powered inventory selection module.

Selects the most relevant ad inventory (websites, TV networks, streaming platforms)
from static CSV files using GPT-4o, based on the RFP brief text.

Strategy:
- Websites (34K entries): Batch chunking → per-chunk top 10 → final aggregation → top 5
- TV networks (394 entries): Single-pass → top 5
- Streaming platforms (2,833 entries): Single-pass → top 6
"""

import os
import json
import hashlib
import time
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

from core.ai_utils import make_openai_request

# ---------------------------------------------------------------------------
# Module-level DataFrame cache (lives for process lifetime)
# ---------------------------------------------------------------------------
_inventory_cache: Dict[str, pd.DataFrame] = {}

INVENTORY_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'inventory')

INVENTORY_FILES = {
    'websites': 'ARI Media_Affinity_Sites_Complete_All_Audiences_FINAL - Top Media Affinity Sites.csv',
    'tv_networks': 'ARI Media_Affinity_Sites_Complete_All_Audiences_FINAL - Top TV Network Affinities.csv',
    'streaming_platforms': 'ARI Media_Affinity_Sites_Complete_All_Audiences_FINAL - Top Streaming Platforms.csv',
}

# UK CSV variants (same column layout as the US files, sourced from the
# client's DCG UK inventory export). If a UK file is missing, UK requests fall
# back to the US file (websites: filtered to UK domains) with UK market
# context in the GPT prompts.
UK_INVENTORY_FILES = {
    'websites': 'ARI Media_Affinity_Sites_Complete_All_Audiences_FINAL - Top Media Affinity Sites UK.csv',
    'tv_networks': 'ARI Media_Affinity_Sites_Complete_All_Audiences_FINAL - Top TV Network Affinities UK.csv',
    'streaming_platforms': 'ARI Media_Affinity_Sites_Complete_All_Audiences_FINAL - Top Streaming Platforms UK.csv',
}


def _has_uk_file(inventory_type: str) -> bool:
    filename = UK_INVENTORY_FILES.get(inventory_type)
    return bool(filename) and os.path.exists(os.path.join(INVENTORY_DIR, filename))


# Column used to de-duplicate when combining markets (Global = US + UK).
_DEDUP_KEY = {
    'websites': 'Domain Name',
    'tv_networks': 'App/Platform Name',
    'streaming_platforms': 'App/Platform Name',
}

# UK publishers in the global websites CSV that don't use a .uk TLD.
# Matched as domain suffixes, so subdomains (amp.theguardian.com,
# bestof.dailymail.com) match their base entries.
UK_WEBSITE_ALLOWLIST = (
    'theguardian.com',
    'bbc.com',
    'bbcgoodfood.com',
    'dailymail.com',
)

# 4000 (was 5000): row lines now carry the Market Requests volume, and a 5000-row
# chunk lands too close to GPT-4o's 128K context limit.
CHUNK_SIZE = 4000  # entries per website chunk
MAX_WORKERS = 4

# ---------------------------------------------------------------------------
# Audience targeting (deterministic, pre-GPT)
# ---------------------------------------------------------------------------
# The inventory CSVs carry one measured audience signal: the `Audience` column
# (General Market, Women Owned, Hispanic/Latino, AAPI, ...). When the brief /
# audience profile clearly targets one of these segments, rows tagged for it are
# moved to the front of the inventory so GPT sees them first instead of finding
# them drowned among ~28K "General Market" rows.
#
# Maps detection keywords → the CSV `Audience` values they select.
_AUDIENCE_TARGET_KEYWORDS = {
    ('hispanic', 'latino', 'latina', 'latinx', 'spanish-language', 'spanish language'):
        ('Hispanic/Latino',),
    ('aapi', 'asian american', 'asian-american', 'pacific islander'):
        ('AAPI', 'Asian American'),
    ('african american', 'african-american', 'black audience', 'black consumers', 'black community'):
        ('African American',),
    ('lgbtq', 'lgbt+', 'queer audience'):
        ('LGBTQ+',),
    ('native american', 'indigenous'):
        ('Native American',),
}

# Gender is special-cased: psychographic profiles always quote a gender split
# (e.g. "57% Female"), so the bare word "female" would match almost every
# campaign. Only treat the campaign as female-targeted when the split is
# clearly female-dominant or the brief says so explicitly.
_FEMALE_EXPLICIT_KEYWORDS = ('women', "women's", 'moms', 'mothers', 'female audience', 'female-focused')


def _detect_audience_targets(brief_text: str, audience_context: str) -> List[str]:
    """Return the CSV `Audience` values this campaign clearly targets."""
    import re
    text = f"{brief_text}\n{audience_context}".lower()
    targets: List[str] = []

    for keywords, csv_values in _AUDIENCE_TARGET_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            targets.extend(csv_values)

    female_dominant = any(
        int(m) >= 55 for m in re.findall(r'(\d{1,2})%\s*female', text)
    )
    if female_dominant or any(kw in text for kw in _FEMALE_EXPLICIT_KEYWORDS):
        targets.append('Women Owned')

    return targets


def _prioritize_audience_rows(df: pd.DataFrame, targets: List[str]):
    """Stable-partition inventory: audience-matched rows first, original order kept.

    Returns (df, n_matched) so callers know how many boosted rows lead the frame.
    """
    if not targets or 'Audience' not in df.columns:
        return df, 0
    target_set = {t.lower() for t in targets}
    mask = df['Audience'].astype(str).str.strip().str.lower().isin(target_set)
    n_matched = int(mask.sum())
    if n_matched == 0:
        return df, 0
    print(f"  [inventory] Audience boost: {n_matched} rows matching {targets} moved to front")
    return pd.concat([df[mask], df[~mask]], ignore_index=True), n_matched


def _format_requests(value) -> str:
    """Compact human form of the Market Requests volume (e.g. 71158907 → '71M')."""
    try:
        n = int(float(str(value).replace(',', '')))
    except (ValueError, TypeError):
        return ''
    if n >= 1_000_000:
        return f"{n // 1_000_000}M"
    if n >= 1_000:
        return f"{n // 1_000}K"
    return str(n)


# ---------------------------------------------------------------------------
# Inventory loading
# ---------------------------------------------------------------------------

def _load_inventory(inventory_type: str, market: str = "US") -> Optional[pd.DataFrame]:
    """Load and cache an inventory CSV (cache keyed by type + market).

    - UK: tries the UK CSV variant first, falling back to the US file (with a
      logged warning) when no UK file exists yet.
    - Global: combines the US and UK inventories (de-duplicated), per the
      client's definition that Global inventory = US + UK.
    """
    cache_key = f"{inventory_type}:{market}"
    if cache_key in _inventory_cache:
        return _inventory_cache[cache_key]

    if market == "Global":
        us_df = _load_inventory(inventory_type, "US")
        uk_df = _load_inventory(inventory_type, "UK")
        frames = [df for df in (us_df, uk_df) if df is not None]
        if not frames:
            return None
        combined = pd.concat(frames, ignore_index=True)
        key = _DEDUP_KEY.get(inventory_type)
        if key and key in combined.columns:
            combined = combined.drop_duplicates(subset=[key], keep='first').reset_index(drop=True)
        _inventory_cache[cache_key] = combined
        print(f"  [inventory] Loaded {cache_key}: {len(combined)} entries (US+UK combined)")
        return combined

    filename = INVENTORY_FILES.get(inventory_type)
    if not filename:
        return None

    if market == "UK":
        if _has_uk_file(inventory_type):
            filename = UK_INVENTORY_FILES[inventory_type]
        else:
            print(f"  [inventory] No UK file for {inventory_type} — falling back to US inventory with UK prompt context")

    filepath = os.path.join(INVENTORY_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  [inventory] File not found: {filepath}")
        return None

    df = pd.read_csv(filepath)
    _inventory_cache[cache_key] = df
    print(f"  [inventory] Loaded {cache_key}: {len(df)} entries, columns={list(df.columns)}")
    return df


def _filter_websites_for_market(df: pd.DataFrame, market: str) -> pd.DataFrame:
    """Filter the global websites inventory to a market-relevant subset.

    Only used as a FALLBACK when no dedicated UK websites file exists: the
    global CSV has no country column, so UK relevance is inferred from the
    domain (.uk TLDs plus an allowlist of UK publishers on other TLDs).
    """
    if market != "UK" or _has_uk_file('websites'):
        return df

    def _is_uk_domain(domain) -> bool:
        d = str(domain).strip().lower()
        if d.endswith('.uk'):
            return True
        return any(d == allowed or d.endswith('.' + allowed) for allowed in UK_WEBSITE_ALLOWLIST)

    filtered = df[df['Domain Name'].apply(_is_uk_domain)]
    print(f"  [inventory] UK website filter: {len(df)} → {len(filtered)} entries")
    return filtered


# ---------------------------------------------------------------------------
# Compact formatting (token-efficient for GPT-4o)
# ---------------------------------------------------------------------------

def _format_website_row(row) -> str:
    """Format a single website row as compact text.
    CSV columns: Domain Name, Type, Site Rating, Category, Behavioral Keywords, Market Requests, Audience
    """
    parts = []
    domain = row.get('Domain Name', '')
    parts.append(str(domain).strip())

    category = row.get('Category', '')
    if pd.notna(category) and str(category).strip():
        parts.append(str(category).strip())

    keywords = row.get('Behavioral Keywords', '')
    if pd.notna(keywords) and str(keywords).strip():
        parts.append(str(keywords).strip()[:80])

    audience = row.get('Audience', '')
    if pd.notna(audience) and str(audience).strip():
        parts.append(str(audience).strip()[:60])

    requests = _format_requests(row.get('Market Requests', ''))
    if requests:
        parts.append(requests)

    return ' | '.join(parts)


def _format_tv_streaming_row(row) -> str:
    """Format a single TV/streaming row as compact text.
    CSV columns: App/Platform Name, Publisher Name, Type, Site Rating, Category, Behavioral Keywords, Market Requests, Audience
    """
    parts = []
    name = row.get('App/Platform Name', '')
    parts.append(str(name).strip())

    publisher = row.get('Publisher Name', '')
    if pd.notna(publisher) and str(publisher).strip():
        parts.append(str(publisher).strip())

    category = row.get('Category', '')
    if pd.notna(category) and str(category).strip():
        parts.append(str(category).strip())

    keywords = row.get('Behavioral Keywords', '')
    if pd.notna(keywords) and str(keywords).strip():
        parts.append(str(keywords).strip()[:80])

    audience = row.get('Audience', '')
    if pd.notna(audience) and str(audience).strip():
        parts.append(str(audience).strip()[:60])

    requests = _format_requests(row.get('Market Requests', ''))
    if requests:
        parts.append(requests)

    return ' | '.join(parts)


def _format_inventory_block(df: pd.DataFrame, formatter, max_rows: int = None) -> str:
    """Format a DataFrame into a compact text block."""
    rows = df.head(max_rows) if max_rows else df
    lines = []
    for _, row in rows.iterrows():
        line = formatter(row)
        if line.strip():
            lines.append(line)
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# GPT-4o selection calls
# ---------------------------------------------------------------------------

def _market_prompt_section(market: str) -> str:
    """Extra prompt context for non-US markets."""
    if market == "UK":
        return (
            "\n## Market\n"
            "This is a UNITED KINGDOM campaign. Prefer UK-relevant publishers, "
            "networks and platforms available to UK audiences; deprioritise US-only inventory.\n"
        )
    if market == "Global":
        return (
            "\n## Market\n"
            "This is a GLOBAL campaign spanning US and UK markets. Select a mix of "
            "publishers, networks and platforms with broad reach across both markets.\n"
        )
    return ""


_AUDIENCE_KEYWORDS_IN_BRIEF = (
    'target audience', 'audience', 'demographic', 'consumer', 'shopper',
    'gen z', 'millennial', 'gen x', 'boomer', 'hhi', 'income', 'aged',
    'psychographic', 'persona',
)


def _brief_for_prompt(brief_text: str, limit: int = 3000) -> str:
    """First `limit` chars of the brief, plus any audience-describing paragraphs
    that fall beyond the cutoff (so a late "Target Audience" section in a long
    RFP still reaches the selector)."""
    head = brief_text[:limit]
    if len(brief_text) <= limit:
        return head

    extras: List[str] = []
    budget = 1200
    pos = 0
    for para in brief_text.split('\n\n'):
        start = pos
        pos += len(para) + 2
        # Paragraphs fully inside the head are already included
        if start + len(para) <= limit:
            continue
        p = para.strip()
        if not p:
            continue
        lower = p.lower()
        if any(kw in lower for kw in _AUDIENCE_KEYWORDS_IN_BRIEF):
            take = p[:budget - sum(len(e) for e in extras)]
            if take:
                extras.append(take)
            if sum(len(e) for e in extras) >= budget:
                break

    if not extras:
        return head
    return head + "\n\n## Audience details (from later in the brief)\n" + "\n\n".join(extras)


def _select_from_chunk(
    brief_text: str,
    audience_context: str,
    chunk_text: str,
    inventory_type: str,
    top_n: int,
    chunk_label: str = "",
    market: str = "US",
    audience_targets: Optional[List[str]] = None,
) -> List[dict]:
    """Ask GPT-4o to select the top N most relevant items from a chunk."""

    type_label = {
        'websites': 'website',
        'tv_networks': 'TV network',
        'streaming_platforms': 'streaming platform',
    }.get(inventory_type, 'media')

    column_hint = {
        'websites': 'Domain | Category | Keywords | Audience | MonthlyRequests',
        'tv_networks': 'Name | Publisher | Category | Keywords | Audience | MonthlyRequests',
        'streaming_platforms': 'Name | Publisher | Category | Keywords | Audience | MonthlyRequests',
    }.get(inventory_type, 'Name | Category')

    system_prompt = (
        "You are a media planning expert. Given an RFP brief and available "
        "ad inventory, select the most relevant entries for this campaign's target audience. "
        "Consider audience demographics, interests, and campaign objectives when scoring relevance."
    )

    audience_section = ""
    if audience_context:
        audience_section = f"\n## Audience Context\n{audience_context}\n"

    targets_note = ""
    if audience_targets:
        targets_note = (
            f"Inventory tagged for the campaign's target segments "
            f"({', '.join(sorted(set(audience_targets)))}) is listed FIRST — "
            f"strongly prefer these entries when they fit the campaign. "
        )

    user_prompt = (
        f"## RFP Brief\n{_brief_for_prompt(brief_text)}\n"
        f"{audience_section}"
        f"{_market_prompt_section(market)}"
        f"\n## Available {type_label} inventory ({column_hint})\n"
        f"Audience = the audience segment this inventory over-indexes with. "
        f"MonthlyRequests = relative ad request volume (higher = more scale).\n"
        f"{targets_note}\n"
        f"{chunk_text}\n\n"
        f"Select the top {top_n} most relevant {type_label} entries for this campaign. "
        f"Prioritize audience fit first, then prefer higher-volume inventory among "
        f"equally relevant options. "
        f'Return JSON with a "selections" array containing exactly {top_n} items:\n'
        f'{{"selections": [{{"name": "...", "category": "...", "relevance_score": <100-400>, "rationale": "..."}}]}}\n\n'
        f"Score 100-400 where 400 = perfect audience match. "
        f"In each rationale, state the specific audience attribute the pick serves. "
        f"Ensure variety across categories."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    label = f" [{chunk_label}]" if chunk_label else ""
    print(f"    [inventory] Calling GPT-4o for {inventory_type}{label} (top {top_n})...")

    result = make_openai_request(
        messages=messages,
        model="gpt-4o",
        response_format={"type": "json_object"},
        temperature=0.0,
        max_tokens=2000,
        max_retries=2,
    )

    if not result:
        print(f"    [inventory] GPT-4o returned None for {inventory_type}{label}")
        return []

    # make_openai_request with json_object format returns parsed dict directly.
    # It may also return {"raw_content": "..."} on parse failure,
    # or {"content": "..."} without json_object format.
    parsed = result

    # Handle raw_content fallback from make_openai_request
    if isinstance(parsed, dict) and 'raw_content' in parsed:
        try:
            parsed = json.loads(parsed['raw_content'])
        except (json.JSONDecodeError, TypeError):
            print(f"    [inventory] Failed to parse raw_content for {inventory_type}{label}")
            return []

    # Handle {"content": "..."} wrapper (non-json_object mode)
    if isinstance(parsed, dict) and 'content' in parsed and isinstance(parsed['content'], str):
        try:
            parsed = json.loads(parsed['content'])
        except (json.JSONDecodeError, TypeError):
            print(f"    [inventory] Failed to parse content for {inventory_type}{label}")
            return []

    # GPT-4o json_object mode always returns a dict. The array is inside a key.
    if isinstance(parsed, dict):
        # Log keys for debugging
        print(f"    [inventory] Response keys for {inventory_type}{label}: {list(parsed.keys())}")

        # First: find any key that holds a list (the selections array)
        list_candidates = {k: v for k, v in parsed.items() if isinstance(v, list)}
        if list_candidates:
            # Prefer known key names, otherwise take the first/longest list
            for key in ('results', 'items', 'selections', 'top', 'data', 'inventory',
                        'top_websites', 'top_tv_networks', 'top_streaming_platforms',
                        'websites', 'tv_networks', 'streaming_platforms'):
                if key in list_candidates:
                    parsed = list_candidates[key]
                    break
            else:
                # Take the longest list (most likely the selections)
                parsed = max(list_candidates.values(), key=len)
        elif 'name' in parsed:
            # Single item response
            parsed = [parsed]

    if not isinstance(parsed, list):
        print(f"    [inventory] Unexpected response format for {inventory_type}{label}: {type(parsed)}")
        return []

    print(f"    [inventory] Got {len(parsed)} selections for {inventory_type}{label}")
    return parsed


def _aggregate_website_winners(
    brief_text: str,
    audience_context: str,
    all_winners: List[dict],
    top_n: int = 5,
    market: str = "US",
) -> List[dict]:
    """Final aggregation pass: select top 5 from all chunk winners."""

    if len(all_winners) <= top_n:
        return all_winners

    # Format winners as compact text for the aggregation call
    winner_lines = []
    for w in all_winners:
        name = w.get('name', '')
        cat = w.get('category', '')
        score = w.get('relevance_score', 0)
        rationale = w.get('rationale', '')[:80]
        winner_lines.append(f"{name} | {cat} | Score: {score} | {rationale}")

    winner_text = '\n'.join(winner_lines)

    system_prompt = (
        "You are a media planning expert. From pre-screened website candidates, "
        "select the final top picks ensuring category diversity and maximum audience relevance."
    )

    audience_section = ""
    if audience_context:
        audience_section = f"\n## Audience Context\n{audience_context}\n"

    user_prompt = (
        f"## RFP Brief\n{_brief_for_prompt(brief_text)}\n"
        f"{audience_section}"
        f"{_market_prompt_section(market)}"
        f"\n## Pre-screened website candidates ({len(all_winners)} total)\n"
        f"{winner_text}\n\n"
        f"Select the final top {top_n} websites. Ensure category diversity. "
        f"In each rationale, state the specific audience attribute the pick serves. "
        f'Return JSON with a "selections" array containing exactly {top_n} items:\n'
        f'{{"selections": [{{"name": "...", "category": "...", "relevance_score": <100-400>, "rationale": "..."}}]}}'
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    print(f"    [inventory] Final aggregation: {len(all_winners)} candidates → top {top_n}")

    result = make_openai_request(
        messages=messages,
        model="gpt-4o",
        response_format={"type": "json_object"},
        temperature=0.0,
        max_tokens=1500,
        max_retries=2,
    )

    if not result:
        # Fallback: return top-scored items from chunk passes
        print(f"    [inventory] Aggregation failed, using top-scored chunk winners")
        sorted_winners = sorted(all_winners, key=lambda x: x.get('relevance_score', 0), reverse=True)
        return sorted_winners[:top_n]

    # make_openai_request with json_object returns parsed dict directly
    parsed = result

    if isinstance(parsed, dict) and 'raw_content' in parsed:
        try:
            parsed = json.loads(parsed['raw_content'])
        except (json.JSONDecodeError, TypeError):
            sorted_winners = sorted(all_winners, key=lambda x: x.get('relevance_score', 0), reverse=True)
            return sorted_winners[:top_n]

    if isinstance(parsed, dict):
        for key in ('results', 'items', 'selections', 'top', 'data'):
            if key in parsed and isinstance(parsed[key], list):
                parsed = parsed[key]
                break
        else:
            for v in parsed.values():
                if isinstance(v, list):
                    parsed = v
                    break

    if not isinstance(parsed, list):
        sorted_winners = sorted(all_winners, key=lambda x: x.get('relevance_score', 0), reverse=True)
        return sorted_winners[:top_n]

    return parsed[:top_n]


# ---------------------------------------------------------------------------
# Per-inventory-type selection
# ---------------------------------------------------------------------------

def select_websites(brief_text: str, audience_context: str = "", market: str = "US") -> Optional[str]:
    """
    Select top 5 websites via batch chunking.
    Returns JSON string matching session_state.media_affinity format.
    """
    df = _load_inventory('websites', market)
    if df is None:
        return None

    df = _filter_websites_for_market(df, market)
    if df.empty:
        print(f"  [inventory] No website inventory left after {market} filter")
        return None

    targets = _detect_audience_targets(brief_text, audience_context)
    df, n_boosted = _prioritize_audience_rows(df, targets)

    # Split into chunks
    chunks = [df.iloc[i:i + CHUNK_SIZE] for i in range(0, len(df), CHUNK_SIZE)]
    print(f"  [inventory] Websites: {len(df)} entries → {len(chunks)} chunks of ~{CHUNK_SIZE}")

    # Process chunks in parallel
    all_winners = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {}
        for idx, chunk_df in enumerate(chunks):
            chunk_text = _format_inventory_block(chunk_df, _format_website_row)
            # Only chunks that contain boosted rows get the targets note.
            chunk_targets = targets if idx * CHUNK_SIZE < n_boosted else None
            future = pool.submit(
                _select_from_chunk,
                brief_text, audience_context, chunk_text,
                'websites', 10, f"chunk {idx+1}/{len(chunks)}", market,
                chunk_targets,
            )
            futures[future] = idx

        for future in as_completed(futures):
            idx = futures[future]
            try:
                winners = future.result()
                all_winners.extend(winners)
            except Exception as e:
                print(f"    [inventory] Website chunk {idx+1} failed: {e}")

    if not all_winners:
        return None

    # Final aggregation
    final = _aggregate_website_winners(brief_text, audience_context, all_winners, top_n=5, market=market)

    # Format to match session_state.media_affinity contract
    output = []
    for item in final:
        name = item.get('name', '')
        domain = name.replace('https://', '').replace('http://', '').strip('/')
        output.append({
            "name": domain,
            "url": f"https://{domain}" if not domain.startswith('http') else domain,
            "category": item.get('category', ''),
            "qvi": item.get('relevance_score', 200),
            "rationale": item.get('rationale', ''),
        })

    return json.dumps(output)


def select_tv_networks(brief_text: str, audience_context: str = "", market: str = "US") -> Optional[List[dict]]:
    """
    Select top 5 TV networks in a single pass.
    Returns list matching session_state.audience_media_consumption['tv_networks'] format.
    """
    df = _load_inventory('tv_networks', market)
    if df is None:
        return None

    targets = _detect_audience_targets(brief_text, audience_context)
    df, _ = _prioritize_audience_rows(df, targets)

    inventory_text = _format_inventory_block(df, _format_tv_streaming_row)
    print(f"  [inventory] TV networks: {len(df)} entries, single pass")

    results = _select_from_chunk(
        brief_text, audience_context, inventory_text,
        'tv_networks', 5, "single pass", market, targets
    )

    if not results:
        return None

    output = []
    for item in results:
        output.append({
            "name": item.get('name', ''),
            "category": item.get('category', ''),
            "qvi": item.get('relevance_score', 200),
            "rationale": item.get('rationale', ''),
        })
    return output


def select_streaming_platforms(brief_text: str, audience_context: str = "", market: str = "US") -> Optional[List[dict]]:
    """
    Select top 6 streaming platforms in a single pass.
    Returns list matching session_state.audience_media_consumption['streaming_platforms'] format.
    """
    df = _load_inventory('streaming_platforms', market)
    if df is None:
        return None

    targets = _detect_audience_targets(brief_text, audience_context)
    df, _ = _prioritize_audience_rows(df, targets)

    inventory_text = _format_inventory_block(df, _format_tv_streaming_row)
    print(f"  [inventory] Streaming platforms: {len(df)} entries, single pass")

    results = _select_from_chunk(
        brief_text, audience_context, inventory_text,
        'streaming_platforms', 6, "single pass", market, targets
    )

    if not results:
        return None

    output = []
    for item in results:
        output.append({
            "name": item.get('name', ''),
            "category": item.get('category', ''),
            "qvi": item.get('relevance_score', 200),
            "rationale": item.get('rationale', ''),
        })
    return output


# ---------------------------------------------------------------------------
# Audience context
# ---------------------------------------------------------------------------

def build_audience_context(audience_insights: dict) -> str:
    """Compact, human-readable audience summary for the selection prompts.

    Replaces json.dumps(insights)[:2000], which front-loaded Big Five scores and
    truncated mid-JSON — the media-relevant fields often never made it in.
    """
    if not audience_insights or not isinstance(audience_insights, dict):
        return ""

    lines: List[str] = []

    def add_list(label: str, key: str, cap: int = 5):
        values = audience_insights.get(key)
        if isinstance(values, list) and values:
            items = [str(v).strip() for v in values[:cap] if str(v).strip()]
            if items:
                lines.append(f"{label}: {'; '.join(items)}")

    signals = audience_insights.get('activation_signals') or {}
    demo = signals.get('demographics')
    if isinstance(demo, list) and demo:
        lines.append(f"Demographics: {'; '.join(str(d).strip() for d in demo[:5])}")

    for label, key in (
        ("Age range", 'age_range'),
        ("Income", 'income_level'),
    ):
        value = audience_insights.get(key)
        if value and isinstance(value, str):
            lines.append(f"{label}: {value.strip()}")

    add_list("Media preferences", 'media_preferences')
    add_list("Interests", 'interests')
    add_list("Top values", 'top_values')
    add_list("Lifestyle", 'lifestyle_activities')
    add_list("Hobbies", 'hobbies')
    add_list("Shopping behaviors", 'shopping_behaviors')
    add_list("Motivations", 'motivations')
    add_list("Preferred brands", 'preferred_brands')

    return "\n".join(lines)[:2000]


# ---------------------------------------------------------------------------
# Caching helpers
# ---------------------------------------------------------------------------

def _cache_key(brief_text: str, market: str = "US") -> str:
    """Generate a stable cache key from market + brief text."""
    return hashlib.md5(f"{market}:{brief_text}".encode('utf-8')).hexdigest()[:16]


def _get_cached(brief_text: str, market: str = "US") -> Optional[dict]:
    """Check session_state cache for previous results."""
    if not HAS_STREAMLIT:
        return None
    cache = st.session_state.get('_inventory_cache', {})
    key = _cache_key(brief_text, market)
    return cache.get(key)


def _set_cached(brief_text: str, results: dict, market: str = "US"):
    """Store results in session_state cache."""
    if not HAS_STREAMLIT:
        return
    if '_inventory_cache' not in st.session_state:
        st.session_state._inventory_cache = {}
    key = _cache_key(brief_text, market)
    st.session_state._inventory_cache[key] = results


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def select_all_inventory(brief_text: str, audience_context: str = "", market: str = "US") -> dict:
    """
    Select relevant inventory across all three types.

    Args:
        market: "US" (default), "UK", or "Global" (US + UK combined) —
            selects market-specific inventory.

    Returns dict with keys:
        'media_affinity': JSON string (websites) or None
        'tv_networks': list of dicts or None
        'streaming_platforms': list of dicts or None
    """
    # Check cache first
    cached = _get_cached(brief_text, market)
    if cached:
        print("  [inventory] Cache hit — returning cached inventory results")
        return cached

    results = {
        'media_affinity': None,
        'tv_networks': None,
        'streaming_platforms': None,
    }

    # Check if any inventory files exist
    any_found = False
    for inv_type in INVENTORY_FILES:
        filepath = os.path.join(INVENTORY_DIR, INVENTORY_FILES[inv_type])
        if os.path.exists(filepath):
            any_found = True
            break

    if not any_found:
        print("  [inventory] No inventory files found in data/inventory/, skipping")
        return results

    # Run all three in parallel using one shared pool
    start = time.time()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        future_websites = pool.submit(select_websites, brief_text, audience_context, market)
        future_tv = pool.submit(select_tv_networks, brief_text, audience_context, market)
        future_streaming = pool.submit(select_streaming_platforms, brief_text, audience_context, market)

        # Collect results
        try:
            results['media_affinity'] = future_websites.result()
        except Exception as e:
            print(f"  [inventory] Website selection failed: {e}")

        try:
            results['tv_networks'] = future_tv.result()
        except Exception as e:
            print(f"  [inventory] TV network selection failed: {e}")

        try:
            results['streaming_platforms'] = future_streaming.result()
        except Exception as e:
            print(f"  [inventory] Streaming platform selection failed: {e}")

    elapsed = time.time() - start
    print(f"  [inventory] All selections completed in {elapsed:.1f}s")

    # Cache results
    _set_cached(brief_text, results, market)

    return results
