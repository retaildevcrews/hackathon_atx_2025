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
        """Initialize with test candidate data based on criteria API seed data."""
        self.enabled = True  # Always enabled for local testing
        self.mock_candidates = {
            # Software Engineer Hiring Candidates
            "Alice-Rivera": {
                "id": "alice-rivera-resume-id",
                "candidate_id": "Alice-Rivera",
                "title": "Senior Backend Engineer - Alice Rivera",
                "name": "Alice Rivera - Platform Engineering Resume",
                "content": """
ALICE RIVERA
Senior Backend Engineer
Email: alice.rivera@email.com | Phone: (555) 234-5678 | LinkedIn: linkedin.com/in/alicerivera

SUMMARY
Senior backend engineer with 8+ years leading large-scale distributed systems and multi-region service migrations.
Expert in microservices architecture, cloud platforms, and team leadership. Proven track record of scaling
systems from startup to enterprise level.

TECHNICAL SKILLS
• Languages: Java, Python, Go, Scala, SQL
• Frameworks: Spring Boot, Django, gRPC, Apache Kafka
• Cloud: AWS (Expert), GCP, Kubernetes, Docker, Terraform
• Databases: PostgreSQL, MongoDB, Redis, Cassandra, DynamoDB
• Monitoring: Prometheus, Grafana, DataDog, New Relic
• Architecture: Microservices, Event-driven systems, CQRS, Service Mesh

EXPERIENCE

Senior Staff Engineer | TechGiant Corp | 2021-Present
• Led multi-region service migration affecting 10M+ users with 99.9% uptime
• Architected event-driven microservices platform reducing latency by 60%
• Mentored 8 engineers and established architectural review board
• Designed disaster recovery procedures tested across 3 AWS regions
• Implemented comprehensive observability stack saving $200K annually in debugging time

Principal Engineer | ScaleUp Inc | 2018-2021
• Built payment processing system handling $50M+ monthly transactions
• Led migration from monolith to 15 microservices with zero-downtime deployments
• Established SRE practices including SLOs, error budgets, and incident response
• Designed API gateway with rate limiting serving 1M+ requests/minute
• Created engineering onboarding program reducing ramp-up time by 40%

Backend Engineer | StartupXYZ | 2016-2018
• Developed real-time analytics pipeline processing 1TB+ daily data
• Implemented distributed caching layer improving response times by 75%
• Built automated deployment pipeline reducing release cycle from weeks to hours
• Collaborated with product teams on technical requirements and feasibility

SYSTEM DESIGN HIGHLIGHTS
• Multi-Region Architecture: Designed active-active setup across US/EU with automatic failover
• Event Sourcing: Implemented audit trail system for financial compliance requirements
• API Design: Created RESTful and GraphQL APIs with comprehensive documentation
• Performance Optimization: Reduced database query times by 80% through strategic indexing

LEADERSHIP & MENTORING
• Technical lead for 12-person backend team
• Conducted 50+ technical interviews and refined hiring process
• Speaker at 3 industry conferences on distributed systems topics
• Open source contributor to Apache Kafka and Kubernetes projects

EDUCATION
M.S. Computer Science | Stanford University | 2016
B.S. Software Engineering | UC Berkeley | 2014

CERTIFICATIONS
• AWS Certified Solutions Architect - Professional
• Certified Kubernetes Administrator (CKA)
                """,
                "decision_kit_id": "senior-backend-engineer-shortlist"
            },
            "Benjamin-Cho": {
                "id": "benjamin-cho-resume-id",
                "candidate_id": "Benjamin-Cho",
                "title": "Senior Backend Engineer - Benjamin Cho",
                "name": "Benjamin Cho - Distributed Systems Resume",
                "content": """
BENJAMIN CHO
Senior Backend Engineer
Email: benjamin.cho@email.com | Phone: (555) 345-6789 | GitHub: github.com/bcho-dev

SUMMARY
Passionate backend engineer with 6+ years specializing in distributed caching, high-performance systems,
and data infrastructure. Strong expertise in building scalable solutions that handle millions of
concurrent users with sub-millisecond response times.

TECHNICAL SKILLS
• Languages: Java, Python, C++, Rust, JavaScript
• Frameworks: Spring Boot, Netty, Express.js, FastAPI
• Caching: Redis, Memcached, Hazelcast, Apache Ignite
• Databases: PostgreSQL, MySQL, MongoDB, InfluxDB, Elasticsearch
• Message Queues: Apache Kafka, RabbitMQ, AWS SQS
• Cloud: AWS, Azure, Docker, Kubernetes, Service Mesh (Istio)

EXPERIENCE

Senior Engineer | DataFlow Systems | 2020-Present
• Architected distributed caching layer serving 5M+ concurrent users
• Built real-time data pipeline processing 100K+ events per second
• Implemented Redis cluster with automatic sharding and failover
• Optimized database queries reducing P99 latency from 500ms to 50ms
• Led initiative to migrate legacy systems to cloud-native architecture

Backend Engineer | CloudTech Solutions | 2018-2020
• Developed high-throughput API gateway handling 10M+ daily requests
• Built distributed session management system with 99.99% availability
• Implemented circuit breaker pattern preventing cascade failures
• Created monitoring dashboard providing real-time system insights
• Collaborated with DevOps team on deployment automation

Software Engineer | StartupABC | 2017-2018
• Built recommendation engine serving personalized content to 1M+ users
• Implemented efficient caching strategies reducing server costs by 45%
• Developed A/B testing framework for product feature validation
• Created data analytics pipeline for business intelligence reporting

TECHNICAL ACHIEVEMENTS
• Cache Hit Ratio: Achieved 95%+ cache hit ratios through intelligent pre-warming
• Performance: Reduced API response times by 80% through strategic caching
• Scalability: Designed systems handling 10x traffic spikes during peak events
• Reliability: Maintained 99.95+ uptime across all distributed services

CACHING EXPERTISE
• Redis Clustering: Built and managed Redis clusters with automatic failover
• Cache Strategies: Implemented write-through, write-behind, and refresh-ahead patterns
• Memory Optimization: Optimized memory usage reducing infrastructure costs by 30%
• Distributed Consistency: Solved cache coherence in multi-region deployments

PROJECTS
• High-Performance Trading System: Built low-latency order matching engine
• Real-time Analytics Platform: Created stream processing system with Apache Kafka
• Distributed Configuration Service: Developed centralized config management

EDUCATION
B.S. Computer Science | University of Washington | 2017
Minor in Mathematics

CERTIFICATIONS
• AWS Certified Solutions Architect
• Redis Certified Developer
                """,
                "decision_kit_id": "senior-backend-engineer-shortlist"
            },
            "Priya-Natarajan": {
                "id": "priya-natarajan-resume-id",
                "candidate_id": "Priya-Natarajan",
                "title": "Senior Backend Engineer - Priya Natarajan",
                "name": "Priya Natarajan - SRE & Observability Resume",
                "content": """
PRIYA NATARAJAN
Senior Backend Engineer & SRE Advocate
Email: priya.natarajan@email.com | Phone: (555) 456-7890 | Blog: observability-insights.dev

SUMMARY
Site Reliability Engineer turned backend developer with 7+ years building observable, resilient systems.
Expert in monitoring, alerting, and incident response. Passionate about creating systems that not only work
but can be understood, debugged, and optimized by the entire engineering team.

TECHNICAL SKILLS
• Languages: Python, Go, Java, Bash, TypeScript
• Observability: Prometheus, Grafana, Jaeger, OpenTelemetry, DataDog
• Cloud: GCP (Expert), AWS, Kubernetes, Helm, Terraform
• Databases: PostgreSQL, BigQuery, InfluxDB, TimescaleDB
• Monitoring: AlertManager, PagerDuty, Custom metrics & dashboards
• Infrastructure: Docker, Kubernetes, Service Mesh, GitOps (ArgoCD)

EXPERIENCE

Senior SRE/Backend Engineer | ReliableCloud Inc | 2021-Present
• Built comprehensive observability platform serving 200+ microservices
• Implemented distributed tracing reducing mean time to resolution by 70%
• Created SLO framework with error budgets for 50+ critical services
• Established on-call rotation and incident response procedures
• Designed auto-scaling policies saving 40% on infrastructure costs
• Led post-mortem culture resulting in 60% reduction in repeat incidents

Platform Engineer | MonitorTech Corp | 2019-2021
• Developed real-time anomaly detection system using machine learning
• Built custom Prometheus exporters for business-specific metrics
• Implemented chaos engineering practices improving system resilience
• Created runbooks and troubleshooting guides for 100+ services
• Designed multi-region monitoring setup with 5-second failover time

Backend Engineer | StartupOps | 2017-2019
• Built logging aggregation system processing 10GB+ daily logs
• Implemented health check framework with dependency tracking
• Created automated rollback system based on error rate thresholds
• Developed cost optimization tools reducing cloud spend by 35%
• Established engineering metrics dashboard for team productivity

OBSERVABILITY EXPERTISE
• Metrics: Designed comprehensive metric hierarchies with proper labeling
• Logging: Built structured logging standards with correlation IDs
• Tracing: Implemented distributed tracing across 50+ microservices
• Alerting: Created intelligent alerting reducing false positives by 80%
• Dashboards: Built executive and engineering dashboards for different audiences

RELIABILITY ACHIEVEMENTS
• Uptime: Maintained 99.99% uptime for critical payment processing services
• MTTR: Reduced mean time to recovery from 45 minutes to 8 minutes
• Incident Response: Led 200+ incident responses with detailed post-mortems
• Performance: Improved system performance visibility leading to 50% latency reduction

SRE PRACTICES
• Error Budgets: Established SLO framework balancing reliability and feature velocity
• Chaos Engineering: Regular game days testing system resilience
• Capacity Planning: Predictive scaling based on business metrics
• Automation: "Toil" reduction through intelligent automation and runbooks

PROJECTS
• Observability Platform: Built company-wide monitoring solution from scratch
• Incident Management System: Created automated incident workflow and escalation
• Performance Testing Framework: Continuous load testing with automated alerts
• Cost Monitoring: Real-time cloud cost tracking with anomaly detection

SPEAKING & COMMUNITY
• Presented at SREcon on "Building Observability Culture"
• Organizer of local SRE meetup (500+ members)
• Technical blogger with 10K+ monthly readers
• Mentor for underrepresented groups in tech

EDUCATION
M.S. Computer Science | Carnegie Mellon University | 2017
B.S. Electrical Engineering | MIT | 2015

CERTIFICATIONS
• Google Cloud Professional Cloud Architect
• Certified Kubernetes Administrator (CKA)
• Prometheus Certified Associate
                """,
                "decision_kit_id": "senior-backend-engineer-shortlist"
            },

            # Additional candidates from other rubrics for variety
            "LG-OLED-C3": {
                "id": "lg-oled-c3-spec-id",
                "candidate_id": "LG-OLED-C3",
                "title": "LG OLED C3 55\" Television",
                "name": "LG OLED C3 55\" - Product Specification",
                "content": """
LG OLED C3 55" (OLED55C3PUA) - Premium OLED Television
Model Year: 2025 | Screen Size: 55 inches | Panel Type: OLED Evo

PICTURE QUALITY - EXCELLENT
• Display Technology: OLED Evo with self-lit pixels
• Resolution: 4K Ultra HD (3840 x 2160)
• HDR Support: Dolby Vision IQ, HDR10 Pro, HLG
• Processor: α9 Gen6 AI Processor 4K with AI Picture Pro
• Peak Brightness: 800 nits (typical), deep perfect blacks
• Color Gamut: 100% DCI-P3, wide color spectrum
• Viewing Angle: Perfect 178° with no color shifting

GAMING PERFORMANCE - EXCELLENT
• Input Lag: 5.7ms (Game Optimizer mode)
• Refresh Rate: 120Hz native, up to 144Hz (PC mode)
• HDMI Features: 4x HDMI 2.1 ports with 48Gbps bandwidth
• Gaming Features: VRR, ALLM, G-SYNC, FreeSync Premium
• Game Optimizer: Dedicated gaming dashboard with genre presets
• Cloud Gaming: NVIDIA GeForce Now, Google Stadia ready

SMART PLATFORM - EXCELLENT
• Operating System: webOS 23 with redesigned interface
• Processor: Quad-core ARM with 4GB RAM
• Voice Control: LG ThinQ AI, Google Assistant, Amazon Alexa
• App Store: LG Content Store with 300+ apps
• Streaming Apps: Netflix, Disney+, Amazon Prime, Apple TV+, YouTube
• AirPlay 2 & HomeKit: Full Apple ecosystem integration
• Magic Remote: Point, click, scroll, voice control

SOUND QUALITY - GOOD
• Audio System: 2.2 channel, 40W total output
• Audio Technology: Dolby Atmos, DTS:X, AI Sound Pro
• Speakers: Down-firing woofers, front-firing tweeters
• Sound Modes: Cinema, Sports, Music, Game
• Audio Return Channel: eARC support for soundbar connection
• Bluetooth: Audio streaming to headphones/speakers

DESIGN & BUILD - EXCELLENT
• Design: Gallery Design with ultra-slim profile
• Thickness: 45mm at thickest point
• Bezel: Virtually borderless Cinema Screen Design
• Stand: Crescent-shaped stand with cable management
• Wall Mount: Compatible with 300x200mm VESA mounts
• Build Quality: Premium materials, solid construction

EASE OF USE - EXCELLENT
• Setup: Quick Setup wizard with auto-calibration
• Remote: Magic Remote with pointer and voice control
• Menu System: Intuitive webOS interface
• Settings: Easy picture and sound adjustment modes
• Mobile App: LG ThinQ for smartphone control
• Universal Control: Control cable box and soundbar

ENERGY EFFICIENCY - GOOD
• Power Consumption: 139W (typical), 0.5W (standby)
• Energy Star: Certified energy efficient
• Eco Settings: Multiple power saving modes
• Auto Power Off: Configurable sleep timer
• Screen Saver: OLED protection features

PRICE/VALUE - GOOD
• MSRP: $1,799 (55")
• Street Price: $1,499-$1,599 (current market)
• Value Proposition: Premium OLED technology at competitive price
• Warranty: 2-year manufacturer warranty
• Comparison: Competitive with Sony A80L, more affordable than Samsung QN95C

SPECIFICATIONS
• Dimensions: 48.3" x 27.6" x 1.8" (without stand)
• Weight: 41.9 lbs (without stand), 48.5 lbs (with stand)
• Connectivity: 4x HDMI 2.1, 3x USB, Ethernet, Wi-Fi 6, Bluetooth 5.0
• Supported Formats: MP4, MKV, AVI, JPEG, MP3, FLAC, DTS
                """,
                "decision_kit_id": "2025-living-room-tv-comparison"
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
