// Users routes - Created by Balaji Koneti
import { Router } from 'express';
import { User } from '../../models/user.model';

// Create router instance
const router = Router();

// Middleware to verify JWT token
const authenticateToken = (req: any, res: any, next: any) => {
  try {
    // Get token from Authorization header
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN
    
    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'Access token required'
      });
    }
    
    // For now, just check if token exists (in production, verify JWT)
    req.user = { id: 'temp' }; // Temporary user
    next();
    
  } catch (error) {
    return res.status(403).json({
      success: false,
      message: 'Invalid token'
    });
  }
};

// All user routes require authentication
router.use(authenticateToken);

// Get all users (admin only)
router.get('/', async (req, res) => {
  try {
    // Get all users (excluding passwords)
    const users = await User.find({}, { password: 0 }).sort({ createdAt: -1 });
    
    res.json(users);
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Failed to fetch users',
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Get user by ID
router.get('/:id', async (req, res) => {
  try {
    const user = await User.findById(req.params.id, { password: 0 });
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }
    
    return res.json(user);
  } catch (error) {
    return res.status(500).json({
      success: false,
      message: 'Failed to fetch user',
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Export router
export default router;
