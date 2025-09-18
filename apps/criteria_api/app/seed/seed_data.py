import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.utils.db import SessionLocal
from app.models.criteria_orm import CriteriaORM
from app.models.rubric_orm import RubricORM
from app.models.rubric_criterion_orm import RubricCriterionORM
from app.models.candidate_orm import CandidateORM
from app.models.decision_kit_orm import DecisionKitORM, DecisionKitCandidateORM

"""Realistic multi-domain seed data.

Each rubric models a plausible real-world evaluation scenario. For every rubric we:
  1. Create the rubric (published v1.0.0) with weighted criteria summing to 1.0
  2. Create a single decision kit contextual to that rubric
  3. Seed a small, meaningful set of candidates (or items) for comparison

Design goals:
  - Deterministic names (no random suffixes) for clarity and stable snapshots
  - Limited volume to keep test runs fast and avoid SQLite locking
  - Domain breadth to showcase adaptability (consumer electronics, hiring, vendor selection)
"""

# README Example Coverage Mapping:
# - Televisions comparison -> TV Evaluation
# - Hiring packet / promotion dossier -> Software Engineer Hiring (covers internal review as well)
# - Grant proposal reviews -> Grant Proposal Review
# - Classroom / project assessment -> Classroom Project Assessment
# - Startup pitch scoring -> Startup Pitch Scoring
# - Compliance readiness -> Compliance Readiness Assessment
# - Open source project triage -> Open Source Project Triage
# - Community budget allocation -> Community Budget Allocation
# - Home espresso setup -> Home Espresso Setup Selection
# - Conference talk submissions -> Conference Talk Submissions
# - Backyard renovation ideas -> Backyard Renovation Prioritization
# (Cloud storage vendor selection intentionally omitted to reduce seed scope)

