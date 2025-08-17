from fastapi import APIRouter, HTTPException
from backend.models.schemas import ChatRequest, ChatResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependencies - would normally be injected
workflow = None

def set_workflow(wf):
    global workflow
    workflow = wf

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat requests"""
    
    if not workflow:
        raise HTTPException(status_code=500, detail="Workflow not initialized")
    
    try:
        # Process query through workflow
        result = await workflow.process_query(
            query=request.query,
            mode=request.mode,
            student_id=request.student_id,
            file_ids=request.file_ids
        )
        
        # Format sources for response
        sources = [
            {"source": source, "relevance": 0.8} 
            for source in result.get("sources", [])
        ]
        
        return ChatResponse(
            response=result.get("content", "No response generated"),
            sources=sources,
            mode=request.mode,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")