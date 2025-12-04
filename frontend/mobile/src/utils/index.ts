// Formatters
export const formatCurrency = (value: number, currency = 'USD', locale = 'es-MX'): string => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

export const formatNumber = (value: number, decimals = 0, locale = 'es-MX'): string => {
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
};

export const formatDate = (date: string | Date, locale = 'es-MX'): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const formatDateTime = (date: string | Date, locale = 'es-MX'): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleString(locale, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatRelativeTime = (date: string | Date): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHours = Math.floor(diffMin / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSec < 60) return 'Hace un momento';
  if (diffMin < 60) return `Hace ${diffMin} min`;
  if (diffHours < 24) return `Hace ${diffHours}h`;
  if (diffDays < 7) return `Hace ${diffDays} días`;
  return formatDate(d);
};

// Validators
export const isValidEmail = (email: string): boolean => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
};

export const isValidPhone = (phone: string): boolean => {
  const regex = /^\+?[1-9]\d{1,14}$/;
  return regex.test(phone.replace(/[\s\-\(\)]/g, ''));
};

export const isValidTaxId = (taxId: string): boolean => {
  // Mexican RFC format (simplified)
  const regex = /^[A-Z&Ñ]{3,4}[0-9]{6}[A-Z0-9]{3}$/i;
  return regex.test(taxId);
};

// String helpers
export const capitalize = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

export const truncate = (str: string, length: number): string => {
  if (str.length <= length) return str;
  return `${str.substring(0, length)}...`;
};

export const getInitials = (name: string, maxLength = 2): string => {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .substring(0, maxLength);
};

// Array helpers
export const groupBy = <T>(array: T[], key: keyof T): Record<string, T[]> => {
  return array.reduce((result, item) => {
    const groupKey = String(item[key]);
    if (!result[groupKey]) {
      result[groupKey] = [];
    }
    result[groupKey].push(item);
    return result;
  }, {} as Record<string, T[]>);
};

export const sortBy = <T>(array: T[], key: keyof T, order: 'asc' | 'desc' = 'asc'): T[] => {
  return [...array].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];
    if (aVal < bVal) return order === 'asc' ? -1 : 1;
    if (aVal > bVal) return order === 'asc' ? 1 : -1;
    return 0;
  });
};

// Status helpers
export const getStatusColor = (status: string): string => {
  const statusColors: Record<string, string> = {
    // General
    active: '#4caf50',
    inactive: '#9e9e9e',
    pending: '#ff9800',
    completed: '#4caf50',
    cancelled: '#f44336',
    
    // Orders
    draft: '#9e9e9e',
    confirmed: '#2196f3',
    processing: '#ff9800',
    shipped: '#9c27b0',
    delivered: '#4caf50',
    
    // Payments
    paid: '#4caf50',
    partial: '#ff9800',
    overdue: '#f44336',
    
    // Purchase Orders
    sent: '#2196f3',
    received: '#4caf50',
    
    // HR
    vacation: '#ff9800',
    absent: '#f44336',
  };
  
  return statusColors[status.toLowerCase()] || '#9e9e9e';
};

export const getStatusLabel = (status: string): string => {
  const statusLabels: Record<string, string> = {
    // General
    active: 'Activo',
    inactive: 'Inactivo',
    pending: 'Pendiente',
    completed: 'Completado',
    cancelled: 'Cancelado',
    
    // Orders
    draft: 'Borrador',
    confirmed: 'Confirmado',
    processing: 'Procesando',
    shipped: 'Enviado',
    delivered: 'Entregado',
    
    // Payments
    paid: 'Pagado',
    partial: 'Parcial',
    overdue: 'Vencido',
    
    // Purchase Orders
    sent: 'Enviado',
    received: 'Recibido',
    
    // HR
    vacation: 'Vacaciones',
    absent: 'Ausente',
  };
  
  return statusLabels[status.toLowerCase()] || status;
};

// Debounce
export const debounce = <T extends (...args: any[]) => void>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  
  return (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      func(...args);
    }, wait);
  };
};

// Platform-specific
export const isIOS = (): boolean => {
  // Will be replaced with actual Platform check when running
  return false;
};

export const isAndroid = (): boolean => {
  return !isIOS();
};
