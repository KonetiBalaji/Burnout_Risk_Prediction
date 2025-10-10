// Prediction service for burnout risk analysis - Created by Balaji Koneti
import { PredictionResult, IPredictionResult } from '../models/predictionResult.model';
import { extractAllFeatures, normalizeFeatures, ExtractedFeatures } from '../utils/featureExtractor';
import { logger } from '../utils/logger';
import { mlApiClient, MLPredictionResponse } from './mlApiClient.service';

// Interface for prediction request
export interface PredictionRequest {
  userId: string;
  startDate: Date;
  endDate: Date;
  additionalData?: {
    sleepQuality?: number;
    exerciseFrequency?: number;
    nutritionQuality?: number;
    socialSupport?: number;
    jobSatisfaction?: number;
  };
}

// Interface for prediction response
export interface PredictionResponse {
  success: boolean;
  prediction?: IPredictionResult;
  message?: string;
}

// Function to generate burnout risk prediction
export async function generatePrediction(
  request: PredictionRequest
): Promise<PredictionResponse> {
  try {
    const { userId, startDate, endDate, additionalData } = request;
    
    // Extract features from user data
    const features = await extractAllFeatures(userId, startDate, endDate);
    
    // Override with additional data if provided
    if (additionalData) {
      if (additionalData.sleepQuality !== undefined) {
        features.sleepQuality = additionalData.sleepQuality;
      }
      if (additionalData.exerciseFrequency !== undefined) {
        features.exerciseFrequency = additionalData.exerciseFrequency;
      }
      if (additionalData.nutritionQuality !== undefined) {
        features.nutritionQuality = additionalData.nutritionQuality;
      }
      if (additionalData.socialSupport !== undefined) {
        features.socialInteraction = additionalData.socialSupport;
      }
      if (additionalData.jobSatisfaction !== undefined) {
        features.workLifeBalance = additionalData.jobSatisfaction;
      }
    }
    
    // Get prediction from ML service
    const mlPrediction = await mlApiClient.predictBurnoutRisk(
      userId,
      features as Record<string, number>,
      'latest'
    );
    
    // Extract values from ML prediction
    const riskScore = mlPrediction.risk_score;
    const riskLevel = mlPrediction.risk_level as 'low' | 'medium' | 'high' | 'critical';
    const confidence = mlPrediction.confidence;
    
    // Convert ML recommendations to our format
    const recommendations = convertMLRecommendations(mlPrediction.recommendations, features, riskLevel);
    
    // Create prediction result
    const prediction = new PredictionResult({
      userId: userId as any,
      predictionDate: new Date(),
      riskLevel,
      riskScore,
      confidence,
      factors: {
        workload: features.workloadLevel,
        stressLevel: features.stressLevel,
        workLifeBalance: features.workLifeBalance,
        socialSupport: features.socialInteraction,
        jobSatisfaction: features.workLifeBalance,
        physicalHealth: features.exerciseFrequency,
        mentalHealth: features.sleepQuality,
        sleepQuality: features.sleepQuality,
        exerciseFrequency: features.exerciseFrequency,
        nutritionQuality: features.nutritionQuality
      },
      recommendations,
      dataPoints: {
        calendarEvents: features.totalEvents,
        emailMessages: features.emailCount,
        surveyResponses: 0, // Placeholder
        biometricData: 0 // Placeholder
      },
      modelVersion: mlPrediction.model_version
    });
    
    // Save prediction to database
    await prediction.save();
    
    // Log successful prediction
    logger.info(`Prediction generated for user ${userId}: Risk Level ${riskLevel}, Score ${riskScore}`);
    
    return {
      success: true,
      prediction
    };
    
  } catch (error) {
    logger.error('Error generating prediction:', error);
    return {
      success: false,
      message: 'Failed to generate prediction. Please try again.'
    };
  }
}

// Function to convert ML service recommendations to our format
function convertMLRecommendations(
  mlRecommendations: string[],
  features: ExtractedFeatures,
  riskLevel: string
): IPredictionResult['recommendations'] {
  const recommendations: IPredictionResult['recommendations'] = [];
  
  try {
    // Convert simple string recommendations to structured format
    mlRecommendations.forEach((rec, index) => {
      recommendations.push({
        priority: riskLevel === 'critical' || riskLevel === 'high' ? 'high' : 'medium',
        category: 'general',
        title: `Recommendation ${index + 1}`,
        description: rec,
        actionItems: [
          'Review the recommendation above',
          'Consider implementing suggested changes',
          'Monitor your progress regularly'
        ]
      });
    });
    
    // Add additional context-based recommendations if needed
    if (features.workloadLevel > 3) {
      recommendations.push({
        priority: 'high',
        category: 'workload',
        title: 'Reduce Workload',
        description: 'Your workload is significantly high. Consider delegating tasks or discussing workload distribution with your manager.',
        actionItems: [
          'Review your current tasks and identify what can be delegated',
          'Schedule a meeting with your manager to discuss workload',
          'Break down large tasks into smaller, manageable chunks',
          'Set realistic deadlines for your projects'
        ],
        resources: [
          'https://example.com/workload-management-guide',
          'https://example.com/delegation-tips'
        ]
      });
    }
    
    // If no recommendations from ML service, provide general ones
    if (recommendations.length === 0) {
      recommendations.push({
        priority: 'medium',
        category: 'lifestyle',
        title: 'Maintain Current Practices',
        description: 'Continue monitoring your well-being and make adjustments as needed.',
        actionItems: [
          'Continue regular self-assessment',
          'Stay aware of stress indicators',
          'Maintain work-life boundaries',
          'Keep up with current healthy habits'
        ]
      });
    }
    
    return recommendations;
    
  } catch (error) {
    logger.error('Error converting ML recommendations:', error);
    return [{
      priority: 'medium',
      category: 'lifestyle',
      title: 'General Well-being',
      description: 'Focus on maintaining a healthy work-life balance and managing stress effectively.',
      actionItems: [
        'Take regular breaks',
        'Maintain healthy sleep habits',
        'Stay connected with colleagues and friends',
        'Monitor your stress levels'
      ]
    }];
  }
}


// Function to get latest prediction for user
export async function getLatestPrediction(userId: string): Promise<IPredictionResult | null> {
  try {
    const prediction = await PredictionResult.findLatestByUser(userId as any);
    return prediction;
  } catch (error) {
    logger.error('Error getting latest prediction:', error);
    return null;
  }
}

// Function to get prediction history for user
export async function getPredictionHistory(
  userId: string,
  limit: number = 10
): Promise<IPredictionResult[]> {
  try {
    const predictions = await PredictionResult.find({ userId })
      .sort({ predictionDate: -1 })
      .limit(limit);
    return predictions;
  } catch (error) {
    logger.error('Error getting prediction history:', error);
    return [];
  }
}
