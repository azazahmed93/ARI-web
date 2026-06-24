"""
Platform → Heatmap-channel normalization map.

WHY THIS EXISTS
---------------
The app carries two unrelated media vocabularies that drifted apart historically
(see git: segment generator ~Apr 2025 vs. the trend heatmap reused & relabeled
"Performance"→"Recommendation" Mar 2026):

  1. Audience-Insights "Recommended Platform"  — free-form media-BUY-TYPE names
     emitted by core.ai_insights.generate_audience_segments() in
     segment['platform_targeting'][*]['platform'].
     Real examples seen in code/output:
       "Display", "Video", "CTV/OTT", "OTT/CTV", "Audio", "Audio Streaming",
       "Mobile Video", "Video Channels", "Programmatic Video Platforms",
       "Sports Streaming Services", "Desktop and Tablet Display", "Mobile Gaming",
       "Programmatic", "Spanish Media Networks", "Digital Out-of-Home"

  2. "Audience Segment Media Recommendation" heatmap — a FIXED list of 10 ad-FORMAT
     channels in app.components.marketing_trends (the `categories` list):
       Rich Media, DOOH, Interactive Video, Social Display Boost,
       High Impact Display, Connected TV, Streaming Audio, In-Game Ads,
       Online Video, Native Ads

These never had a bridge between them. This module is that bridge.

DESIGN
------
- Keyword/substring matching (case-insensitive), ORDERED most-specific-first —
  same approach as core.benchmark_config.get_platform_benchmark(), because the
  platform names are free-form and GPT-generated (no enum to exact-match).
- Returns a `primary` heatmap channel (best single match) PLUS `spans` (all
  heatmap channels the buy-type reasonably covers) — because some buy-types are
  umbrellas: "Display" covers 4 heatmap channels, "Video" covers 3.
- `representable=False` flags buy-types that have NO heatmap channel at all
  (Search, Paid Social feed, Programmatic-as-method, network/language targeting).

KNOWN STRUCTURAL GAPS (intentionally surfaced, not hidden):
- RARELY-SOURCED heatmap channels: "In-Game Ads" only fills from an explicit
  "gaming" mention; "Interactive Video" only from "interactive [video]". Normal
  segments almost never emit these words, so those rows are usually orphaned.
- UMBRELLA buy-types: "Display" maps across 4 heatmap channels and "Video" across
  3 — there is no single heatmap cell that equals them.
- Segment names with NO heatmap channel at all (representable=False): "Search",
  "Programmatic" (as a buying method), "Spanish Media Networks" / language-network
  targeting.
"""

from typing import List, Optional, Dict

# The heatmap's fixed channels. MUST stay in sync with the `categories` list in
# app/components/marketing_trends.py (generate_audience_segment_trend_data).
HEATMAP_CHANNELS: List[str] = [
    "Rich Media", "DOOH", "Interactive Video", "Social Display Boost",
    "High Impact Display", "Connected TV", "Streaming Audio",
    "In-Game Ads", "Online Video", "Native Ads",
]