RUBRIC_DEFINITIONS = [
    {
        "name": "TV Evaluation",
        "description": "Compares consumer 2025 mid-range 55\" televisions across critical buyer criteria.",
        "criteria": [
            {"name": "Picture Quality", "weight": 0.20, "description": "Resolution, contrast, HDR performance.", "levels": [
                (5, "Excellent", "OLED/QLED, deep blacks, wide color gamut"),
                (4, "Good", "High contrast 4K LED"),
                (3, "Fair", "Acceptable 4K/HD with some uniformity issues"),
                (2, "Poor", "Visible banding or light bleed"),
                (1, "Very Poor", "Low resolution / severe artifacts")
            ]},
            {"name": "Sound Quality", "weight": 0.10, "description": "Clarity, fullness, spatial effects.", "levels": [
                (5, "Excellent", "Integrated Atmos, rich dynamics"),
                (4, "Good", "Clear dialog, balanced"),
                (3, "Fair", "Usable but thin"),
                (2, "Poor", "Muffled or tinny"),
                (1, "Very Poor", "Distorted at moderate volume")
            ]},
            {"name": "Gaming Performance", "weight": 0.15, "description": "Input lag, refresh rate, HDMI 2.1 features.", "levels": [
                (5, "Excellent", "<=5ms, 120Hz, VRR, ALLM"),
                (4, "Good", "Low lag, 120Hz without full VRR"),
                (3, "Fair", "~15ms, stable 60Hz"),
                (2, "Poor", ">25ms noticeable lag"),
                (1, "Very Poor", "Unsuitable for modern gaming")
            ]},
            {"name": "Smart Platform", "weight": 0.15, "description": "App breadth, UI responsiveness, voice integration.", "levels": [
                (5, "Excellent", "Full catalog, fast nav, assistants integrated"),
                (4, "Good", "Most apps, responsive"),
                (3, "Fair", "Some omissions or minor lag"),
                (2, "Poor", "Frequent stutter / missing key apps"),
                (1, "Very Poor", "Unreliable or extremely limited")
            ]},
            {"name": "Ease of Use", "weight": 0.10, "description": "Onboarding, remote ergonomics, settings clarity.", "levels": [
                (5, "Excellent", "Intuitive setup + clear menus"),
                (4, "Good", "Mostly straightforward"),
                (3, "Fair", "Some buried options"),
                (2, "Poor", "Confusing or inconsistent"),
                (1, "Very Poor", "Frustrating navigation")
            ]},
            {"name": "Design & Build", "weight": 0.05, "description": "Aesthetics, bezel, stand / mount flexibility.", "levels": [
                (5, "Excellent", "Premium minimal design"),
                (4, "Good", "Modern"),
                (3, "Fair", "Standard bulk"),
                (2, "Poor", "Chunky / uneven"),
                (1, "Very Poor", "Obtrusive")
            ]},
            {"name": "Energy Efficiency", "weight": 0.05, "description": "Typical HDR streaming power draw.", "levels": [
                (5, "Excellent", "Top-tier efficiency"),
                (4, "Good", "Better than average"),
                (3, "Fair", "Typical"),
                (2, "Poor", "Above average consumption"),
                (1, "Very Poor", "Inefficient")
            ]},
            {"name": "Price/Value", "weight": 0.15, "description": "Feature set vs MSRP / market street price.", "levels": [
                (5, "Excellent", "Outstanding value"),
                (4, "Good", "Strong offering"),
                (3, "Fair", "Acceptable trade-offs"),
                (2, "Poor", "Paying a premium for little"),
                (1, "Very Poor", "Overpriced")
            ]},
        ],
        "decision_kit": {
            "name_original": "2025 Living Room TV Comparison",
            "description": "Shortlist for a mid-range family media room upgrade",
            "candidates": [
                {"name": "LG OLED C3 55\"", "description": "OLED panel with excellent contrast"},
                {"name": "Samsung QN90C 55\"", "description": "Mini-LED brightness leader"},
                {"name": "Sony Bravia XR A80L", "description": "Strong processing + motion handling"},
            ],
        },
    },
    {
        "name": "Grant Proposal Review",
        "description": "Evaluates research or innovation grant proposals for funding allocation.",
        "criteria": [
            {"name": "Impact Potential", "weight": 0.30, "description": "Projected societal or market benefit.", "levels": [
                (5, "Excellent", "Transformative potential"),(4,"Good","Meaningful improvement"),(3,"Fair","Incremental"),(2,"Low","Limited scope"),(1,"Minimal","Niche / unclear") ]},
            {"name": "Feasibility", "weight": 0.20, "description": "Technical + operational viability.", "levels": [
                (5,"Excellent","Clear path + resources"),(4,"Good","Minor gaps"),(3,"Fair","Some risks"),(2,"Weak","Significant uncertainties"),(1,"Poor","Not credible") ]},
            {"name": "Team Capability", "weight": 0.20, "description": "Experience + execution track record.", "levels": [
                (5,"Excellent","Veteran, complementary team"),(4,"Good","Relevant experience"),(3,"Fair","Some gaps"),(2,"Weak","Little track record"),(1,"Poor","Unproven") ]},
            {"name": "Budget Realism", "weight": 0.15, "description": "Appropriateness of requested funds.", "levels": [
                (5,"Excellent","Efficient & justified"),(4,"Good","Reasonable"),(3,"Fair","Some padding"),(2,"Weak","Inflated"),(1,"Poor","Unjustified") ]},
            {"name": "Alignment with Program Goals", "weight": 0.15, "description": "Strategic fit to funding mission.", "levels": [
                (5,"Excellent","Direct core alignment"),(4,"Good","Strong adjacency"),(3,"Fair","Partial fit"),(2,"Weak","Peripheral"),(1,"Poor","Misaligned") ]},
        ],
        "decision_kit": {
            "name_original": "Spring Grant Shortlist",
            "description": "Shortlist of grant proposals for board review",
            "candidates": [
                {"name": "Urban Air Quality Sensors", "description": "Low-cost mesh network"},
                {"name": "Food Waste Analytics Platform", "description": "Hospitality waste reduction"},
                {"name": "STEM Outreach Mobile Lab", "description": "Rural education initiative"},
            ],
        },
    },
    {
        "name": "Classroom Project Assessment",
        "description": "Rubric for capstone student project evaluation.",
        "criteria": [
            {"name": "Technical Depth", "weight": 0.25, "description": "Complexity & rigor.", "levels": [(5,"Excellent","Advanced concepts mastered"),(4,"Good","Solid implementation"),(3,"Fair","Meets basics"),(2,"Weak","Shallow"),(1,"Poor","Minimal")]} ,
            {"name": "Functionality", "weight": 0.20, "description": "Feature completeness.", "levels": [(5,"Excellent","All features + stretch"),(4,"Good","Core complete"),(3,"Fair","Most features"),(2,"Weak","Partially working"),(1,"Poor","Fails")]} ,
            {"name": "Code Quality", "weight": 0.20, "description": "Structure, clarity, tests.", "levels": [(5,"Excellent","Modular + tested"),(4,"Good","Readable"),(3,"Fair","Some duplication"),(2,"Weak","Spaghetti"),(1,"Poor","Disorganized")]} ,
            {"name": "Presentation", "weight": 0.15, "description": "Clarity of demo + narrative.", "levels": [(5,"Excellent","Compelling & clear"),(4,"Good","Organized"),(3,"Fair","Some gaps"),(2,"Weak","Hard to follow"),(1,"Poor","Unclear")]} ,
            {"name": "Innovation", "weight": 0.20, "description": "Creativity & novelty.", "levels": [(5,"Excellent","Highly original"),(4,"Good","Notable twist"),(3,"Fair","Typical"),(2,"Low","Derivative"),(1,"None","Copied")]} ,
        ],
        "decision_kit": {
            "name_original": "CS Capstone Evaluation",
            "description": "Final cohort capstone judging",
            "candidates": [
                {"name": "Smart Campus Navigator", "description": "Indoor routing app"},
                {"name": "Meal Plan Optimizer", "description": "Nutritional + cost model"},
                {"name": "Adaptive Study Scheduler", "description": "Personalized planning"},
            ],
        },
    },
    {
        "name": "Startup Pitch Scoring",
        "description": "Investor pitch evaluation rubric.",
        "criteria": [
            {"name": "Market Size", "weight": 0.20, "description": "Addressable opportunity.", "levels": [(5,"Excellent","Massive global"),(4,"Good","Large"),(3,"Fair","Moderate"),(2,"Low","Niche"),(1,"Minimal","Very small")]},
            {"name": "Product Differentiation", "weight": 0.20, "description": "Edge vs incumbents.", "levels": [(5,"Excellent","Clear moat"),(4,"Good","Distinct value"),(3,"Fair","Some overlap"),(2,"Weak","Easily copied"),(1,"Poor","Undifferentiated")]},
            {"name": "Traction", "weight": 0.15, "description": "Growth indicators.", "levels": [(5,"Excellent","Rapid adoption"),(4,"Good","Steady growth"),(3,"Fair","Early signs"),(2,"Weak","Sparse"),(1,"Poor","None")]},
            {"name": "Team Strength", "weight": 0.20, "description": "Experience mix.", "levels": [(5,"Excellent","Serial operators"),(4,"Good","Relevant exp"),(3,"Fair","Partial"),(2,"Weak","Gaps"),(1,"Poor","Inexperienced")]},
            {"name": "Business Model Clarity", "weight": 0.15, "description": "Path to revenue.", "levels": [(5,"Excellent","Clear & scalable"),(4,"Good","Sound"),(3,"Fair","Some risk"),(2,"Weak","Unclear"),(1,"Poor","Not viable")]},
            {"name": "Defensibility", "weight": 0.10, "description": "Sustainable advantage.", "levels": [(5,"Excellent","Strong IP/network"),(4,"Good","Some barriers"),(3,"Fair","Limited"),(2,"Weak","Thin"),(1,"Poor","None")]},
        ],
        "decision_kit": {
            "name_original": "Seed Pitch Day",
            "description": "Investor committee evaluation set",
            "candidates": [
                {"name": "LoopCart", "description": "Circular packaging logistics"},
                {"name": "SynthEdge", "description": "Edge AI model compression"},
                {"name": "FarmTrace", "description": "Soil carbon monitoring"},
            ],
        },
    },
    {
        "name": "Compliance Readiness Assessment",
        "description": "Pre-audit readiness evaluation rubric.",
        "criteria": [
            {"name": "Policy Coverage", "weight": 0.25, "description": "Documented controls breadth.", "levels": [(5,"Excellent","Comprehensive"),(4,"Good","Most areas"),(3,"Fair","Moderate gaps"),(2,"Weak","Major gaps"),(1,"Poor","Sparse")]} ,
            {"name": "Control Effectiveness", "weight": 0.25, "description": "Operational execution.", "levels": [(5,"Excellent","Consistent evidence"),(4,"Good","Generally effective"),(3,"Fair","Mixed"),(2,"Weak","Inconsistent"),(1,"Poor","Ineffective")]} ,
            {"name": "Evidence Quality", "weight": 0.20, "description": "Completeness & clarity.", "levels": [(5,"Excellent","Auditable & current"),(4,"Good","Mostly current"),(3,"Fair","Some stale"),(2,"Weak","Sparse"),(1,"Poor","Missing")]} ,
            {"name": "Risk Management", "weight": 0.15, "description": "Identification & mitigation.", "levels": [(5,"Excellent","Proactive"),(4,"Good","Regular"),(3,"Fair","Reactive"),(2,"Weak","Ad hoc"),(1,"Poor","Absent")]} ,
            {"name": "Training & Awareness", "weight": 0.15, "description": "Staff compliance enablement.", "levels": [(5,"Excellent","Embedded"),(4,"Good","Regular"),(3,"Fair","Periodic"),(2,"Weak","Rare"),(1,"Poor","None")]} ,
        ],
        "decision_kit": {
            "name_original": "SOC2 Pre-Audit Checklist",
            "description": "Internal readiness snapshot",
            "candidates": [
                {"name": "Accounting System Controls", "description": "Financial process scope"},
                {"name": "Access Governance", "description": "Joiner/mover/leaver review"},
                {"name": "Incident Response Program", "description": "Playbooks & metrics"},
            ],
        },
    },
    {
        "name": "Open Source Project Triage",
        "description": "Evaluates inbound OSS project candidates for foundation incubation.",
        "criteria": [
            {"name": "Community Activity", "weight": 0.25, "description": "Stars, commits, contributors.", "levels": [(5,"Excellent","Vibrant"),(4,"Good","Active"),(3,"Fair","Moderate"),(2,"Weak","Low"),(1,"Poor","Dormant")]} ,
            {"name": "Governance Maturity", "weight": 0.20, "description": "Structure & policies.", "levels": [(5,"Excellent","Formalized"),(4,"Good","Emerging"),(3,"Fair","Basic"),(2,"Weak","Ad hoc"),(1,"Poor","None")]} ,
            {"name": "Ecosystem Relevance", "weight": 0.20, "description": "Strategic alignment.", "levels": [(5,"Excellent","High leverage"),(4,"Good","Aligned"),(3,"Fair","Some fit"),(2,"Weak","Peripheral"),(1,"Poor","Unrelated")]} ,
            {"name": "Security Practices", "weight": 0.15, "description": "Vulnerability & release hygiene.", "levels": [(5,"Excellent","Automated & responsive"),(4,"Good","Tracked"),(3,"Fair","Manual"),(2,"Weak","Slow"),(1,"Poor","Neglected")]} ,
            {"name": "Documentation Quality", "weight": 0.20, "description": "Ease of adoption.", "levels": [(5,"Excellent","Comprehensive"),(4,"Good","Solid"),(3,"Fair","Usable"),(2,"Weak","Sparse"),(1,"Poor","Outdated")]} ,
        ],
        "decision_kit": {
            "name_original": "OSS Incubation Candidates",
            "description": "Projects under consideration",
            "candidates": [
                {"name": "MeshGraphQL", "description": "Federated graph router"},
                {"name": "LogStreamX", "description": "Streaming log pipeline"},
                {"name": "AutoScalerLite", "description": "Lightweight scaling operator"},
            ],
        },
    },
    {
        "name": "Community Budget Allocation",
        "description": "Prioritizes community capital projects proposals.",
        "criteria": [
            {"name": "Benefit Reach", "weight": 0.30, "description": "Population impacted.", "levels": [(5,"Excellent","City-wide"),(4,"Good","Multi-neighborhood"),(3,"Fair","Neighborhood"),(2,"Low","Street"),(1,"Minimal","Few households")]} ,
            {"name": "Cost Efficiency", "weight": 0.20, "description": "Benefit per dollar.", "levels": [(5,"Excellent","High ROI"),(4,"Good","Positive"),(3,"Fair","Neutral"),(2,"Low","Marginal"),(1,"Poor","Negative")]},
            {"name": "Sustainability", "weight": 0.20, "description": "Environmental longevity.", "levels": [(5,"Excellent","Net-positive"),(4,"Good","Low impact"),(3,"Fair","Neutral"),(2,"Weak","Some negative"),(1,"Poor","Harmful")]} ,
            {"name": "Feasibility", "weight": 0.15, "description": "Execution practicality.", "levels": [(5,"Excellent","Ready to start"),(4,"Good","Minor prep"),(3,"Fair","Some dependencies"),(2,"Weak","Complex"),(1,"Poor","Blocked")]} ,
            {"name": "Equity Impact", "weight": 0.15, "description": "Benefit to underserved groups.", "levels": [(5,"Excellent","Significant uplift"),(4,"Good","Meaningful"),(3,"Fair","Moderate"),(2,"Low","Limited"),(1,"None","No impact")]} ,
        ],
        "decision_kit": {
            "name_original": "Civic Project Funding Round",
            "description": "Participatory budget cycle",
            "candidates": [
                {"name": "Community Wi-Fi Expansion", "description": "Public access nodes"},
                {"name": "Urban Tree Canopy Boost", "description": "Heat mitigation"},
                {"name": "Neighborhood Micro Library", "description": "Literacy access"},
            ],
        },
    },
    {
        "name": "Home Espresso Setup Selection",
        "description": "Choosing a balanced prosumer espresso equipment bundle.",
        "criteria": [
            {"name": "Espresso Quality", "weight": 0.30, "description": "Shot consistency & flavor potential.", "levels": [(5,"Excellent","Competition capable"),(4,"Good","Cafe comparable"),(3,"Fair","Solid home"),(2,"Weak","Inconsistent"),(1,"Poor","Watery / harsh")]} ,
            {"name": "Temperature Stability", "weight": 0.15, "description": "Thermal management.", "levels": [(5,"Excellent","PID multi-boiler"),(4,"Good","PID single"),(3,"Fair","Stable after warmup"),(2,"Weak","Fluctuates"),(1,"Poor","Unstable")]} ,
            {"name": "Workflow Ergonomics", "weight": 0.15, "description": "Ease of daily use & cleaning.", "levels": [(5,"Excellent","Streamlined"),(4,"Good","Minor friction"),(3,"Fair","Some fiddling"),(2,"Weak","Awkward"),(1,"Poor","Cumbersome")]} ,
            {"name": "Milk Frothing Performance", "weight": 0.15, "description": "Steam power & texture control.", "levels": [(5,"Excellent","Microfoam fast"),(4,"Good","Consistent"),(3,"Fair","Acceptable"),(2,"Weak","Slow"),(1,"Poor","Weak")]} ,
            {"name": "Build & Reliability", "weight": 0.15, "description": "Longevity & serviceability.", "levels": [(5,"Excellent","Commercial-grade"),(4,"Good","Robust"),(3,"Fair","Decent"),(2,"Weak","Plastic heavy"),(1,"Poor","Fragile")]} ,
            {"name": "Counter Footprint", "weight": 0.10, "description": "Space efficiency.", "levels": [(5,"Excellent","Compact"),(4,"Good","Moderate"),(3,"Fair","Large"),(2,"Weak","Bulky"),(1,"Poor","Huge")]} ,
        ],
        "decision_kit": {
            "name_original": "Prosumer Espresso Comparison",
            "description": "Shortlist for home setup",
            "candidates": [
                {"name": "Lelit Bianca V3", "description": "Flow profiling dual boiler"},
                {"name": "Profitec Pro 700", "description": "Stable dual boiler"},
                {"name": "Breville Dual Boiler", "description": "Value temperature control"},
            ],
        },
    },
    {
        "name": "Conference Talk Submissions",
        "description": "Tech conference CFP rubric.",
        "criteria": [
            {"name": "Relevance", "weight": 0.25, "description": "Fit to conference theme.", "levels": [(5,"Excellent","Central theme"),(4,"Good","Strong fit"),(3,"Fair","Peripheral"),(2,"Weak","Tangential"),(1,"Poor","Off-topic")]} ,
            {"name": "Clarity", "weight": 0.20, "description": "Abstract readability & focus.", "levels": [(5,"Excellent","Crystal clear"),(4,"Good","Well written"),(3,"Fair","Understandable"),(2,"Weak","Vague"),(1,"Poor","Confusing")]} ,
            {"name": "Practical Value", "weight": 0.20, "description": "Actionable takeaways.", "levels": [(5,"Excellent","High utility"),(4,"Good","Useful"),(3,"Fair","Some value"),(2,"Weak","Thin"),(1,"Poor","None")]} ,
            {"name": "Originality", "weight": 0.20, "description": "Novelty of perspective.", "levels": [(5,"Excellent","Fresh insight"),(4,"Good","Some originality"),(3,"Fair","Common topic"),(2,"Weak","Rehashed"),(1,"Poor","Stale")]} ,
            {"name": "Speaker Credibility", "weight": 0.15, "description": "Experience & delivery history.", "levels": [(5,"Excellent","Renowned expert"),(4,"Good","Experienced"),(3,"Fair","Some talks"),(2,"Weak","Few samples"),(1,"Poor","Unproven")]} ,
        ],
        "decision_kit": {
            "name_original": "2025 CFP Shortlist",
            "description": "Program committee selection set",
            "candidates": [
                {"name": "Scaling Event-Driven AI Systems", "description": "Architecture patterns"},
                {"name": "Memory-Efficient Vector Indexing", "description": "Storage & recall"},
                {"name": "Unifying Policy-as-Code and Observability", "description": "Holistic governance"},
            ],
        },
    },
    {
        "name": "Backyard Renovation Prioritization",
        "description": "Home outdoor improvement decision rubric.",
        "criteria": [
            {"name": "Family Enjoyment", "weight": 0.30, "description": "Expected usage & joy.", "levels": [(5,"Excellent","Daily high use"),(4,"Good","Frequent"),(3,"Fair","Occasional"),(2,"Low","Rare"),(1,"Minimal","Seldom")]},
            {"name": "Maintenance Effort", "weight": 0.15, "description": "Ongoing care required.", "levels": [(5,"Excellent","Very low"),(4,"Good","Low"),(3,"Fair","Moderate"),(2,"High","Demanding"),(1,"Extreme","Burden")]},
            {"name": "Cost", "weight": 0.15, "description": "Relative investment.", "levels": [(5,"Excellent","Low cost"),(4,"Good","Affordable"),(3,"Fair","Moderate"),(2,"High","Costly"),(1,"Poor","Expensive")]},
            {"name": "Property Value Impact", "weight": 0.20, "description": "Resale contribution.", "levels": [(5,"Excellent","Notable increase"),(4,"Good","Positive"),(3,"Fair","Neutral"),(2,"Low","Minimal"),(1,"None","No impact")]},
            {"name": "Seasonal Flexibility", "weight": 0.20, "description": "Multi-season usability.", "levels": [(5,"Excellent","Year-round"),(4,"Good","Most seasons"),(3,"Fair","Warm months"),(2,"Low","Short season"),(1,"Poor","Very limited")]} ,
        ],
        "decision_kit": {
            "name_original": "Backyard Project Shortlist",
            "description": "Household planning session",
            "candidates": [
                {"name": "Pergola + Lighting", "description": "Shade + ambiance"},
                {"name": "Raised Garden Beds", "description": "Seasonal vegetables"},
                {"name": "Fire Pit Seating Area", "description": "Evening gathering spot"},
            ],
        },
    },
    {
        "name": "Software Engineer Hiring",
        "description": "Evaluation rubric for senior backend engineer candidates.",
        "criteria": [
            {"name": "System Design", "weight": 0.25, "description": "Architectural reasoning & trade-offs.", "levels": [
                (5, "Excellent", "Scalable, resilient, cost-aware designs"),
                (4, "Strong", "Solid patterns, minor gaps"),
                (3, "Adequate", "Covers basics"),
                (2, "Weak", "Superficial / missing concerns"),
                (1, "Poor", "Incorrect or brittle")
            ]},
            {"name": "Coding Quality", "weight": 0.20, "description": "Clarity, correctness, maintainability.", "levels": [
                (5, "Excellent", "Idiomatic, clean abstractions"),
                (4, "Good", "Minor style issues"),
                (3, "Fair", "Readable but verbose"),
                (2, "Weak", "Bug-prone / unclear"),
                (1, "Poor", "Chaotic / incorrect")
            ]},
            {"name": "Problem Solving", "weight": 0.15, "description": "Approach, decomposition, iteration.", "levels": [
                (5, "Excellent", "Explores space & optimizes"),
                (4, "Good", "Solid plan, minor detours"),
                (3, "Fair", "Linear progress"),
                (2, "Weak", "Stuck or narrow"),
                (1, "Poor", "No viable path")
            ]},
            {"name": "Communication", "weight": 0.15, "description": "Clarity, collaboration, receptive feedback.", "levels": [
                (5, "Excellent", "Concise & adaptive"),
                (4, "Good", "Clear with small gaps"),
                (3, "Fair", "Under-explains details"),
                (2, "Weak", "Hard to follow"),
                (1, "Poor", "Disorganized")
            ]},
            {"name": "Reliability & Operations", "weight": 0.10, "description": "Observability, deployment, incident mindset.", "levels": [
                (5, "Excellent", "Proactive resilience & metrics"),
                (4, "Good", "Addresses core ops"),
                (3, "Fair", "Mentions basic monitoring"),
                (2, "Weak", "Minimal ops awareness"),
                (1, "Poor", "Ignores operations")
            ]},
            {"name": "Culture & Collaboration", "weight": 0.15, "description": "Growth mindset, inclusivity, mentoring.", "levels": [
                (5, "Excellent", "Elevates team dynamics"),
                (4, "Good", "Positive partner"),
                (3, "Fair", "Neutral presence"),
                (2, "Weak", "Limited empathy"),
                (1, "Poor", "Detrimental")
            ]},
        ],
        "decision_kit": {
            "name_original": "Senior Backend Engineer Shortlist",
            "description": "Final-round candidates for backend platform role",
            "candidates": [
                {"name": "Alice Rivera", "description": "Led multi-region service migrations"},
                {"name": "Benjamin Cho", "description": "Strong on distributed caching"},
                {"name": "Priya Natarajan", "description": "Observability & SRE advocate"},
                {"name": "Marcus O'Neill", "description": "Scalability + data pipeline experience"},
                
            ],
        },
    },
]

