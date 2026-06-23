from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Dict, Any
from app.services.document_parser import document_parser
from app.services.document_analyzer import document_analyzer

router = APIRouter()

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