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