"""Deterministic candidate IDs aligned with apps/agent/seed/seed_data.py

Keys:
- Top-level key: rubric name (as defined in RUBRIC_DEFINITIONS -> 'name')
- Inner key: exact candidate display name from the decision kit 'candidates' list
- Value: desired candidate.id string (must be globally unique)
"""
CANDIDATE_ID_MAP = {
    "TV Evaluation": {
        "LG OLED C3 55\"": "Candidate-TV-LG-OLED-C3-55",
        "Samsung QN90C 55\"": "Candidate-TV-SAMSUNG-QN90C-55",
        "Sony Bravia XR A80L": "Candidate-TV-SONY-BRAVIA-XR-A80L",
    },
    "Grant Proposal Review": {
        "Urban Air Quality Sensors": "Candidate-GRANT-URBAN-AIR-QUALITY-SENSORS",
        "Food Waste Analytics Platform": "Candidate-GRANT-FOOD-WASTE-ANALYTICS-PLATFORM",
        "STEM Outreach Mobile Lab": "Candidate-GRANT-STEM-OUTREACH-MOBILE-LAB",
    },
    "Classroom Project Assessment": {
        "Smart Campus Navigator": "Candidate-CLASSROOM-SMART-CAMPUS-NAVIGATOR",
        "Meal Plan Optimizer": "Candidate-CLASSROOM-MEAL-PLAN-OPTIMIZER",
        "Adaptive Study Scheduler": "Candidate-CLASSROOM-ADAPTIVE-STUDY-SCHEDULER",
    },
    "Startup Pitch Scoring": {
        "LoopCart": "Candidate-PITCH-LOOPCART",
        "SynthEdge": "Candidate-PITCH-SYNTHEDGE",
        "FarmTrace": "Candidate-PITCH-FARMTRACE",
    },
    "Compliance Readiness Assessment": {
        "Accounting System Controls": "Candidate-COMPLIANCE-ACCOUNTING-SYSTEM-CONTROLS",
        "Access Governance": "Candidate-COMPLIANCE-ACCESS-GOVERNANCE",
        "Incident Response Program": "Candidate-COMPLIANCE-INCIDENT-RESPONSE-PROGRAM",
    },
    "Open Source Project Triage": {
        "MeshGraphQL": "Candidate-OSS-MESHGRAPHQL",
        "LogStreamX": "Candidate-OSS-LOGSTREAMX",
        "AutoScalerLite": "Candidate-OSS-AUTOSCALERLITE",
    },
    "Community Budget Allocation": {
        "Community Wi-Fi Expansion": "Candidate-COMMUNITY-WIFI-EXPANSION",
        "Urban Tree Canopy Boost": "Candidate-COMMUNITY-URBAN-TREE-CANOPY-BOOST",
        "Neighborhood Micro Library": "Candidate-COMMUNITY-NEIGHBORHOOD-MICRO-LIBRARY",
    },
    "Home Espresso Setup Selection": {
        "Lelit Bianca V3": "Candidate-ESPRESSO-LELIT-BIANCA-V3",
        "Profitec Pro 700": "Candidate-ESPRESSO-PROFITEC-PRO-700",
        "Breville Dual Boiler": "Candidate-ESPRESSO-BREVILLE-DUAL-BOILER",
    },
    "Conference Talk Submissions": {
        "Scaling Event-Driven AI Systems": "Candidate-CFP-SCALING-EVENT-DRIVEN-AI-SYSTEMS",
        "Memory-Efficient Vector Indexing": "Candidate-CFP-MEMORY-EFFICIENT-VECTOR-INDEXING",
        "Unifying Policy-as-Code and Observability": "Candidate-CFP-POLICY-AS-CODE-AND-OBSERVABILITY",
    },
    "Backyard Renovation Prioritization": {
        "Pergola + Lighting": "Candidate-BACKYARD-PERGOLA-LIGHTING",
        "Raised Garden Beds": "Candidate-BACKYARD-RAISED-GARDEN-BEDS",
        "Fire Pit Seating Area": "Candidate-BACKYARD-FIRE-PIT-SEATING-AREA",
    },
    "Software Engineer Hiring": {
        "Alice Rivera": "Candidate-HIRING-ALICE-RIVERA",
        "Benjamin Cho": "Candidate-HIRING-BENJAMIN-CHO",
        "Priya Natarajan": "Candidate-HIRING-PRIYA-NATARAJAN",
        "Marcus O'Neill": "Candidate-HIRING-MARCUS-ONEILL",
        
    },
}


