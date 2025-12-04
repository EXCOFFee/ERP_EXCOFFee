import api from './api';

export interface Product {
  id: string;
  sku: string;
  name: string;
  description?: string;
  category: string;
  price: number;
  cost: number;
  stock: number;
  minStock: number;
  unit: string;
  barcode?: string;
  imageUrl?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Warehouse {
  id: string;
  code: string;
  name: string;
  address?: string;
  isActive: boolean;
}

export interface StockMovement {
  id: string;
  productId: string;
  warehouseId: string;
  type: 'in' | 'out' | 'transfer' | 'adjustment';
  quantity: number;
  reason?: string;
  reference?: string;
  createdAt: string;
  createdBy: string;
}

export interface ProductFilters {
  search?: string;
  category?: string;
  isActive?: boolean;
  lowStock?: boolean;
  page?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

class InventoryService {
  // Products
  async getProducts(filters: ProductFilters = {}): Promise<PaginatedResponse<Product>> {
    const { data } = await api.get('/inventory/products', { params: filters });
    return data;
  }

  async getProduct(id: string): Promise<Product> {
    const { data } = await api.get(`/inventory/products/${id}`);
    return data;
  }

  async getProductByBarcode(barcode: string): Promise<Product> {
    const { data } = await api.get(`/inventory/products/barcode/${barcode}`);
    return data;
  }

  async createProduct(product: Partial<Product>): Promise<Product> {
    const { data } = await api.post('/inventory/products', product);
    return data;
  }

  async updateProduct(id: string, product: Partial<Product>): Promise<Product> {
    const { data } = await api.patch(`/inventory/products/${id}`, product);
    return data;
  }

  async deleteProduct(id: string): Promise<void> {
    await api.delete(`/inventory/products/${id}`);
  }

  // Warehouses
  async getWarehouses(): Promise<Warehouse[]> {
    const { data } = await api.get('/inventory/warehouses');
    return data;
  }

  async getWarehouse(id: string): Promise<Warehouse> {
    const { data } = await api.get(`/inventory/warehouses/${id}`);
    return data;
  }

  // Stock
  async getProductStock(productId: string, warehouseId?: string): Promise<{ stock: number; reserved: number; available: number }> {
    const { data } = await api.get(`/inventory/stock/${productId}`, { 
      params: warehouseId ? { warehouseId } : {} 
    });
    return data;
  }

  async adjustStock(movement: Omit<StockMovement, 'id' | 'createdAt' | 'createdBy'>): Promise<StockMovement> {
    const { data } = await api.post('/inventory/stock/adjust', movement);
    return data;
  }

  async transferStock(
    productId: string,
    fromWarehouseId: string,
    toWarehouseId: string,
    quantity: number
  ): Promise<StockMovement> {
    const { data } = await api.post('/inventory/stock/transfer', {
      productId,
      fromWarehouseId,
      toWarehouseId,
      quantity,
    });
    return data;
  }

  async getStockMovements(productId: string): Promise<StockMovement[]> {
    const { data } = await api.get(`/inventory/stock/movements/${productId}`);
    return data;
  }

  // Categories
  async getCategories(): Promise<string[]> {
    const { data } = await api.get('/inventory/categories');
    return data;
  }

  // Low stock alerts
  async getLowStockProducts(): Promise<Product[]> {
    const { data } = await api.get('/inventory/products', { 
      params: { lowStock: true } 
    });
    return data.data;
  }
}

export const inventoryService = new InventoryService();
export default inventoryService;
