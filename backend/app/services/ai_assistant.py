import os
from typing import Any, Optional
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class SmartHRAIAssistant:
    def __init__(self) -> None:
        self.model_name: str = os.getenv("OLLAMA_MODEL", "llama3")
        try:
            self.llm: Optional[OllamaLLM] = OllamaLLM(
                base_url="http://ollama-service:11434", 
                model=self.model_name
            )
        except Exception:
            self.llm = None

    def execute_hr_query(self, user_prompt: str, employee_context: Optional[dict[str, Any]] = None) -> str:
        """Processes continuous conversational text strings within an HR domain scope."""
        sys_context = (
            "You are an embedded enterprise SmartHR AI executive copilot. "
            "Provide clear, actionable, professional answers regarding company tracking, "
            "payroll, or attendance. Be concise and maintain data privacy standards."
        )
        
        if employee_context:
            sys_context += f" Current Context: Profile under evaluation represents Employee ID #{employee_context.get('id')}."

        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="System Guidelines: {context}\n\nUser Inquiry: {question}\n\nAssistant Response:"
        )

        if not self.llm:
            return "AI Operational Exception: Local Ollama service agent unreachable. Ensure system service port 11434 is running."

        try:
            runnable_chain = prompt_template | self.llm | StrOutputParser()
            response = runnable_chain.invoke({"context": sys_context, "question": user_prompt})
            return str(response).strip()
        except Exception as e:
            return f"Processing Error across LangChain workflow: {str(e)}"

hr_ai_assistant = SmartHRAIAssistant()