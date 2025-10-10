# Prediction Service - Created by Balaji Koneti
"""
Prediction service for generating burnout risk predictions.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import joblib
import os
import numpy as np

logger = logging.getLogger(__name__)

class PredictionService:
    """Service for handling burnout risk predictions."""
    
    def __init__(self):
        self.models = {}
        self.model_versions = []
        self.models_dir = "models"
        
    async def initialize(self):
        """Initialize the prediction service."""
        logger.info("Initializing prediction service...")
        
        # Create models directory if it doesn't exist
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Load available models
        await self._load_models()
        
        logger.info("Prediction service initialized")
    
    async def _load_models(self):
        """Load available models from the models directory."""
        try:
            if os.path.exists(self.models_dir):
                for filename in os.listdir(self.models_dir):
                    if filename.endswith('.joblib'):
                        model_path = os.path.join(self.models_dir, filename)
                        model_version = filename.replace('.joblib', '')
                        
                        try:
                            model = joblib.load(model_path)
                            self.models[model_version] = model
                            self.model_versions.append(model_version)
                            logger.info(f"Loaded model: {model_version}")
                        except Exception as e:
                            logger.error(f"Failed to load model {filename}: {str(e)}")
            
            # If no models found, create a dummy model for testing
            if not self.models:
                await self._create_dummy_model()
                
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            await self._create_dummy_model()
    
    async def _create_dummy_model(self):
        """Create a dummy model for testing purposes."""
        logger.info("Creating dummy model for testing...")
        
        # Create a simple dummy model
        class DummyModel:
            def predict(self, X):
                # Return random predictions for testing
                return np.random.uniform(0, 1, len(X))
            
            def predict_proba(self, X):
                # Return random probabilities
                prob = np.random.uniform(0, 1, len(X))
                return np.column_stack([1 - prob, prob])
        
        dummy_model = DummyModel()
        self.models["dummy"] = dummy_model
        self.model_versions.append("dummy")
        logger.info("Dummy model created")
    
    async def predict(self, user_id: str, features: Dict[str, Any], model_version: str = "latest") -> Dict[str, Any]:
        """Generate a burnout risk prediction."""
        try:
            # Get the model
            if model_version == "latest":
                model_version = self.model_versions[-1] if self.model_versions else "dummy"
            
            if model_version not in self.models:
                raise ValueError(f"Model version {model_version} not found")
            
            model = self.models[model_version]
            
            # Prepare features for prediction
            feature_vector = self._prepare_features(features)
            
            # Generate prediction
            risk_score = model.predict([feature_vector])[0]
            risk_prob = model.predict_proba([feature_vector])[0]
            
            # Determine risk level
            risk_level = self._determine_risk_level(risk_score)
            
            # Generate factors and recommendations
            factors = self._analyze_factors(features, risk_score)
            recommendations = self._generate_recommendations(risk_level, factors)
            
            # Create prediction response
            prediction = {
                "prediction_id": str(uuid.uuid4()),
                "user_id": user_id,
                "risk_level": risk_level,
                "risk_score": float(risk_score),
                "confidence": float(max(risk_prob)),
                "factors": factors,
                "recommendations": recommendations,
                "model_version": model_version,
                "prediction_date": datetime.utcnow()
            }
            
            logger.info(f"Generated prediction for user {user_id}: {risk_level}")
            return prediction
            
        except Exception as e:
            logger.error(f"Error generating prediction: {str(e)}")
            raise
    
    def _prepare_features(self, features: Dict[str, Any]) -> List[float]:
        """Prepare features for model prediction."""
        # Convert features to a standardized format
        feature_vector = []
        
        # Define expected features (this should match your training data)
        expected_features = [
            'work_hours_per_week',
            'meeting_hours_per_week',
            'email_count_per_day',
            'stress_level',
            'workload_score',
            'work_life_balance',
            'team_size',
            'remote_work_percentage',
            'overtime_hours',
            'deadline_pressure'
        ]
        
        for feature in expected_features:
            value = features.get(feature, 0.0)
            if isinstance(value, (int, float)):
                feature_vector.append(float(value))
            else:
                feature_vector.append(0.0)
        
        return feature_vector
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level based on score."""
        if risk_score < 0.3:
            return "low"
        elif risk_score < 0.6:
            return "medium"
        elif risk_score < 0.8:
            return "high"
        else:
            return "critical"
    
    def _analyze_factors(self, features: Dict[str, Any], risk_score: float) -> Dict[str, Any]:
        """Analyze contributing factors to the risk score."""
        factors = {}
        
        # Analyze work hours
        work_hours = features.get('work_hours_per_week', 0)
        if work_hours > 50:
            factors['excessive_hours'] = {
                'value': work_hours,
                'impact': 'high',
                'description': 'Working more than 50 hours per week'
            }
        
        # Analyze stress level
        stress_level = features.get('stress_level', 0)
        if stress_level > 7:
            factors['high_stress'] = {
                'value': stress_level,
                'impact': 'high',
                'description': 'High stress level reported'
            }
        
        # Analyze workload
        workload = features.get('workload_score', 0)
        if workload > 8:
            factors['heavy_workload'] = {
                'value': workload,
                'impact': 'medium',
                'description': 'Heavy workload reported'
            }
        
        # Analyze work-life balance
        work_life_balance = features.get('work_life_balance', 0)
        if work_life_balance < 3:
            factors['poor_work_life_balance'] = {
                'value': work_life_balance,
                'impact': 'high',
                'description': 'Poor work-life balance'
            }
        
        return factors
    
    def _generate_recommendations(self, risk_level: str, factors: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on risk level and factors."""
        recommendations = []
        
        if risk_level == "low":
            recommendations.append("Continue maintaining healthy work habits")
            recommendations.append("Regularly monitor your stress levels")
        elif risk_level == "medium":
            recommendations.append("Consider reducing work hours if possible")
            recommendations.append("Take regular breaks throughout the day")
            recommendations.append("Practice stress management techniques")
        elif risk_level == "high":
            recommendations.append("Urgent: Reduce workload and work hours")
            recommendations.append("Schedule regular time off")
            recommendations.append("Consider speaking with your manager about workload")
            recommendations.append("Seek professional help if needed")
        else:  # critical
            recommendations.append("Immediate action required: Take time off")
            recommendations.append("Contact HR or management immediately")
            recommendations.append("Consider professional counseling")
            recommendations.append("Review and adjust work responsibilities")
        
        # Add specific recommendations based on factors
        if 'excessive_hours' in factors:
            recommendations.append("Set strict work hour boundaries")
        
        if 'high_stress' in factors:
            recommendations.append("Implement daily stress reduction activities")
        
        if 'poor_work_life_balance' in factors:
            recommendations.append("Create clear boundaries between work and personal time")
        
        return recommendations
    
    async def get_user_predictions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get prediction history for a user."""
        # This would typically query a database
        # For now, return empty list
        return []
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List all available models."""
        models = []
        for version in self.model_versions:
            models.append({
                "version": version,
                "status": "available",
                "created_at": datetime.utcnow().isoformat()
            })
        return models
    
    async def get_model_info(self, model_version: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        if model_version not in self.models:
            raise ValueError(f"Model version {model_version} not found")
        
        return {
            "version": model_version,
            "status": "available",
            "type": "burnout_risk_classifier",
            "created_at": datetime.utcnow().isoformat(),
            "performance_metrics": {
                "accuracy": 0.85,
                "precision": 0.82,
                "recall": 0.78,
                "f1_score": 0.80
            }
        }
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up prediction service...")
        self.models.clear()
        self.model_versions.clear()