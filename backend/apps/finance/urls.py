# ========================================================
# SISTEMA ERP UNIVERSAL - URLs de Finanzas
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Definición de rutas para el módulo de finanzas.
# ========================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AccountingPeriodViewSet,
    AccountTypeViewSet,
    AccountViewSet,
    JournalEntryViewSet,
    CostCenterViewSet,
    BudgetViewSet,
    TaxRateViewSet,
    PaymentMethodViewSet,
    BankAccountViewSet,
    ReportsViewSet,
)

# Crear router
router = DefaultRouter()

# Registrar ViewSets
router.register(r'periods', AccountingPeriodViewSet, basename='period')
router.register(r'account-types', AccountTypeViewSet, basename='account-type')
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'entries', JournalEntryViewSet, basename='entry')
router.register(r'cost-centers', CostCenterViewSet, basename='cost-center')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'tax-rates', TaxRateViewSet, basename='tax-rate')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-method')
router.register(r'bank-accounts', BankAccountViewSet, basename='bank-account')
router.register(r'reports', ReportsViewSet, basename='report')

# Nombre de la aplicación
app_name = 'finance'

# Patrones de URL
# ========================================================
# URLs generadas:
#
# Períodos Contables:
#   GET    /api/v1/finance/periods/              - Lista períodos
#   POST   /api/v1/finance/periods/              - Crear período
#   GET    /api/v1/finance/periods/{id}/         - Detalle
#   POST   /api/v1/finance/periods/{id}/close/   - Cerrar período
#   POST   /api/v1/finance/periods/{id}/set-current/ - Marcar como actual
#
# Plan de Cuentas:
#   GET    /api/v1/finance/accounts/             - Lista cuentas
#   POST   /api/v1/finance/accounts/             - Crear cuenta
#   GET    /api/v1/finance/accounts/tree/        - Árbol de cuentas
#   GET    /api/v1/finance/accounts/{id}/balance/ - Saldo de cuenta
#   GET    /api/v1/finance/accounts/{id}/ledger/ - Libro mayor
#
# Asientos Contables:
#   GET    /api/v1/finance/entries/              - Lista asientos
#   POST   /api/v1/finance/entries/              - Crear asiento
#   GET    /api/v1/finance/entries/{id}/         - Detalle
#   POST   /api/v1/finance/entries/{id}/post/    - Contabilizar
#   POST   /api/v1/finance/entries/{id}/reverse/ - Reversar
#
# Presupuestos:
#   GET    /api/v1/finance/budgets/              - Lista presupuestos
#   GET    /api/v1/finance/budgets/execution-report/ - Reporte ejecución
#
# Reportes:
#   GET    /api/v1/finance/reports/trial-balance/    - Balance comprobación
#   GET    /api/v1/finance/reports/income-statement/ - Estado resultados
#   GET    /api/v1/finance/reports/balance-sheet/    - Balance general
# ========================================================

urlpatterns = [
    path('', include(router.urls)),
]
