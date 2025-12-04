# ========================================================
# SISTEMA ERP UNIVERSAL - URLs de Compras
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Configuración de rutas para el módulo de compras.
# ========================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SupplierCategoryViewSet,
    SupplierViewSet,
    SupplierContactViewSet,
    SupplierProductViewSet,
    PurchaseRequisitionViewSet,
    PurchaseOrderViewSet,
    GoodsReceiptViewSet,
    SupplierInvoiceViewSet,
    SupplierPaymentViewSet,
    SupplierEvaluationViewSet,
    PurchaseReportViewSet,
)

app_name = 'purchasing'

router = DefaultRouter()

# Proveedores
router.register(r'supplier-categories', SupplierCategoryViewSet, basename='supplier-categories')
router.register(r'suppliers', SupplierViewSet, basename='suppliers')
router.register(r'supplier-contacts', SupplierContactViewSet, basename='supplier-contacts')
router.register(r'supplier-products', SupplierProductViewSet, basename='supplier-products')

# Proceso de compras
router.register(r'requisitions', PurchaseRequisitionViewSet, basename='requisitions')
router.register(r'orders', PurchaseOrderViewSet, basename='orders')
router.register(r'receipts', GoodsReceiptViewSet, basename='receipts')

# Facturación y pagos
router.register(r'invoices', SupplierInvoiceViewSet, basename='invoices')
router.register(r'payments', SupplierPaymentViewSet, basename='payments')

# Evaluaciones y reportes
router.register(r'evaluations', SupplierEvaluationViewSet, basename='evaluations')
router.register(r'reports', PurchaseReportViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
]
