// ========================================================
// SISTEMA ERP UNIVERSAL - Servicio de Ventas
// ========================================================

import { api, apiGet, apiPost, apiPut } from './api';
import type { PaginatedResponse, ListParams } from './inventory.service';

// Tipos
export interface CustomerGroup {
  id: string;
  code: string;
  name: string;
  description?: string;
  discount_percentage: number;
  credit_limit: number;
  payment_terms?: string;
  is_active: boolean;
}

export interface Customer {
  id: string;
  code: string;
  name: string;
  legal_name?: string;
  tax_id?: string;
  customer_type: 'individual' | 'company';
  group?: CustomerGroup;
  email?: string;
  phone?: string;
  mobile?: string;
  website?: string;
  credit_limit: number;
  current_balance: number;
  is_active: boolean;
  created_at: string;
}

export interface CustomerAddress {
  id: string;
  customer: string;
  address_type: 'billing' | 'shipping' | 'both';
  address_line1: string;
  address_line2?: string;
  city: string;
  state?: string;
  postal_code?: string;
  country: string;
  is_default: boolean;
}

export interface SalesQuotation {
  id: string;
  number: string;
  customer: Customer;
  date: string;
  valid_until: string;
  status: 'draft' | 'sent' | 'accepted' | 'rejected' | 'expired' | 'converted';
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total: number;
  notes?: string;
  items: SalesQuotationItem[];
}

export interface SalesQuotationItem {
  id: string;
  product: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  discount_percent: number;
  tax_percent: number;
  subtotal: number;
  total: number;
}

export interface SalesOrder {
  id: string;
  number: string;
  customer: Customer;
  quotation?: string;
  date: string;
  delivery_date?: string;
  status: 'draft' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  payment_status: 'pending' | 'partial' | 'paid';
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total: number;
  amount_paid: number;
  notes?: string;
  items: SalesOrderItem[];
}

export interface SalesOrderItem {
  id: string;
  product: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  discount_percent: number;
  tax_percent: number;
  subtotal: number;
  total: number;
  quantity_shipped: number;
}

export interface SalesInvoice {
  id: string;
  number: string;
  customer: Customer;
  order?: string;
  date: string;
  due_date: string;
  status: 'draft' | 'sent' | 'paid' | 'partial' | 'overdue' | 'cancelled';
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total: number;
  amount_paid: number;
  balance: number;
}

export interface CustomerPayment {
  id: string;
  number: string;
  customer: Customer;
  date: string;
  amount: number;
  payment_method: string;
  reference?: string;
  notes?: string;
}

// ========== GRUPOS DE CLIENTES ==========
export const customerGroupService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<CustomerGroup>>('/sales/customer-groups/', params),
  
  get: (id: string) => 
    apiGet<CustomerGroup>(`/sales/customer-groups/${id}/`),
  
  create: (data: Partial<CustomerGroup>) => 
    apiPost<CustomerGroup>('/sales/customer-groups/', data),
  
  update: (id: string, data: Partial<CustomerGroup>) => 
    apiPut<CustomerGroup>(`/sales/customer-groups/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/sales/customer-groups/${id}/`),
};

// ========== CLIENTES ==========
export const customerService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<Customer>>('/sales/customers/', params),
  
  get: (id: string) => 
    apiGet<Customer>(`/sales/customers/${id}/`),
  
  create: (data: Partial<Customer>) => 
    apiPost<Customer>('/sales/customers/', data),
  
  update: (id: string, data: Partial<Customer>) => 
    apiPut<Customer>(`/sales/customers/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/sales/customers/${id}/`),
  
  getStatement: (id: string) => 
    apiGet(`/sales/customers/${id}/statement/`),
  
  getOrders: (id: string, params?: ListParams) => 
    apiGet<PaginatedResponse<SalesOrder>>(`/sales/customers/${id}/orders/`, params),
  
  getInvoices: (id: string, params?: ListParams) => 
    apiGet<PaginatedResponse<SalesInvoice>>(`/sales/customers/${id}/invoices/`, params),
};

