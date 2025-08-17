from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

from backend.config import Config
from backend.core.llm import GeminiLLMWrapper
from backend.core.embeddings import EmbeddingManager
from backend.core.vectorstore import VectorStoreManager
from backend.core.agents import TeacherAgent, QuizAgent, RevisionAgent
from backend.core.langgraph import EdTechWorkflow
from backend.api import upload, chat

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global components
llm_wrapper = None
embedding_manager = None
vector_store = None
workflow = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize components on startup"""
    global llm_wrapper, embedding_manager, vector_store, workflow
    
    try:
        # Validate configuration
        Config.validate_config()
        
        # Initialize components - NO MORE PARAMETER PASSING!
        llm_wrapper = GeminiLLMWrapper()  # ← Clean!
        embedding_manager = EmbeddingManager()  # ← Clean!
        vector_store = VectorStoreManager()  # ← Clean!
        
        # Initialize agents
        teacher_agent = TeacherAgent(llm_wrapper)
        quiz_agent = QuizAgent(llm_wrapper)
        revision_agent = RevisionAgent(llm_wrapper)
        
        # Initialize workflow
        workflow = EdTechWorkflow(teacher_agent, quiz_agent, revision_agent, vector_store)
        
        # Set dependencies for routers
        upload.set_dependencies(vector_store, embedding_manager)
        chat.set_workflow(workflow)
        
        logger.info("Application initialized successfully")
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise e
    
    yield
    
    # Cleanup on shutdown
    logger.info("Application shutting down")

# Create FastAPI app
app = FastAPI(
    title="RAG EdTech Chatbot API",
    description="Educational chatbot with RAG capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "RAG EdTech Chatbot API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=True
    )