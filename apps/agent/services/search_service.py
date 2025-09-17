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

    async def search(self, query: str, top: int = 3, decision_kit_id: str | None = None) -> list[dict[str, Any]]:
        """Search for documents in Azure Search index.

        Args:
            query: Search query string
            top: Maximum number of results to return
            decision_kit_id: Optional decision kit ID to filter results

        Returns:
            List of documents with id, score, content, and metadata
        """
        if not self.enabled:
            return [
                {
                    "id": "stub-1",
                    "score": 0.0,
                    "content": f"Stub result for query: {query}",
                    "title": "Stub Title",
                    "name": "Stub Name",
                    "candidate_id": "stub-candidate-1",
                    "decision_kit_id": decision_kit_id or "stub-decision-kit",
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

        payload = {
            "search": query,
            "top": top,
            "select": "id,title,name,candidate_id,decision_kit_id,content"
        }

        # Add decision kit filter if provided
        if decision_kit_id:
            payload["filter"] = f"decision_kit_id eq '{decision_kit_id}'"

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                results = [
                    {
                        "id": doc.get("id"),
                        "score": doc.get("@search.score"),
                        "content": doc.get("content", ""),
                        "title": doc.get("title", ""),
                        "name": doc.get("name", ""),
                        "candidate_id": doc.get("candidate_id", ""),
                        "decision_kit_id": doc.get("decision_kit_id", ""),
                    }
                    for doc in data.get("value", [])
                ]
                return results
        except Exception as exc:  # noqa: BLE001
            logger.exception("Azure Search query failed", exc_info=exc)
            return []

    async def get_document_by_id(self, document_id: str) -> dict[str, Any] | None:
        """Retrieve a specific document by its ID from Azure Search.

        Args:
            document_id: The unique identifier of the document to retrieve

        Returns:
            Document data with 'id', 'content', and other fields, or None if not found
        """
        if not self.enabled:
            logger.warning("Azure Search not configured; returning stub document")
            return {
                "id": document_id,
                "content": f"Stub document content for ID: {document_id}. This is sample text for testing purposes.",
                "title": f"Stub Title for {document_id}",
                "name": f"Stub Name for {document_id}",
                "candidate_id": f"stub-candidate-{document_id}",
                "decision_kit_id": "stub-decision-kit",
            }

        # Safe guard: endpoint should be a string if enabled, but be defensive.
        endpoint_raw = self.settings.azure_search_endpoint or ""
        endpoint = endpoint_raw.rstrip("/")
        url = f"{endpoint}/indexes/{self.settings.azure_search_index}/docs('{document_id}')?api-version=2023-11-01&$select=id,title,name,candidate_id,decision_kit_id,content"
        headers = {
            "Content-Type": "application/json",
            "api-key": self.settings.azure_search_api_key or "",
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # First try direct document lookup using the ID as primary key
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    doc = resp.json()
                    return {
                        "id": doc.get("id", document_id),
                        "content": doc.get("content", ""),
                        "title": doc.get("title", ""),
                        "name": doc.get("name", ""),
                        "candidate_id": doc.get("candidate_id", ""),
                        "decision_kit_id": doc.get("decision_kit_id", ""),
                    }

                elif resp.status_code == 404:
                    # Direct lookup failed, try searching by candidate_id field
                    logger.info(f"Direct lookup failed for '{document_id}', trying search by candidate_id field")
                    return await self._search_by_candidate_id(document_id)

                else:
                    resp.raise_for_status()

        except Exception as exc:  # noqa: BLE001
            logger.exception(f"Failed to retrieve document '{document_id}' from Azure Search", exc_info=exc)
            return None

    async def _search_by_candidate_id(self, candidate_id: str) -> dict[str, Any] | None:
        """Search for a document by candidate_id field instead of primary key.

        Args:
            candidate_id: The candidate_id value to search for

        Returns:
            Document data if found, None otherwise
        """
        if not self.enabled:
            return None

        endpoint_raw = self.settings.azure_search_endpoint or ""
        endpoint = endpoint_raw.rstrip("/")
        url = f"{endpoint}/indexes/{self.settings.azure_search_index}/docs/search?api-version=2023-11-01"
        headers = {
            "Content-Type": "application/json",
            "api-key": self.settings.azure_search_api_key or "",
        }

        payload = {
            "search": "*",
            "filter": f"candidate_id eq '{candidate_id}'",
            "top": 1,
            "select": "id,title,name,candidate_id,decision_kit_id,content"
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()

                documents = data.get("value", [])
                if documents:
                    doc = documents[0]  # Take first match
                    logger.info(f"Found document by candidate_id '{candidate_id}': {doc.get('id', 'N/A')}")
                    return {
                        "id": doc.get("id", candidate_id),
                        "content": doc.get("content", ""),
                        "title": doc.get("title", ""),
                        "name": doc.get("name", ""),
                        "candidate_id": doc.get("candidate_id", ""),
                        "decision_kit_id": doc.get("decision_kit_id", ""),
                    }
                else:
                    logger.warning(f"No document found with candidate_id '{candidate_id}'")
                    return None

        except Exception as exc:
            logger.exception(f"Failed to search by candidate_id '{candidate_id}'", exc_info=exc)
            return None

    async def get_documents_by_ids(self, document_ids: list[str]) -> dict[str, dict[str, Any]]:
        """Retrieve multiple documents by their IDs from Azure Search.

        Args:
            document_ids: List of document IDs to retrieve

        Returns:
            Dictionary mapping document_id -> document_data for successfully retrieved documents
        """
        results = {}

        for doc_id in document_ids:
            doc = await self.get_document_by_id(doc_id)
            if doc:
                results[doc_id] = doc
            else:
                logger.warning(f"Document '{doc_id}' could not be retrieved")

        return results

    # Candidate-specific methods (aliases for document methods to maintain consistency with criteria_api)
    async def get_candidate_by_id(self, candidate_id: str) -> dict[str, Any] | None:
        """Retrieve a specific candidate by its ID from Azure Search.

        This is an alias for get_document_by_id to maintain consistency with criteria_api terminology.
        """
        return await self.get_document_by_id(candidate_id)

    async def get_candidates_by_ids(self, candidate_ids: list[str]) -> dict[str, dict[str, Any]]:
        """Retrieve multiple candidates by their IDs from Azure Search.

        This is an alias for get_documents_by_ids to maintain consistency with criteria_api terminology.
        """
        return await self.get_documents_by_ids(candidate_ids)

    async def get_candidates_by_decision_kit(self, decision_kit_id: str, top: int = 50) -> list[dict[str, Any]]:
        """Retrieve all candidates for a specific decision kit.

        Args:
            decision_kit_id: The decision kit ID to filter by
            top: Maximum number of candidates to return

        Returns:
            List of candidate documents with full metadata
        """
        if not self.enabled:
            return [
                {
                    "id": f"stub-{i}",
                    "content": f"Stub candidate {i} content for decision kit {decision_kit_id}",
                    "title": f"Stub Candidate {i}",
                    "name": f"candidate_{i}",
                    "candidate_id": f"stub-candidate-{i}",
                    "decision_kit_id": decision_kit_id,
                }
                for i in range(1, min(top + 1, 4))  # Return up to 3 stub results
            ]

        endpoint_raw = self.settings.azure_search_endpoint or ""
        endpoint = endpoint_raw.rstrip("/")
        url = f"{endpoint}/indexes/{self.settings.azure_search_index}/docs/search?api-version=2023-11-01"
        headers = {
            "Content-Type": "application/json",
            "api-key": self.settings.azure_search_api_key or "",
        }

        payload = {
            "search": "*",  # Search all documents
            "filter": f"decision_kit_id eq '{decision_kit_id}'",
            "top": top,
            "select": "id,title,name,candidate_id,decision_kit_id,content"
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                results = [
                    {
                        "id": doc.get("id"),
                        "content": doc.get("content", ""),
                        "title": doc.get("title", ""),
                        "name": doc.get("name", ""),
                        "candidate_id": doc.get("candidate_id", ""),
                        "decision_kit_id": doc.get("decision_kit_id", ""),
                    }
                    for doc in data.get("value", [])
                ]
                return results
        except Exception as exc:  # noqa: BLE001
            logger.exception(f"Failed to retrieve candidates for decision kit '{decision_kit_id}'", exc_info=exc)
            return []


@lru_cache(maxsize=1)
def get_search_service() -> AzureSearchService:
    """Return a cached singleton AzureSearchService instance.

    Prevents rebuilding configuration each request. If search configuration
    changes at runtime a restart is required to reflect new env values.
    """
    return AzureSearchService()
