from fastapi import APIRouter, UploadFile, File, HTTPException
from PyPDF2 import PdfReader
import hashlib
import os
import logging
from backend.models.schemas import UploadResponse
from backend.config import Config

logger = logging.getLogger(__name__)

router = APIRouter()

# This would normally be injected via dependency injection
vector_store = None
embedding_manager = None

def set_dependencies(vs, em):
    global vector_store, embedding_manager
    vector_store = vs
    embedding_manager = em

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a PDF file"""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Generate file ID
        content = await file.read()
        file_id = hashlib.md5(content).hexdigest()[:10]
        
        # Save file
        file_path = os.path.join(Config.UPLOAD_DIR, f"{file_id}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Extract text from PDF
        text = extract_text_from_pdf(content)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Create chunks
        metadata = {
            "source": file.filename,
            "file_id": file_id,
            "file_path": file_path
        }
        
        documents = embedding_manager.create_chunks(text, metadata)
        
        # Add to vector store
        success = vector_store.add_documents(documents)
        
        if success:
            return UploadResponse(
                success=True,
                message="File uploaded and processed successfully",
                file_id=file_id,
                chunks_created=len(documents)
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to process file")
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF content"""
    try:
        from io import BytesIO
        pdf_file = BytesIO(content)
        reader = PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return ""