# Training Service - Created by Balaji Koneti
"""
Training service for training burnout risk prediction models.
Updated to use advanced training pipeline with proper feature engineering and model selection.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

# Import advanced training components
from .training.advanced_training_pipeline import AdvancedTrainingPipeline

logger = logging.getLogger(__name__)

class TrainingService:
    """Service for training burnout risk prediction models."""
    
    def __init__(self):
        self.training_jobs = {}
        self.models_dir = "models"
        self.advanced_pipeline = AdvancedTrainingPipeline()
        
    async def initialize(self):
        """Initialize the training service."""
        logger.info("Initializing training service...")
        
        # Create models directory if it doesn't exist
        os.makedirs(self.models_dir, exist_ok=True)
        
        logger.info("Training service initialized")
    
    async def start_training(self, dataset_path: str, model_type: str = "comprehensive", 
                           hyperparameters: Optional[Dict[str, Any]] = None) -> str:
        """Start a model training job."""
        try:
            training_id = str(uuid.uuid4())
            
            # Initialize training job
            self.training_jobs[training_id] = {
                "status": "started",
                "model_type": model_type,
                "dataset_path": dataset_path,
                "hyperparameters": hyperparameters or {},
                "start_time": datetime.utcnow(),
                "progress": 0,
                "metrics": {}
            }
            
            # Start training in background
            asyncio.create_task(self._train_model(training_id))
            
            logger.info(f"Started training job {training_id}")
            return training_id
            
        except Exception as e:
            logger.error(f"Error starting training: {str(e)}")
            raise
    
    async def _train_model(self, training_id: str):
        """Train the model in the background."""
        try:
            job = self.training_jobs[training_id]
            
            # Update status
            job["status"] = "initializing"
            job["progress"] = 5
            
            # Initialize advanced pipeline
            await self.advanced_pipeline.feature_pipeline.initialize()
            
            job["status"] = "loading_data"
            job["progress"] = 10
            
            # Get user IDs for training (in production, this would come from the dataset)
            user_ids = await self._get_training_user_ids(job["dataset_path"])
            
            job["status"] = "feature_engineering"
            job["progress"] = 30
            
            # Use advanced training pipeline for comprehensive training
            if job["model_type"] == "comprehensive":
                logger.info(f"Using comprehensive training pipeline for job {training_id}")
                
                training_results = await self.advanced_pipeline.train_comprehensive_model(
                    user_ids=user_ids,
                    lookback_days=30,
                    optimization_enabled=True
                )
                
                job["status"] = "completed"
                job["progress"] = 100
                job["training_results"] = training_results
                job["model_version"] = f"comprehensive_{training_id[:8]}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                job["end_time"] = datetime.utcnow()
                
                # Extract metrics from training results
                if training_results.get('best_model'):
                    best_model_info = training_results['best_model']
                    job["metrics"] = best_model_info.get('metrics', {})
                
                logger.info(f"Comprehensive training job {training_id} completed successfully")
            
            else:
                # Fallback to legacy training for other model types
                logger.info(f"Using legacy training for job {training_id}")
                
                job["status"] = "loading_data"
                job["progress"] = 20
                
                # Load and prepare data
                X, y = await self._load_training_data(job["dataset_path"])
                
                job["status"] = "preprocessing"
                job["progress"] = 40
                
                # Preprocess data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42, stratify=y
                )
                
                job["status"] = "training"
                job["progress"] = 60
                
                # Train model
                model = await self._create_model(job["model_type"], job["hyperparameters"])
                model.fit(X_train, y_train)
                
                job["status"] = "evaluating"
                job["progress"] = 80
                
                # Evaluate model
                y_pred = model.predict(X_test)
                metrics = self._calculate_metrics(y_test, y_pred)
                job["metrics"] = metrics
                
                job["status"] = "saving"
                job["progress"] = 90
                
                # Save model
                model_version = f"legacy_{training_id[:8]}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                model_path = os.path.join(self.models_dir, f"{model_version}.joblib")
                joblib.dump(model, model_path)
                
                job["status"] = "completed"
                job["progress"] = 100
                job["model_version"] = model_version
                job["end_time"] = datetime.utcnow()
                
                logger.info(f"Legacy training job {training_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error in training job {training_id}: {str(e)}")
            self.training_jobs[training_id]["status"] = "failed"
            self.training_jobs[training_id]["error"] = str(e)
    
    async def _get_training_user_ids(self, dataset_path: str) -> List[str]:
        """Get user IDs for training from dataset or generate synthetic ones."""
        try:
            # In production, this would load user IDs from the dataset
            # For now, generate synthetic user IDs
            return [f"user_{i:03d}" for i in range(1, 51)]  # 50 users
        except Exception as e:
            logger.error(f"Error getting training user IDs: {str(e)}")
            # Fallback to synthetic user IDs
            return [f"user_{i:03d}" for i in range(1, 11)]  # 10 users
    
    async def _load_training_data(self, dataset_path: str):
        """Load training data from file."""
        try:
            if not os.path.exists(dataset_path):
                # Generate dummy data for testing
                logger.info("Dataset not found, generating dummy data")
                return self._generate_dummy_data()
            
            # Load data from file
            if dataset_path.endswith('.csv'):
                df = pd.read_csv(dataset_path)
            elif dataset_path.endswith('.json'):
                df = pd.read_json(dataset_path)
            else:
                raise ValueError(f"Unsupported file format: {dataset_path}")
            
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
            logger.error(f"Error loading training data: {str(e)}")
            # Fallback to dummy data
            return self._generate_dummy_data()
    
    def _generate_dummy_data(self):
        """Generate dummy training data for testing."""
        np.random.seed(42)
        n_samples = 1000
        
        # Generate features
        X = np.random.rand(n_samples, 10)
        
        # Generate target based on features (simulate burnout risk)
        # Higher work hours, stress, and workload increase burnout risk
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
        # Simple rule-based target generation
        burnout_risk = (
            X[:, 0] * 0.3 +  # work_hours_per_week
            X[:, 3] * 0.4 +  # stress_level
            X[:, 4] * 0.3    # workload_score
        )
        return (burnout_risk > 0.5).astype(int)
    
    async def _create_model(self, model_type: str, hyperparameters: Dict[str, Any]):
        """Create a model based on type and hyperparameters."""
        if model_type == "baseline":
            return RandomForestClassifier(
                n_estimators=hyperparameters.get('n_estimators', 100),
                max_depth=hyperparameters.get('max_depth', 10),
                random_state=42
            )
        elif model_type == "advanced":
            return RandomForestClassifier(
                n_estimators=hyperparameters.get('n_estimators', 200),
                max_depth=hyperparameters.get('max_depth', 15),
                min_samples_split=hyperparameters.get('min_samples_split', 5),
                min_samples_leaf=hyperparameters.get('min_samples_leaf', 2),
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def _calculate_metrics(self, y_true, y_pred):
        """Calculate model performance metrics."""
        return {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, average='weighted')),
            "recall": float(recall_score(y_true, y_pred, average='weighted')),
            "f1_score": float(f1_score(y_true, y_pred, average='weighted'))
        }
    
    async def get_training_status(self, training_id: str) -> Dict[str, Any]:
        """Get the status of a training job."""
        if training_id not in self.training_jobs:
            raise ValueError(f"Training job {training_id} not found")
        
        job = self.training_jobs[training_id]
        
        return {
            "training_id": training_id,
            "status": job["status"],
            "progress": job["progress"],
            "model_type": job["model_type"],
            "start_time": job["start_time"],
            "end_time": job.get("end_time"),
            "metrics": job.get("metrics", {}),
            "model_version": job.get("model_version"),
            "error": job.get("error")
        }
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up training service...")
        self.training_jobs.clear()