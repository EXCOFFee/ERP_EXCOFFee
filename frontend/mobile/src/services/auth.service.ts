import api from './api';
import {
  LoginCredentials,
  LoginResponse,
  RegisterData,
  RefreshTokenResponse,
  PasswordChangeData,
  PasswordResetData,
  PasswordResetConfirmData,
  User,
} from '../types/auth';

class AuthService {
  private basePath = '/auth';

  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>(`${this.basePath}/token/`, {
      email: credentials.email,
      password: credentials.password,
    });
    return response.data;
  }

  async register(data: RegisterData): Promise<User> {
    const response = await api.post<User>(`${this.basePath}/register/`, data);
    return response.data;
  }

  async logout(): Promise<void> {
    await api.post(`${this.basePath}/logout/`);
  }

  async refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
    const response = await api.post<RefreshTokenResponse>(
      `${this.basePath}/token/refresh/`,
      { refresh: refreshToken }
    );
    return response.data;
  }

  async getProfile(): Promise<User> {
    const response = await api.get<User>(`${this.basePath}/profile/`);
    return response.data;
  }

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await api.patch<User>(`${this.basePath}/profile/`, data);
    return response.data;
  }

  async changePassword(data: PasswordChangeData): Promise<void> {
    await api.post(`${this.basePath}/password/change/`, {
      old_password: data.currentPassword,
      new_password: data.newPassword,
      confirm_password: data.confirmPassword,
    });
  }

  async requestPasswordReset(data: PasswordResetData): Promise<void> {
    await api.post(`${this.basePath}/password/reset/`, data);
  }

  async confirmPasswordReset(data: PasswordResetConfirmData): Promise<void> {
    await api.post(`${this.basePath}/password/reset/confirm/`, {
      uid: data.uid,
      token: data.token,
      new_password: data.newPassword,
      confirm_password: data.confirmPassword,
    });
  }

  async verifyToken(token: string): Promise<boolean> {
    try {
      await api.post(`${this.basePath}/token/verify/`, { token });
      return true;
    } catch {
      return false;
    }
  }
}

export const authService = new AuthService();
