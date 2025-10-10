# Simple ML Model for Burnout Prediction - Created by Balaji Koneti
# This module implements a basic machine learning model for testing

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.preprocessing import StandardScaler
import joblib
import logging

logger = logging.getLogger(__name__)

class BurnoutPredictionModel:
    """
    Simple burnout prediction model using Random Forest
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            'work_hours_per_week',
            'meeting_hours_per_week', 
            'email_count_per_day',
            'stress_level',
            'workload_score',
            'work_life_balance',
            'overtime_hours',
            'deadline_pressure',
            'team_size',
            'remote_work_percentage'
        ]
    
    def generate_synthetic_training_data(self, n_samples=1000):
        """
        Generate synthetic training data for model training
        """
        logger.info(f"Generating {n_samples} synthetic training samples...")
        
        np.random.seed(42)
        
        # Generate features
        data = {
            'work_hours_per_week': np.random.normal(45, 10, n_samples),
            'meeting_hours_per_week': np.random.normal(15, 5, n_samples),
            'email_count_per_day': np.random.normal(25, 10, n_samples),
            'stress_level': np.random.normal(6, 2, n_samples),
            'workload_score': np.random.normal(6.5, 2, n_samples),
            'work_life_balance': np.random.normal(5, 2, n_samples),
            'overtime_hours': np.random.exponential(5, n_samples),
            'deadline_pressure': np.random.normal(6, 2, n_samples),
            'team_size': np.random.poisson(8, n_samples),
            'remote_work_percentage': np.random.uniform(0, 100, n_samples)
        }
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Ensure realistic ranges
        df['work_hours_per_week'] = np.clip(df['work_hours_per_week'], 20, 80)
        df['meeting_hours_per_week'] = np.clip(df['meeting_hours_per_week'], 0, 40)
        df['email_count_per_day'] = np.clip(df['email_count_per_day'], 0, 100)
        df['stress_level'] = np.clip(df['stress_level'], 1, 10)
        df['workload_score'] = np.clip(df['workload_score'], 1, 10)
        df['work_life_balance'] = np.clip(df['work_life_balance'], 1, 10)
        df['overtime_hours'] = np.clip(df['overtime_hours'], 0, 40)
        df['deadline_pressure'] = np.clip(df['deadline_pressure'], 1, 10)
        df['team_size'] = np.clip(df['team_size'], 1, 20)
        df['remote_work_percentage'] = np.clip(df['remote_work_percentage'], 0, 100)
        
        # Generate target variable (burnout risk) based on features
        # Higher work hours, stress, workload, and lower work-life balance increase burnout risk
        burnout_score = (
            (df['work_hours_per_week'] - 40) / 40 * 0.2 +
            (df['stress_level'] - 5) / 5 * 0.25 +
            (df['workload_score'] - 5) / 5 * 0.2 +
            (5 - df['work_life_balance']) / 5 * 0.15 +
            df['overtime_hours'] / 20 * 0.1 +
            (df['deadline_pressure'] - 5) / 5 * 0.1
        )
        
        # Add some noise
        burnout_score += np.random.normal(0, 0.1, n_samples)
        
        # Convert to binary classification (0: no burnout risk, 1: burnout risk)
        df['burnout_risk'] = (burnout_score > 0.5).astype(int)
        
        # Add some additional realistic patterns
        # Managers tend to have higher burnout risk
        manager_mask = np.random.random(n_samples) < 0.2  # 20% are managers
        df.loc[manager_mask, 'burnout_risk'] = np.random.choice([0, 1], size=manager_mask.sum(), p=[0.3, 0.7])
        
        # High-stress departments
        high_stress_mask = np.random.random(n_samples) < 0.3  # 30% in high-stress roles
        df.loc[high_stress_mask, 'burnout_risk'] = np.random.choice([0, 1], size=high_stress_mask.sum(), p=[0.2, 0.8])
        
        return df
    
    def train(self, X, y):
        """
        Train the model
        """
        logger.info("Training burnout prediction model...")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        logger.info("Model training completed!")
    
    def predict(self, X):
        """
        Make predictions
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        return predictions, probabilities
    
    def predict_single(self, features):
        """
        Predict burnout risk for a single user
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Convert features to array
        feature_array = np.array([features[f] for f in self.feature_names]).reshape(1, -1)
        
        # Scale features
        feature_array_scaled = self.scaler.transform(feature_array)
        
        # Make prediction
        prediction = self.model.predict(feature_array_scaled)[0]
        probability = self.model.predict_proba(feature_array_scaled)[0]
        
        # Determine risk level
        risk_score = probability[1]  # Probability of burnout risk
        if risk_score < 0.3:
            risk_level = 'low'
        elif risk_score < 0.6:
            risk_level = 'medium'
        elif risk_score < 0.8:
            risk_level = 'high'
        else:
            risk_level = 'critical'
        
        return {
            'prediction': prediction,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'confidence': max(probability)
        }
    
    def evaluate(self, X, y):
        """
        Evaluate model performance
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")
        
        X_scaled = self.scaler.transform(X)
        y_pred = self.model.predict(X_scaled)
        
        accuracy = accuracy_score(y, y_pred)
        precision = precision_score(y, y_pred, average='weighted')
        recall = recall_score(y, y_pred, average='weighted')
        f1 = f1_score(y, y_pred, average='weighted')
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'classification_report': classification_report(y, y_pred)
        }
    
    def save_model(self, filepath):
        """
        Save the trained model
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """
        Load a trained model
        """
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.is_trained = model_data['is_trained']
        
        logger.info(f"Model loaded from {filepath}")

def train_and_evaluate_model():
    """
    Train and evaluate the burnout prediction model
    """
    logger.info("Starting model training and evaluation...")
    
    # Initialize model
    model = BurnoutPredictionModel()
    
    # Generate training data
    df = model.generate_synthetic_training_data(n_samples=2000)
    
    # Prepare features and target
    X = df[model.feature_names]
    y = df['burnout_risk']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train model
    model.train(X_train, y_train)
    
    # Evaluate model
    metrics = model.evaluate(X_test, y_test)
    
    # Print results
    print("\nModel Performance Metrics:")
    print("=" * 40)
    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1-Score:  {metrics['f1_score']:.4f}")
    
    print("\nClassification Report:")
    print(metrics['classification_report'])
    
    # Test with some sample predictions
    print("\nSample Predictions:")
    print("=" * 40)
    
    # High-risk employee
    high_risk_features = {
        'work_hours_per_week': 60,
        'meeting_hours_per_week': 25,
        'email_count_per_day': 50,
        'stress_level': 8,
        'workload_score': 9,
        'work_life_balance': 2,
        'overtime_hours': 20,
        'deadline_pressure': 9,
        'team_size': 12,
        'remote_work_percentage': 20
    }
    
    high_risk_pred = model.predict_single(high_risk_features)
    print(f"High-risk employee: {high_risk_pred['risk_level']} (score: {high_risk_pred['risk_score']:.3f})")
    
    # Low-risk employee
    low_risk_features = {
        'work_hours_per_week': 40,
        'meeting_hours_per_week': 10,
        'email_count_per_day': 20,
        'stress_level': 4,
        'workload_score': 5,
        'work_life_balance': 8,
        'overtime_hours': 0,
        'deadline_pressure': 3,
        'team_size': 6,
        'remote_work_percentage': 80
    }
    
    low_risk_pred = model.predict_single(low_risk_features)
    print(f"Low-risk employee: {low_risk_pred['risk_level']} (score: {low_risk_pred['risk_score']:.3f})")
    
    # Save model
    model.save_model('models/burnout_model.pkl')
    
    return model, metrics

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Train and evaluate model
    model, metrics = train_and_evaluate_model()
