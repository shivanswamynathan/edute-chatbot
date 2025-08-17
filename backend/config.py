import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Model Settings
    GEMINI_MODEL: str = "gemini-2.0-flash"
    EMBEDDING_MODEL: str = "models/embedding-001"
    
    # Storage Paths
    UPLOAD_DIR: str = "data/uploads"
    EMBEDDINGS_DIR: str = "data/embeddings"
    VECTOR_STORE_PATH: str = "data/embeddings/faiss_index"
    
    # Chunking Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Retrieval Settings
    TOP_K_DOCS: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    @classmethod
    def validate_config(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        
        # Create directories
        os.makedirs(cls.UPLOAD_DIR, exist_ok=True)
        os.makedirs(cls.EMBEDDINGS_DIR, exist_ok=True)