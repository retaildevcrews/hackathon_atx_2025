from __future__ import annotations

from fastapi import APIRouter, Depends

from models.invoke import InvokeRequest, InvokeResponse
from services.search_service import get_search_service, AzureSearchService
from services.chain_service import get_chain_service, ChainService
from config import get_settings

router = APIRouter()


@router.post("/invoke", response_model=InvokeResponse)
async def invoke(
    req: InvokeRequest,
    chain: ChainService = Depends(get_chain_service),
    search: AzureSearchService = Depends(get_search_service),
) -> InvokeResponse:  # noqa: D401
    output = chain.run(req.prompt)
    settings = get_settings()
    # ChainService sets llm None if stubbed
    stub = chain.llm is None
    results = await search.search(req.prompt, top=1)
    if results:
        first = results[0]
        snippet = first.get("content")
        output = f"{output}\n\n[search snippet]\n{snippet}" if snippet else output
    return InvokeResponse(output=output, model=settings.azure_openai_deployment, stub=stub)
