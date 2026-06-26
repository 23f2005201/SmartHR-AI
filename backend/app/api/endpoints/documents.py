from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from typing import Dict, Any
import logging

from app.services.document_parser import document_parser
from app.services.document_analyzer import document_analyzer
from app.services.rag_service import rag_knowledge_service
from app.app import RoleChecker

logger = logging.getLogger("uvicorn.error")
router = APIRouter()
allow_hr_admin = RoleChecker(["Admin", "HR"])

# --- 📥 1. NEW RAG POLICY/HANDBOOK INGESTION ENDPOINT ---
@router.post("/upload-policy", response_model=Dict[str, Any])
async def upload_corporate_policy(
    file: UploadFile = File(...),
    current_user = Depends(allow_hr_admin)  # Guarded: Only HR/Admin can upload global policies
):
    """
    Accepts corporate handbooks, policy sheets, or codes of conduct,
    extracts structural text blocks, and registers them into the RAG vector search matrix.
    """
    filename = file.filename or "policy.pdf"
    if not (filename.endswith(".pdf") or filename.endswith(".docx") or filename.endswith(".txt")):
        raise HTTPException(
            status_code=400, 
            detail="Invalid format. Only PDF, DOCX, and TXT formats are accepted for RAG ingestion."
        )
        
    try:
        file_bytes = await file.read()
        
        # Leverage your existing document_parser cleanly!
        if filename.endswith(".txt"):
            extracted_text = file_bytes.decode("utf-8", errors="ignore")
        else:
            extracted_text = document_parser.extract_text(file_bytes, filename)
            
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="Document contains no parseable text blocks.")
            
        # Push into our in-memory vector index mesh
        rag_knowledge_service.ingest_document_text(filename, extracted_text)
        
        return {
            "status": "success",
            "filename": filename,
            "message": "Document intelligence RAG pipeline mapped and registered successfully."
        }
    except Exception as e:
        logger.error(f"❌ Document RAG ingestion pipeline failure: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal RAG pipeline error: {str(e)}")


# --- 📝 2. YOUR ORIGINAL LEAVE SLIP ANALYZER ---
@router.post("/parse-leave-slip", response_model=Dict[str, Any])
async def parse_leave_slip(file: UploadFile = File(...)):
    """Upload point for analyzing leave certificates and medical documents on the fly."""
    filename = file.filename or "document.pdf"
    if not (filename.endswith(".pdf") or filename.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Invalid format. Only PDF and DOCX formats accepted.")
    
    try:
        file_bytes = await file.read()
        extracted_text = document_parser.extract_text(file_bytes, filename)
        parsed_json = document_analyzer.analyze_leave_slip(extracted_text)
        return parsed_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal document pipeline disruption: {str(e)}")


# --- 📄 3. YOUR ORIGINAL RESUME PARSER ---
@router.post("/parse-resume", response_model=Dict[str, Any])
async def parse_resume(file: UploadFile = File(...)):
    """Parses application resumes to expedite onboarding workflow creation."""
    filename = file.filename or "resume.pdf"
    if not (filename.endswith(".pdf") or filename.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Invalid format. Only PDF and DOCX formats accepted.")
        
    try:
        file_bytes = await file.read()
        extracted_text = document_parser.extract_text(file_bytes, filename)
        parsed_json = document_analyzer.analyze_resume(extracted_text)
        return parsed_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal parser processing crash: {str(e)}")