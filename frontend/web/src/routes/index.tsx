// ========================================================
// SISTEMA ERP UNIVERSAL - Rutas de la aplicación
// ========================================================

import { Routes, Route, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';

import MainLayout from '@layouts/MainLayout';
import AuthLayout from '@layouts/AuthLayout';
import LoadingScreen from '@components/common/LoadingScreen';
import ProtectedRoute from '@components/auth/ProtectedRoute';

// Lazy loading de páginas
const LoginPage = lazy(() => import('@pages/auth/LoginPage'));
const RegisterPage = lazy(() => import('@pages/auth/RegisterPage'));
const ForgotPasswordPage = lazy(() => import('@pages/auth/ForgotPasswordPage'));

const DashboardPage = lazy(() => import('@pages/dashboard/DashboardPage'));

// Inventario
const ProductListPage = lazy(() => import('@pages/inventory/ProductListPage'));
const ProductDetailPage = lazy(() => import('@pages/inventory/ProductDetailPage'));
const ProductFormPage = lazy(() => import('@pages/inventory/ProductFormPage'));
const WarehouseListPage = lazy(() => import('@pages/inventory/WarehouseListPage'));
const StockMovementsPage = lazy(() => import('@pages/inventory/StockMovementsPage'));

// Ventas
const CustomerListPage = lazy(() => import('@pages/sales/CustomerListPage'));
const CustomerDetailPage = lazy(() => import('@pages/sales/CustomerDetailPage'));
const SalesOrderListPage = lazy(() => import('@pages/sales/SalesOrderListPage'));
const SalesOrderDetailPage = lazy(() => import('@pages/sales/SalesOrderDetailPage'));
const InvoiceListPage = lazy(() => import('@pages/sales/InvoiceListPage'));

// Compras
const SupplierListPage = lazy(() => import('@pages/purchasing/SupplierListPage'));
const PurchaseOrderListPage = lazy(() => import('@pages/purchasing/PurchaseOrderListPage'));
const GoodsReceiptListPage = lazy(() => import('@pages/purchasing/GoodsReceiptListPage'));

// Finanzas
const AccountListPage = lazy(() => import('@pages/finance/AccountListPage'));
const JournalListPage = lazy(() => import('@pages/finance/JournalListPage'));
const LedgerPage = lazy(() => import('@pages/finance/LedgerPage'));
const FinancialReportsPage = lazy(() => import('@pages/finance/FinancialReportsPage'));

// Recursos Humanos
const EmployeeListPage = lazy(() => import('@pages/hr/EmployeeListPage'));
const DepartmentListPage = lazy(() => import('@pages/hr/DepartmentListPage'));
const PayrollPage = lazy(() => import('@pages/hr/PayrollPage'));
const AttendancePage = lazy(() => import('@pages/hr/AttendancePage'));

// Configuración
const SettingsPage = lazy(() => import('@pages/settings/SettingsPage'));
const CompanySettingsPage = lazy(() => import('@pages/settings/CompanySettingsPage'));
const UsersPage = lazy(() => import('@pages/settings/UsersPage'));
const RolesPage = lazy(() => import('@pages/settings/RolesPage'));

// Error pages
const NotFoundPage = lazy(() => import('@pages/errors/NotFoundPage'));
const ForbiddenPage = lazy(() => import('@pages/errors/ForbiddenPage'));

function AppRoutes() {
  return (
    <Suspense fallback={<LoadingScreen />}>
      <Routes>
        {/* Rutas de autenticación */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        </Route>

        {/* Rutas protegidas */}
        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
            {/* Dashboard */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />

            {/* Inventario */}
            <Route path="/inventory">
              <Route index element={<Navigate to="/inventory/products" replace />} />
              <Route path="products" element={<ProductListPage />} />
              <Route path="products/new" element={<ProductFormPage />} />
              <Route path="products/:id" element={<ProductDetailPage />} />
              <Route path="products/:id/edit" element={<ProductFormPage />} />
              <Route path="warehouses" element={<WarehouseListPage />} />
              <Route path="movements" element={<StockMovementsPage />} />
            </Route>

            {/* Ventas */}
            <Route path="/sales">
              <Route index element={<Navigate to="/sales/orders" replace />} />
              <Route path="customers" element={<CustomerListPage />} />
              <Route path="customers/:id" element={<CustomerDetailPage />} />
              <Route path="orders" element={<SalesOrderListPage />} />
              <Route path="orders/:id" element={<SalesOrderDetailPage />} />
              <Route path="invoices" element={<InvoiceListPage />} />
            </Route>

            {/* Compras */}
            <Route path="/purchasing">
              <Route index element={<Navigate to="/purchasing/orders" replace />} />
              <Route path="suppliers" element={<SupplierListPage />} />
              <Route path="orders" element={<PurchaseOrderListPage />} />
              <Route path="receipts" element={<GoodsReceiptListPage />} />
            </Route>

            {/* Finanzas */}
            <Route path="/finance">
              <Route index element={<Navigate to="/finance/accounts" replace />} />
              <Route path="accounts" element={<AccountListPage />} />
              <Route path="journals" element={<JournalListPage />} />
              <Route path="ledger" element={<LedgerPage />} />
              <Route path="reports" element={<FinancialReportsPage />} />
            </Route>

            {/* Recursos Humanos */}
            <Route path="/hr">
              <Route index element={<Navigate to="/hr/employees" replace />} />
              <Route path="employees" element={<EmployeeListPage />} />
              <Route path="departments" element={<DepartmentListPage />} />
              <Route path="payroll" element={<PayrollPage />} />
              <Route path="attendance" element={<AttendancePage />} />
            </Route>

            {/* Configuración */}
            <Route path="/settings">
              <Route index element={<SettingsPage />} />
              <Route path="company" element={<CompanySettingsPage />} />
              <Route path="users" element={<UsersPage />} />
              <Route path="roles" element={<RolesPage />} />
            </Route>

            {/* Página no encontrada dentro del layout */}
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Route>

        {/* Páginas de error */}
        <Route path="/forbidden" element={<ForbiddenPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Suspense>
  );
}

export default AppRoutes;
