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
  Finance: undefined;
  AccountForm: { accountId?: string };
  JournalEntryList: undefined;
  FinancialReports: undefined;
  HR: undefined;
  EmployeeForm: { employeeId?: string };
  DepartmentList: undefined;
  Attendance: undefined;
  Payroll: undefined;
  Settings: undefined;
  Profile: undefined;
};

// Finance Stack
export type FinanceStackParamList = {
  FinanceHome: undefined;
  AccountList: undefined;
  AccountDetail: { accountId: string };
  AccountForm: { accountId?: string };
  JournalEntryList: undefined;
  JournalEntryDetail: { entryId: string };
  JournalEntryForm: { entryId?: string };
  FinancialReports: undefined;
};

// HR Stack
export type HRStackParamList = {
  HRHome: undefined;
  EmployeeList: undefined;
  EmployeeDetail: { employeeId: string };
  EmployeeForm: { employeeId?: string };
  DepartmentList: undefined;
  DepartmentDetail: { departmentId: string };
  DepartmentForm: { departmentId?: string };
  Attendance: undefined;
  Payroll: undefined;
  PayslipDetail: { payslipId: string };
};

// Declaración global para React Navigation
declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}
