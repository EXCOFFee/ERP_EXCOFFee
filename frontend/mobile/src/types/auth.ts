// Tipos de autenticación

export interface User {
  id: number;
  email: string;
  username: string;
  firstName: string;
  lastName: string;
  fullName: string;
  avatar?: string;
  isActive: boolean;
  isStaff: boolean;
  isSuperuser: boolean;
  roles: Role[];
  permissions: string[];
  company?: Company;
  createdAt: string;
  lastLogin?: string;
}

export interface Role {
  id: number;
  name: string;
  code: string;
  permissions: string[];
}

export interface Company {
  id: number;
  name: string;
  logo?: string;
  taxId?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface RefreshTokenResponse {
  access: string;
  refresh?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface PasswordChangeData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface PasswordResetData {
  email: string;
}

export interface PasswordResetConfirmData {
  uid: string;
  token: string;
  newPassword: string;
  confirmPassword: string;
}
