import numpy as np
import os
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
ATTRITION_PATH = os.path.join(MODEL_DIR, "attrition_model.pkl")
LEAVE_PATH = os.path.join(MODEL_DIR, "leave_pattern_model.pkl")

class AIAnalyticsService:
    def __init__(self):
        self.initialize_models()

    def initialize_models(self):
        """Trains dummy models automatically on startup if pkl files are missing."""
        if not os.path.exists(ATTRITION_PATH):
            print("AI Engine: Training baseline Attrition Prediction model...")
            # Features: [years_at_company, monthly_salary_in_thousands, over_time_hours_weekly, satisfaction_score_1_to_5]
            X_train = np.array([
                [1, 30, 0, 5], [5, 45, 10, 2], [2, 80, 2, 4], [8, 35, 15, 1],
                [3, 50, 0, 4], [4, 40, 12, 2], [1, 25, 4, 3], [7, 120, 8, 5]
            ])
            y_train = np.array([0, 1, 0, 1, 0, 1, 0, 0]) # 1 = Risk of Leaving
            
            pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('classifier', LogisticRegression(random_state=42))
            ])
            pipeline.fit(X_train, y_train)
            with open(ATTRITION_PATH, 'wb') as f:
                pickle.dump(pipeline, f)

        if not os.path.exists(LEAVE_PATH):
            print("AI Engine: Training baseline Leave Pattern model...")
            # Features: [sick_leaves_taken, casual_leaves_taken, consecutive_days_requested]
            X_train = np.array([
                [0, 1, 1], [4, 0, 3], [1, 2, 1], [5, 1, 4],
                [0, 0, 1], [6, 2, 5], [2, 1, 2], [8, 0, 4]
            ])
            y_train = np.array([0, 1, 0, 1, 0, 1, 0, 1]) # 1 = Anomalous/High-Risk Pattern
            
            pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('classifier', RandomForestClassifier(n_estimators=10, random_state=42))
            ])
            pipeline.fit(X_train, y_train)
            with open(LEAVE_PATH, 'wb') as f:
                pickle.dump(pipeline, f)

    def predict_attrition(self, tenure: float, salary: float, overtime: float, satisfaction: float) -> dict:
        """Evaluates the structural probability of employee attrition risk."""
        with open(ATTRITION_PATH, 'rb') as f:
            model = pickle.load(f)
        
        salary_k = salary / 1000.0
        features = np.array([[tenure, salary_k, overtime, satisfaction]])
        prediction = int(model.predict(features)[0])
        probability = float(model.predict_proba(features)[0][1])

        return {
            "attrition_risk": "High" if prediction == 1 or probability > 0.5 else "Low",
            "risk_probability": round(probability * 100, 2),
            "recommendation": "Initiate pulse check review. Overtime load reduction advised." if probability > 0.5 else "Retention score within optimal profile boundaries."
        }

    def analyze_leave_pattern(self, sick: int, casual: int, consecutive: int) -> dict:
        """Determines if a forward leave application indicates a burnout profile."""
        with open(LEAVE_PATH, 'rb') as f:
            model = pickle.load(f)
        
        features = np.array([[sick, casual, consecutive]])
        prediction = int(model.predict(features)[0])
        probability = float(model.predict_proba(features)[0][1])

        return {
            "irregular_pattern_detected": True if prediction == 1 else False,
            "pattern_anomaly_score": round(probability * 100, 2),
            "classification": "Burnout Indicator / Concentrated Pattern Flagged" if prediction == 1 else "Standard Routine Allocation Parameters"
        }

ai_analytics_service = AIAnalyticsService()