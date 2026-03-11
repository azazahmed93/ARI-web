"""
OpenX OpenAudience GraphQL API client.

Handles all communication with the OpenX API for audience creation and activation.
"""

import os
import time
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

# ---------- Configuration ----------

OPENX_API_URL = os.environ.get("OPENX_API_URL", "https://api.openx.com/oa/graphql")
OPENX_API_KEY = os.environ.get("OPENX_API_KEY", "")
OPENX_PROVIDER_ID = os.environ.get("OPENX_PROVIDER_ID", "")

DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
BACKOFF_BASE = 1.5

# ---------- GraphQL Queries ----------

QUERY_PING = """
query { ping }
"""

QUERY_SEGMENTS_BY_CATEGORY = """
query SegmentsByCategory($category: String!, $limit: Int!, $offset: Int!) {
  segmentsByCategory(category: $category, limit: $limit, offset: $offset) {
    id
    name
    category
    sub_category
    path
    provider_id
  }
}
"""

QUERY_SEGMENTS_COUNT_BY_CATEGORY = """
query SegmentsCountByCategory($category: String!) {
  segmentsCountByCategory(category: $category)
}
"""

QUERY_OPTIONS_BY_PATH = """
query OptionsByPath($path: String!, $filter: String) {
  optionsByPath(path: $path, filter: $filter) {
    id
    name
    path
    children {
      id
      name
      path
    }
  }
}
"""

QUERY_ESTIMATE_AUDIENCE = """
query EstimateAudience($params: AudienceCreateParams!) {
  audienceEstimate(input: $params) {
    id_type
    count
  }
}
"""

MUTATION_CREATE_AUDIENCE = """
mutation CreateAudience($params: AudienceCreateParams!) {
  audienceCreate(input: $params) {
    id
    name
    status
    export_type
    export_targets
    normalized_definition
    created_date
  }
}
"""

MUTATION_ACTIVATE_AUDIENCE = """
mutation ActivateAudience($audienceId: uuid!) {
  audienceActivate(id: $audienceId)
}
"""

QUERY_AUDIENCE_STATUS = """
query AudienceStatus($audienceId: ID!) {
  audience(id: $audienceId) {
    id
    name
    status
    estimated_reach
    created_date
    updated_date
  }
}
"""

MUTATION_CREATE_DEAL = """
mutation CreateDeal($input: DealCreateParams!, $deal_id_prefix: String) {
  dealCreate(input: $input, deal_id_prefix: $deal_id_prefix) {
    id
    name
    deal_id
    status
    currency
    deal_price
    pmp_deal_type
    start_date
    created_date
  }
}
"""

QUERY_DEAL_BY_ID = """
query DealById($id: String!) {
  dealById(id: $id) {
    id
    name
    deal_id
    status
    start_date
    end_date
    created_date
  }
}
"""


# ---------- Service ----------

