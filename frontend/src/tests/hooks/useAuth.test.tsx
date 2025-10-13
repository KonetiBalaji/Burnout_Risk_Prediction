// useAuth hook tests - Created by Balaji Koneti
import { renderHook, act, waitFor } from '@testing-library/react';
import { useAuth, AuthProvider } from '../../hooks/useAuth';
import { authService } from '../../services/authService';

// Mock the auth service
vi.mock('../../services/authService', () => ({
  authService: {
    login: vi.fn(),
    register: vi.fn(),
    getProfile: vi.fn(),
    updateProfile: vi.fn(),
  },
}));

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

describe('useAuth Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockLocalStorage.getItem.mockReturnValue(null);
  });

  describe('initialization', () => {
    it('should initialize with no user and token when no stored token', async () => {
      mockLocalStorage.getItem.mockReturnValue(null);
      (authService.getProfile as any).mockResolvedValue(null);

      const { result } = renderHook(() => useAuth(), {
        wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
      });

      await waitFor(() => {
        expect(result.current.user).toBeNull();
        expect(result.current.token).toBeNull();
        expect(result.current.loading).toBe(false);
      });
    });

    it('should initialize with user when valid token exists', async () => {
      const mockToken = 'valid-token';
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        firstName: 'John',
        lastName: 'Doe',
        role: 'user',
        isActive: true,
        createdAt: new Date(),
      };

      mockLocalStorage.getItem.mockReturnValue(mockToken);
      (authService.getProfile as any).mockResolvedValue(mockUser);

      const { result } = renderHook(() => useAuth(), {
        wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
      });

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser);
        expect(result.current.token).toBe(mockToken);
        expect(result.current.loading).toBe(false);
      });
    });

    it('should clear invalid token', async () => {
      const mockToken = 'invalid-token';
      mockLocalStorage.getItem.mockReturnValue(mockToken);
      (authService.getProfile as any).mockResolvedValue(null);

      const { result } = renderHook(() => useAuth(), {
        wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
      });

      await waitFor(() => {
        expect(result.current.user).toBeNull();
        expect(result.current.token).toBeNull();
        expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('token');
      });
    });
  });

  describe('login', () => {
    it('should login successfully with valid credentials', async () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        firstName: 'John',
        lastName: 'Doe',
        role: 'user',
        isActive: true,
        createdAt: new Date(),
      };
      const mockToken = 'auth-token';

      (authService.login as any).mockResolvedValue({
        success: true,
        data: {
          user: mockUser,
          token: mockToken,
        },
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
      });

      let loginResult: boolean;
      await act(async () => {
        loginResult = await result.current.login('test@example.com', 'password123');
      });

      expect(loginResult).toBe(true);
      expect(result.current.user).toEqual(mockUser);
      expect(result.current.token).toBe(mockToken);
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('token', mockToken);
    });

    it('should handle login failure', async () => {
      (authService.login as any).mockResolvedValue({
        success: false,
        message: 'Invalid credentials',
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
      });

      let loginResult: boolean;
      await act(async () => {
        loginResult = await result.current.login('test@example.com', 'wrongpassword');
      });

      expect(loginResult).toBe(false);
      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
    });

    it('should handle login error', async () => {
      (authService.login as any).mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useAuth(), {
        wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
      });

      let loginResult: boolean;
      await act(async () => {
        loginResult = await result.current.login('test@example.com', 'password123');
      });

      expect(loginResult).toBe(false);
    });
  });

  describe('register', () => {
    it('should register successfully', async () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        firstName: 'John',
        lastName: 'Doe',
        role: 'user',
        isActive: true,
        createdAt: new Date(),
      };
      const mockToken = 'auth-token';

      (authService.register as any).mockResolvedValue({
        success: true,
        data: {
          user: mockUser,
          token: mockToken,
        },
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
      });

      let registerResult: boolean;
      await act(async () => {
        registerResult = await result.current.register(
          'test@example.com',
          'password123',
          'John',
          'Doe'
        );
      });

      expect(registerResult).toBe(true);
      expect(result.current.user).toEqual(mockUser);
      expect(result.current.token).toBe(mockToken);
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith('token', mockToken);
    });

    it('should handle registration failure', async () => {
      (authService.register as any).mockResolvedValue({
        success: false,
        message: 'Email already exists',
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
      });

      let registerResult: boolean;
      await act(async () => {
        registerResult = await result.current.register(
          'test@example.com',
          'password123',
          'John',
          'Doe'
        );
      });

      expect(registerResult).toBe(false);
      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
    });
  });

  describe('logout', () => {
    it('should clear user state and token', async () => {
      const { result } = renderHook(() => useAuth(), {
        wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
      });

      // Set initial state
      act(() => {
        result.current.user = {
          id: '1',
          email: 'test@example.com',
          firstName: 'John',
          lastName: 'Doe',
          role: 'user',
          isActive: true,
          createdAt: new Date(),
        };
        result.current.token = 'auth-token';
      });

      act(() => {
        result.current.logout();
      });

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('token');
    });
  });

  describe('updateProfile', () => {
    it('should update profile successfully', async () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        firstName: 'John',
        lastName: 'Doe',
        role: 'user',
        isActive: true,
        createdAt: new Date(),
      };
      const mockToken = 'auth-token';

      // Set initial state
      const { result } = renderHook(() => useAuth(), {
        wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
      });

      act(() => {
        result.current.user = mockUser;
        result.current.token = mockToken;
      });

      const updatedUser = { ...mockUser, firstName: 'Jane' };
      (authService.updateProfile as any).mockResolvedValue({
        success: true,
        data: { user: updatedUser },
      });

      let updateResult: boolean;
      await act(async () => {
        updateResult = await result.current.updateProfile({ firstName: 'Jane' });
      });

      expect(updateResult).toBe(true);
      expect(result.current.user).toEqual(updatedUser);
    });

    it('should handle update failure', async () => {
      const mockToken = 'auth-token';
      const { result } = renderHook(() => useAuth(), {
        wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
      });

      act(() => {
        result.current.token = mockToken;
      });

      (authService.updateProfile as any).mockResolvedValue({
        success: false,
        message: 'Update failed',
      });

      let updateResult: boolean;
      await act(async () => {
        updateResult = await result.current.updateProfile({ firstName: 'Jane' });
      });

      expect(updateResult).toBe(false);
    });

    it('should return false when no token', async () => {
      const { result } = renderHook(() => useAuth(), {
        wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
      });

      let updateResult: boolean;
      await act(async () => {
        updateResult = await result.current.updateProfile({ firstName: 'Jane' });
      });

      expect(updateResult).toBe(false);
    });
  });
});
