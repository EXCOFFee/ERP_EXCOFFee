// ========================================================
// SISTEMA ERP UNIVERSAL - Servicio de Compras
// ========================================================

import { api, apiGet, apiPost, apiPut } from './api';
import type { PaginatedResponse, ListParams } from './inventory.service';

// Tipos
export interface SupplierCategory {
  id: string;
  code: string;
  name: string;
  description?: string;
  is_active: boolean;
}

export interface Supplier {
  id: string;
  code: string;
  name: string;
  legal_name?: string;
  tax_id?: string;
  category?: SupplierCategory;
  email?: string;
  phone?: string;
  website?: string;
  payment_terms?: string;
  credit_limit: number;
  current_balance: number;
  rating: number;
  is_active: boolean;
  created_at: string;
}

export interface SupplierContact {
  id: string;
  supplier: string;
  name: string;
  position?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  is_primary: boolean;
}

export interface PurchaseRequisition {
  id: string;
  number: string;
  requester: string;
  department?: string;
  date: string;
  required_date?: string;
  status: 'draft' | 'pending' | 'approved' | 'rejected' | 'ordered';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  notes?: string;
  items: PurchaseRequisitionItem[];
}

export interface PurchaseRequisitionItem {
  id: string;
  product: string;
  product_name: string;
  quantity: number;
  estimated_price?: number;
  notes?: string;
}

export interface PurchaseOrder {
  id: string;
  number: string;
  supplier: Supplier;
  requisition?: string;
  date: string;
  expected_date?: string;
  status: 'draft' | 'sent' | 'confirmed' | 'partial' | 'received' | 'cancelled';
  payment_status: 'pending' | 'partial' | 'paid';
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total: number;
  amount_paid: number;
  notes?: string;
  items: PurchaseOrderItem[];
}

export interface PurchaseOrderItem {
  id: string;
  product: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  discount_percent: number;
  tax_percent: number;
  subtotal: number;
  total: number;
  quantity_received: number;
}

export interface GoodsReceipt {
  id: string;
  number: string;
  purchase_order: string;
  supplier: Supplier;
  date: string;
  status: 'draft' | 'confirmed' | 'cancelled';
  notes?: string;
  items: GoodsReceiptItem[];
}

export interface GoodsReceiptItem {
  id: string;
  order_item: string;
  quantity_received: number;
  warehouse: string;
  notes?: string;
}

export interface SupplierInvoice {
  id: string;
  number: string;
  supplier_invoice_number: string;
  supplier: Supplier;
  purchase_order?: string;
  date: string;
  due_date: string;
  status: 'draft' | 'pending' | 'paid' | 'partial' | 'overdue' | 'cancelled';
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total: number;
  amount_paid: number;
  balance: number;
}

export interface SupplierPayment {
  id: string;
  number: string;
  supplier: Supplier;
  date: string;
  amount: number;
  payment_method: string;
  reference?: string;
  notes?: string;
}

export interface SupplierEvaluation {
  id: string;
  supplier: Supplier;
  evaluation_date: string;
  period_start: string;
  period_end: string;
  quality_score: number;
  delivery_score: number;
  price_score: number;
  service_score: number;
  overall_score: number;
  comments?: string;
}

// ========== CATEGORÍAS DE PROVEEDORES ==========
export const supplierCategoryService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<SupplierCategory>>('/purchasing/supplier-categories/', params),
  
  get: (id: string) => 
    apiGet<SupplierCategory>(`/purchasing/supplier-categories/${id}/`),
  
  create: (data: Partial<SupplierCategory>) => 
    apiPost<SupplierCategory>('/purchasing/supplier-categories/', data),
  
  update: (id: string, data: Partial<SupplierCategory>) => 
    apiPut<SupplierCategory>(`/purchasing/supplier-categories/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/purchasing/supplier-categories/${id}/`),
};

// ========== PROVEEDORES ==========
export const supplierService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<Supplier>>('/purchasing/suppliers/', params),
  
  get: (id: string) => 
    apiGet<Supplier>(`/purchasing/suppliers/${id}/`),
  
  create: (data: Partial<Supplier>) => 
    apiPost<Supplier>('/purchasing/suppliers/', data),
  
  update: (id: string, data: Partial<Supplier>) => 
    apiPut<Supplier>(`/purchasing/suppliers/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/purchasing/suppliers/${id}/`),
  
  getStatement: (id: string) => 
    apiGet(`/purchasing/suppliers/${id}/statement/`),
  
  getOrders: (id: string, params?: ListParams) => 
    apiGet<PaginatedResponse<PurchaseOrder>>(`/purchasing/suppliers/${id}/orders/`, params),
  
  getInvoices: (id: string, params?: ListParams) => 
    apiGet<PaginatedResponse<SupplierInvoice>>(`/purchasing/suppliers/${id}/invoices/`, params),
  
  getEvaluations: (id: string, params?: ListParams) => 
    apiGet<PaginatedResponse<SupplierEvaluation>>(`/purchasing/suppliers/${id}/evaluations/`, params),
};

