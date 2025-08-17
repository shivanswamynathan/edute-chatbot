from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from typing import List, Tuple, Optional
import os
import pickle
import logging
from backend.config import Config

logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self):
        """Initialize with config values directly"""
        self.store_path = Config.VECTOR_STORE_PATH
        self.embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=Config.GEMINI_API_KEY,
            model=Config.EMBEDDING_MODEL
        )
        self.vector_store: Optional[FAISS] = None
        self.load_or_create_store()
    
    def load_or_create_store(self):
        """Load existing vector store or create new one"""
        try:
            if os.path.exists(f"{self.store_path}.pkl"):
                self.vector_store = FAISS.load_local(
                    self.store_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("Loaded existing vector store")
            else:
                # Create empty store
                dummy_doc = Document(page_content="dummy", metadata={"source": "init"})
                self.vector_store = FAISS.from_documents([dummy_doc], self.embeddings)
                logger.info("Created new vector store")
        except Exception as e:
            logger.error(f"Vector store initialization error: {e}")
            dummy_doc = Document(page_content="dummy", metadata={"source": "init"})
            self.vector_store = FAISS.from_documents([dummy_doc], self.embeddings)
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to vector store"""
        try:
            if not documents:
                return False
            
            self.vector_store.add_documents(documents)
            self.save_store()
            logger.info(f"Added {len(documents)} documents to vector store")
            return True
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False
    
    def similarity_search(
        self, 
        query: str, 
        k: int = None,  # Use config default if not provided
        filter_dict: Optional[dict] = None
    ) -> List[Tuple[Document, float]]:
        """Search for similar documents"""
        if k is None:
            k = Config.TOP_K_DOCS  # Use config value
            
        try:
            if filter_dict:
                # FAISS doesn't support metadata filtering directly
                # We'll implement post-filtering
                results = self.vector_store.similarity_search_with_score(query, k=k*2)
                filtered_results = []
                
                for doc, score in results:
                    if self._matches_filter(doc.metadata, filter_dict):
                        filtered_results.append((doc, score))
                        if len(filtered_results) >= k:
                            break
                
                return filtered_results[:k]
            else:
                return self.vector_store.similarity_search_with_score(query, k=k)
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def _matches_filter(self, metadata: dict, filter_dict: dict) -> bool:
        """Check if document metadata matches filter criteria"""
        for key, value in filter_dict.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True
    
    def save_store(self):
        """Save vector store to disk"""
        try:
            os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
            self.vector_store.save_local(self.store_path)
            logger.info("Vector store saved successfully")
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")