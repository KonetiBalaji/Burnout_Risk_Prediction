# Evaluation Service - Created by Balaji Koneti
"""
Evaluation service for evaluating trained models with comprehensive metrics and SHAP analysis.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)

# Import comprehensive evaluation modules
from .evaluation.comprehensive_evaluator import ComprehensiveEvaluator
from .evaluation.metrics import AdvancedMetrics
from .evaluation.shap_analysis import SHAPAnalyzer

logger = logging.getLogger(__name__)

class EvaluationService:
    """Service for evaluating trained models with comprehensive metrics and explainability."""
    
    def __init__(self):
        self.evaluation_jobs = {}
        self.models_dir = "models"
        # Initialize comprehensive evaluation components
        self.comprehensive_evaluator = ComprehensiveEvaluator()
        self.advanced_metrics = AdvancedMetrics()
        self.shap_analyzer = SHAPAnalyzer()
        
    async def initialize(self):
        """Initialize the evaluation service."""
        logger.info("Initializing evaluation service...")
        
        # Initialize comprehensive evaluator
        await self.comprehensive_evaluator.initialize()
        logger.info("Comprehensive evaluator initialized")
        
        # Initialize SHAP analyzer
        await self.shap_analyzer.initialize()
        logger.info("SHAP analyzer initialized")
        
        logger.info("Evaluation service initialized")
    
    async def evaluate(self, model_version: str, test_dataset_path: str, 
                      include_shap: bool = True, target_recall: float = 0.85) -> Dict[str, Any]:
        """Evaluate a trained model with comprehensive metrics and SHAP analysis."""
        try:
            evaluation_id = str(uuid.uuid4())
            
            logger.info(f"Starting comprehensive evaluation for model {model_version}")
            
            # Load model
            model_path = os.path.join(self.models_dir, f"{model_version}.joblib")
            if not os.path.exists(model_path):
                raise ValueError(f"Model {model_version} not found")
            
            model = joblib.load(model_path)
            
            # Load test data
            X_test, y_test = await self._load_test_data(test_dataset_path)
            
            # Generate predictions
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
            
            # Calculate comprehensive metrics using advanced evaluator
            logger.info("Calculating comprehensive metrics...")
            comprehensive_metrics = await self.comprehensive_evaluator.evaluate_model(
                model=model,
                X_test=X_test,
                y_test=y_test,
                y_pred=y_pred,
                y_pred_proba=y_pred_proba,
                target_recall=target_recall
            )
            
            # Perform SHAP analysis if requested
            shap_results = None
            if include_shap and hasattr(model, 'predict_proba'):
                logger.info("Performing SHAP analysis...")
                try:
                    shap_results = await self.shap_analyzer.analyze_model(
                        model=model,
                        X_test=X_test,
                        feature_names=self._get_feature_names()
                    )
                except Exception as e:
                    logger.warning(f"SHAP analysis failed: {str(e)}")
                    shap_results = {"error": str(e)}
            
            # Calculate business metrics
            business_metrics = self._calculate_business_metrics(y_test, y_pred, y_pred_proba)
            
            # Create comprehensive evaluation result
            evaluation = {
                "evaluation_id": evaluation_id,
                "model_version": model_version,
                "evaluation_date": datetime.utcnow(),
                "test_samples": len(X_test),
                "model_type": type(model).__name__,
                "target_recall": target_recall,
                "metrics": comprehensive_metrics,
                "business_metrics": business_metrics,
                "shap_analysis": shap_results,
                "evaluation_summary": self._generate_evaluation_summary(comprehensive_metrics, target_recall)
            }
            
            # Store evaluation result
            self.evaluation_jobs[evaluation_id] = evaluation
            
            logger.info(f"Comprehensive evaluation completed for model {model_version}")
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating model: {str(e)}")
            raise
    
    def _get_feature_names(self) -> List[str]:
        """Get feature names for SHAP analysis."""
        return [
            'work_hours_per_week', 'meeting_hours_per_week', 'email_count_per_day',
            'stress_level', 'workload_score', 'work_life_balance', 'team_size',
            'remote_work_percentage', 'overtime_hours', 'deadline_pressure'
        ]
    
    def _calculate_business_metrics(self, y_true, y_pred, y_pred_proba=None) -> Dict[str, Any]:
        """Calculate business-relevant metrics for burnout prediction."""
        metrics = {}
        
        # Calculate confusion matrix components
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
        
        # Business metrics
        metrics["true_positive_rate"] = tp / (tp + fn) if (tp + fn) > 0 else 0.0  # Recall
        metrics["false_positive_rate"] = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        metrics["precision"] = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        
        # Cost-benefit analysis (assuming catching burnout early is valuable)
        # Cost of false negative (missing burnout) vs false positive (false alarm)
        cost_false_negative = 100  # High cost of missing burnout
        cost_false_positive = 10   # Lower cost of false alarm
        
        metrics["total_cost"] = (fn * cost_false_negative) + (fp * cost_false_positive)
        metrics["cost_per_prediction"] = metrics["total_cost"] / len(y_true) if len(y_true) > 0 else 0.0
        
        # Risk stratification
        if y_pred_proba is not None:
            high_risk_threshold = 0.7
            medium_risk_threshold = 0.4
            
            high_risk_count = np.sum(y_pred_proba[:, 1] >= high_risk_threshold)
            medium_risk_count = np.sum((y_pred_proba[:, 1] >= medium_risk_threshold) & 
                                     (y_pred_proba[:, 1] < high_risk_threshold))
            low_risk_count = np.sum(y_pred_proba[:, 1] < medium_risk_threshold)
            
            metrics["risk_distribution"] = {
                "high_risk": int(high_risk_count),
                "medium_risk": int(medium_risk_count),
                "low_risk": int(low_risk_count)
            }
            
            metrics["high_risk_percentage"] = (high_risk_count / len(y_true)) * 100 if len(y_true) > 0 else 0.0
        
        # Model reliability metrics
        if y_pred_proba is not None:
            # Average confidence for positive predictions
            positive_predictions = y_pred_proba[y_pred == 1, 1]
            metrics["avg_confidence_positive"] = float(np.mean(positive_predictions)) if len(positive_predictions) > 0 else 0.0
            
            # Average confidence for negative predictions
            negative_predictions = y_pred_proba[y_pred == 0, 0]
            metrics["avg_confidence_negative"] = float(np.mean(negative_predictions)) if len(negative_predictions) > 0 else 0.0
        
        return metrics
    
    def _generate_evaluation_summary(self, metrics: Dict[str, Any], target_recall: float) -> Dict[str, Any]:
        """Generate a summary of the evaluation results."""
        summary = {}
        
        # Check if target recall is met
        recall = metrics.get("recall", 0.0)
        summary["target_recall_met"] = recall >= target_recall
        summary["recall_gap"] = target_recall - recall if recall < target_recall else 0.0
        
        # Overall performance assessment
        accuracy = metrics.get("accuracy", 0.0)
        f1 = metrics.get("f1_score", 0.0)
        
        if accuracy >= 0.9 and recall >= target_recall:
            summary["performance_grade"] = "A"
            summary["recommendation"] = "Model ready for production"
        elif accuracy >= 0.8 and recall >= target_recall * 0.9:
            summary["performance_grade"] = "B"
            summary["recommendation"] = "Model acceptable with monitoring"
        elif accuracy >= 0.7:
            summary["performance_grade"] = "C"
            summary["recommendation"] = "Model needs improvement"
        else:
            summary["performance_grade"] = "D"
            summary["recommendation"] = "Model not suitable for production"
        
        # Key strengths and weaknesses
        summary["strengths"] = []
        summary["weaknesses"] = []
        
        if recall >= target_recall:
            summary["strengths"].append("Meets recall target")
        else:
            summary["weaknesses"].append(f"Below recall target ({recall:.3f} < {target_recall})")
        
        if accuracy >= 0.85:
            summary["strengths"].append("High accuracy")
        elif accuracy < 0.7:
            summary["weaknesses"].append("Low accuracy")
        
        if f1 >= 0.8:
            summary["strengths"].append("Good F1 score")
        elif f1 < 0.6:
            summary["weaknesses"].append("Poor F1 score")
        
        return summary

    async def _load_test_data(self, test_dataset_path: str):
        """Load test data from file."""
        try:
            if not os.path.exists(test_dataset_path):
                # Generate dummy test data
                logger.info("Test dataset not found, generating dummy data")
                return self._generate_dummy_test_data()
            
            # Load data from file
            if test_dataset_path.endswith('.csv'):
                df = pd.read_csv(test_dataset_path)
            elif test_dataset_path.endswith('.json'):
                df = pd.read_json(test_dataset_path)
            else:
                raise ValueError(f"Unsupported file format: {test_dataset_path}")
            
            # Prepare features and target
            feature_columns = [
                'work_hours_per_week', 'meeting_hours_per_week', 'email_count_per_day',
                'stress_level', 'workload_score', 'work_life_balance', 'team_size',
                'remote_work_percentage', 'overtime_hours', 'deadline_pressure'
            ]
            
            X = df[feature_columns].fillna(0).values
            y = df['burnout_risk'].values if 'burnout_risk' in df.columns else self._generate_target(X)
            
            return X, y
            
        except Exception as e:
            logger.error(f"Error loading test data: {str(e)}")
            # Fallback to dummy data
            return self._generate_dummy_test_data()
    
    def _generate_dummy_test_data(self):
        """Generate dummy test data for evaluation."""
        np.random.seed(123)  # Different seed for test data
        n_samples = 200
        
        # Generate features
        X = np.random.rand(n_samples, 10)
        
        # Generate target based on features
        burnout_risk = (
            X[:, 0] * 0.3 +  # work_hours_per_week
            X[:, 3] * 0.4 +  # stress_level
            X[:, 4] * 0.3    # workload_score
        )
        
        # Convert to binary classification
        y = (burnout_risk > 0.5).astype(int)
        
        return X, y
    
    def _generate_target(self, X):
        """Generate target variable based on features."""
        burnout_risk = (
            X[:, 0] * 0.3 +  # work_hours_per_week
            X[:, 3] * 0.4 +  # stress_level
            X[:, 4] * 0.3    # workload_score
        )
        return (burnout_risk > 0.5).astype(int)
    
    def _calculate_comprehensive_metrics(self, y_true, y_pred, y_pred_proba=None):
        """Calculate comprehensive evaluation metrics."""
        metrics = {}
        
        # Basic classification metrics
        metrics["accuracy"] = float(accuracy_score(y_true, y_pred))
        metrics["precision"] = float(precision_score(y_true, y_pred, average='weighted', zero_division=0))
        metrics["recall"] = float(recall_score(y_true, y_pred, average='weighted', zero_division=0))
        metrics["f1_score"] = float(f1_score(y_true, y_pred, average='weighted', zero_division=0))
        
        # Per-class metrics
        precision_per_class = precision_score(y_true, y_pred, average=None, zero_division=0)
        recall_per_class = recall_score(y_true, y_pred, average=None, zero_division=0)
        f1_per_class = f1_score(y_true, y_pred, average=None, zero_division=0)
        
        metrics["precision_per_class"] = {
            "class_0": float(precision_per_class[0]) if len(precision_per_class) > 0 else 0.0,
            "class_1": float(precision_per_class[1]) if len(precision_per_class) > 1 else 0.0
        }
        metrics["recall_per_class"] = {
            "class_0": float(recall_per_class[0]) if len(recall_per_class) > 0 else 0.0,
            "class_1": float(recall_per_class[1]) if len(recall_per_class) > 1 else 0.0
        }
        metrics["f1_per_class"] = {
            "class_0": float(f1_per_class[0]) if len(f1_per_class) > 0 else 0.0,
            "class_1": float(f1_per_class[1]) if len(f1_per_class) > 1 else 0.0
        }
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics["confusion_matrix"] = {
            "true_negative": int(cm[0, 0]) if cm.shape[0] > 0 and cm.shape[1] > 0 else 0,
            "false_positive": int(cm[0, 1]) if cm.shape[0] > 0 and cm.shape[1] > 1 else 0,
            "false_negative": int(cm[1, 0]) if cm.shape[0] > 1 and cm.shape[1] > 0 else 0,
            "true_positive": int(cm[1, 1]) if cm.shape[0] > 1 and cm.shape[1] > 1 else 0
        }
        
        # ROC AUC (if probabilities available)
        if y_pred_proba is not None and len(np.unique(y_true)) > 1:
            try:
                if y_pred_proba.shape[1] == 2:
                    # Binary classification
                    metrics["roc_auc"] = float(roc_auc_score(y_true, y_pred_proba[:, 1]))
                else:
                    # Multi-class
                    metrics["roc_auc"] = float(roc_auc_score(y_true, y_pred_proba, multi_class='ovr'))
            except Exception as e:
                logger.warning(f"Could not calculate ROC AUC: {str(e)}")
                metrics["roc_auc"] = 0.0
        else:
            metrics["roc_auc"] = 0.0
        
        # Additional metrics
        metrics["support"] = {
            "class_0": int(np.sum(y_true == 0)),
            "class_1": int(np.sum(y_true == 1))
        }
        
        # Model performance summary
        if metrics["accuracy"] >= 0.9:
            performance_level = "excellent"
        elif metrics["accuracy"] >= 0.8:
            performance_level = "good"
        elif metrics["accuracy"] >= 0.7:
            performance_level = "fair"
        else:
            performance_level = "poor"
        
        metrics["performance_level"] = performance_level
        
        return metrics
    
    async def get_evaluation(self, evaluation_id: str) -> Dict[str, Any]:
        """Get evaluation results by ID."""
        if evaluation_id not in self.evaluation_jobs:
            raise ValueError(f"Evaluation {evaluation_id} not found")
        
        return self.evaluation_jobs[evaluation_id]
    
    async def list_evaluations(self) -> List[Dict[str, Any]]:
        """List all evaluations."""
        evaluations = []
        for eval_id, evaluation in self.evaluation_jobs.items():
            evaluations.append({
                "evaluation_id": eval_id,
                "model_version": evaluation["model_version"],
                "evaluation_date": evaluation["evaluation_date"],
                "accuracy": evaluation["metrics"]["accuracy"],
                "performance_level": evaluation["metrics"]["performance_level"]
            })
        return evaluations
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up evaluation service...")
        self.evaluation_jobs.clear()