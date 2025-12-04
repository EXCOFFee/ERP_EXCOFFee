# ========================================================
# SISTEMA ERP UNIVERSAL - URLs de Ventas
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Configuración de rutas para el módulo de ventas.
# ========================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CustomerGroupViewSet,
    CustomerViewSet,
    CustomerAddressViewSet,
    CustomerContactViewSet,
    QuotationViewSet,
    SalesOrderViewSet,
    InvoiceViewSet,
    PaymentViewSet,
    ShipmentViewSet,
    PriceListViewSet,
    PromotionViewSet,
    SalesReportViewSet,
)

app_name = 'sales'

router = DefaultRouter()
router.register(r'customer-groups', CustomerGroupViewSet, basename='customer-groups')
router.register(r'customers', CustomerViewSet, basename='customers')
router.register(r'customer-addresses', CustomerAddressViewSet, basename='customer-addresses')
router.register(r'customer-contacts', CustomerContactViewSet, basename='customer-contacts')
router.register(r'quotations', QuotationViewSet, basename='quotations')
router.register(r'orders', SalesOrderViewSet, basename='orders')
router.register(r'invoices', InvoiceViewSet, basename='invoices')
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'shipments', ShipmentViewSet, basename='shipments')
router.register(r'price-lists', PriceListViewSet, basename='price-lists')
router.register(r'promotions', PromotionViewSet, basename='promotions')
router.register(r'reports', SalesReportViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
]
