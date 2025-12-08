import { describe, it, expect } from 'vitest';
import {
  authReducer,
  login,
  logout,
  setCredentials,
  clearError,
  updateUser,
} from '../../store/slices/authSlice';
import type { AuthState, User, Role } from '../../types';

const mockRole: Role = {
  id: '1',
  code: 'user',
  name: 'User',
  permissions: [],
};

const mockUser: User = {
  id: '1',
  username: 'testuser',
  email: 'test@example.com',
  firstName: 'Test',
  lastName: 'User',
  fullName: 'Test User',
  role: mockRole,
  permissions: [],
  isActive: true,
  createdAt: '2024-01-01T00:00:00Z',
};

describe('authSlice', () => {
  describe('reducers', () => {
    it('should return initial state', () => {
      const state = authReducer(undefined, { type: 'unknown' });
      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
    });

    it('should handle setCredentials', () => {
      const credentials = {
        user: mockUser,
        token: 'token',
        refreshToken: 'refreshToken',
      };
      const state = authReducer(undefined, setCredentials(credentials));
      expect(state.user).toEqual(mockUser);
      expect(state.isAuthenticated).toBe(true);
      expect(state.token).toBe('token');
    });

    it('should handle logout', () => {
      const initialState: AuthState = {
        user: mockUser,
        isAuthenticated: true,
        isLoading: false,
        error: null,
        token: 'token',
        refreshToken: 'refreshToken',
      };
      const action = { type: logout.fulfilled.type };
      const state = authReducer(initialState, action);
      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.token).toBeNull();
    });

    it('should handle updateUser', () => {
      const initialState: AuthState = {
        user: mockUser,
        isAuthenticated: true,
        isLoading: false,
        error: null,
        token: 'token',
        refreshToken: 'refreshToken',
      };
      const state = authReducer(initialState, updateUser({ firstName: 'Updated' }));
      expect((state.user as User)?.firstName).toBe('Updated');
    });

    it('should handle clearError', () => {
      const initialState: AuthState = {
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: 'Some error',
        token: null,
        refreshToken: null,
      };
      const state = authReducer(initialState, clearError());
      expect(state.error).toBeNull();
    });
  });

  describe('async thunks', () => {
    it('should handle login.pending', () => {
      const action = { type: login.pending.type };
      const state = authReducer(undefined, action);
      expect(state.isLoading).toBe(true);
      expect(state.error).toBeNull();
    });

    it('should handle login.fulfilled', () => {
      const payload = {
        user: mockUser,
        access: 'access_token',
        refresh: 'refresh_token',
      };
      const action = { type: login.fulfilled.type, payload };
      const state = authReducer(undefined, action);
      expect(state.isLoading).toBe(false);
      expect(state.user).toEqual(mockUser);
      expect(state.isAuthenticated).toBe(true);
      expect(state.token).toBe('access_token');
    });

    it('should handle login.rejected', () => {
      const action = {
        type: login.rejected.type,
        payload: 'Invalid credentials',
      };
      const state = authReducer(undefined, action);
      expect(state.isLoading).toBe(false);
      expect(state.error).toBe('Invalid credentials');
    });
  });
});
