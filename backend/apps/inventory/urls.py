# ========================================================
# SISTEMA ERP UNIVERSAL - URLs de Inventario
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Definición de rutas para el módulo de inventario.
# ========================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    BrandViewSet,
    UnitOfMeasureViewSet,
    WarehouseViewSet,
    WarehouseLocationViewSet,
    ProductViewSet,
    StockViewSet,
    LotViewSet,
    SerialNumberViewSet,
    InventoryTransactionViewSet,
    StockTransferViewSet,
)

# Usar DefaultRouter para generar URLs automáticamente
router = DefaultRouter()

# Registrar ViewSets
# El router genera automáticamente las rutas CRUD estándar:
# - list: GET /categories/
# - create: POST /categories/
# - retrieve: GET /categories/{id}/
# - update: PUT /categories/{id}/
# - partial_update: PATCH /categories/{id}/
# - destroy: DELETE /categories/{id}/

router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'units', UnitOfMeasureViewSet, basename='unit')
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'locations', WarehouseLocationViewSet, basename='location')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'stock', StockViewSet, basename='stock')
router.register(r'lots', LotViewSet, basename='lot')
router.register(r'serial-numbers', SerialNumberViewSet, basename='serial-number')
router.register(r'transactions', InventoryTransactionViewSet, basename='transaction')
router.register(r'transfers', StockTransferViewSet, basename='transfer')

# Nombre de la aplicación para namespacing
app_name = 'inventory'

# Patrones de URL
# ========================================================
# Las URLs generadas incluyen:
#
# Categorías:
#   GET    /api/v1/inventory/categories/           - Lista categorías
#   POST   /api/v1/inventory/categories/           - Crea categoría
#   GET    /api/v1/inventory/categories/{id}/      - Detalle categoría
#   PUT    /api/v1/inventory/categories/{id}/      - Actualiza categoría
#   DELETE /api/v1/inventory/categories/{id}/      - Elimina categoría
#   GET    /api/v1/inventory/categories/tree/      - Árbol de categorías
#   GET    /api/v1/inventory/categories/{id}/products/ - Productos de categoría
#
# Productos:
#   GET    /api/v1/inventory/products/             - Lista productos
#   POST   /api/v1/inventory/products/             - Crea producto
#   GET    /api/v1/inventory/products/{id}/        - Detalle producto
#   GET    /api/v1/inventory/products/barcode/{code}/ - Buscar por código
#   GET    /api/v1/inventory/products/{id}/stock/  - Stock del producto
#   GET    /api/v1/inventory/products/{id}/movements/ - Movimientos
#   GET    /api/v1/inventory/products/{id}/lots/   - Lotes del producto
#   POST   /api/v1/inventory/products/{id}/adjust-stock/ - Ajustar stock
#   GET    /api/v1/inventory/products/low-stock/   - Productos con bajo stock
#
# Stock:
#   GET    /api/v1/inventory/stock/                - Lista stock
#   POST   /api/v1/inventory/stock/add/            - Agregar stock
#   POST   /api/v1/inventory/stock/remove/         - Remover stock
#   POST   /api/v1/inventory/stock/reserve/        - Reservar stock
#   POST   /api/v1/inventory/stock/release/        - Liberar reserva
#
# Almacenes:
#   GET    /api/v1/inventory/warehouses/           - Lista almacenes
#   GET    /api/v1/inventory/warehouses/{id}/locations/ - Ubicaciones
#   GET    /api/v1/inventory/warehouses/{id}/stock/ - Stock del almacén
#   GET    /api/v1/inventory/warehouses/{id}/valuation/ - Valoración
#   GET    /api/v1/inventory/warehouses/{id}/low-stock/ - Bajo stock
#
# Lotes:
#   GET    /api/v1/inventory/lots/                 - Lista lotes
#   GET    /api/v1/inventory/lots/expiring/        - Lotes por vencer
#   GET    /api/v1/inventory/lots/expired/         - Lotes vencidos
#
# Números de Serie:
#   GET    /api/v1/inventory/serial-numbers/       - Lista series
#   GET    /api/v1/inventory/serial-numbers/lookup/{serial}/ - Buscar serie
#
# Transacciones:
#   GET    /api/v1/inventory/transactions/         - Historial movimientos
#   GET    /api/v1/inventory/transactions/summary/ - Resumen
#
# Transferencias:
#   GET    /api/v1/inventory/transfers/            - Lista transferencias
#   POST   /api/v1/inventory/transfers/{id}/confirm/ - Confirmar
#   POST   /api/v1/inventory/transfers/{id}/ship/  - Despachar
#   POST   /api/v1/inventory/transfers/{id}/receive/ - Recibir
#   POST   /api/v1/inventory/transfers/{id}/cancel/ - Cancelar
# ========================================================

urlpatterns = [
    # Incluir todas las rutas del router
    path('', include(router.urls)),
]
