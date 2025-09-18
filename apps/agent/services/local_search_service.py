"""
Local mock search service for development/testing.
Returns pre-defined candidate data instead of calling Azure Search.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class LocalSearchService:
    """Mock search service that returns local test data."""

    def __init__(self):
        """Initialize with test candidate data."""
        self.enabled = True  # Always enabled for local testing
        self.mock_candidates = {
            "Candidate-LMAOGUID": {
                "id": "aHR0cHM6Ly9kZWNpc2lvbmtpdHN0b3JhZ2UuYmxvYi5jb3JlLndpbmRvd3MubmV0L2RvY3MvbGdfc3BlYy5wZGY1",
                "candidate_id": "Candidate-LMAOGUID",
                "title": "Software Engineer Candidate - LG Electronics",
                "name": "John Doe - Senior Backend Engineer Resume",
                "content": """
JOHN DOE
Senior Backend Engineer
Email: john.doe@email.com | Phone: (555) 123-4567

SUMMARY
Experienced backend engineer with 5+ years developing scalable microservices and distributed systems.
Expertise in Python, Java, and cloud architecture. Strong track record of leading technical initiatives
and mentoring junior developers.

TECHNICAL SKILLS
• Languages: Python, Java, JavaScript, SQL
• Frameworks: Django, Flask, Spring Boot, FastAPI
• Cloud: AWS (EC2, S3, RDS, Lambda), Docker, Kubernetes
• Databases: PostgreSQL, Redis, MongoDB
• Tools: Git, Jenkins, Terraform, Prometheus, Grafana

EXPERIENCE

Senior Backend Engineer | TechCorp Inc. | 2021-Present
• Designed and implemented microservices architecture serving 1M+ daily users
• Led migration from monolith to microservices, reducing deployment time by 70%
• Implemented comprehensive monitoring and alerting using Prometheus and Grafana
• Mentored 3 junior engineers and conducted technical interviews
• Collaborated with product teams to deliver features on tight deadlines

Backend Engineer | StartupXYZ | 2019-2021
• Built REST APIs using Django and PostgreSQL handling 100K+ requests/day
• Implemented caching layer with Redis, improving response times by 40%
• Set up CI/CD pipelines using Jenkins and Docker
• Participated in on-call rotation and incident response

PROJECTS
• Payment Processing System: Designed fault-tolerant payment service with 99.9% uptime
• Real-time Analytics Platform: Built data pipeline processing 10GB+ daily events
• API Gateway: Implemented rate limiting, authentication, and request routing

EDUCATION
B.S. Computer Science | University of Technology | 2019
                """,
                "decision_kit_id": "test-decision-kit-1"
            },
            "Candidate-TESTCAND1": {
                "id": "test-candidate-1-id",
                "candidate_id": "Candidate-TESTCAND1",
                "title": "Frontend Developer Candidate",
                "name": "Jane Smith - React Developer Resume",
                "content": """
JANE SMITH
Frontend Developer
Email: jane.smith@email.com | Phone: (555) 987-6543

SUMMARY
Creative frontend developer with 4+ years building responsive web applications.
Passionate about user experience and modern JavaScript frameworks.

TECHNICAL SKILLS
• Languages: JavaScript, TypeScript, HTML5, CSS3
• Frameworks: React, Vue.js, Angular, Next.js
• Tools: Webpack, Babel, ESLint, Jest, Cypress
• Design: Figma, Adobe XD, Responsive Design

EXPERIENCE

Frontend Developer | DesignCo | 2020-Present
• Built responsive web apps using React and TypeScript
• Implemented pixel-perfect designs from Figma mockups
• Optimized bundle size and performance, achieving 95+ Lighthouse scores
• Collaborated with UX designers and backend engineers

Junior Developer | WebStudio | 2019-2020
• Developed landing pages and marketing sites
• Maintained legacy jQuery applications
• Learned modern JavaScript and React fundamentals

PROJECTS
• E-commerce Platform: Built shopping cart and checkout flow in React
• Dashboard Application: Created data visualization using D3.js and React
• Mobile App: Developed React Native app for iOS and Android
                """,
                "decision_kit_id": "test-decision-kit-1"
            },
            "Candidate-TESTCAND2": {
                "id": "test-candidate-2-id",
                "candidate_id": "Candidate-TESTCAND2",
                "title": "DevOps Engineer Candidate",
                "name": "Mike Johnson - DevOps Engineer Resume",
                "content": """
MIKE JOHNSON
DevOps Engineer
Email: mike.johnson@email.com | Phone: (555) 456-7890

SUMMARY
DevOps engineer with 6+ years automating deployment pipelines and managing cloud infrastructure.
Expert in containerization, orchestration, and infrastructure as code.

TECHNICAL SKILLS
• Cloud: AWS, Azure, GCP
• Containers: Docker, Kubernetes, Helm
• CI/CD: Jenkins, GitLab CI, GitHub Actions
• IaC: Terraform, CloudFormation, Ansible
• Monitoring: Prometheus, Grafana, ELK Stack
• Languages: Python, Bash, Go

EXPERIENCE

Senior DevOps Engineer | CloudTech Solutions | 2021-Present
• Managed multi-cloud infrastructure across AWS, Azure, and GCP
• Implemented GitOps workflows using ArgoCD and Flux
• Reduced deployment time from hours to minutes using automated pipelines
• Built comprehensive monitoring and alerting for 50+ microservices

DevOps Engineer | InfraCompany | 2018-2021
• Migrated legacy applications to Kubernetes clusters
• Implemented Infrastructure as Code using Terraform
• Set up centralized logging and monitoring solutions
• Automated backup and disaster recovery procedures

CERTIFICATIONS
• AWS Certified Solutions Architect - Professional
• Certified Kubernetes Administrator (CKA)
• HashiCorp Certified: Terraform Associate
                """,
                "decision_kit_id": "test-decision-kit-1"
            }
        }

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
