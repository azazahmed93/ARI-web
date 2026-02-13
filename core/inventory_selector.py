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

CHUNK_SIZE = 5000  # entries per website chunk
MAX_WORKERS = 4


# ---------------------------------------------------------------------------
# Inventory loading
# ---------------------------------------------------------------------------

def _load_inventory(inventory_type: str) -> Optional[pd.DataFrame]:
    """Load and cache an inventory CSV. Returns None if file not found."""
    if inventory_type in _inventory_cache:
        return _inventory_cache[inventory_type]

    filename = INVENTORY_FILES.get(inventory_type)
    if not filename:
        return None

    filepath = os.path.join(INVENTORY_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  [inventory] File not found: {filepath}")
        return None

    df = pd.read_csv(filepath)
    _inventory_cache[inventory_type] = df
    print(f"  [inventory] Loaded {inventory_type}: {len(df)} entries, columns={list(df.columns)}")
    return df


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

def _select_from_chunk(
    brief_text: str,
    audience_context: str,
    chunk_text: str,
    inventory_type: str,
    top_n: int,
    chunk_label: str = "",
) -> List[dict]:
    """Ask GPT-4o to select the top N most relevant items from a chunk."""

    type_label = {
        'websites': 'website',
        'tv_networks': 'TV network',
        'streaming_platforms': 'streaming platform',
    }.get(inventory_type, 'media')

    column_hint = {
        'websites': 'Domain | Category | Keywords | Audience',
        'tv_networks': 'Name | Publisher | Category | Keywords | Audience',
        'streaming_platforms': 'Name | Publisher | Category | Keywords | Audience',
    }.get(inventory_type, 'Name | Category')

    system_prompt = (
        "You are a media planning expert. Given an RFP brief and available "
        "ad inventory, select the most relevant entries for this campaign's target audience. "
        "Consider audience demographics, interests, and campaign objectives when scoring relevance."
    )

    audience_section = ""
    if audience_context:
        audience_section = f"\n## Audience Context\n{audience_context}\n"

    user_prompt = (
        f"## RFP Brief\n{brief_text[:3000]}\n"
        f"{audience_section}"
        f"\n## Available {type_label} inventory ({column_hint})\n"
        f"{chunk_text}\n\n"
        f"Select the top {top_n} most relevant {type_label} entries for this campaign. "
        f'Return JSON with a "selections" array containing exactly {top_n} items:\n'
        f'{{"selections": [{{"name": "...", "category": "...", "relevance_score": <100-400>, "rationale": "..."}}]}}\n\n'
        f"Score 100-400 where 400 = perfect audience match. "
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
        temperature=0.3,
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
        f"## RFP Brief\n{brief_text[:3000]}\n"
        f"{audience_section}"
        f"\n## Pre-screened website candidates ({len(all_winners)} total)\n"
        f"{winner_text}\n\n"
        f"Select the final top {top_n} websites. Ensure category diversity. "
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
        temperature=0.3,
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

def select_websites(brief_text: str, audience_context: str = "") -> Optional[str]:
    """
    Select top 5 websites via batch chunking.
    Returns JSON string matching session_state.media_affinity format.
    """
    df = _load_inventory('websites')
    if df is None:
        return None

    # Split into chunks
    chunks = [df.iloc[i:i + CHUNK_SIZE] for i in range(0, len(df), CHUNK_SIZE)]
    print(f"  [inventory] Websites: {len(df)} entries → {len(chunks)} chunks of ~{CHUNK_SIZE}")

    # Process chunks in parallel
    all_winners = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {}
        for idx, chunk_df in enumerate(chunks):
            chunk_text = _format_inventory_block(chunk_df, _format_website_row)
            future = pool.submit(
                _select_from_chunk,
                brief_text, audience_context, chunk_text,
                'websites', 10, f"chunk {idx+1}/{len(chunks)}"
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
    final = _aggregate_website_winners(brief_text, audience_context, all_winners, top_n=5)

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
        })

    return json.dumps(output)


def select_tv_networks(brief_text: str, audience_context: str = "") -> Optional[List[dict]]:
    """
    Select top 5 TV networks in a single pass.
    Returns list matching session_state.audience_media_consumption['tv_networks'] format.
    """
    df = _load_inventory('tv_networks')
    if df is None:
        return None

    inventory_text = _format_inventory_block(df, _format_tv_streaming_row)
    print(f"  [inventory] TV networks: {len(df)} entries, single pass")

    results = _select_from_chunk(
        brief_text, audience_context, inventory_text,
        'tv_networks', 5, "single pass"
    )

    if not results:
        return None

    output = []
    for item in results:
        output.append({
            "name": item.get('name', ''),
            "category": item.get('category', ''),
            "qvi": item.get('relevance_score', 200),
        })
    return output


def select_streaming_platforms(brief_text: str, audience_context: str = "") -> Optional[List[dict]]:
    """
    Select top 6 streaming platforms in a single pass.
    Returns list matching session_state.audience_media_consumption['streaming_platforms'] format.
    """
    df = _load_inventory('streaming_platforms')
    if df is None:
        return None

    inventory_text = _format_inventory_block(df, _format_tv_streaming_row)
    print(f"  [inventory] Streaming platforms: {len(df)} entries, single pass")

    results = _select_from_chunk(
        brief_text, audience_context, inventory_text,
        'streaming_platforms', 6, "single pass"
    )

    if not results:
        return None

    output = []
    for item in results:
        output.append({
            "name": item.get('name', ''),
            "category": item.get('category', ''),
            "qvi": item.get('relevance_score', 200),
        })
    return output


# ---------------------------------------------------------------------------
# Caching helpers
# ---------------------------------------------------------------------------

def _cache_key(brief_text: str) -> str:
    """Generate a stable cache key from brief text."""
    return hashlib.md5(brief_text.encode('utf-8')).hexdigest()[:16]


def _get_cached(brief_text: str) -> Optional[dict]:
    """Check session_state cache for previous results."""
    if not HAS_STREAMLIT:
        return None
    cache = st.session_state.get('_inventory_cache', {})
    key = _cache_key(brief_text)
    return cache.get(key)


def _set_cached(brief_text: str, results: dict):
    """Store results in session_state cache."""
    if not HAS_STREAMLIT:
        return
    if '_inventory_cache' not in st.session_state:
        st.session_state._inventory_cache = {}
    key = _cache_key(brief_text)
    st.session_state._inventory_cache[key] = results


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def select_all_inventory(brief_text: str, audience_context: str = "") -> dict:
    """
    Select relevant inventory across all three types.

    Returns dict with keys:
        'media_affinity': JSON string (websites) or None
        'tv_networks': list of dicts or None
        'streaming_platforms': list of dicts or None
    """
    # Check cache first
    cached = _get_cached(brief_text)
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
        future_websites = pool.submit(select_websites, brief_text, audience_context)
        future_tv = pool.submit(select_tv_networks, brief_text, audience_context)
        future_streaming = pool.submit(select_streaming_platforms, brief_text, audience_context)

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
    _set_cached(brief_text, results)

    return results
