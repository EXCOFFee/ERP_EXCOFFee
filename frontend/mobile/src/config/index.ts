import Constants from 'expo-constants';

export const APP_CONFIG = {
  // API
  API_BASE_URL: Constants.expoConfig?.extra?.apiUrl || 'http://localhost:8000/api/v1',
  API_TIMEOUT: 30000,
  
  // Auth
  TOKEN_KEY: 'erp_access_token',
  REFRESH_TOKEN_KEY: 'erp_refresh_token',
  USER_KEY: 'erp_user',
  
  // Pagination
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
  
  // Cache
  CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
  
  // Features
  FEATURES: {
    BIOMETRIC_AUTH: true,
    OFFLINE_MODE: true,
    BARCODE_SCANNER: true,
    PUSH_NOTIFICATIONS: true,
  },
  
  // App Info
  APP_NAME: 'Universal ERP',
  APP_VERSION: '1.0.0',
  BUILD_NUMBER: '1',
  
  // Limits
  MAX_IMAGE_SIZE: 5 * 1024 * 1024, // 5MB
  MAX_UPLOAD_FILES: 5,
  
  // Localization
  DEFAULT_LANGUAGE: 'es',
  SUPPORTED_LANGUAGES: ['es', 'en'],
  DEFAULT_CURRENCY: 'MXN',
  DEFAULT_LOCALE: 'es-MX',
  
  // Theme
  PRIMARY_COLOR: '#1976D2',
  SECONDARY_COLOR: '#9C27B0',
};

export const ROUTES = {
  // Auth
  AUTH: {
    LOGIN: 'Login',
    REGISTER: 'Register',
    FORGOT_PASSWORD: 'ForgotPassword',
  },
  
  // Main
  MAIN: {
    DASHBOARD: 'Dashboard',
    INVENTORY: 'Inventory',
    SALES: 'Sales',
    PURCHASING: 'Purchasing',
    MORE: 'More',
  },
  
  // Inventory
  INVENTORY: {
    HOME: 'InventoryHome',
    PRODUCTS: 'ProductList',
    PRODUCT_DETAIL: 'ProductDetail',
    PRODUCT_FORM: 'ProductForm',
    WAREHOUSES: 'WarehouseList',
    WAREHOUSE_DETAIL: 'WarehouseDetail',
    STOCK: 'StockList',
    STOCK_ADJUSTMENT: 'StockAdjustment',
    SCANNER: 'BarcodeScanner',
  },
  
  // Sales
  SALES: {
    HOME: 'SalesHome',
    CUSTOMERS: 'CustomerList',
    CUSTOMER_DETAIL: 'CustomerDetail',
    ORDERS: 'OrderList',
    ORDER_DETAIL: 'OrderDetail',
    ORDER_CREATE: 'OrderCreate',
    INVOICES: 'InvoiceList',
    INVOICE_DETAIL: 'InvoiceDetail',
  },
  
  // Purchasing
  PURCHASING: {
    HOME: 'PurchasingHome',
    SUPPLIERS: 'SupplierList',
    SUPPLIER_DETAIL: 'SupplierDetail',
    ORDERS: 'PurchaseOrderList',
    ORDER_DETAIL: 'PurchaseOrderDetail',
    ORDER_CREATE: 'PurchaseOrderCreate',
    RECEIPTS: 'GoodsReceiptList',
    RECEIPT_DETAIL: 'GoodsReceiptDetail',
  },
  
  // More
  MORE: {
    HOME: 'MoreHome',
    PROFILE: 'Profile',
    SETTINGS: 'Settings',
    FINANCE: 'FinanceHome',
    HR: 'HRHome',
    ABOUT: 'About',
  },
};

export const ORDER_STATUSES = [
  { value: 'draft', label: 'Borrador', color: '#9e9e9e' },
  { value: 'confirmed', label: 'Confirmado', color: '#2196f3' },
  { value: 'processing', label: 'Procesando', color: '#ff9800' },
  { value: 'shipped', label: 'Enviado', color: '#9c27b0' },
  { value: 'delivered', label: 'Entregado', color: '#4caf50' },
  { value: 'cancelled', label: 'Cancelado', color: '#f44336' },
];

export const PAYMENT_STATUSES = [
  { value: 'pending', label: 'Pendiente', color: '#ff9800' },
  { value: 'partial', label: 'Parcial', color: '#2196f3' },
  { value: 'paid', label: 'Pagado', color: '#4caf50' },
];

export const PURCHASE_ORDER_STATUSES = [
  { value: 'draft', label: 'Borrador', color: '#9e9e9e' },
  { value: 'sent', label: 'Enviado', color: '#2196f3' },
  { value: 'confirmed', label: 'Confirmado', color: '#9c27b0' },
  { value: 'partial', label: 'Parcial', color: '#ff9800' },
  { value: 'received', label: 'Recibido', color: '#4caf50' },
  { value: 'cancelled', label: 'Cancelado', color: '#f44336' },
];

export const UNITS = [
  { value: 'pza', label: 'Pieza' },
  { value: 'kg', label: 'Kilogramo' },
  { value: 'g', label: 'Gramo' },
  { value: 'lt', label: 'Litro' },
  { value: 'ml', label: 'Mililitro' },
  { value: 'm', label: 'Metro' },
  { value: 'cm', label: 'Centímetro' },
  { value: 'm2', label: 'Metro cuadrado' },
  { value: 'm3', label: 'Metro cúbico' },
  { value: 'caja', label: 'Caja' },
  { value: 'paq', label: 'Paquete' },
];

export default APP_CONFIG;
