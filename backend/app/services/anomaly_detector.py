from typing import Any, cast

from sqlalchemy.orm import Session

from app.models.payroll import PayrollRecord
from app.models.attendance import Attendance


class CorporateInsightsService:
    @staticmethod
    def inspect_payroll_variance(
        db: Session,
        employee_id: int,
        incoming_net: float,
    ) -> dict[str, Any]:
        historical_records = (
            db.query(PayrollRecord)
            .filter(PayrollRecord.employee_id == employee_id)
            .order_by(PayrollRecord.id.desc())
            .limit(3)
            .all()
        )

        if not historical_records:
            return {
                "status": "Clear",
                "variance_percentage": 0.0,
                "reason": "No historical payment records on ledger; setting baseline profile.",
            }

        historical_net_values: list[float] = []

        for record in historical_records:
            net_salary = cast(Any, record.net_salary)
            historical_net_values.append(float(net_salary or 0.0))

        avg_historical_net: float = sum(historical_net_values) / len(historical_net_values)

        if avg_historical_net == 0:
            return {
                "status": "Clear",
                "variance_percentage": 0.0,
                "reason": "Zero value baseline detected.",
            }

        variance: float = (incoming_net - avg_historical_net) / avg_historical_net
        variance_percentage: float = round(variance * 100, 2)

        if abs(variance) >= 0.25:
            return {
                "status": "Flagged Anomaly",
                "variance_percentage": variance_percentage,
                "reason": (
                    f"Payment bounds exceed historical base parameters by "
                    f"{variance_percentage}%. Review manually."
                ),
            }

        return {
            "status": "Clear",
            "variance_percentage": variance_percentage,
            "reason": "Variance within safe industrial margin limits (+/- 25%).",
        }

    @staticmethod
    def process_productivity_insights(
        db: Session,
        employee_id: int,
    ) -> dict[str, Any]:
        total_days = (
            db.query(Attendance)
            .filter(Attendance.employee_id == employee_id)
            .count()
        )

        days_present = (
            db.query(Attendance)
            .filter(
                Attendance.employee_id == employee_id,
                Attendance.status == "Present",
            )
            .count()
        )

        if total_days == 0:
            return {
                "score": 75.0,
                "velocity": "Baseline Stable",
                "insight": "Awaiting a broader tracking sample size.",
            }

        attendance_ratio: float = days_present / total_days
        productivity_score: float = round(attendance_ratio * 100, 2)

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
            "insight": insight,
        }