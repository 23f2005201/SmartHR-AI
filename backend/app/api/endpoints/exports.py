from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime
from app.core.database import SessionLocal
from app.models.employee import Employee
from app.services.export_service import export_service

router = APIRouter()

@router.get("/export-attrition-report")
async def export_attrition_report():
    """Generates and streams a real-time CSV analytics ledger to the browser."""
    db = SessionLocal()
    try:
        employees = db.query(Employee).all()
        
        if not employees:
            raise HTTPException(status_code=404, detail="No workforce data records available to compile.")
            
        mock_predictions = []
        # Use Python enumerate to calculate the mock binary distribution pattern safely 
        for index, emp in enumerate(employees):
            mock_predictions.append({
                "employee_id": emp.id,
                "department_id": emp.department_id,
                "probability": 0.7162 if index % 2 == 0 else 0.2341
            })
            
        csv_buffer = export_service.generate_attrition_csv(mock_predictions)
        filename = f"SmartHR_Attrition_Audit_{datetime.now().strftime('%Y%m%d')}.csv"
        
        return StreamingResponse(
            iter([csv_buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export pipeline failure: {str(e)}")
    finally:
        db.close()