// ========================================================
// SISTEMA ERP UNIVERSAL - Tipos de Autenticación
// ========================================================

export interface User {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  fullName: string;
  avatar?: string;
  role: Role;
  permissions: string[];
  company?: Company;
  branch?: Branch;
  isActive: boolean;
  lastLogin?: string;
  createdAt: string;
}

export interface Role {
  id: string;
  code: string;
  name: string;
  permissions: Permission[];
}

export interface Permission {
  id: string;
  code: string;
  name: string;
  module: string;
}

export interface Company {
  id: string;
  code: string;
  name: string;
  logo?: string;
}

export interface Branch {
  id: string;
  code: string;
  name: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: {
    id: string;
    email: string;
    full_name: string;
    role: string | null;
    role_code: string | null;
    is_superuser: boolean;
  };
}

// Usuario simplificado que viene del login
export interface LoginUser {
  id: string;
  email: string;
  full_name: string;
  role: string | null;
  role_code: string | null;
  is_superuser: boolean;
}

export interface AuthState {
  user: User | LoginUser | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  password: string;
  confirmPassword: string;
}

export interface ChangePasswordData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface ProfileUpdateData {
  firstName?: string;
  lastName?: string;
  email?: string;
  phone?: string;
  avatar?: File;
}