def _ensure_rubric(db: Session, definition: dict):
    existing = db.query(RubricORM).filter(RubricORM.name_normalized == definition["name"].lower()).first()
    if existing:
        return existing
    rubric_id = str(uuid.uuid4())
    rubric = RubricORM(
        id=rubric_id,
        name_normalized=definition["name"].lower(),
        name_original=definition["name"],
        version="1.0.0",
        description=definition["description"],
        published=True,
        published_at=datetime.now(timezone.utc),
    )
    db.add(rubric)
    db.flush()
    # Criteria + association ordering
    for pos, cdef in enumerate(definition["criteria"]):
        crit_id = str(uuid.uuid4())
        levels_lines = [f"{sc} - {label}: {desc}" for sc, label, desc in cdef["levels"]]
        definition_text = f"Summary: {cdef['description']}\nLevels:\n" + "\n".join(levels_lines)
        db.add(CriteriaORM(
            id=crit_id,
            name=cdef["name"],
            description=cdef["description"],
            definition=definition_text,
        ))
        db.add(RubricCriterionORM(
            id=str(uuid.uuid4()),
            rubric_id=rubric_id,
            criterion_id=crit_id,
            position=pos,
            weight=cdef["weight"],
        ))
    return rubric


def _ensure_decision_kit_with_candidates(db: Session, rubric: RubricORM, kit_def: dict):
    # Name normalized used for idempotency
    nm = kit_def["name_original"].lower()
    existing = db.query(DecisionKitORM).filter(DecisionKitORM.name_normalized == nm).first()
    if existing:
        return existing
    dk = DecisionKitORM(
        id=str(uuid.uuid4()),
        name_normalized=nm,
        name_original=kit_def["name_original"],
        description=kit_def["description"],
        rubric_id=rubric.id,
        rubric_version=rubric.version,
        rubric_published=rubric.published,
    )
    db.add(dk)
    db.flush()
    # Determine rubric name as defined in seed (use rubric.name_original)
    rubric_name = rubric.name_original
    cand_id_lookup = CANDIDATE_ID_MAP.get(rubric_name, {})

    for pos, cdef in enumerate(kit_def.get("candidates", [])):
        display_name = cdef["name"]
        # Prefer deterministic ID from map; fall back to UUID if not found
        deterministic_id = cand_id_lookup.get(display_name, None)
        cand = CandidateORM(
            id=deterministic_id or str(uuid.uuid4()),
            name=display_name,
            name_normalized=display_name.lower(),
            description=cdef.get("description"),
        )
        db.add(cand)
        db.flush()
        db.add(DecisionKitCandidateORM(
            id=str(uuid.uuid4()),
            decision_kit_id=dk.id,
            candidate_id=cand.id,
            position=pos,
            name_normalized=cand.name_normalized,
        ))
    return dk


def seed():
    """Idempotently seed realistic rubrics, one decision kit per rubric, and contextual candidates.

    Safe to call multiple times; existing rubrics or kits are left untouched.

            Deployment note:
                By default the application now DROPS and RECREATES the schema on startup to ensure only
                curated seed data is present (eliminating stale or ad hoc test records). To retain data
                between restarts set PRESERVE_DB_ON_START=true. The former DB_RESET_ON_START flag is obsolete.
    """
    db: Session = SessionLocal()
    try:
        for rdef in RUBRIC_DEFINITIONS:
            rubric = _ensure_rubric(db, rdef)
            _ensure_decision_kit_with_candidates(db, rubric, rdef["decision_kit"])
        db.commit()
    finally:
        db.close()
