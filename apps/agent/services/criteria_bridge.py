"""
Bridge service to integrate agent evaluation with existing criteria_api.
Uses HTTP calls to the criteria_api service for rubric and criteria data.
"""

import logging
from typing import Any, Dict, List, Optional
import httpx
from functools import lru_cache

from config import get_settings

logger = logging.getLogger(__name__)


class CriteriaAPIBridge:
    """Bridge service to connect agent evaluation with criteria_api."""

    def __init__(self, criteria_api_base_url: str = "http://localhost:8000"):
        """Initialize bridge service.

        Args:
            criteria_api_base_url: Base URL for criteria_api service
        """
        self.base_url = criteria_api_base_url.rstrip("/")
        self.timeout = 30.0

    async def get_rubric(self, rubric_id: str) -> Optional[Dict[str, Any]]:
        """Get rubric by ID from criteria_api.

        Args:
            rubric_id: ID of the rubric

        Returns:
            Rubric data with criteria, or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/rubrics/{rubric_id}")

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                rubric_data = response.json()

                # Transform to evaluation format
                return await self._transform_rubric_for_evaluation(rubric_data)

        except httpx.HTTPError as e:
            logger.error(f"Error fetching rubric '{rubric_id}': {e}")
            return None

    async def list_rubrics(self) -> List[Dict[str, Any]]:
        """List all available rubrics from criteria_api.

        Returns:
            List of rubric information
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/rubrics/")
                response.raise_for_status()
                rubrics = response.json()

                # Transform to simple list format
                return [
                    {
                        "rubric_name": rubric["name"],
                        "rubric_id": rubric["id"],
                        "domain": "General",  # criteria_api doesn't have domain field
                        "version": rubric["version"],
                        "description": rubric["description"],
                        "published": rubric["published"],
                        "created_at": rubric["createdAt"]
                    }
                    for rubric in rubrics
                ]

        except httpx.HTTPError as e:
            logger.error(f"Error listing rubrics: {e}")
            return []

    async def get_criteria(self, criteria_id: str) -> Optional[Dict[str, Any]]:
        """Get criteria details by ID.

        Args:
            criteria_id: ID of the criteria

        Returns:
            Criteria data or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/criteria/{criteria_id}")

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Error fetching criteria '{criteria_id}': {e}")
            return None

    async def _transform_rubric_for_evaluation(self, rubric_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform criteria_api rubric format to evaluation format.

        Args:
            rubric_data: Rubric data from criteria_api

        Returns:
            Transformed rubric data for evaluation
        """
        # Get detailed criteria information
        criteria = []

        for criteria_entry in rubric_data.get("criteria", []):
            criteria_id = criteria_entry["criteriaId"]
            weight = criteria_entry["weight"]

            # Fetch full criteria details
            criteria_details = await self.get_criteria(criteria_id)

            if criteria_details:
                criteria.append({
                    "criterion_id": criteria_id,
                    "description": criteria_details["description"],
                    "definition": criteria_details["definition"],
                    "weight": weight,
                    "scoring_criteria": self._create_default_scoring_criteria()
                })

        return {
            "rubric_id": rubric_data["id"],
            "rubric_name": rubric_data["name"],
            "domain": "General",  # Default since criteria_api doesn't have domain
            "version": rubric_data["version"],
            "description": rubric_data["description"],
            "criteria": criteria
        }

    def _create_default_scoring_criteria(self) -> Dict[str, str]:
        """Create default 1-5 scoring criteria for evaluation.

        Returns:
            Default scoring criteria dictionary
        """
        return {
            "5": "Excellent - Exceeds expectations with exceptional quality",
            "4": "Very Good - Meets expectations with high quality",
            "3": "Good - Meets expectations with acceptable quality",
            "2": "Fair - Below expectations with some issues",
            "1": "Poor - Well below expectations with significant issues"
        }

    async def health_check(self) -> bool:
        """Check if criteria_api service is available.

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/healthz")
                return response.status_code == 200
        except:
            return False


@lru_cache(maxsize=1)
def get_criteria_api_bridge() -> CriteriaAPIBridge:
    """Get singleton criteria API bridge instance."""
    settings = get_settings()

    return CriteriaAPIBridge(settings.criteria_api_url)
