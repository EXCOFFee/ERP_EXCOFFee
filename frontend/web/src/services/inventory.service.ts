// ========================================================
// SISTEMA ERP UNIVERSAL - Servicio de Inventario
// ========================================================

import { api, apiGet, apiPost, apiPut } from './api';

// Tipos
export interface Category {
  id: string;
  code: string;
  name: string;
  description?: string;
  parent?: string;
  level: number;
  is_active: boolean;
  children?: Category[];
}

export interface Brand {
  id: string;
  code: string;
  name: string;
  description?: string;
  logo?: string;
  website?: string;
  is_active: boolean;
}

export interface UnitOfMeasure {
  id: string;
  code: string;
  name: string;
  symbol: string;
  unit_type: 'unit' | 'weight' | 'volume' | 'length' | 'area' | 'time';
  is_active: boolean;
}

export interface Warehouse {
  id: string;
  code: string;
  name: string;
  address?: string;
  city?: string;
  manager?: string;
  is_active: boolean;
}

export interface Product {
  id: string;
  sku: string;
  barcode?: string;
  name: string;
  description?: string;
  category?: Category;
  brand?: Brand;
  unit: UnitOfMeasure;
  cost_price: number;
  sale_price: number;
  min_stock: number;
  max_stock: number;
  reorder_point: number;
  is_active: boolean;
  track_inventory: boolean;
  track_lots: boolean;
  track_serials: boolean;
  image?: string;
  created_at: string;
  updated_at: string;
}

export interface Stock {
  id: string;
  product: Product;
  warehouse: Warehouse;
  quantity: number;
  reserved_quantity: number;
  available_quantity: number;
}

export interface StockMovement {
  id: string;
  product: string;
  warehouse: string;
  movement_type: 'in' | 'out' | 'adjustment' | 'transfer';
  quantity: number;
  reference?: string;
  notes?: string;
  created_at: string;
  created_by: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ListParams {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
  is_active?: boolean;
  [key: string]: any;
}

// ========== CATEGORÍAS ==========
export const categoryService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<Category>>('/inventory/categories/', params),
  
  getTree: () => 
    apiGet<Category[]>('/inventory/categories/tree/'),
  
  get: (id: string) => 
    apiGet<Category>(`/inventory/categories/${id}/`),
  
  create: (data: Partial<Category>) => 
    apiPost<Category>('/inventory/categories/', data),
  
  update: (id: string, data: Partial<Category>) => 
    apiPut<Category>(`/inventory/categories/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/inventory/categories/${id}/`),
};

// ========== MARCAS ==========
export const brandService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<Brand>>('/inventory/brands/', params),
  
  get: (id: string) => 
    apiGet<Brand>(`/inventory/brands/${id}/`),
  
  create: (data: Partial<Brand>) => 
    apiPost<Brand>('/inventory/brands/', data),
  
  update: (id: string, data: Partial<Brand>) => 
    apiPut<Brand>(`/inventory/brands/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/inventory/brands/${id}/`),
};

// ========== UNIDADES DE MEDIDA ==========
export const unitService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<UnitOfMeasure>>('/inventory/units/', params),
  
  get: (id: string) => 
    apiGet<UnitOfMeasure>(`/inventory/units/${id}/`),
  
  create: (data: Partial<UnitOfMeasure>) => 
    apiPost<UnitOfMeasure>('/inventory/units/', data),
  
  update: (id: string, data: Partial<UnitOfMeasure>) => 
    apiPut<UnitOfMeasure>(`/inventory/units/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/inventory/units/${id}/`),
};

// ========== ALMACENES ==========
export const warehouseService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<Warehouse>>('/inventory/warehouses/', params),
  
  get: (id: string) => 
    apiGet<Warehouse>(`/inventory/warehouses/${id}/`),
  
  create: (data: Partial<Warehouse>) => 
    apiPost<Warehouse>('/inventory/warehouses/', data),
  
  update: (id: string, data: Partial<Warehouse>) => 
    apiPut<Warehouse>(`/inventory/warehouses/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/inventory/warehouses/${id}/`),
  
  getStock: (id: string) => 
    apiGet<Stock[]>(`/inventory/warehouses/${id}/stock/`),
};

