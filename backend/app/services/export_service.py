import csv
import io
from typing import List, Dict, Any
from datetime import datetime

class ExportService:
    @staticmethod
    def generate_attrition_csv(predictions: List[Dict[str, Any]]) -> io.StringIO:
        """Compiles machine learning pipeline predictions into a clean CSV memory stream."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write enterprise data headers
        writer.writerow([
            "Export Timestamp", 
            "Employee ID", 
            "Department ID", 
            "Attrition Risk Probability", 
            "Risk Assessment Profile State"
        ])
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for record in predictions:
            prob = record.get("probability", 0.0)
            risk_state = "High Risk Profile" if prob > 0.5 else "Stable Retention Profile"
            
            writer.writerow([
                timestamp,
                record.get("employee_id", "N/A"),
                record.get("department_id", "N/A"),
                f"{prob * 100:.2f}%",
                risk_state
            ])
            
        output.seek(0)
        return output

export_service = ExportService()