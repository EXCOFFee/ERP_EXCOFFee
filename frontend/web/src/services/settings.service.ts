// ========================================================
// SISTEMA ERP UNIVERSAL - Servicios de Configuración
// ========================================================

import { api, apiGet, apiPost, apiPut } from './api';

// ========== TIPOS ==========
export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone?: string;
  role: Role | null;
  role_id?: string;
  is_active: boolean;
  is_superuser: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

export interface Role {
  id: string;
  code: string;
  name: string;
  description?: string;
  permissions: Permission[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Permission {
  id: string;
  code: string;
  name: string;
  module: string;
  description?: string;
}

export interface Company {
  id: string;
  name: string;
  legal_name: string;
  tax_id: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  logo?: string;
  website?: string;
  currency: string;
  timezone: string;
  date_format: string;
  fiscal_year_start: number;
}

interface ListParams {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
}

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ========== USUARIOS ==========
export const userService = {
  list: (params?: ListParams & { role?: string; is_active?: boolean }) =>
    apiGet<PaginatedResponse<User>>('/auth/users/', params),

  get: (id: string) =>
    apiGet<User>(`/auth/users/${id}/`),

  create: (data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    role_id?: string;
    is_active?: boolean;
  }) =>
    apiPost<User>('/auth/users/', data),

  update: (id: string, data: Partial<User>) =>
    apiPut<User>(`/auth/users/${id}/`, data),

  delete: (id: string) =>
    api.delete(`/auth/users/${id}/`),

  activate: (id: string) =>
    apiPost(`/auth/users/${id}/activate/`),

  deactivate: (id: string) =>
    apiPost(`/auth/users/${id}/deactivate/`),

  resetPassword: (id: string) =>
    apiPost(`/auth/users/${id}/reset-password/`),
};

// ========== ROLES ==========
export const roleService = {
  list: (params?: ListParams) =>
    apiGet<PaginatedResponse<Role>>('/auth/roles/', params),

  get: (id: string) =>
    apiGet<Role>(`/auth/roles/${id}/`),

  create: (data: {
    code: string;
    name: string;
    description?: string;
    permissions?: string[];
  }) =>
    apiPost<Role>('/auth/roles/', data),

  update: (id: string, data: Partial<Role>) =>
    apiPut<Role>(`/auth/roles/${id}/`, data),

  delete: (id: string) =>
    api.delete(`/auth/roles/${id}/`),
};

// ========== PERMISOS ==========
export const permissionService = {
  list: (params?: ListParams & { module?: string }) =>
    apiGet<PaginatedResponse<Permission>>('/auth/permissions/', params),

  getModules: () =>
    apiGet<string[]>('/auth/permissions/modules/'),
};

// ========== EMPRESA ==========
export const companyService = {
  get: () =>
    apiGet<Company>('/core/company/'),

  update: (data: Partial<Company>) =>
    apiPut<Company>('/core/company/', data),

  uploadLogo: (file: File) => {
    const formData = new FormData();
    formData.append('logo', file);
    return api.patch<Company>('/core/company/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// ========== SERVICIO UNIFICADO ==========
export const settingsService = {
  // Usuarios
  getUsers: userService.list,
  getUser: userService.get,
  createUser: userService.create,
  updateUser: userService.update,
  deleteUser: userService.delete,

  // Roles
  getRoles: roleService.list,
  getRole: roleService.get,
  createRole: roleService.create,
  updateRole: roleService.update,
  deleteRole: roleService.delete,

  // Permisos
  getPermissions: permissionService.list,

  // Empresa
  getCompany: companyService.get,
  updateCompany: companyService.update,
};
