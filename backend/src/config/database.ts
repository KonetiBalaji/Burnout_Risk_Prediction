// Database configuration and connection - Created by Balaji Koneti
import mongoose from 'mongoose';
import { MONGODB_URI, NODE_ENV } from './env';
import { logger } from '../utils/logger';

// MongoDB connection options for Mongoose 7.x
const mongoOptions = {
  maxPoolSize: 10, // Maximum number of connections in the connection pool
  serverSelectionTimeoutMS: 5000, // How long to try to connect before timing out
  socketTimeoutMS: 45000, // How long a send or receive operation can take before timing out
  bufferCommands: false, // Disable mongoose buffering
};

// Connect to MongoDB database
export const connectDatabase = async (): Promise<void> => {
  try {
    // Connect to MongoDB using the URI from environment variables
    await mongoose.connect(MONGODB_URI, mongoOptions);
    
    // Log successful connection
    logger.info('Successfully connected to MongoDB database');
    
    // Log database name for verification
    logger.info(`Database name: ${mongoose.connection.db?.databaseName}`);
    
  } catch (error) {
    // Log connection error with details
    logger.error('Failed to connect to MongoDB:', error);
    
    // Exit process if database connection fails in production
    if (NODE_ENV === 'production') {
      process.exit(1);
    }
  }
};

// Handle MongoDB connection events
mongoose.connection.on('connected', () => {
  logger.info('Mongoose connected to MongoDB');
});

mongoose.connection.on('error', (error) => {
  logger.error('Mongoose connection error:', error);
});

mongoose.connection.on('disconnected', () => {
  logger.warn('Mongoose disconnected from MongoDB');
});

// Graceful shutdown handler
process.on('SIGINT', async () => {
  try {
    // Close MongoDB connection gracefully
    await mongoose.connection.close();
    logger.info('MongoDB connection closed through app termination');
    process.exit(0);
  } catch (error) {
    logger.error('Error during MongoDB disconnection:', error);
    process.exit(1);
  }
});

// Export mongoose instance for use in other modules
export default mongoose;
