// ========================================================
// SISTEMA ERP UNIVERSAL - Cliente API Axios
// ========================================================

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

// Configuración base
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';
const API_TIMEOUT = 30000;

// Función para obtener el store dinámicamente (evitar dependencia circular)
let storeInstance: any = null;
export const setStoreInstance = (store: any) => {
  storeInstance = store;
};

// Crear instancia de Axios
export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Interceptor de request: agregar token de autenticación
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (storeInstance) {
      const state = storeInstance.getState();
      const token = state.auth.token;
      
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Interceptor de response: manejar errores y refresh de token
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    // Si el error es 401 y no es un retry
    if (error.response?.status === 401 && !originalRequest._retry && storeInstance) {
      originalRequest._retry = true;
      
      try {
        const state = storeInstance.getState();
        const refreshToken = state.auth.refreshToken;
        
        if (refreshToken) {
          // Intentar refrescar el token
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });
          
          const newToken = response.data.access;
          
          // Actualizar el store
          storeInstance.dispatch({ type: 'auth/refreshToken/fulfilled', payload: { token: newToken } });
          
          // Reintentar la petición original
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Si falla el refresh, cerrar sesión
        storeInstance.dispatch({ type: 'auth/logout/fulfilled' });
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Funciones de utilidad para peticiones
export const apiGet = async <T>(url: string, params?: Record<string, any>): Promise<T> => {
  const response = await api.get<T>(url, { params });
  return response.data;
};

export const apiPost = async <T>(url: string, data?: any): Promise<T> => {
  const response = await api.post<T>(url, data);
  return response.data;
};

export const apiPut = async <T>(url: string, data: any): Promise<T> => {
  const response = await api.put<T>(url, data);
  return response.data;
};

export const apiPatch = async <T>(url: string, data: any): Promise<T> => {
  const response = await api.patch<T>(url, data);
  return response.data;
};

export const apiDelete = async <T>(url: string): Promise<T> => {
  const response = await api.delete<T>(url);
  return response.data;
};

// Exportar tipos de error
export type { AxiosError };
