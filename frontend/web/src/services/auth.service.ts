// ========================================================
// SISTEMA ERP UNIVERSAL - Servicio de Autenticación
// ========================================================

import { api } from './api';
import type {
  LoginCredentials,
  LoginResponse,
  User,
  RegisterData,
  PasswordResetRequest,
  PasswordResetConfirm,
  ChangePasswordData,
  ProfileUpdateData,
} from '@/types/auth';

const AUTH_ENDPOINTS = {
  LOGIN: '/auth/login/',
  LOGOUT: '/auth/logout/',
  REGISTER: '/auth/register/',
  REFRESH: '/auth/refresh/',
  PROFILE: '/auth/profile/',
  CHANGE_PASSWORD: '/auth/change-password/',
  RESET_PASSWORD: '/auth/password-reset/',
  RESET_PASSWORD_CONFIRM: '/auth/password-reset/confirm/',
  VERIFY_EMAIL: '/auth/verify-email/',
};

export const authService = {
  /**
   * Iniciar sesión
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>(AUTH_ENDPOINTS.LOGIN, credentials);
    return response.data;
  },

  /**
   * Cerrar sesión
   */
  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refreshToken');
    if (refreshToken) {
      try {
        await api.post(AUTH_ENDPOINTS.LOGOUT, { refresh: refreshToken });
      } catch (error) {
        // Ignorar errores de logout - el token podría ya estar expirado
        console.warn('Error durante logout:', error);
      }
    }
  },

  /**
   * Registrar nuevo usuario
   */
  async register(data: RegisterData): Promise<User> {
    const response = await api.post<User>(AUTH_ENDPOINTS.REGISTER, data);
    return response.data;
  },

  /**
   * Refrescar token de acceso
   */
  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    const response = await api.post<{ access: string }>(AUTH_ENDPOINTS.REFRESH, {
      refresh: refreshToken,
    });
    return response.data;
  },

  /**
   * Obtener perfil del usuario actual
   */
  async getProfile(): Promise<User> {
    const response = await api.get<User>(AUTH_ENDPOINTS.PROFILE);
    return response.data;
  },

  /**
   * Actualizar perfil
   */
  async updateProfile(data: ProfileUpdateData): Promise<User> {
    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined) {
        formData.append(key, value);
      }
    });
    const response = await api.patch<User>(AUTH_ENDPOINTS.PROFILE, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  /**
   * Cambiar contraseña
   */
  async changePassword(data: ChangePasswordData): Promise<void> {
    await api.post(AUTH_ENDPOINTS.CHANGE_PASSWORD, data);
  },

  /**
   * Solicitar restablecimiento de contraseña
   */
  async requestPasswordReset(data: PasswordResetRequest): Promise<void> {
    await api.post(AUTH_ENDPOINTS.RESET_PASSWORD, data);
  },

  /**
   * Confirmar restablecimiento de contraseña
   */
  async confirmPasswordReset(data: PasswordResetConfirm): Promise<void> {
    await api.post(AUTH_ENDPOINTS.RESET_PASSWORD_CONFIRM, data);
  },

  /**
   * Verificar email
   */
  async verifyEmail(token: string): Promise<void> {
    await api.post(AUTH_ENDPOINTS.VERIFY_EMAIL, { token });
  },
};
