import os
import logging
import numpy as np
import joblib
from typing import Dict, Any

logger = logging.getLogger("uvicorn.error")

class AnalyticsEngine:
    def __init__(self):
        # Resolve absolute paths to model binary vectors inside container structure
        self.model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
        self.attrition_model_path = os.path.join(self.model_dir, "attrition_pipeline.joblib")
        self.burnout_model_path = os.path.join(self.model_dir, "burnout_rf_model.joblib")
        
        self.attrition_model = self._load_model_asset(self.attrition_model_path)
        self.burnout_model = self._load_model_asset(self.burnout_model_path)

    def _load_model_asset(self, path: str) -> Any:
        """Safely reads serialized joblib weights on startup with fallback validation flags."""
        if os.path.exists(path):
            try:
                logger.info(f"🧠 SmartHR AI loading model binary from: {path}")
                return joblib.load(path)
            except Exception as e:
                logger.error(f"❌ Failed to parse model at {path}: {str(e)}")
        else:
            logger.warning(f"⚠️ Model weight file missing at {path}. Operating in mock fallback mode.")
        return None

    def predict_employee_attrition(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates real probability scores utilizing the loaded Scikit-Learn pipeline matrix.
        Input signature expects: years_at_company, monthly_salary, weekly_overtime_hours, satisfaction_score
        """
        if not self.attrition_model:
            # Fallback mock calculations if pipeline assets are compiling or missing
            prob = 71.62 if data.get("weekly_overtime_hours", 0) > 10 else 23.41
            risk = "High" if prob > 50 else "Low"
            return {
                "attrition_risk": risk,
                "risk_probability": prob,
                "recommendation": "Mock Fallback: Review scheduling constraints and satisfaction parameters immediately."
            }

        try:
            # Extract features in the precise array dimensions expected by your pipeline scalar
            features = np.array([[
                float(data.get("years_at_company", 0.0)),
                float(data.get("monthly_salary", 0.0)),
                float(data.get("weekly_overtime_hours", 0.0)),
                float(data.get("satisfaction_score", 3.0))
            ]])

            # Evaluate probability profiles using Scikit-Learn API hooks
            prob_matrix = self.attrition_model.predict_proba(features)[0]
            risk_probability = round(float(prob_matrix[1]) * 100, 2)
            attrition_risk = "High" if risk_probability > 50.0 else "Low"
            
            recommendation = (
                "High turnover signature flagged. Schedule an active check-in and re-evaluate compensation balance."
                if attrition_risk == "High" else "Retention profile stable. Maintain current engagement benchmarks."
            )

            return {
                "attrition_risk": attrition_risk,
                "risk_probability": risk_probability,
                "recommendation": recommendation
            }
        except Exception as e:
            logger.error(f"Prediction engine computational failure: {str(e)}")
            return {"error": "Internal inference calculations failed."}

    def analyze_leave_sequence_burnout(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates current requested time configurations against historic sick parameters.
        Input signature expects: sick_leaves_taken, casual_leaves_taken, consecutive_days_requested
        """
        if not self.burnout_model:
            # Fallback mock configuration metrics
            score = 84.50 if data.get("consecutive_days_requested", 0) >= 5 else 12.30
            return {
                "classification": "Anomalous Burnout Risk Profile" if score > 50 else "Standard Leave Metric",
                "irregular_pattern_detected": score > 50,
                "pattern_anomaly_score": score
            }

        try:
            features = np.array([[
                int(data.get("sick_leaves_taken", 0)),
                int(data.get("casual_leaves_taken", 0)),
                int(data.get("consecutive_days_requested", 0))
            ]])

            anomaly_score = round(float(self.burnout_model.predict_proba(features)[0][1]) * 100, 2)
            irregular_pattern = anomaly_score > 60.0
            classification = "Anomalous Multi-Request Metric" if irregular_pattern else "Standard Internal Log Deviation"

            return {
                "classification": classification,
                "irregular_pattern_detected": irregular_pattern,
                "pattern_anomaly_score": anomaly_score
            }
        except Exception as e:
            logger.error(f"RandomForest computational matrix exception: {str(e)}")
            return {"error": "Internal leave evaluation sequence failed."}

# Singleton instantiation layout instance
analytics_engine = AnalyticsEngine()