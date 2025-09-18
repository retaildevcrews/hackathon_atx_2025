"""
Mock seed data for LocalSearchService.
"""
from typing import Dict, Any

MOCK_CANDIDATES: Dict[str, Dict[str, Any]] = {
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

# Additional candidates mirroring criteria_api seed decision kits
MOCK_CANDIDATES.update({
    # TV Evaluation
    "Candidate-TV-LG-OLED-C3-55": {
        "id": "tv-lg-oled-c3-55",
        "candidate_id": "Candidate-TV-LG-OLED-C3-55",
        "title": "LG OLED C3 55\"",
        "name": "LG OLED C3 55\"",
        "content": "LG C3 OLED: Excellent contrast, perfect blacks, wide color gamut. Great for movies and gaming.",
        "decision_kit_id": "tv-evaluation"
    },
    "Candidate-TV-SAMSUNG-QN90C-55": {
        "id": "tv-samsung-qn90c-55",
        "candidate_id": "Candidate-TV-SAMSUNG-QN90C-55",
        "title": "Samsung QN90C 55\"",
        "name": "Samsung QN90C 55\"",
        "content": "Samsung QN90C: Mini-LED peak brightness, strong HDR highlights, excellent anti-reflective screen.",
        "decision_kit_id": "tv-evaluation"
    },
    "Candidate-TV-SONY-BRAVIA-XR-A80L": {
        "id": "tv-sony-bravia-xr-a80l",
        "candidate_id": "Candidate-TV-SONY-BRAVIA-XR-A80L",
        "title": "Sony Bravia XR A80L",
        "name": "Sony Bravia XR A80L",
        "content": "Sony A80L: Strong motion handling and upscaling with Cognitive Processor XR; excellent cinematic image.",
        "decision_kit_id": "tv-evaluation"
    },

    # Grant Proposal Review
    "Candidate-GRANT-URBAN-AIR-QUALITY-SENSORS": {
        "id": "grant-urban-air-quality-sensors",
        "candidate_id": "Candidate-GRANT-URBAN-AIR-QUALITY-SENSORS",
        "title": "Urban Air Quality Sensors",
        "name": "Urban Air Quality Sensors",
        "content": "Low-cost mesh sensor network proposal to monitor urban air quality across neighborhoods.",
        "decision_kit_id": "grant-proposal-review"
    },
    "Candidate-GRANT-FOOD-WASTE-ANALYTICS-PLATFORM": {
        "id": "grant-food-waste-analytics-platform",
        "candidate_id": "Candidate-GRANT-FOOD-WASTE-ANALYTICS-PLATFORM",
        "title": "Food Waste Analytics Platform",
        "name": "Food Waste Analytics Platform",
        "content": "Analytics platform targeting hospitality industry waste reduction with actionable insights.",
        "decision_kit_id": "grant-proposal-review"
    },
    "Candidate-GRANT-STEM-OUTREACH-MOBILE-LAB": {
        "id": "grant-stem-outreach-mobile-lab",
        "candidate_id": "Candidate-GRANT-STEM-OUTREACH-MOBILE-LAB",
        "title": "STEM Outreach Mobile Lab",
        "name": "STEM Outreach Mobile Lab",
        "content": "Mobile laboratory initiative to bring STEM education to rural areas.",
        "decision_kit_id": "grant-proposal-review"
    },

    # Classroom Project Assessment
    "Candidate-CLASSROOM-SMART-CAMPUS-NAVIGATOR": {
        "id": "classroom-smart-campus-navigator",
        "candidate_id": "Candidate-CLASSROOM-SMART-CAMPUS-NAVIGATOR",
        "title": "Smart Campus Navigator",
        "name": "Smart Campus Navigator",
        "content": "Indoor routing mobile app for campus navigation using beacons and maps.",
        "decision_kit_id": "classroom-project-assessment"
    },
    "Candidate-CLASSROOM-MEAL-PLAN-OPTIMIZER": {
        "id": "classroom-meal-plan-optimizer",
        "candidate_id": "Candidate-CLASSROOM-MEAL-PLAN-OPTIMIZER",
        "title": "Meal Plan Optimizer",
        "name": "Meal Plan Optimizer",
        "content": "Optimization tool balancing nutrition and cost for student meal plans.",
        "decision_kit_id": "classroom-project-assessment"
    },
    "Candidate-CLASSROOM-ADAPTIVE-STUDY-SCHEDULER": {
        "id": "classroom-adaptive-study-scheduler",
        "candidate_id": "Candidate-CLASSROOM-ADAPTIVE-STUDY-SCHEDULER",
        "title": "Adaptive Study Scheduler",
        "name": "Adaptive Study Scheduler",
        "content": "Personalized study scheduling app adapting to performance and availability.",
        "decision_kit_id": "classroom-project-assessment"
    },

    # Startup Pitch Scoring
    "Candidate-PITCH-LOOPCART": {
        "id": "pitch-loopcart",
        "candidate_id": "Candidate-PITCH-LOOPCART",
        "title": "LoopCart",
        "name": "LoopCart",
        "content": "Circular packaging logistics startup focused on reusable containers.",
        "decision_kit_id": "startup-pitch-scoring"
    },
    "Candidate-PITCH-SYNTHEDGE": {
        "id": "pitch-synthedge",
        "candidate_id": "Candidate-PITCH-SYNTHEDGE",
        "title": "SynthEdge",
        "name": "SynthEdge",
        "content": "Edge AI model compression technology improving inference efficiency.",
        "decision_kit_id": "startup-pitch-scoring"
    },
    "Candidate-PITCH-FARMTRACE": {
        "id": "pitch-farmtrace",
        "candidate_id": "Candidate-PITCH-FARMTRACE",
        "title": "FarmTrace",
        "name": "FarmTrace",
        "content": "Soil carbon monitoring platform for regenerative agriculture.",
        "decision_kit_id": "startup-pitch-scoring"
    },

    # Compliance Readiness Assessment
    "Candidate-COMPLIANCE-ACCOUNTING-SYSTEM-CONTROLS": {
        "id": "compliance-accounting-system-controls",
        "candidate_id": "Candidate-COMPLIANCE-ACCOUNTING-SYSTEM-CONTROLS",
        "title": "Accounting System Controls",
        "name": "Accounting System Controls",
        "content": "Evaluation of financial process controls for audit readiness.",
        "decision_kit_id": "compliance-readiness"
    },
    "Candidate-COMPLIANCE-ACCESS-GOVERNANCE": {
        "id": "compliance-access-governance",
        "candidate_id": "Candidate-COMPLIANCE-ACCESS-GOVERNANCE",
        "title": "Access Governance",
        "name": "Access Governance",
        "content": "Joiner/mover/leaver access review and governance program.",
        "decision_kit_id": "compliance-readiness"
    },
    "Candidate-COMPLIANCE-INCIDENT-RESPONSE-PROGRAM": {
        "id": "compliance-incident-response-program",
        "candidate_id": "Candidate-COMPLIANCE-INCIDENT-RESPONSE-PROGRAM",
        "title": "Incident Response Program",
        "name": "Incident Response Program",
        "content": "Playbooks, metrics, and response procedures for incidents.",
        "decision_kit_id": "compliance-readiness"
    },

    # Open Source Project Triage
    "Candidate-OSS-MESHGRAPHQL": {
        "id": "oss-meshgraphql",
        "candidate_id": "Candidate-OSS-MESHGRAPHQL",
        "title": "MeshGraphQL",
        "name": "MeshGraphQL",
        "content": "Federated graph router project targeting multi-source APIs.",
        "decision_kit_id": "oss-project-triage"
    },
    "Candidate-OSS-LOGSTREAMX": {
        "id": "oss-logstreamx",
        "candidate_id": "Candidate-OSS-LOGSTREAMX",
        "title": "LogStreamX",
        "name": "LogStreamX",
        "content": "Streaming log pipeline for high-throughput observability.",
        "decision_kit_id": "oss-project-triage"
    },
    "Candidate-OSS-AUTOSCALERLITE": {
        "id": "oss-autoscalerlite",
        "candidate_id": "Candidate-OSS-AUTOSCALERLITE",
        "title": "AutoScalerLite",
        "name": "AutoScalerLite",
        "content": "Lightweight scaling operator for container orchestrators.",
        "decision_kit_id": "oss-project-triage"
    },

    # Community Budget Allocation
    "Candidate-COMMUNITY-WIFI-EXPANSION": {
        "id": "community-wifi-expansion",
        "candidate_id": "Candidate-COMMUNITY-WIFI-EXPANSION",
        "title": "Community Wi-Fi Expansion",
        "name": "Community Wi-Fi Expansion",
        "content": "Public access Wi-Fi nodes expansion across neighborhoods.",
        "decision_kit_id": "community-budget-allocation"
    },
    "Candidate-COMMUNITY-URBAN-TREE-CANOPY-BOOST": {
        "id": "community-urban-tree-canopy-boost",
        "candidate_id": "Candidate-COMMUNITY-URBAN-TREE-CANOPY-BOOST",
        "title": "Urban Tree Canopy Boost",
        "name": "Urban Tree Canopy Boost",
        "content": "Heat mitigation through expanded urban tree canopy.",
        "decision_kit_id": "community-budget-allocation"
    },
    "Candidate-COMMUNITY-NEIGHBORHOOD-MICRO-LIBRARY": {
        "id": "community-neighborhood-micro-library",
        "candidate_id": "Candidate-COMMUNITY-NEIGHBORHOOD-MICRO-LIBRARY",
        "title": "Neighborhood Micro Library",
        "name": "Neighborhood Micro Library",
        "content": "Compact lending libraries to improve neighborhood literacy access.",
        "decision_kit_id": "community-budget-allocation"
    },

    # Home Espresso Setup Selection
    "Candidate-ESPRESSO-LELIT-BIANCA-V3": {
        "id": "espresso-lelit-bianca-v3",
        "candidate_id": "Candidate-ESPRESSO-LELIT-BIANCA-V3",
        "title": "Lelit Bianca V3",
        "name": "Lelit Bianca V3",
        "content": "Flow profiling dual boiler espresso machine with excellent temperature control.",
        "decision_kit_id": "home-espresso-selection"
    },
    "Candidate-ESPRESSO-PROFITEC-PRO-700": {
        "id": "espresso-profitec-pro-700",
        "candidate_id": "Candidate-ESPRESSO-PROFITEC-PRO-700",
        "title": "Profitec Pro 700",
        "name": "Profitec Pro 700",
        "content": "Stable dual boiler machine known for build quality and reliability.",
        "decision_kit_id": "home-espresso-selection"
    },
    "Candidate-ESPRESSO-BREVILLE-DUAL-BOILER": {
        "id": "espresso-breville-dual-boiler",
        "candidate_id": "Candidate-ESPRESSO-BREVILLE-DUAL-BOILER",
        "title": "Breville Dual Boiler",
        "name": "Breville Dual Boiler",
        "content": "Great value machine with precise temperature control.",
        "decision_kit_id": "home-espresso-selection"
    },

    # Conference Talk Submissions
    "Candidate-CFP-SCALING-EVENT-DRIVEN-AI-SYSTEMS": {
        "id": "cfp-scaling-event-driven-ai-systems",
        "candidate_id": "Candidate-CFP-SCALING-EVENT-DRIVEN-AI-SYSTEMS",
        "title": "Scaling Event-Driven AI Systems",
        "name": "Scaling Event-Driven AI Systems",
        "content": "Talk on architecture patterns for scaling event-driven AI systems.",
        "decision_kit_id": "conference-talk-submissions"
    },
    "Candidate-CFP-MEMORY-EFFICIENT-VECTOR-INDEXING": {
        "id": "cfp-memory-efficient-vector-indexing",
        "candidate_id": "Candidate-CFP-MEMORY-EFFICIENT-VECTOR-INDEXING",
        "title": "Memory-Efficient Vector Indexing",
        "name": "Memory-Efficient Vector Indexing",
        "content": "Explores storage and recall strategies for vector databases.",
        "decision_kit_id": "conference-talk-submissions"
    },
    "Candidate-CFP-POLICY-AS-CODE-AND-OBSERVABILITY": {
        "id": "cfp-policy-as-code-and-observability",
        "candidate_id": "Candidate-CFP-POLICY-AS-CODE-AND-OBSERVABILITY",
        "title": "Unifying Policy-as-Code and Observability",
        "name": "Unifying Policy-as-Code and Observability",
        "content": "Holistic governance combining policy-as-code with observability.",
        "decision_kit_id": "conference-talk-submissions"
    },

    # Backyard Renovation Prioritization
    "Candidate-BACKYARD-PERGOLA-LIGHTING": {
        "id": "backyard-pergola-lighting",
        "candidate_id": "Candidate-BACKYARD-PERGOLA-LIGHTING",
        "title": "Pergola + Lighting",
        "name": "Pergola + Lighting",
        "content": "Shade structure with ambient lighting for outdoor enjoyment.",
        "decision_kit_id": "backyard-renovation"
    },
    "Candidate-BACKYARD-RAISED-GARDEN-BEDS": {
        "id": "backyard-raised-garden-beds",
        "candidate_id": "Candidate-BACKYARD-RAISED-GARDEN-BEDS",
        "title": "Raised Garden Beds",
        "name": "Raised Garden Beds",
        "content": "Seasonal vegetable beds for home gardening.",
        "decision_kit_id": "backyard-renovation"
    },
    "Candidate-BACKYARD-FIRE-PIT-SEATING-AREA": {
        "id": "backyard-fire-pit-seating-area",
        "candidate_id": "Candidate-BACKYARD-FIRE-PIT-SEATING-AREA",
        "title": "Fire Pit Seating Area",
        "name": "Fire Pit Seating Area",
        "content": "Evening gathering spot centered on a fire pit.",
        "decision_kit_id": "backyard-renovation"
    },

    # Software Engineer Hiring
    "Candidate-HIRING-ALICE-RIVERA": {
        "id": "hiring-alice-rivera",
        "candidate_id": "Candidate-HIRING-ALICE-RIVERA",
        "title": "Alice Rivera",
        "name": "Alice Rivera",
        "content": "Senior backend engineer who led multi-region service migrations.",
        "decision_kit_id": "software-engineer-hiring"
    },
    "Candidate-HIRING-BENJAMIN-CHO": {
        "id": "hiring-benjamin-cho",
        "candidate_id": "Candidate-HIRING-BENJAMIN-CHO",
        "title": "Benjamin Cho",
        "name": "Benjamin Cho",
        "content": "Strong distributed caching experience and platform performance work.",
        "decision_kit_id": "software-engineer-hiring"
    },
    "Candidate-HIRING-PRIYA-NATARAJAN": {
        "id": "hiring-priya-natarajan",
        "candidate_id": "Candidate-HIRING-PRIYA-NATARAJAN",
        "title": "Priya Natarajan",
        "name": "Priya Natarajan",
        "content": "Observability and SRE advocate with strong reliability mindset.",
        "decision_kit_id": "software-engineer-hiring"
    },
    "Candidate-HIRING-MARCUS-ONEILL": {
        "id": "hiring-marcus-oneill",
        "candidate_id": "Candidate-HIRING-MARCUS-ONEILL",
        "title": "Marcus O'Neill",
        "name": "Marcus O'Neill",
        "content": "Scalability and data pipeline experience in production systems.",
        "decision_kit_id": "software-engineer-hiring"
    },
})

