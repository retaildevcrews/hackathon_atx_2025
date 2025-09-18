"""
Local mock search service for development/testing.
Returns pre-defined candidate data instead of calling Azure Search.
"""

import logging
from typing import Dict, List, Optional, Any
from seed.seed_data import MOCK_CANDIDATES

logger = logging.getLogger(__name__)


class LocalSearchService:
    """Mock search service that returns local test data."""

    def __init__(self):
        """Initialize with test candidate data."""
        self.enabled = True  # Always enabled for local testing
        self.mock_candidates = dict(MOCK_CANDIDATES)

    async def get_candidates_by_ids(self, candidate_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get multiple candidates by their IDs.

        Args:
            candidate_ids: List of candidate IDs to retrieve

        Returns:
            Dictionary mapping candidate_id to candidate data
        """
        logger.info(f"LOCAL SEARCH: Fetching {len(candidate_ids)} candidates: {candidate_ids}")

        result = {}
        for candidate_id in candidate_ids:
            if candidate_id in self.mock_candidates:
                result[candidate_id] = self.mock_candidates[candidate_id]
                logger.info(f"LOCAL SEARCH: Found candidate {candidate_id}")
            else:
                logger.warning(f"LOCAL SEARCH: Candidate {candidate_id} not found in mock data")

        return result

    async def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a single document/candidate by ID.

        Args:
            document_id: The candidate ID to retrieve

        Returns:
            Candidate data or None if not found
        """
        logger.info(f"LOCAL SEARCH: Fetching single candidate: {document_id}")

        if document_id in self.mock_candidates:
            candidate = self.mock_candidates[document_id]
            logger.info(f"LOCAL SEARCH: Found candidate {document_id}")
            return candidate
        else:
            logger.warning(f"LOCAL SEARCH: Candidate {document_id} not found in mock data")
            return None

    def add_test_candidate(self, candidate_id: str, candidate_data: Dict[str, Any]) -> None:
        """Add a new test candidate to the mock data.

        Args:
            candidate_id: Unique identifier for the candidate
            candidate_data: Dictionary with candidate information
        """
        self.mock_candidates[candidate_id] = candidate_data
        logger.info(f"LOCAL SEARCH: Added test candidate {candidate_id}")

    def list_available_candidates(self) -> List[str]:
        """List all available candidate IDs in the mock data.

        Returns:
            List of candidate IDs
        """
        return list(self.mock_candidates.keys())

    async def search(self, query: str, top: int = 3, decision_kit_id: str = None) -> List[Dict[str, Any]]:
        """Search for candidates (mock implementation).

        Args:
            query: Search query string
            top: Maximum number of results to return
            decision_kit_id: Optional decision kit ID to filter results

        Returns:
            List of candidate documents matching search
        """
        logger.info(f"LOCAL SEARCH: Mock search for query '{query}', top={top}")

        # Simple mock search - return first 'top' candidates
        candidates = list(self.mock_candidates.values())[:top]

        # Format as search results
        results = []
        for i, candidate in enumerate(candidates):
            results.append({
                "id": candidate["id"],
                "score": 1.0 - (i * 0.1),  # Decreasing relevance scores
                "content": candidate["content"],
                "title": candidate["title"],
                "name": candidate["name"],
                "candidate_id": candidate["candidate_id"],
                "decision_kit_id": candidate.get("decision_kit_id", "test-decision-kit")
            })

        logger.info(f"LOCAL SEARCH: Returning {len(results)} mock search results")
        return results

    def find_candidate_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find a candidate by display name (case-insensitive).

        Args:
            name: Display name to search for

        Returns:
            Candidate data if found, otherwise None
        """
        target = (name or "").strip().lower()
        if not target:
            return None

        for cand in self.mock_candidates.values():
            cand_name = str(cand.get("name", "")).strip().lower()
            if cand_name == target:
                return cand
        return None
