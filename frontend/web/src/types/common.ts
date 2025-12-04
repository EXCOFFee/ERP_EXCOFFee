// ========================================================
// SISTEMA ERP UNIVERSAL - Tipos comunes
// ========================================================

// Respuesta paginada de la API
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Parámetros de paginación
export interface PaginationParams {
  page?: number;
  pageSize?: number;
  ordering?: string;
  search?: string;
}

// Respuesta de error de la API
export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, string[]>;
}

// Estado de carga
export type LoadingState = 'idle' | 'loading' | 'succeeded' | 'failed';

// Opciones de select
export interface SelectOption<T = string> {
  value: T;
  label: string;
  disabled?: boolean;
}

// Filtros base
export interface BaseFilters {
  search?: string;
  isActive?: boolean;
  createdFrom?: string;
  createdTo?: string;
}

// Columna de tabla
export interface TableColumn<T> {
  id: keyof T | string;
  label: string;
  sortable?: boolean;
  width?: number | string;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, row: T) => React.ReactNode;
}

// Acción de menú
export interface MenuAction {
  label: string;
  icon?: React.ReactNode;
  onClick: () => void;
  color?: 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'success';
  disabled?: boolean;
  divider?: boolean;
}

// Breadcrumb item
export interface BreadcrumbItem {
  label: string;
  path?: string;
  icon?: React.ReactNode;
}

// Estadísticas de dashboard
export interface DashboardStat {
  label: string;
  value: number | string;
  change?: number;
  changeType?: 'increase' | 'decrease';
  icon?: React.ReactNode;
  color?: string;
}

// Gráfico de datos
export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

export interface ChartDataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
  borderColor?: string | string[];
  borderWidth?: number;
}

// Notificación
export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  read: boolean;
  createdAt: string;
  link?: string;
}

// Auditoría
export interface AuditInfo {
  createdAt: string;
  createdBy?: string;
  updatedAt: string;
  updatedBy?: string;
}

// Entidad base
export interface BaseEntity extends AuditInfo {
  id: string;
  isActive: boolean;
}

// Documento base
export interface BaseDocument extends BaseEntity {
  number: string;
  date: string;
  status: string;
  notes?: string;
}

// Dirección
export interface Address {
  id?: string;
  addressType?: 'billing' | 'shipping' | 'main' | 'other';
  street: string;
  street2?: string;
  city: string;
  state?: string;
  postalCode?: string;
  country: string;
  isDefault?: boolean;
}

// Contacto
export interface Contact {
  id?: string;
  name: string;
  position?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  isPrimary?: boolean;
}

// Moneda
export interface Currency {
  id: string;
  code: string;
  name: string;
  symbol: string;
  exchangeRate: number;
  isDefault: boolean;
}

// Unidad de medida
export interface UnitOfMeasure {
  id: string;
  code: string;
  name: string;
  symbol: string;
  category: string;
}

// Impuesto
export interface Tax {
  id: string;
  code: string;
  name: string;
  rate: number;
  type: 'percentage' | 'fixed';
  isDefault: boolean;
}

// Archivo adjunto
export interface Attachment {
  id: string;
  name: string;
  type: string;
  size: number;
  url: string;
  uploadedAt: string;
  uploadedBy?: string;
}
