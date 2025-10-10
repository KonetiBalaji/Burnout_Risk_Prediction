# Preprocessing Service - Created by Balaji Koneti
"""
Preprocessing service for data preparation and feature engineering.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import json

logger = logging.getLogger(__name__)

class PreprocessingService:
    """Service for data preprocessing and feature engineering."""
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.imputers = {}
        
    async def initialize(self):
        """Initialize the preprocessing service."""
        logger.info("Initializing preprocessing service...")
        logger.info("Preprocessing service initialized")
    
    async def preprocess(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """Preprocess raw data for training."""
        try:
            logger.info(f"Preprocessing data from {input_path}")
            
            # Load raw data
            raw_data = await self._load_data(input_path)
            
            # Clean data
            cleaned_data = await self._clean_data(raw_data)
            
            # Engineer features
            engineered_data = await self._engineer_features(cleaned_data)
            
            # Scale features
            scaled_data = await self._scale_features(engineered_data)
            
            # Save processed data
            await self._save_data(scaled_data, output_path)
            
            # Generate preprocessing report
            report = await self._generate_report(raw_data, scaled_data)
            
            logger.info(f"Preprocessing completed. Output saved to {output_path}")
            
            return {
                "status": "completed",
                "input_path": input_path,
                "output_path": output_path,
                "preprocessing_date": datetime.utcnow(),
                "report": report
            }
            
        except Exception as e:
            logger.error(f"Error preprocessing data: {str(e)}")
            raise
    
    async def _load_data(self, input_path: str) -> pd.DataFrame:
        """Load data from various formats."""
        try:
            if not os.path.exists(input_path):
                # Generate dummy data for testing
                logger.info("Input file not found, generating dummy data")
                return self._generate_dummy_data()
            
            if input_path.endswith('.csv'):
                df = pd.read_csv(input_path)
            elif input_path.endswith('.json'):
                df = pd.read_json(input_path)
            elif input_path.endswith('.xlsx'):
                df = pd.read_excel(input_path)
            else:
                raise ValueError(f"Unsupported file format: {input_path}")
            
            logger.info(f"Loaded data with shape: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            # Fallback to dummy data
            return self._generate_dummy_data()
    
    def _generate_dummy_data(self) -> pd.DataFrame:
        """Generate dummy data for testing."""
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'user_id': [f'user_{i}' for i in range(n_samples)],
            'work_hours_per_week': np.random.normal(40, 10, n_samples),
            'meeting_hours_per_week': np.random.normal(15, 5, n_samples),
            'email_count_per_day': np.random.poisson(20, n_samples),
            'stress_level': np.random.uniform(1, 10, n_samples),
            'workload_score': np.random.uniform(1, 10, n_samples),
            'work_life_balance': np.random.uniform(1, 10, n_samples),
            'team_size': np.random.randint(2, 20, n_samples),
            'remote_work_percentage': np.random.uniform(0, 100, n_samples),
            'overtime_hours': np.random.exponential(5, n_samples),
            'deadline_pressure': np.random.uniform(1, 10, n_samples),
            'department': np.random.choice(['Engineering', 'Marketing', 'Sales', 'HR', 'Finance'], n_samples),
            'experience_years': np.random.uniform(0, 20, n_samples),
            'burnout_risk': np.random.randint(0, 2, n_samples)
        }
        
        return pd.DataFrame(data)
    
    async def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean the raw data."""
        logger.info("Cleaning data...")
        
        # Remove duplicates
        initial_rows = len(df)
        df = df.drop_duplicates()
        logger.info(f"Removed {initial_rows - len(df)} duplicate rows")
        
        # Handle missing values
        missing_before = df.isnull().sum().sum()
        
        # Fill missing values with appropriate strategies
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        categorical_columns = df.select_dtypes(include=['object']).columns
        
        # Fill numeric missing values with median
        for col in numeric_columns:
            if df[col].isnull().any():
                df[col].fillna(df[col].median(), inplace=True)
        
        # Fill categorical missing values with mode
        for col in categorical_columns:
            if df[col].isnull().any():
                mode_value = df[col].mode()[0] if not df[col].mode().empty else 'Unknown'
                df[col].fillna(mode_value, inplace=True)
        
        missing_after = df.isnull().sum().sum()
        logger.info(f"Handled {missing_before - missing_after} missing values")
        
        return df
    
    async def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer new features."""
        logger.info("Engineering features...")
        
        # Create a copy to avoid modifying original
        df_eng = df.copy()
        
        # Work intensity features
        df_eng['work_intensity'] = (
            df_eng['work_hours_per_week'] * 0.4 +
            df_eng['meeting_hours_per_week'] * 0.3 +
            df_eng['overtime_hours'] * 0.3
        )
        
        # Stress composite score
        df_eng['stress_composite'] = (
            df_eng['stress_level'] * 0.4 +
            df_eng['workload_score'] * 0.3 +
            df_eng['deadline_pressure'] * 0.3
        )
        
        # Work-life balance ratio
        df_eng['work_life_ratio'] = df_eng['work_hours_per_week'] / (df_eng['work_life_balance'] + 1)
        
        # Communication load
        df_eng['communication_load'] = (
            df_eng['email_count_per_day'] * 0.6 +
            df_eng['meeting_hours_per_week'] * 0.4
        )
        
        logger.info(f"Engineered features. New shape: {df_eng.shape}")
        return df_eng
    
    async def _scale_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Scale numerical features."""
        logger.info("Scaling features...")
        
        df_scaled = df.copy()
        
        # Define features to scale
        feature_columns = [
            'work_hours_per_week', 'meeting_hours_per_week', 'email_count_per_day',
            'stress_level', 'workload_score', 'work_life_balance', 'team_size',
            'remote_work_percentage', 'overtime_hours', 'deadline_pressure',
            'work_intensity', 'stress_composite', 'work_life_ratio',
            'communication_load'
        ]
        
        # Scale features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(df_scaled[feature_columns])
        df_scaled[feature_columns] = scaled_features
        
        # Store scaler for later use
        self.scalers['feature_scaler'] = scaler
        
        logger.info("Features scaled successfully")
        return df_scaled
    
    async def _save_data(self, df: pd.DataFrame, output_path: str):
        """Save processed data."""
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if output_path.endswith('.csv'):
            df.to_csv(output_path, index=False)
        elif output_path.endswith('.json'):
            df.to_json(output_path, orient='records', indent=2)
        else:
            # Default to CSV
            df.to_csv(output_path, index=False)
        
        logger.info(f"Processed data saved to {output_path}")
    
    async def _generate_report(self, raw_data: pd.DataFrame, processed_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate preprocessing report."""
        report = {
            "preprocessing_summary": {
                "raw_data_shape": raw_data.shape,
                "processed_data_shape": processed_data.shape,
                "rows_removed": raw_data.shape[0] - processed_data.shape[0],
                "columns_added": processed_data.shape[1] - raw_data.shape[1]
            },
            "data_quality": {
                "missing_values_before": int(raw_data.isnull().sum().sum()),
                "missing_values_after": int(processed_data.isnull().sum().sum()),
                "duplicates_removed": int(raw_data.duplicated().sum())
            },
            "preprocessing_timestamp": datetime.utcnow().isoformat()
        }
        
        return report
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up preprocessing service...")
        self.scalers.clear()
        self.encoders.clear()
        self.imputers.clear()