class OpenXService:
    """GraphQL client for the OpenX OpenAudience API."""

    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or OPENX_API_URL
        self.api_key = api_key or OPENX_API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "x-apikey": self.api_key,
        })

    # ------ helpers ------

    @staticmethod
    def is_configured() -> bool:
        """Check whether the required env vars are set."""
        return bool(os.environ.get("OPENX_API_KEY"))

    def ping(self) -> bool:
        """Return True if the API responds to a ping query."""
        result = self._execute(QUERY_PING)
        if result and "ping" in result:
            logger.info("OpenX API ping: %s", result["ping"])
            return True
        return False

    def _execute(
        self,
        query: str,
        variables: dict = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ) -> Optional[dict]:
        """Execute a GraphQL request with exponential backoff.

        Returns the ``data`` dict on success, or None on failure.
        Does **not** retry on 401/403 (auth errors).
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        last_error = None
        for attempt in range(max_retries):
            try:
                resp = self.session.post(self.api_url, json=payload, timeout=timeout)

                # Don't retry auth errors
                if resp.status_code in (401, 403):
                    logger.error("OpenX auth error (%s): %s", resp.status_code, resp.text[:200])
                    return None

                resp.raise_for_status()
                body = resp.json()

                if "errors" in body:
                    logger.warning("OpenX GraphQL errors: %s", body["errors"])
                    return None

                return body.get("data")

            except requests.exceptions.RequestException as exc:
                last_error = exc
                # Log the response body for 4xx errors to aid debugging
                resp_body = ""
                if hasattr(exc, "response") and exc.response is not None:
                    try:
                        resp_body = exc.response.text[:500]
                    except Exception:
                        pass
                wait = BACKOFF_BASE ** attempt
                logger.warning(
                    "OpenX request attempt %d/%d failed: %s — retrying in %.1fs%s",
                    attempt + 1, max_retries, exc, wait,
                    f"\n  Response body: {resp_body}" if resp_body else "",
                )
                time.sleep(wait)

        logger.error("OpenX request failed after %d retries: %s", max_retries, last_error)
        return None

    # ------ Segments ------

    def get_segments_by_category(
        self, category: str, limit: int = 200, offset: int = 0
    ) -> list:
        """Fetch segments for a given category (e.g. demographic_age, location)."""
        data = self._execute(
            QUERY_SEGMENTS_BY_CATEGORY,
            {"category": category, "limit": limit, "offset": offset},
        )
        if data:
            return data.get("segmentsByCategory", [])
        return []

    def get_segments_count_by_category(self, category: str) -> int:
        """Return the total count of segments in *category*."""
        data = self._execute(
            QUERY_SEGMENTS_COUNT_BY_CATEGORY,
            {"category": category},
        )
        if data:
            return data.get("segmentsCountByCategory", 0)
        return 0

    # ------ Options (taxonomy, geo, device types) ------

    def get_options_by_path(self, path: str, filter_text: str = None) -> list:
        """Query the options tree (e.g. ``domain.categories``, ``geo.us.states``)."""
        variables = {"path": path}
        if filter_text:
            variables["filter"] = filter_text
        data = self._execute(QUERY_OPTIONS_BY_PATH, variables)
        if data:
            return data.get("optionsByPath", [])
        return []

    def get_all_segments_by_category(self, category: str) -> list:
        """Fetch ALL segments for a category, handling pagination."""
        all_segs = []
        offset = 0
        batch = 500
        while True:
            page = self.get_segments_by_category(category, limit=batch, offset=offset)
            if not page:
                break
            all_segs.extend(page)
            if len(page) < batch:
                break
            offset += batch
        return all_segs

    # ------ Audiences ------

    def estimate_audience(self, params: dict) -> list:
        """Get a reach estimate before audience creation."""
        data = self._execute(QUERY_ESTIMATE_AUDIENCE, {"params": params})
        if data and "audienceEstimate" in data:
            return data["audienceEstimate"]
        return []

    def create_audience(self, params: dict) -> Optional[dict]:
        """Create a new audience.

        *params* should match the ``AudienceCreateInput`` schema::

            {
                "name": "Brand - Segment Name",
                "export_type": "oa_match",
                "export_targets": ["user", "ctv"],
                "direct_audience_provider": "<provider_id>",
                "normalized_definition": { ... }
            }
        """
        data = self._execute(MUTATION_CREATE_AUDIENCE, {"params": params})
        if data and "audienceCreate" in data:
            return data["audienceCreate"]
        return None

    def activate_audience(self, audience_id: str) -> bool:
        """Activate a created audience.  Returns True on success.

        The API returns the audience uuid on success.
        """
        data = self._execute(MUTATION_ACTIVATE_AUDIENCE, {"audienceId": audience_id})
        if data and "audienceActivate" in data:
            # API returns the uuid string directly, not an object
            return bool(data["audienceActivate"])
        return False

    def get_audience_status(self, audience_id: str) -> Optional[dict]:
        """Poll audience activation status."""
        data = self._execute(QUERY_AUDIENCE_STATUS, {"audienceId": audience_id})
        if data:
            return data.get("audience")
        return None

    # ------ Deals ------

    def create_deal(
        self, params: dict, deal_id_prefix: str = None
    ) -> Optional[dict]:
        """Create a new deal with audience targeting.

        *params* should match the ``DealCreateParams`` schema.
        Returns the created Deal object on success, or None on failure.
        """
        variables: dict = {"input": params}
        if deal_id_prefix:
            variables["deal_id_prefix"] = deal_id_prefix
        data = self._execute(MUTATION_CREATE_DEAL, variables)
        if data and "dealCreate" in data:
            return data["dealCreate"]
        return None

    def get_deal(self, deal_id: str) -> Optional[dict]:
        """Fetch a deal by its ID."""
        data = self._execute(QUERY_DEAL_BY_ID, {"id": deal_id})
        if data:
            return data.get("dealById")
        return None
