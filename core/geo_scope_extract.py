"""
LLM half of campaign geo-scope detection (see core/geo_scope.py for the
deterministic resolver). Kept separate so the pure scoring path never imports
the OpenAI client. Port of ari-api's geo-scope-extract.ts.
"""
from core.ai_utils import make_openai_request
from core.geo_scope import NATIONAL_SCOPE, resolve_geo_scope

_SYSTEM = (
    "You extract the geographic scope of advertising campaigns from briefs. "
    "You must return ONLY valid JSON with no additional text."
)

_PROMPT = """Determine WHERE this advertising campaign's media will run / where its target audience lives, based ONLY on explicit statements in the brief: target markets, flight geography, "statewide", store/dealer footprint the campaign supports, phrases like "in the Phoenix and Tucson markets".

Do NOT treat these as campaign geography: brand or agency headquarters and addresses, legal notices, place names inside brand or product names (e.g. "Arizona Iced Tea", "Texas Roadhouse"), past case studies, or passing examples.

If the brief says national / nationwide / US-wide, or gives no explicit campaign geography, the scope is "national" with empty lists.

Return ONLY this JSON:
{
  "scope": "national" or "regional",
  "states": ["full US state names the campaign explicitly targets"],
  "regions": ["named multi-state regions the campaign targets, e.g. Southwest, Pacific Northwest, New England"],
  "markets": ["explicitly named cities/metros/DMAs the campaign targets, e.g. Phoenix, Dallas-Fort Worth"],
  "evidence": "short quote from the brief that establishes the scope"
}

Brief:
"""


def extract_geo_scope(brief_text):
    """Ask the model where the campaign runs, then resolve deterministically. Never raises."""
    try:
        raw = make_openai_request(
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": _PROMPT + (brief_text or "")[:6000]},
            ],
            model="gpt-4o",
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=300,
            max_retries=2,
        )
        scope = resolve_geo_scope(raw if isinstance(raw, dict) else None)
        print(f"Geo scope: {scope['type']} ({scope['label']}) states={scope['states']} dmas={scope['dma_codes']}")
        return scope
    except Exception as e:
        print(f"⚠ Geo scope extraction failed — defaulting to national: {e}")
        return dict(NATIONAL_SCOPE)
