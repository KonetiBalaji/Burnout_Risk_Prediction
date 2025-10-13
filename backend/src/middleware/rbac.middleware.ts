// Role-Based Access Control Middleware - Created by Balaji Koneti
import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';

// Interface for authenticated request
export interface AuthenticatedRequest extends Request {
  user?: {
    userId: string;
    email: string;
    role: string;
  };
}

// Define user roles and their permissions
export const ROLES = {
  ADMIN: 'admin',
  MANAGER: 'manager',
  USER: 'user'
} as const;

export type UserRole = typeof ROLES[keyof typeof ROLES];

// Define permissions for each role
const PERMISSIONS = {
  [ROLES.ADMIN]: [
    'users:read',
    'users:write',
    'users:delete',
    'predictions:read',
    'predictions:write',
    'predictions:delete',
    'analytics:read',
    'system:admin',
    'data:export',
    'reports:generate'
  ],
  [ROLES.MANAGER]: [
    'users:read',
    'predictions:read',
    'predictions:write',
    'analytics:read',
    'team:manage',
    'reports:generate'
  ],
  [ROLES.USER]: [
    'predictions:read',
    'profile:read',
    'profile:write'
  ]
} as const;

/**
 * Check if user has required permission
 */
function hasPermission(userRole: UserRole, requiredPermission: string): boolean {
  const userPermissions = PERMISSIONS[userRole] || [];
  return userPermissions.includes(requiredPermission);
}

/**
 * Check if user has required role
 */
function hasRole(userRole: UserRole, requiredRoles: UserRole[]): boolean {
  return requiredRoles.includes(userRole);
}

/**
 * RBAC middleware factory
 */
export function requirePermission(permission: string) {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction): void => {
    try {
      if (!req.user) {
        logger.warn('Unauthorized access attempt - no user in request');
        res.status(401).json({
          success: false,
          message: 'Authentication required'
        });
        return;
      }

      const userRole = req.user.role as UserRole;
      
      if (!hasPermission(userRole, permission)) {
        logger.warn(`Access denied for user ${req.user.email} - insufficient permissions for ${permission}`);
        res.status(403).json({
          success: false,
          message: 'Insufficient permissions',
          required: permission,
          userRole: userRole
        });
        return;
      }

      logger.debug(`Access granted for user ${req.user.email} to ${permission}`);
      next();

    } catch (error) {
      logger.error('Error in RBAC middleware:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error'
      });
    }
  };
}

/**
 * RBAC middleware for role-based access
 */
export function requireRole(roles: UserRole[]) {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction): void => {
    try {
      if (!req.user) {
        logger.warn('Unauthorized access attempt - no user in request');
        res.status(401).json({
          success: false,
          message: 'Authentication required'
        });
        return;
      }

      const userRole = req.user.role as UserRole;
      
      if (!hasRole(userRole, roles)) {
        logger.warn(`Access denied for user ${req.user.email} - insufficient role. Required: ${roles.join(', ')}, User role: ${userRole}`);
        res.status(403).json({
          success: false,
          message: 'Insufficient role permissions',
          required: roles,
          userRole: userRole
        });
        return;
      }

      logger.debug(`Role access granted for user ${req.user.email} with role ${userRole}`);
      next();

    } catch (error) {
      logger.error('Error in role-based middleware:', error);
      res.status(500).json({
        success: false,
        message: 'Internal server error'
      });
    }
  };
}

/**
 * Admin-only access middleware
 */
export const requireAdmin = requireRole([ROLES.ADMIN]);

/**
 * Manager or Admin access middleware
 */
export const requireManagerOrAdmin = requireRole([ROLES.MANAGER, ROLES.ADMIN]);

/**
 * User resource access middleware - users can only access their own resources
 */
export function requireOwnResourceOrAdmin(req: AuthenticatedRequest, res: Response, next: NextFunction): void {
  try {
    if (!req.user) {
      logger.warn('Unauthorized access attempt - no user in request');
      res.status(401).json({
        success: false,
        message: 'Authentication required'
      });
      return;
    }

    const userRole = req.user.role as UserRole;
    const resourceUserId = req.params.userId || req.params.id;

    // Admins can access any resource
    if (userRole === ROLES.ADMIN) {
      next();
      return;
    }

    // Users can only access their own resources
    if (req.user.userId !== resourceUserId) {
      logger.warn(`Access denied for user ${req.user.email} - trying to access resource ${resourceUserId}`);
      res.status(403).json({
        success: false,
        message: 'Access denied - you can only access your own resources'
      });
      return;
    }

    next();

  } catch (error) {
    logger.error('Error in resource access middleware:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
}

/**
 * Team access middleware - managers can access their team members' resources
 */
export function requireTeamAccess(req: AuthenticatedRequest, res: Response, next: NextFunction): void {
  try {
    if (!req.user) {
      logger.warn('Unauthorized access attempt - no user in request');
      res.status(401).json({
        success: false,
        message: 'Authentication required'
      });
      return;
    }

    const userRole = req.user.role as UserRole;
    const resourceUserId = req.params.userId || req.params.id;

    // Admins can access any resource
    if (userRole === ROLES.ADMIN) {
      next();
      return;
    }

    // Managers can access their team members (this would need team relationship data)
    if (userRole === ROLES.MANAGER) {
      // TODO: Implement team relationship check
      // For now, allow managers to access any resource
      // In production, you would check if the resource user is in the manager's team
      next();
      return;
    }

    // Users can only access their own resources
    if (req.user.userId !== resourceUserId) {
      logger.warn(`Access denied for user ${req.user.email} - trying to access resource ${resourceUserId}`);
      res.status(403).json({
        success: false,
        message: 'Access denied - insufficient permissions'
      });
      return;
    }

    next();

  } catch (error) {
    logger.error('Error in team access middleware:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
}

/**
 * Get user permissions
 */
export function getUserPermissions(role: UserRole): string[] {
  return PERMISSIONS[role] || [];
}

/**
 * Check if user can perform action
 */
export function canUserPerformAction(role: UserRole, action: string): boolean {
  return hasPermission(role, action);
}
