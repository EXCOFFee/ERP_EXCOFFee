import api from './api';

export interface Supplier {
  id: string;
  code: string;
  name: string;
  contactName?: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  taxId?: string;
  paymentTerms?: number;
  rating?: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface PurchaseOrderItem {
  id: string;
  productId: string;
  productName: string;
  productSku: string;
  quantity: number;
  unitPrice: number;
  receivedQuantity: number;
  total: number;
}

export interface PurchaseOrder {
  id: string;
  orderNumber: string;
  supplierId: string;
  supplierName: string;
  status: 'draft' | 'sent' | 'confirmed' | 'partial' | 'received' | 'cancelled';
  items: PurchaseOrderItem[];
  subtotal: number;
  tax: number;
  total: number;
  notes?: string;
  expectedDate?: string;
  receivedDate?: string;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

export interface GoodsReceipt {
  id: string;
  receiptNumber: string;
  purchaseOrderId: string;
  supplierId: string;
  supplierName: string;
  status: 'pending' | 'completed' | 'partial';
  items: {
    productId: string;
    productName: string;
    expectedQuantity: number;
    receivedQuantity: number;
    notes?: string;
  }[];
  receivedDate: string;
  receivedBy: string;
  notes?: string;
  createdAt: string;
}

export interface SupplierFilters {
  search?: string;
  isActive?: boolean;
  minRating?: number;
  page?: number;
  limit?: number;
}

export interface PurchaseOrderFilters {
  search?: string;
  supplierId?: string;
  status?: string;
  startDate?: string;
  endDate?: string;
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

class PurchasingService {
  // Suppliers
  async getSuppliers(filters: SupplierFilters = {}): Promise<PaginatedResponse<Supplier>> {
    const { data } = await api.get('/purchasing/suppliers', { params: filters });
    return data;
  }

  async getSupplier(id: string): Promise<Supplier> {
    const { data } = await api.get(`/purchasing/suppliers/${id}`);
    return data;
  }

  async createSupplier(supplier: Partial<Supplier>): Promise<Supplier> {
    const { data } = await api.post('/purchasing/suppliers', supplier);
    return data;
  }

  async updateSupplier(id: string, supplier: Partial<Supplier>): Promise<Supplier> {
    const { data } = await api.patch(`/purchasing/suppliers/${id}`, supplier);
    return data;
  }

  async deleteSupplier(id: string): Promise<void> {
    await api.delete(`/purchasing/suppliers/${id}`);
  }

  async getSupplierOrders(supplierId: string): Promise<PurchaseOrder[]> {
    const { data } = await api.get(`/purchasing/suppliers/${supplierId}/orders`);
    return data;
  }

  async getSupplierProducts(supplierId: string): Promise<{ productId: string; productName: string; lastPrice: number }[]> {
    const { data } = await api.get(`/purchasing/suppliers/${supplierId}/products`);
    return data;
  }

  // Purchase Orders
  async getPurchaseOrders(filters: PurchaseOrderFilters = {}): Promise<PaginatedResponse<PurchaseOrder>> {
    const { data } = await api.get('/purchasing/orders', { params: filters });
    return data;
  }

  async getPurchaseOrder(id: string): Promise<PurchaseOrder> {
    const { data } = await api.get(`/purchasing/orders/${id}`);
    return data;
  }

  async createPurchaseOrder(order: Partial<PurchaseOrder>): Promise<PurchaseOrder> {
    const { data } = await api.post('/purchasing/orders', order);
    return data;
  }

  async updatePurchaseOrder(id: string, order: Partial<PurchaseOrder>): Promise<PurchaseOrder> {
    const { data } = await api.patch(`/purchasing/orders/${id}`, order);
    return data;
  }

  async sendPurchaseOrder(id: string): Promise<PurchaseOrder> {
    const { data } = await api.post(`/purchasing/orders/${id}/send`);
    return data;
  }

  async confirmPurchaseOrder(id: string): Promise<PurchaseOrder> {
    const { data } = await api.post(`/purchasing/orders/${id}/confirm`);
    return data;
  }

  async cancelPurchaseOrder(id: string, reason?: string): Promise<PurchaseOrder> {
    const { data } = await api.post(`/purchasing/orders/${id}/cancel`, { reason });
    return data;
  }

  // Goods Receipt
  async getGoodsReceipts(orderId?: string): Promise<GoodsReceipt[]> {
    const { data } = await api.get('/purchasing/receipts', { 
      params: orderId ? { orderId } : {} 
    });
    return data;
  }

  async getGoodsReceipt(id: string): Promise<GoodsReceipt> {
    const { data } = await api.get(`/purchasing/receipts/${id}`);
    return data;
  }

  async createGoodsReceipt(receipt: {
    purchaseOrderId: string;
    items: { productId: string; receivedQuantity: number; notes?: string }[];
    notes?: string;
  }): Promise<GoodsReceipt> {
    const { data } = await api.post('/purchasing/receipts', receipt);
    return data;
  }

  // Dashboard stats
  async getDashboardStats(): Promise<{
    pendingOrders: number;
    thisMonthSpending: number;
    pendingReceipts: number;
    topSuppliers: { id: string; name: string; totalOrders: number }[];
  }> {
    const { data } = await api.get('/purchasing/dashboard/stats');
    return data;
  }

  // Reorder suggestions
  async getReorderSuggestions(): Promise<{
    productId: string;
    productName: string;
    currentStock: number;
    minStock: number;
    suggestedQuantity: number;
    preferredSupplier?: { id: string; name: string };
  }[]> {
    const { data } = await api.get('/purchasing/reorder-suggestions');
    return data;
  }
}

export const purchasingService = new PurchasingService();
export default purchasingService;
