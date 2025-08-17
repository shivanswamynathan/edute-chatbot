from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from typing import List
import logging
from backend.config import Config 

logger = logging.getLogger(__name__)

class EmbeddingManager:
    def __init__(self):
        """Initialize with config values directly"""
        self.embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=Config.GEMINI_API_KEY,
            model=Config.EMBEDDING_MODEL
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def create_chunks(self, text: str, metadata: dict = None) -> List[Document]:
        """Split text into chunks and create Document objects"""
        try:
            chunks = self.text_splitter.split_text(text)
            documents = []
            
            for i, chunk in enumerate(chunks):
                doc_metadata = metadata.copy() if metadata else {}
                doc_metadata['chunk_id'] = i
                documents.append(Document(
                    page_content=chunk,
                    metadata=doc_metadata
                ))
            
            return documents
        except Exception as e:
            logger.error(f"Chunking error: {e}")
            return []
    
    async def embed_documents(self, documents: List[Document]) -> List[List[float]]:
        """Generate embeddings for documents"""
        try:
            texts = [doc.page_content for doc in documents]
            embeddings = await self.embeddings.aembed_documents(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            return []
    
    async def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query"""
        try:
            return await self.embeddings.aembed_query(query)
        except Exception as e:
            logger.error(f"Query embedding error: {e}")
            return []