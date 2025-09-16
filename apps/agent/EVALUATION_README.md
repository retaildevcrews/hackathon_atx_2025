# Document Evaluation Agent

A clean, modular FastAPI service for evaluating documents against customizable rubrics using LangChain and Azure OpenAI. **Integrates with existing criteria_api service** for rubric and criteria management.

## Features

- **Document Evaluation**: Assess documents against structured rubrics with weighted criteria
- **Batch Processing**: Evaluate all criteria in a single LLM call for efficiency
- **Azure Integration**: Uses Azure OpenAI and Azure Search for document retrieval
- **Clean Architecture**: Modular design with separation of concerns
- **Criteria API Integration**: Reuses existing rubric infrastructure instead of duplicating data
- **Service Orchestration**: Agent service focuses on evaluation logic while criteria_api handles data management

## Architecture

```
apps/
├── criteria_api/              # Existing rubric and criteria management
│   ├── models/
│   │   ├── rubric.py         # Rubric data models
│   │   └── criteria.py       # Criteria data models
│   ├── services/             # CRUD operations for rubrics/criteria
│   └── routes/               # REST API for rubric management
│
└── agent/                     # Document evaluation service
    ├── main.py               # FastAPI application entry point
    ├── config.py            # Application configuration
    ├── models/
    │   └── invoke.py        # Evaluation-specific models only
    ├── routes/
    │   ├── invoke.py        # Original invoke endpoint
    │   └── evaluation.py   # New evaluation endpoints
    ├── services/
    │   ├── criteria_bridge.py    # Bridge to criteria_api
    │   ├── search_service.py     # Azure Search integration
    │   └── evaluation_service.py # Document evaluation logic
    └── prompts/
        └── evaluation_prompts.py # LLM prompt templates
```

## Service Integration

The agent service integrates with the existing criteria_api instead of duplicating rubric management:

- **Rubric Data**: Retrieved via HTTP calls to criteria_api endpoints
- **Criteria Details**: Fetched from criteria_api with full definitions
- **No Data Duplication**: Single source of truth for rubrics and criteria
- **Clean Separation**: Agent focuses on evaluation logic, criteria_api handles data

## API Endpoints

### Evaluation Endpoints

- `POST /evaluation/evaluate` - Evaluate document against rubric (by ID or name)
- `GET /evaluation/rubrics` - List available rubrics (from criteria_api)
- `GET /evaluation/rubrics/{rubric_id}` - Get rubric details
- `GET /evaluation/health` - Evaluation service health check

### Original Endpoints

- `POST /invoke` - Original invoke functionality
- `GET /healthz` - Application health check
- `GET /version` - Application version

## Setup

### 1. Environment Variables

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-gpt-4-deployment
AZURE_OPENAI_API_VERSION=2024-02-01

# Azure Search Configuration (optional)
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-search-key
AZURE_SEARCH_INDEX=documents

# Criteria API Integration
CRITERIA_API_URL=http://localhost:8001
```

### 2. Start Services

```bash
# Start criteria_api service first (handles database initialization)
cd apps/criteria_api  
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Start agent service
cd apps/agent
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The `criteria_api` service automatically:
- ✅ **Initializes the database** with proper schema
- ✅ **Handles migrations** for schema updates  
- ✅ **Seeds sample data** if database is empty
- ✅ **Provides health checks** for service monitoring### 3. Use Pre-seeded Data

The `criteria_api` automatically creates sample rubrics on first startup:

- **📺 TV Evaluation Rubric** - Comprehensive TV review criteria (Picture Quality, Sound Quality, Smart Features, etc.)
- **🏢 Company Evaluation Rubric** - Business assessment criteria  
- **📱 Other Domain Rubrics** - Additional evaluation frameworks

You can immediately start evaluating documents using these pre-created rubrics, or create new ones via the criteria_api endpoints.

### 4. Create Custom Rubrics (Optional)

Use the criteria_api to create additional rubrics and criteria:

```bash
# Create criteria via criteria_api
curl -X POST "http://localhost:8001/criteria/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Picture Quality",
    "description": "Evaluation of display quality and visual performance",
    "definition": "Assess resolution, color accuracy, brightness, and contrast"
  }'

# Create rubric via criteria_api
curl -X POST "http://localhost:8001/rubrics/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TV Review Rubric",
    "description": "Comprehensive TV evaluation criteria",
    "criteria": [
      {"criteriaId": "criteria-uuid-here", "weight": 0.4}
    ]
  }'
```

