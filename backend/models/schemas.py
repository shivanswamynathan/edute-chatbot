from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class UploadResponse(BaseModel):
    success: bool
    message: str
    file_id: Optional[str] = None
    chunks_created: Optional[int] = None

class ChatRequest(BaseModel):
    query: str
    student_id: str
    mode: str = "learn"  # learn, revision, quiz
    file_ids: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    mode: str
    timestamp: datetime

class AgentResponse(BaseModel):
    content: str
    agent_type: str
    confidence: float
    sources: List[str]