# Ordered rules: first matching keyword wins for `primary`.
# Order is deliberate — specific/compound types before broad umbrellas so that
# e.g. "Mobile Gaming"→In-Game, "Programmatic Video Platforms"→Online Video,
# "Audio Streaming"→Streaming Audio resolve before the generic "display"/
# "streaming" catch-alls.
#
# Each rule: type key, keywords, primary channel (None = unrepresentable),
# spans (channels the buy-type covers), representable flag, note.
PLATFORM_CHANNEL_RULES: List[Dict] = [
    {
        "type": "dooh",
        "keywords": ["dooh", "out of home", "out-of-home", "ooh", "billboard", "transit"],
        "primary": "DOOH", "spans": ["DOOH"], "representable": True,
        "note": "1:1",
    },
    {
        "type": "in_game",
        "keywords": ["in-game", "in game", "gaming", "esports", "gamer", "game"],
        "primary": "In-Game Ads", "spans": ["In-Game Ads"], "representable": True,
        "note": "1:1 (only source that can fill the In-Game Ads channel)",
    },
    {
        "type": "ctv",
        "keywords": ["ctv", "ott", "connected tv", "streaming tv", "smart tv"],
        "primary": "Connected TV", "spans": ["Connected TV"], "representable": True,
        "note": "1:1 concept; strings differ ('CTV/OTT' != 'Connected TV')",
    },
    {
        "type": "audio",
        "keywords": ["audio", "podcast", "music", "radio", "spotify", "pandora"],
        "primary": "Streaming Audio", "spans": ["Streaming Audio"], "representable": True,
        "note": "1:1 concept; strings differ ('Audio' != 'Streaming Audio')",
    },
    {
        "type": "interactive_video",
        "keywords": ["interactive video", "shoppable video"],
        "primary": "Interactive Video", "spans": ["Interactive Video"], "representable": True,
        "note": "1:1",
    },
    {
        "type": "rich_media",
        "keywords": ["rich media", "high impact", "high-impact", "interactive"],
        "primary": "Rich Media", "spans": ["Rich Media"], "representable": True,
        "note": "1:1 with the 'Rich Media' channel; bare 'interactive' lands here. NOT an "
                "umbrella — the heatmap keeps 'Rich Media' and 'Interactive Video' distinct",
    },
    {
        "type": "native",
        "keywords": ["native", "sponsored", "advertorial"],
        "primary": "Native Ads", "spans": ["Native Ads"], "representable": True,
        "note": "1:1 concept; strings differ ('Native' != 'Native Ads')",
    },
    {
        "type": "video",
        "keywords": ["online video", "mobile video", "video channels", "video", "youtube",
                     "vod", "pre-roll", "pre roll"],
        "primary": "Online Video",
        "spans": ["Online Video", "Interactive Video", "Connected TV"], "representable": True,
        "note": "UMBRELLA — 'Video' covers 3 heatmap channels; no single cell",
    },
    {
        "type": "streaming_generic",
        "keywords": ["streaming"],
        "primary": "Online Video",
        "spans": ["Online Video", "Connected TV", "Streaming Audio"], "representable": True,
        "note": "ambiguous ('Sports Streaming Services'); audio/CTV already handled above",
    },
    {
        "type": "paid_social",
        "keywords": ["social", "facebook", "instagram", "tiktok", "snapchat", "twitter", "linkedin"],
        "primary": "Social Display Boost", "spans": ["Social Display Boost"], "representable": True,
        "note": "PARTIAL — heatmap 'Social Display Boost' is display-on-social, not the feed-ad sense",
    },
    {
        "type": "display",
        "keywords": ["display", "banner", "desktop", "tablet"],
        "primary": "High Impact Display",
        "spans": ["High Impact Display", "Social Display Boost", "Rich Media", "Native Ads"],
        "representable": True,
        "note": "UMBRELLA — 'Display' covers 4 heatmap channels; no single cell",
    },
    # ---- Unrepresentable: no heatmap channel exists for these ----
    {
        "type": "search",
        "keywords": ["search", "sem", "paid search", "search engine"],
        "primary": None, "spans": [], "representable": False,
        "note": "NO heatmap channel for search",
    },
    {
        "type": "programmatic_method",
        "keywords": ["programmatic", "pmp", "private marketplace", "open exchange"],
        "primary": None, "spans": [], "representable": False,
        "note": "buying METHOD not a format; spans all — runs after video/display so compounds like 'Programmatic Video' resolve first",
    },
    {
        "type": "network_language",
        "keywords": ["network", "media networks", "spanish", "hispanic", "language", "multicultural"],
        "primary": None, "spans": [], "representable": False,
        "note": "audience/network targeting, not an ad format",
    },
]