// ========== COTIZACIONES ==========
export const quotationService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<SalesQuotation>>('/sales/quotations/', params),
  
  get: (id: string) => 
    apiGet<SalesQuotation>(`/sales/quotations/${id}/`),
  
  create: (data: any) => 
    apiPost<SalesQuotation>('/sales/quotations/', data),
  
  update: (id: string, data: any) => 
    apiPut<SalesQuotation>(`/sales/quotations/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/sales/quotations/${id}/`),
  
  send: (id: string) => 
    apiPost(`/sales/quotations/${id}/send/`),
  
  accept: (id: string) => 
    apiPost(`/sales/quotations/${id}/accept/`),
  
  reject: (id: string) => 
    apiPost(`/sales/quotations/${id}/reject/`),
  
  convertToOrder: (id: string) => 
    apiPost<SalesOrder>(`/sales/quotations/${id}/convert-to-order/`),
};

// ========== ÓRDENES DE VENTA ==========
export const salesOrderService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<SalesOrder>>('/sales/orders/', params),
  
  get: (id: string) => 
    apiGet<SalesOrder>(`/sales/orders/${id}/`),
  
  create: (data: any) => 
    apiPost<SalesOrder>('/sales/orders/', data),
  
  update: (id: string, data: any) => 
    apiPut<SalesOrder>(`/sales/orders/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/sales/orders/${id}/`),
  
  confirm: (id: string) => 
    apiPost(`/sales/orders/${id}/confirm/`),
  
  cancel: (id: string) => 
    apiPost(`/sales/orders/${id}/cancel/`),
  
  createInvoice: (id: string) => 
    apiPost<SalesInvoice>(`/sales/orders/${id}/create-invoice/`),
};

// ========== FACTURAS ==========
export const salesInvoiceService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<SalesInvoice>>('/sales/invoices/', params),
  
  get: (id: string) => 
    apiGet<SalesInvoice>(`/sales/invoices/${id}/`),
  
  create: (data: any) => 
    apiPost<SalesInvoice>('/sales/invoices/', data),
  
  update: (id: string, data: any) => 
    apiPut<SalesInvoice>(`/sales/invoices/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/sales/invoices/${id}/`),
  
  send: (id: string) => 
    apiPost(`/sales/invoices/${id}/send/`),
  
  markAsPaid: (id: string) => 
    apiPost(`/sales/invoices/${id}/mark-paid/`),
};

// ========== PAGOS ==========
export const customerPaymentService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<CustomerPayment>>('/sales/payments/', params),
  
  get: (id: string) => 
    apiGet<CustomerPayment>(`/sales/payments/${id}/`),
  
  create: (data: any) => 
    apiPost<CustomerPayment>('/sales/payments/', data),
  
  delete: (id: string) => 
    api.delete(`/sales/payments/${id}/`),
};

// ========== REPORTES ==========
export const salesReportService = {
  getSummary: (params?: { start_date?: string; end_date?: string }) => 
    apiGet('/sales/reports/summary/', params),
  
  getByCustomer: (params?: { start_date?: string; end_date?: string }) => 
    apiGet('/sales/reports/by-customer/', params),
  
  getByProduct: (params?: { start_date?: string; end_date?: string }) => 
    apiGet('/sales/reports/by-product/', params),
  
  getTopProducts: (params?: { limit?: number; start_date?: string; end_date?: string }) => 
    apiGet('/sales/reports/top-products/', params),
  
  getTopCustomers: (params?: { limit?: number; start_date?: string; end_date?: string }) => 
    apiGet('/sales/reports/top-customers/', params),
};

// ========== SERVICIO UNIFICADO DE VENTAS ==========
export const salesService = {
  // Clientes
  getCustomers: customerService.list,
  getCustomer: customerService.get,
  createCustomer: customerService.create,
  updateCustomer: customerService.update,
  deleteCustomer: customerService.delete,
  getCustomerGroups: () => customerGroupService.list(),

  // Pedidos (alias para compatibilidad)
  getSalesOrders: salesOrderService.list,
  getOrders: salesOrderService.list,
  getOrder: salesOrderService.get,
  getSalesOrder: salesOrderService.get,
  createOrder: salesOrderService.create,
  updateOrder: salesOrderService.update,
  deleteOrder: salesOrderService.delete,
  confirmOrder: salesOrderService.confirm,
  cancelOrder: salesOrderService.cancel,

  // Facturas
  getInvoices: salesInvoiceService.list,
  getInvoice: salesInvoiceService.get,
  createInvoice: salesInvoiceService.create,
  updateInvoice: salesInvoiceService.update,
  deleteInvoice: salesInvoiceService.delete,
  sendInvoice: salesInvoiceService.send,

  // Pagos
  getPayments: customerPaymentService.list,
  getPayment: customerPaymentService.get,
  createPayment: customerPaymentService.create,

  // Reportes
  getReports: salesReportService,
};
