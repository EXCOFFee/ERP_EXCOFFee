import api from './api';

export interface Customer {
  id: string;
  code: string;
  name: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  taxId?: string;
  creditLimit?: number;
  balance: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface OrderItem {
  id: string;
  productId: string;
  productName: string;
  productSku: string;
  quantity: number;
  unitPrice: number;
  discount: number;
  tax: number;
  total: number;
}

export interface Order {
  id: string;
  orderNumber: string;
  customerId: string;
  customerName: string;
  status: 'draft' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  items: OrderItem[];
  subtotal: number;
  discount: number;
  tax: number;
  total: number;
  notes?: string;
  shippingAddress?: string;
  paymentMethod?: string;
  paymentStatus: 'pending' | 'partial' | 'paid';
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

export interface Invoice {
  id: string;
  invoiceNumber: string;
  orderId: string;
  customerId: string;
  customerName: string;
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';
  items: OrderItem[];
  subtotal: number;
  discount: number;
  tax: number;
  total: number;
  amountPaid: number;
  balance: number;
  dueDate: string;
  paidDate?: string;
  createdAt: string;
}

export interface CustomerFilters {
  search?: string;
  isActive?: boolean;
  hasBalance?: boolean;
  page?: number;
  limit?: number;
}

export interface OrderFilters {
  search?: string;
  customerId?: string;
  status?: string;
  paymentStatus?: string;
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

class SalesService {
  // Customers
  async getCustomers(filters: CustomerFilters = {}): Promise<PaginatedResponse<Customer>> {
    const { data } = await api.get('/sales/customers', { params: filters });
    return data;
  }

  async getCustomer(id: string): Promise<Customer> {
    const { data } = await api.get(`/sales/customers/${id}`);
    return data;
  }

  async createCustomer(customer: Partial<Customer>): Promise<Customer> {
    const { data } = await api.post('/sales/customers', customer);
    return data;
  }

  async updateCustomer(id: string, customer: Partial<Customer>): Promise<Customer> {
    const { data } = await api.patch(`/sales/customers/${id}`, customer);
    return data;
  }

  async deleteCustomer(id: string): Promise<void> {
    await api.delete(`/sales/customers/${id}`);
  }

  async getCustomerOrders(customerId: string): Promise<Order[]> {
    const { data } = await api.get(`/sales/customers/${customerId}/orders`);
    return data;
  }

  async getCustomerBalance(customerId: string): Promise<{ balance: number; creditLimit: number; available: number }> {
    const { data } = await api.get(`/sales/customers/${customerId}/balance`);
    return data;
  }

  // Orders
  async getOrders(filters: OrderFilters = {}): Promise<PaginatedResponse<Order>> {
    const { data } = await api.get('/sales/orders', { params: filters });
    return data;
  }

  async getOrder(id: string): Promise<Order> {
    const { data } = await api.get(`/sales/orders/${id}`);
    return data;
  }

  async createOrder(order: Partial<Order>): Promise<Order> {
    const { data } = await api.post('/sales/orders', order);
    return data;
  }

  async updateOrder(id: string, order: Partial<Order>): Promise<Order> {
    const { data } = await api.patch(`/sales/orders/${id}`, order);
    return data;
  }

  async confirmOrder(id: string): Promise<Order> {
    const { data } = await api.post(`/sales/orders/${id}/confirm`);
    return data;
  }

  async cancelOrder(id: string, reason?: string): Promise<Order> {
    const { data } = await api.post(`/sales/orders/${id}/cancel`, { reason });
    return data;
  }

  async shipOrder(id: string, trackingNumber?: string): Promise<Order> {
    const { data } = await api.post(`/sales/orders/${id}/ship`, { trackingNumber });
    return data;
  }

  async deliverOrder(id: string): Promise<Order> {
    const { data } = await api.post(`/sales/orders/${id}/deliver`);
    return data;
  }

  // Invoices
  async getInvoices(filters: OrderFilters = {}): Promise<PaginatedResponse<Invoice>> {
    const { data } = await api.get('/sales/invoices', { params: filters });
    return data;
  }

  async getInvoice(id: string): Promise<Invoice> {
    const { data } = await api.get(`/sales/invoices/${id}`);
    return data;
  }

  async createInvoiceFromOrder(orderId: string): Promise<Invoice> {
    const { data } = await api.post(`/sales/invoices/from-order/${orderId}`);
    return data;
  }

  async recordPayment(invoiceId: string, amount: number, method: string): Promise<Invoice> {
    const { data } = await api.post(`/sales/invoices/${invoiceId}/payment`, { amount, method });
    return data;
  }

  // Dashboard stats
  async getDashboardStats(): Promise<{
    todaySales: number;
    monthSales: number;
    pendingOrders: number;
    overdueInvoices: number;
  }> {
    const { data } = await api.get('/sales/dashboard/stats');
    return data;
  }
}

export const salesService = new SalesService();
export default salesService;