// ========== REQUISICIONES ==========
export const purchaseRequisitionService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<PurchaseRequisition>>('/purchasing/requisitions/', params),
  
  get: (id: string) => 
    apiGet<PurchaseRequisition>(`/purchasing/requisitions/${id}/`),
  
  create: (data: any) => 
    apiPost<PurchaseRequisition>('/purchasing/requisitions/', data),
  
  update: (id: string, data: any) => 
    apiPut<PurchaseRequisition>(`/purchasing/requisitions/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/purchasing/requisitions/${id}/`),
  
  submit: (id: string) => 
    apiPost(`/purchasing/requisitions/${id}/submit/`),
  
  approve: (id: string) => 
    apiPost(`/purchasing/requisitions/${id}/approve/`),
  
  reject: (id: string, reason: string) => 
    apiPost(`/purchasing/requisitions/${id}/reject/`, { reason }),
  
  convertToOrder: (id: string, supplier_id: string) => 
    apiPost<PurchaseOrder>(`/purchasing/requisitions/${id}/convert-to-order/`, { supplier: supplier_id }),
};

// ========== ÓRDENES DE COMPRA ==========
export const purchaseOrderService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<PurchaseOrder>>('/purchasing/orders/', params),
  
  get: (id: string) => 
    apiGet<PurchaseOrder>(`/purchasing/orders/${id}/`),
  
  create: (data: any) => 
    apiPost<PurchaseOrder>('/purchasing/orders/', data),
  
  update: (id: string, data: any) => 
    apiPut<PurchaseOrder>(`/purchasing/orders/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/purchasing/orders/${id}/`),
  
  send: (id: string) => 
    apiPost(`/purchasing/orders/${id}/send/`),
  
  confirm: (id: string) => 
    apiPost(`/purchasing/orders/${id}/confirm/`),
  
  cancel: (id: string) => 
    apiPost(`/purchasing/orders/${id}/cancel/`),
  
  createReceipt: (id: string, data: any) => 
    apiPost<GoodsReceipt>(`/purchasing/orders/${id}/create-receipt/`, data),
};

// ========== RECEPCIONES ==========
export const goodsReceiptService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<GoodsReceipt>>('/purchasing/receipts/', params),
  
  get: (id: string) => 
    apiGet<GoodsReceipt>(`/purchasing/receipts/${id}/`),
  
  create: (data: any) => 
    apiPost<GoodsReceipt>('/purchasing/receipts/', data),
  
  confirm: (id: string) => 
    apiPost(`/purchasing/receipts/${id}/confirm/`),
  
  cancel: (id: string) => 
    apiPost(`/purchasing/receipts/${id}/cancel/`),
};

// ========== FACTURAS DE PROVEEDOR ==========
export const supplierInvoiceService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<SupplierInvoice>>('/purchasing/invoices/', params),
  
  get: (id: string) => 
    apiGet<SupplierInvoice>(`/purchasing/invoices/${id}/`),
  
  create: (data: any) => 
    apiPost<SupplierInvoice>('/purchasing/invoices/', data),
  
  update: (id: string, data: any) => 
    apiPut<SupplierInvoice>(`/purchasing/invoices/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/purchasing/invoices/${id}/`),
};

// ========== PAGOS A PROVEEDORES ==========
export const supplierPaymentService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<SupplierPayment>>('/purchasing/payments/', params),
  
  get: (id: string) => 
    apiGet<SupplierPayment>(`/purchasing/payments/${id}/`),
  
  create: (data: any) => 
    apiPost<SupplierPayment>('/purchasing/payments/', data),
  
  delete: (id: string) => 
    api.delete(`/purchasing/payments/${id}/`),
};

// ========== EVALUACIONES ==========
export const supplierEvaluationService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<SupplierEvaluation>>('/purchasing/evaluations/', params),
  
  get: (id: string) => 
    apiGet<SupplierEvaluation>(`/purchasing/evaluations/${id}/`),
  
  create: (data: Partial<SupplierEvaluation>) => 
    apiPost<SupplierEvaluation>('/purchasing/evaluations/', data),
  
  update: (id: string, data: Partial<SupplierEvaluation>) => 
    apiPut<SupplierEvaluation>(`/purchasing/evaluations/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/purchasing/evaluations/${id}/`),
};

// ========== REPORTES ==========
export const purchasingReportService = {
  getSummary: (params?: { start_date?: string; end_date?: string }) => 
    apiGet('/purchasing/reports/summary/', params),
  
  getBySupplier: (params?: { start_date?: string; end_date?: string }) => 
    apiGet('/purchasing/reports/by-supplier/', params),
  
  getByProduct: (params?: { start_date?: string; end_date?: string }) => 
    apiGet('/purchasing/reports/by-product/', params),
};