// ========== PRODUCTOS ==========
export const productService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<Product>>('/inventory/products/', params),
  
  get: (id: string) => 
    apiGet<Product>(`/inventory/products/${id}/`),
  
  getByCode: (code: string) => 
    apiGet<Product>(`/inventory/products/by-code/${code}/`),
  
  create: (data: Partial<Product>) => 
    apiPost<Product>('/inventory/products/', data),
  
  update: (id: string, data: Partial<Product>) => 
    apiPut<Product>(`/inventory/products/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/inventory/products/${id}/`),
  
  getStock: (id: string) => 
    apiGet<Stock[]>(`/inventory/products/${id}/stock/`),
  
  getMovements: (id: string, params?: ListParams) => 
    apiGet<PaginatedResponse<StockMovement>>(`/inventory/products/${id}/movements/`, params),
};

// ========== STOCK ==========
export const stockService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<Stock>>('/inventory/stock/', params),
  
  get: (id: string) => 
    apiGet<Stock>(`/inventory/stock/${id}/`),
  
  addStock: (data: { product: string; warehouse: string; quantity: number; notes?: string }) => 
    apiPost<Stock>('/inventory/stock/add/', data),
  
  removeStock: (data: { product: string; warehouse: string; quantity: number; notes?: string }) => 
    apiPost<Stock>('/inventory/stock/remove/', data),
  
  adjustStock: (data: { product: string; warehouse: string; quantity: number; reason: string }) => 
    apiPost<Stock>('/inventory/stock/adjust/', data),
};

// ========== MOVIMIENTOS DE STOCK ==========
export const stockMovementService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<StockMovement>>('/inventory/stock-movements/', params),
  
  get: (id: string) => 
    apiGet<StockMovement>(`/inventory/stock-movements/${id}/`),
  
  create: (data: Partial<StockMovement>) => 
    apiPost<StockMovement>('/inventory/stock-movements/', data),
};

// ========== SERVICIO UNIFICADO DE INVENTARIO ==========
export const inventoryService = {
  // Categorías
  getCategories: (params?: ListParams) => categoryService.list(params),
  getCategory: categoryService.get,
  createCategory: categoryService.create,
  updateCategory: categoryService.update,
  deleteCategory: categoryService.delete,
  getCategoryTree: categoryService.getTree,

  // Marcas
  getBrands: (params?: ListParams) => brandService.list(params),
  getBrand: brandService.get,
  createBrand: brandService.create,
  updateBrand: brandService.update,
  deleteBrand: brandService.delete,

  // Unidades de medida
  getUnits: (params?: ListParams) => unitService.list(params),
  getUnit: unitService.get,
  createUnit: unitService.create,
  updateUnit: unitService.update,
  deleteUnit: unitService.delete,

  // Almacenes
  getWarehouses: (params?: ListParams) => warehouseService.list(params),
  getWarehouse: warehouseService.get,
  createWarehouse: warehouseService.create,
  updateWarehouse: warehouseService.update,
  deleteWarehouse: warehouseService.delete,
  getWarehouseStock: warehouseService.getStock,

  // Productos
  getProducts: (params?: ListParams) => productService.list(params),
  getProduct: productService.get,
  getProductByCode: productService.getByCode,
  createProduct: productService.create,
  updateProduct: productService.update,
  deleteProduct: productService.delete,
  getProductStock: productService.getStock,
  getProductMovements: productService.getMovements,

  // Stock
  getStock: stockService.list,
  addStock: stockService.addStock,
  removeStock: stockService.removeStock,
  adjustStock: stockService.adjustStock,

  // Movimientos de Stock
  getStockMovements: (params?: ListParams) => stockMovementService.list(params),
  getStockMovement: stockMovementService.get,
  createStockMovement: stockMovementService.create,
};
