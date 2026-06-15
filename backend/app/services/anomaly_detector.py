from sqlalchemy.orm import Session
from app.models.payroll import PayrollRecord
from app.models.attendance import Attendance

class CorporateInsightsService:
    @staticmethod
    def inspect_payroll_variance(db: Session, employee_id: int, incoming_net: float) -> dict:
        """Flags out-of-bounds payroll deviations compared to historical payouts."""
        historical_records = db.query(PayrollRecord).filter(
            PayrollRecord.employee_id == employee_id
        ).order_by(PayrollRecord.id.desc()).limit(3).all()

        if not historical_records:
            return {"status": "Clear", "variance_percentage": 0.0, "reason": "No historical payment records on ledger; setting baseline profile."}

        avg_historical_net = sum([r.net_salary for r in historical_records]) / len(historical_records)
        
        if avg_historical_net == 0:
            return {"status": "Clear", "variance_percentage": 0.0, "reason": "Zero value baseline detected."}

        variance = (incoming_net - avg_historical_net) / avg_historical_net
        
        # Absolute threshold flag at 25% deviation
        if abs(variance) >= 0.25:
            return {
                "status": "Flagged Anomaly",
                "variance_percentage": round(variance * 100, 2),
                "reason": f"Payment bounds exceed historical base parameters by {round(variance * 100, 2)}%. Review manually."
            }

        return {
            "status": "Clear",
            "variance_percentage": round(variance * 100, 2),
            "reason": "Variance within safe industrial margin limits (+/- 25%)."
        }

    @staticmethod
    def process_productivity_insights(db: Session, employee_id: int) -> dict:
        """Calculates employee consistency ratings based on active attendance ratios."""
        total_days = db.query(Attendance).filter(Attendance.employee_id == employee_id).count()
        days_present = db.query(Attendance).filter(
            Attendance.employee_id == employee_id,
            Attendance.status == "Present"
        ).count()

        if total_days == 0:
            return {"score": 75.0, "velocity": "Baseline Stable", "insight": "Awaiting a broader tracking sample size."}

        attendance_ratio = days_present / total_days
        productivity_score = round(attendance_ratio * 100, 2)

        if productivity_score >= 90.0:
            velocity = "Exceptional Focus"
            insight = "Demonstrates top-tier task-attendance velocity. High organizational impact."
        elif productivity_score >= 75.0:
            velocity = "Consistent / Stable"
            insight = "Maintains steady workspace operations within baseline standards."
        else:
            velocity = "Declining Engagement"
            insight = "Attendance constraints flagged. Recommend conversational health review check."

        return {
            "score": productivity_score,
            "velocity": velocity,
            "insight": insight
        }