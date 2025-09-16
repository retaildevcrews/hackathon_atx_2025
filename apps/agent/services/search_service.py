from __future__ import annotations

import logging
from typing import Any
from functools import lru_cache
import httpx

from config import get_settings

logger = logging.getLogger(__name__)


class AzureSearchService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.enabled = all(
            [
                self.settings.azure_search_endpoint,
                self.settings.azure_search_api_key,
                self.settings.azure_search_index,
            ]
        )
        if not self.enabled:
            logger.warning("Azure Cognitive Search not fully configured; returning stub results.")

    async def search(self, query: str, top: int = 3) -> list[dict[str, Any]]:
        if not self.enabled:
            return [
                {
                    "id": "stub-1",
                    "score": 0.0,
                    "content": f"Stub result for query: {query}",
                }
            ]
        # Safe guard: endpoint should be a string if enabled, but be defensive.
        endpoint_raw = self.settings.azure_search_endpoint or ""
        endpoint = endpoint_raw.rstrip("/")
        url = f"{endpoint}/indexes/{self.settings.azure_search_index}/docs/search?api-version=2023-11-01"
        headers = {
            "Content-Type": "application/json",
            "api-key": self.settings.azure_search_api_key or "",
        }
        payload = {"search": query, "top": top}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                results = [
                    {
                        "id": doc.get("id"),
                        "score": doc.get("@search.score"),
                        "content": doc.get("content") or doc,
                    }
                    for doc in data.get("value", [])
                ]
                return results
        except Exception as exc:  # noqa: BLE001
            logger.exception("Azure Search query failed", exc_info=exc)
            return []


@lru_cache(maxsize=1)
def get_search_service() -> AzureSearchService:
    """Return a cached singleton AzureSearchService instance.

    Prevents rebuilding configuration each request. If search configuration
    changes at runtime a restart is required to reflect new env values.
    """
    return AzureSearchService()