def normalize_platform_to_channel(platform_name: Optional[str]) -> Dict:
    """Map a free-form platform_targeting name to the heatmap's channel vocabulary.

    Returns dict:
        {
          "input": <original>,
          "matched_type": <rule key or 'unknown'>,
          "primary": <heatmap channel str or None>,
          "spans": [<heatmap channels>],
          "representable": <bool>,           # False => no heatmap channel exists
          "is_umbrella": <bool>,             # True => spans >1 channel (no single cell)
          "note": <str>,
        }
    """
    name = (platform_name or "").strip().lower()
    if not name:
        return {"input": platform_name, "matched_type": "unknown", "primary": None,
                "spans": [], "representable": False, "is_umbrella": False,
                "note": "empty"}

    for rule in PLATFORM_CHANNEL_RULES:
        if any(kw in name for kw in rule["keywords"]):
            return {
                "input": platform_name,
                "matched_type": rule["type"],
                "primary": rule["primary"],
                "spans": list(rule["spans"]),
                "representable": rule["representable"],
                "is_umbrella": len(rule["spans"]) > 1,
                "note": rule["note"],
            }

    return {"input": platform_name, "matched_type": "unknown", "primary": None,
            "spans": [], "representable": False, "is_umbrella": False,
            "note": "no keyword matched"}


# Channels never reachable at all (none, currently) vs. only reachable through a
# rare/narrow keyword that segments seldom emit (the practically-orphaned rows).
def channels_without_source() -> List[str]:
    reachable = set()
    for rule in PLATFORM_CHANNEL_RULES:
        reachable.update(rule["spans"])
    return [c for c in HEATMAP_CHANNELS if c not in reachable]


# Channels that are only the PRIMARY of a rule whose keywords are rare in practice
# (segments almost never say "gaming" or "interactive video").
RARELY_SOURCED_CHANNELS: List[str] = ["In-Game Ads", "Interactive Video"]


# Reverse direction: heatmap channel -> friendly media-buy-vocabulary label, so the
# audience card can show buy-type wording ("CTV/OTT", "Display") instead of the
# heatmap's format wording ("Connected TV", "Social Display Boost") while the two
# still refer to the same recommendation.
CHANNEL_TO_BUYTYPE: Dict[str, str] = {
    "Rich Media": "Rich Media",
    "DOOH": "Digital Out-of-Home",
    "Interactive Video": "Interactive Video",
    "Social Display Boost": "Display",
    "High Impact Display": "Display",
    "Connected TV": "CTV/OTT",
    "Streaming Audio": "Audio",
    "In-Game Ads": "In-Game",
    "Online Video": "Video",
    "Native Ads": "Native",
}


def channel_to_display_label(channel: Optional[str]) -> str:
    """Map a heatmap channel back to a media-buy-vocabulary label for display.
    Falls back to the channel name itself if unmapped."""
    if not channel:
        return ""
    return CHANNEL_TO_BUYTYPE.get(channel, channel)


if __name__ == "__main__":
    # Coverage demo over the REAL vocabulary (hardcoded fallbacks + live-run names).
    KNOWN = [
        "Display", "Video", "CTV/OTT", "OTT/CTV", "Audio", "Audio Streaming",
        "Mobile Video", "Video Channels", "Programmatic Video Platforms",
        "Sports Streaming Services", "Desktop and Tablet Display", "Mobile Gaming",
        "Programmatic", "Spanish Media Networks", "Digital Out-of-Home",
        "Native", "Rich Media", "Connected TV", "Paid Social", "Search",
    ]
    print(f"{'platform_targeting name':<32} {'primary channel':<20} {'umbrella?':<10} repr  note")
    print("-" * 110)
    for p in KNOWN:
        r = normalize_platform_to_channel(p)
        prim = r["primary"] or "— none —"
        umb = ("UMBRELLA" if r["is_umbrella"] else "")
        repr_ = "yes" if r["representable"] else "NO"
        print(f"{p:<32} {prim:<20} {umb:<10} {repr_:<4}  {r['note']}")
    never = channels_without_source()
    print("\nHeatmap channels NEVER reachable: " + (", ".join(never) if never else "(none)"))
    print("Heatmap channels RARELY sourced (need a 'gaming'/'interactive video' mention): "
          + ", ".join(RARELY_SOURCED_CHANNELS))
