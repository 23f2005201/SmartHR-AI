import os
from typing import Any, Optional
from langchain_ollama import OllamaLLM

# Import database session components and core models to build the RAG pipeline
from app.core.database import SessionLocal
from app.models.employee import Employee
from app.models.department import Department
from app.models.attendance import Attendance
from app.models.leave import LeaveRequest

class SmartHRAIAssistant:
    def __init__(self) -> None:
        self.model_name: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
        try:
            self.llm: Optional[OllamaLLM] = OllamaLLM(
                base_url="http://ollama-service:11434", 
                model=self.model_name,
                temperature=0.0  # 🎯 Force absolute factual accuracy, disable creativity
            )
        except Exception:
            self.llm = None

    def _gather_live_hrms_context(self) -> str:
        """Queries the local SQLite storage layer to assemble a real-time data context block."""
        db = SessionLocal()
        try:
            total_employees = db.query(Employee).count()
            total_departments = db.query(Department).count()

            from datetime import date
            clocked_in_today = db.query(Attendance).filter(
                Attendance.date == date.today(),
                Attendance.status == "Present"
            ).count()

            pending_leaves_count = db.query(LeaveRequest).filter(
                LeaveRequest.status == "Pending"
            ).count()

            context_summary = (
                f"WORKFORCE HEADCOUNT: {total_employees}\n"
                f"STAFF CLOCKED IN TODAY: {clocked_in_today}\n"
                f"PENDING LEAVES REQUESTS: {pending_leaves_count}"
            )
            return context_summary
        except Exception as e:
            return f"Context Error: {str(e)}"
        finally:
            db.close()

    def execute_hr_query(self, user_prompt: str, employee_context: Optional[dict[str, Any]] = None) -> str:
        """Processes text strings by boxing raw values directly into an un-bypassable instruction layout."""
        if not self.llm:
            return "AI Operational Exception: Local Ollama service agent unreachable."

        live_database_context = self._gather_live_hrms_context()
        
        # 🔍 Debug checkpoint: This prints straight into your docker container logs!
        print(f"\n[RAG DEBUG] Context Sent to LLM:\n{live_database_context}\n", flush=True)

        # 🚀 Aggressive instruction wrap that breaks through the model's internal guardrails
        flattened_prompt = (
            f"INSTRUCTION: You are a cold, precise data reporting terminal. "
            f"Read the variables below and answer the question using ONLY those numbers. "
            f"Do not mention your limitations. Do not say you cannot access data. "
            f"If the data says 3, say 3.\n\n"
            f"DATABASES STATE:\n"
            f"{live_database_context}\n\n"
            f"QUESTION: {user_prompt}\n\n"
            f"ANSWER:"
        )

        try:
            response = self.llm.invoke(flattened_prompt)
            return str(response).strip()
        except Exception as e:
            return f"Processing Error across LangChain workflow: {str(e)}"

hr_ai_assistant = SmartHRAIAssistant()