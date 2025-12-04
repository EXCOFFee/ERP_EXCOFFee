import { NavigatorScreenParams } from '@react-navigation/native';

// Root Stack
export type RootStackParamList = {
  Auth: NavigatorScreenParams<AuthStackParamList>;
  Main: NavigatorScreenParams<MainTabParamList>;
};

// Auth Stack
export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
  ResetPassword: { uid: string; token: string };
};

// Main Tabs
export type MainTabParamList = {
  Dashboard: undefined;
  Inventory: NavigatorScreenParams<InventoryStackParamList>;
  Sales: NavigatorScreenParams<SalesStackParamList>;
  Purchasing: NavigatorScreenParams<PurchasingStackParamList>;
  More: NavigatorScreenParams<MoreStackParamList>;
};

// Inventory Stack
export type InventoryStackParamList = {
  InventoryHome: undefined;
  ProductList: undefined;
  ProductDetail: { id: number };
  ProductForm: { id?: number };
  CategoryList: undefined;
  WarehouseList: undefined;
  StockMovements: undefined;
  BarcodeScanner: undefined;
};

// Sales Stack
export type SalesStackParamList = {
  SalesHome: undefined;
  CustomerList: undefined;
  CustomerDetail: { id: number };
  CustomerForm: { id?: number };
  OrderList: undefined;
  OrderDetail: { id: number };
  OrderForm: { id?: number };
  InvoiceList: undefined;
  InvoiceDetail: { id: number };
};

// Purchasing Stack
export type PurchasingStackParamList = {
  PurchasingHome: undefined;
  SupplierList: undefined;
  SupplierDetail: { id: number };
  PurchaseOrderList: undefined;
  PurchaseOrderDetail: { id: number };
  PurchaseOrderForm: { id?: number };
  GoodsReceiptList: undefined;
  GoodsReceiptDetail: { id: number };
};

// More Stack
export type MoreStackParamList = {
  MoreHome: undefined;
  Finance: NavigatorScreenParams<FinanceStackParamList>;
  HR: NavigatorScreenParams<HRStackParamList>;
  Settings: undefined;
  Profile: undefined;
};

// Finance Stack
export type FinanceStackParamList = {
  FinanceHome: undefined;
  AccountList: undefined;
  TransactionList: undefined;
  FinancialReports: undefined;
};

// HR Stack
export type HRStackParamList = {
  HRHome: undefined;
  EmployeeList: undefined;
  EmployeeDetail: { id: number };
  Attendance: undefined;
  Payroll: undefined;
};

// Declaración global para React Navigation
declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}
