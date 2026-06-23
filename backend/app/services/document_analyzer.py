import os
import json
from typing import Dict, Any
from app.services.ai_assistant import hr_ai_assistant

class DocumentAnalyzerService:
    @staticmethod
    def analyze_leave_slip(raw_text: str) -> Dict[str, Any]:
        """Leverages the local LLM to extract structured leave attributes from raw document text."""
        if not raw_text:
            return {"error": "No textual data provided for parsing analysis."}

        if not hr_ai_assistant.llm:
            return {"error": "Inference service engine currently offline."}

        # Clean raw multi-line strings avoiding breaking token variables
        prompt = (
            "INSTRUCTION: You are a strict data formatting compiler.\n"
            "Analyze the raw medical/leave slip text below and extract target variables.\n"
            "Respond with a valid raw JSON object ONLY. Do not write an introduction or markdown code blocks.\n\n"
            "JSON SCHEMA FORMAT TO EXPECT:\n"
            '{"employee_name": "string or null", "leave_type": "Sick Leave/Casual Leave", "start_date": "YYYY-MM-DD or null", "end_date": "YYYY-MM-DD or null", "medical_reason": "string summary or null"}\n\n'
            f"RAW DOCUMENT CONTENT TEXT:\n{raw_text}\n\n"
            "JSON COMPILER RESPONSE:"
        )

        try:
            response_str = hr_ai_assistant.llm.invoke(prompt).strip()
            
            if response_str.startswith("```"):
                response_str = response_str.split("```")[1]
                if response_str.startswith("json"):
                    response_str = response_str[4:]
            
            return dict(json.loads(response_str.strip()))
        except Exception as e:
            return {
                "error": f"Failed to compute structured metadata parsing: {str(e)}",
                "fallback_text_preview": raw_text[:200]
            }

    @staticmethod
    def analyze_resume(raw_text: str) -> Dict[str, Any]:
        """Extracts standard employee profile fields from a resume draft."""
        if not raw_text:
            return {"error": "No resume text content found."}

        if not hr_ai_assistant.llm:
            return {"error": "Inference service engine currently offline."}

        prompt = (
            "INSTRUCTION: Read the resume text and format details into JSON format fields only.\n"
            "Respond with a valid raw JSON object ONLY. No prose.\n\n"
            "SCHEMA FORMAT:\n"
            '{"first_name": "string", "last_name": "string", "email": "string", "skills": ["skill1", "skill2"], "suggested_salary": 0.0}\n\n'
            f"RESUME CONTENTS:\n{raw_text}\n\n"
            "JSON COMPILER RESPONSE:"
        )
        try:
            response_str = hr_ai_assistant.llm.invoke(prompt).strip()
            if response_str.startswith("```"):
                response_str = response_str.split("```")[1]
                if response_str.startswith("json"):
                    response_str = response_str[4:]
            return dict(json.loads(response_str.strip()))
        except Exception as e:
            return {"error": f"Failed to compile profile metrics: {str(e)}"}

document_analyzer = DocumentAnalyzerService()