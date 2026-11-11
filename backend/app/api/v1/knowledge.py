from fastapi import APIRouter, HTTPException
from backend.app.core.registry import kb_registry

router = APIRouter(prefix="/knowledge", tags=["Spec-Driven Knowledge Base"])

@router.get("/index")
def get_knowledge_index():
    """Returns the full indexed spec-driven knowledge base catalog."""
    index = kb_registry.get_index()
    return index

@router.get("/spec/{spec_id}")
def get_spec_detail(spec_id: str):
    """Returns full markdown content and structured parameters for a specification."""
    spec = kb_registry.get_spec(spec_id)
    if not spec:
        raise HTTPException(status_code=404, detail=f"Spec '{spec_id}' not found in knowledge base.")
    return spec
