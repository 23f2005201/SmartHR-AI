import logging
import os
from datetime import date
from typing import Any, Optional, cast

logger = logging.getLogger("uvicorn.error")


class SmartHRAIAssistant:
    def __init__(self) -> None:
        self.model_name: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
        self.base_url: str = os.getenv(
            "OLLAMA_BASE_URL",
            "http://ollama-service:11434",
        )
        self.llm: Any = None
        self._initialize_llm()

    def _initialize_llm(self) -> None:
        """
        Safely initialize Ollama LLM with full error isolation.
        """

        try:
            # Deferred import to avoid hard failure if package is unavailable
            from langchain_ollama import OllamaLLM

            self.llm = OllamaLLM(
                base_url=self.base_url,
                model=self.model_name,
                temperature=0.0,
                client_kwargs={"timeout": 120},
            )

            logger.info(
                f"✅ Ollama LLM initialized: {self.model_name} @ {self.base_url}"
            )

        except ImportError:
            logger.error(
                "❌ langchain-ollama not installed. "
                "Run: pip install langchain-ollama"
            )
            self.llm = None

        except TypeError as e:
            logger.warning(
                f"⚠️ OllamaLLM timeout/client_kwargs not supported: {str(e)}. "
                "Retrying without timeout."
            )

            try:
                from langchain_ollama import OllamaLLM

                self.llm = OllamaLLM(
                    base_url=self.base_url,
                    model=self.model_name,
                    temperature=0.0,
                )

                logger.info(
                    f"✅ Ollama LLM initialized without timeout: "
                    f"{self.model_name} @ {self.base_url}"
                )

            except Exception as retry_error:
                logger.error(f"❌ Ollama retry init failed: {str(retry_error)}")
                self.llm = None

        except Exception as e:
            logger.error(f"❌ Ollama init failed: {str(e)}")
            self.llm = None

    def _gather_live_hrms_context(self) -> str:
        """
        Queries the database to build a real-time context block.
        Always returns a string, never raises.
        """

        try:
            from app.core.database import SessionLocal
            from app.models.attendance import Attendance
            from app.models.department import Department
            from app.models.employee import Employee
            from app.models.leave import LeaveRequest

            db = SessionLocal()

            try:
                total_employees = db.query(Employee).count()
                total_departments = db.query(Department).count()

                attendance_date = cast(Any, Attendance.date)

                clocked_in_today = (
                    db.query(Attendance)
                    .filter(
                        attendance_date == date.today(),
                        Attendance.status == "Present",
                    )
                    .count()
                )

                pending_leaves = (
                    db.query(LeaveRequest)
                    .filter(LeaveRequest.status == "Pending")
                    .count()
                )

                return (
                    f"TOTAL_EMPLOYEES: {total_employees}\n"
                    f"TOTAL_DEPARTMENTS: {total_departments}\n"
                    f"CLOCKED_IN_TODAY: {clocked_in_today}\n"
                    f"PENDING_LEAVE_REQUESTS: {pending_leaves}"
                )

            finally:
                db.close()

        except Exception as e:
            logger.warning(f"⚠️ Context gather failed: {str(e)}")
            return "CONTEXT_STATUS: Database temporarily unavailable"

    def execute_hr_query(
        self,
        user_prompt: str,
        employee_context: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Execute a natural language HR query with live DB context injection.
        Returns empty string on failure.
        """

        if not self.llm:
            self._initialize_llm()

        if not self.llm:
            return (
                "AI Service Unavailable: "
                "Ollama is unreachable. Please check the service."
            )

        live_context = self._gather_live_hrms_context()

        employee_block = ""
        if employee_context:
            employee_block = f"\nEMPLOYEE_CONTEXT: {employee_context}\n"

        prompt = (
            "SYSTEM: You are a precise SmartHR AI reporting terminal.\n"
            "Use ONLY the live database values below to answer.\n"
            "Never claim you cannot access data - the data is provided below.\n"
            "Be concise, professional, and specific.\n\n"
            "LIVE DATABASE STATE:\n"
            f"{live_context}"
            f"{employee_block}\n\n"
            f"REQUEST: {user_prompt}\n\n"
            "RESPONSE:"
        )

        try:
            response = self.llm.invoke(prompt)
            result = str(response).strip()
            logger.info(f"✅ LLM response: {len(result)} chars")
            return result

        except Exception as e:
            logger.error(f"❌ LLM invoke failed: {str(e)}")
            return ""

    def execute_agent_planning(
        self,
        system_prompt: str,
        user_query: str,
        employee_context: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Dedicated agent planning phase.
        Returns raw LLM output containing JSON tool call objects.
        """

        if not self.llm:
            self._initialize_llm()

        if not self.llm:
            return ""

        live_context = self._gather_live_hrms_context()

        employee_block = (
            f"\nEMPLOYEE_CONTEXT: {employee_context}" if employee_context else ""
        )

        planning_prompt = (
            f"{system_prompt}\n\n"
            "LIVE DATABASE STATE:\n"
            f"{live_context}"
            f"{employee_block}\n\n"
            f"USER QUERY: {user_query}\n\n"
            "OUTPUT ONLY THE REQUIRED JSON TOOL CALL OBJECTS. "
            "NO EXPLANATION. NO EXTRA TEXT. JUST JSON:"
        )

        try:
            response = self.llm.invoke(planning_prompt)
            result = str(response).strip()
            logger.info(f"📋 Agent plan raw output:\n{result[:300]}")
            return result

        except Exception as e:
            logger.error(f"❌ Agent planning failed: {str(e)}")
            return ""


# Singleton instance
hr_ai_assistant = SmartHRAIAssistant()