## Usage Examples

### Evaluate a TV Review

```python
import httpx

# Document to evaluate
document = """
Samsung 65" Neo QLED 8K TV Review

Picture Quality: Exceptional 8K resolution with Quantum Dot technology
delivers stunning color accuracy and brightness. HDR10+ and Dolby Vision
support provide excellent contrast ratios. Peak brightness reaches 4000 nits.

Sound Quality: Object Tracking Sound+ with Dolby Atmos creates immersive
audio experience. 60W speakers with dedicated subwoofer deliver rich bass
and clear dialogue.

Smart Platform: Tizen OS runs smoothly with comprehensive app selection
including Netflix, Disney+, Prime Video, and gaming apps. Interface is
responsive and intuitive.
"""

# Evaluation request
request = {
    "document_text": document,
    "rubric_name": "tv_rubric",
    "document_id": "samsung_qled_001"
}

# Send request
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/evaluation/evaluate",
        json=request
    )
    result = response.json()
    print(f"Overall Score: {result['evaluation']['overall_score']}/5.0")
```

### List Available Rubrics

```python
async with httpx.AsyncClient() as client:
    response = await client.get("http://localhost:8000/evaluation/rubrics")
    rubrics = response.json()["rubrics"]
    for rubric in rubrics:
        print(f"- {rubric['rubric_name']} ({rubric['domain']})")
```

## Evaluation Output

The service returns comprehensive evaluation results:

```json
{
  "status": "success",
  "evaluation": {
    "overall_score": 4.2,
    "document_id": "samsung_qled_001",
    "rubric_name": "tv_rubric",
    "criteria_evaluations": [
      {
        "criterion_id": "picture_quality",
        "criterion_description": "Evaluation of display quality...",
        "weight": 0.35,
        "score": 5.0,
        "reasoning": "Exceptional 8K resolution with advanced features...",
        "evidence": ["8K resolution", "Quantum Dot technology", "4000 nits brightness"],
        "recommendations": [],
        "confidence": 0.95
      }
    ],
    "summary": "This TV demonstrates exceptional performance...",
    "strengths": ["Outstanding picture quality", "Immersive audio"],
    "improvements": ["Could detail pricing", "More gaming performance info"],
    "agent_metadata": {
      "evaluation_model": "langchain-azure-openai",
      "chunks_analyzed": 3,
      "workflow": "batch_evaluation"
    }
  }
}
```

## Key Design Principles

### 1. **Clean Separation of Concerns**

- **Models**: Pure Pydantic data models
- **Services**: Business logic and LLM orchestration
- **Routes**: API endpoints and request handling
- **Database**: Data persistence layer
- **Prompts**: Template management

### 2. **Efficiency Optimizations**

- **Batch Evaluation**: All criteria evaluated in single LLM call
- **Smart Chunking**: Relevant document chunks per criterion
- **Caching**: Singleton services with dependency injection

### 3. **Maintainability**

- **Type Safety**: Full type hints throughout
- **Error Handling**: Graceful degradation with stub responses
- **Logging**: Comprehensive logging for debugging
- **Configuration**: Environment-based configuration

### 4. **Extensibility**

- **Pluggable Rubrics**: Easy to add new evaluation criteria
- **Flexible Scoring**: Customizable scoring criteria per rubric
- **Multiple Domains**: Support for any document type

## Dependencies

Core dependencies (already in existing pyproject.toml):

- `fastapi` - Web framework
- `pydantic` - Data validation
- `sqlite3` - Database (built-in)

Additional LangChain dependencies needed:

- `langchain-openai` - Azure OpenAI integration
- `langchain-core` - Core LangChain functionality

## Deployment

The service is Docker-ready and can be deployed alongside the existing agent service infrastructure.

## Future Enhancements

- **Custom Rubric Creation**: API endpoints for dynamic rubric management
- **Evaluation History**: Track evaluation results over time
- **Batch Document Processing**: Evaluate multiple documents simultaneously
- **Advanced Analytics**: Scoring trends and performance metrics
- **Integration**: Connect with document management systems
