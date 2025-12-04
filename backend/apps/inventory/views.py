# ========================================================
# SISTEMA ERP UNIVERSAL - Vistas de Inventario
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Vistas (ViewSets) para el módulo de inventario.
# Implementa RF2 del SRS - Gestión de Inventario.
# ========================================================

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, F, Q
from django.utils import timezone
from decimal import Decimal

from apps.core.views import BaseViewSet
from apps.authentication.permissions import HasModulePermission

from .models import (
    Category,
    Brand,
    UnitOfMeasure,
    Warehouse,
    WarehouseLocation,
    Product,
    Lot,
    Stock,
    SerialNumber,
    InventoryTransaction,
    StockTransfer,
    StockTransferItem,
)
from .serializers import (
    CategorySerializer,
    BrandSerializer,
    UnitOfMeasureSerializer,
    WarehouseSerializer,
    WarehouseLocationSerializer,
    ProductSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    LotSerializer,
    StockSerializer,
    StockDetailSerializer,
    SerialNumberSerializer,
    InventoryTransactionSerializer,
    StockTransferSerializer,
    StockTransferDetailSerializer,
    StockTransferItemSerializer,
)
from .services import InventoryService


class CategoryViewSet(BaseViewSet):
    """
    ViewSet para gestión de categorías de productos.
    
    Propósito:
        CRUD completo de categorías con soporte para jerarquías.
        Permite organizar productos en categorías y subcategorías.
    
    Endpoints:
        GET /api/v1/inventory/categories/ - Lista categorías
        POST /api/v1/inventory/categories/ - Crea categoría
        GET /api/v1/inventory/categories/{id}/ - Detalle
        PUT /api/v1/inventory/categories/{id}/ - Actualiza
        DELETE /api/v1/inventory/categories/{id}/ - Elimina (soft delete)
        GET /api/v1/inventory/categories/tree/ - Árbol de categorías
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'inventory'
    search_fields = ['name', 'code', 'description']
    filterset_fields = ['parent', 'is_active']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        Retorna las categorías en estructura de árbol.
        
        Propósito:
            Para renderizar menús/selectores jerárquicos en frontend.
        
        Returns:
            Lista de categorías raíz con sus hijos anidados.
        """
        def build_tree(category):
            return {
                'id': str(category.id),
                'name': category.name,
                'code': category.code,
                'children': [build_tree(child) for child in category.children.filter(is_active=True)]
            }
        
        root_categories = Category.objects.filter(
            parent__isnull=True,
            is_active=True
        ).prefetch_related('children')
        
        tree = [build_tree(cat) for cat in root_categories]
        return Response(tree)
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """
        Lista productos de una categoría específica.
        
        Propósito:
            Navegar productos por categoría.
        
        Returns:
            Lista paginada de productos.
        """
        category = self.get_object()
        # Incluir productos de subcategorías
        descendant_ids = [category.id]
        
        def get_descendants(cat):
            for child in cat.children.filter(is_active=True):
                descendant_ids.append(child.id)
                get_descendants(child)
        
        get_descendants(category)
        
        products = Product.objects.filter(
            category_id__in=descendant_ids,
            is_deleted=False,
            is_active=True
        )
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class BrandViewSet(BaseViewSet):
    """
    ViewSet para gestión de marcas.
    
    Propósito:
        CRUD de marcas de productos.
    """
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'inventory'
    search_fields = ['name', 'description']
    ordering = ['name']


class UnitOfMeasureViewSet(BaseViewSet):
    """
    ViewSet para unidades de medida.
    
    Propósito:
        Gestionar unidades para productos y conversiones.
    """
    queryset = UnitOfMeasure.objects.filter(is_active=True)
    serializer_class = UnitOfMeasureSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'inventory'
    search_fields = ['name', 'abbreviation']
    ordering = ['name']


class WarehouseViewSet(BaseViewSet):
    """
    ViewSet para gestión de almacenes.
    
    Propósito:
        CRUD de almacenes y ubicaciones.
    
    Endpoints Adicionales:
        GET /warehouses/{id}/locations/ - Ubicaciones del almacén
        GET /warehouses/{id}/stock/ - Stock del almacén
        GET /warehouses/{id}/valuation/ - Valoración de inventario
    """
    queryset = Warehouse.objects.filter(is_active=True)
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'inventory'
    search_fields = ['name', 'code', 'address']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def locations(self, request, pk=None):
        """
        Lista ubicaciones de un almacén.
        
        Propósito:
            Gestionar zonas/estantes/ubicaciones dentro del almacén.
        """
        warehouse = self.get_object()
        locations = warehouse.locations.filter(is_active=True)
        serializer = WarehouseLocationSerializer(locations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stock(self, request, pk=None):
        """
        Lista stock de productos en el almacén.
        
        Propósito:
            Ver inventario por almacén.
        """
        warehouse = self.get_object()
        stocks = Stock.objects.filter(
            warehouse=warehouse,
            quantity__gt=0
        ).select_related('product', 'product__category')
        
        page = self.paginate_queryset(stocks)
        if page is not None:
            serializer = StockDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = StockDetailSerializer(stocks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def valuation(self, request, pk=None):
        """
        Calcula valoración del inventario del almacén.
        
        Propósito:
            Reportes financieros de inventario.
        
        Returns:
            {
                "total_value": "12345.67",
                "total_items": 500,
                "by_category": [...]
            }
        """
        warehouse = self.get_object()
        result = InventoryService.get_stock_valuation(str(warehouse.id))
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def low_stock(self, request, pk=None):
        """
        Lista productos con stock bajo en el almacén.
        
        Propósito:
            Alertas de reposición.
        """
        warehouse = self.get_object()
        result = InventoryService.get_low_stock_products(str(warehouse.id))
        return Response(result)


class WarehouseLocationViewSet(BaseViewSet):
    """
    ViewSet para ubicaciones de almacén.
    
    Propósito:
        Gestionar ubicaciones físicas (pasillos, estantes, bins).
    """
    queryset = WarehouseLocation.objects.filter(is_active=True)
    serializer_class = WarehouseLocationSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'inventory'
    filterset_fields = ['warehouse', 'location_type']
    search_fields = ['code', 'name']
    ordering = ['warehouse__name', 'code']


class ProductViewSet(BaseViewSet):
    """
    ViewSet para gestión de productos.
    
    Propósito:
        CRUD completo de productos con búsqueda avanzada,
        gestión de stock, precios, y escaneo de códigos.
    
    Endpoints Adicionales:
        GET /products/search/ - Búsqueda avanzada
        GET /products/barcode/{code}/ - Buscar por código de barras
        GET /products/{id}/stock/ - Stock del producto
        GET /products/{id}/movements/ - Historial de movimientos
        GET /products/{id}/lots/ - Lotes del producto
        POST /products/{id}/adjust-stock/ - Ajustar stock
    """
    queryset = Product.objects.filter(is_deleted=False)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'inventory'
    search_fields = ['sku', 'barcode', 'name', 'description']
    filterset_fields = ['category', 'brand', 'is_active', 'product_type']
    ordering_fields = ['name', 'sku', 'created_at', 'sale_price']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Selecciona serializer según la acción."""
        if self.action == 'list':
            return ProductListSerializer
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    @action(detail=False, methods=['get'], url_path='barcode/(?P<code>[^/.]+)')
    def barcode(self, request, code=None):
        """
        Busca producto por código de barras/QR.
        
        Propósito:
            Implementa RU2 - Escaneo de códigos de barras.
            Usado desde apps móviles y lectores de códigos.
        
        Args:
            code: Código de barras, QR o SKU
        
        Query Params:
            warehouse: ID de almacén para obtener stock específico
        
        Returns:
            Información del producto con stock si se especifica almacén.
        """
        warehouse_id = request.query_params.get('warehouse')
        result = InventoryService.search_by_barcode(code, warehouse_id)
        
        if result is None:
            return Response(
                {'error': f'Producto no encontrado: {code}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def stock(self, request, pk=None):
        """
        Obtiene stock del producto en todos los almacenes.
        
        Propósito:
            Ver disponibilidad por ubicación.
        
        Returns:
            Lista de stocks por almacén.
        """
        product = self.get_object()
        stocks = Stock.objects.filter(
            product=product
        ).select_related('warehouse')
        
        serializer = StockDetailSerializer(stocks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """
        Historial de movimientos del producto.
        
        Propósito:
            Trazabilidad completa de entradas y salidas.
        
        Query Params:
            warehouse: Filtrar por almacén
            start_date: Fecha inicio
            end_date: Fecha fin
        """
        product = self.get_object()
        queryset = InventoryTransaction.objects.filter(
            product=product
        ).select_related('warehouse', 'created_by')
        
        # Filtros opcionales
        warehouse = request.query_params.get('warehouse')
        if warehouse:
            queryset = queryset.filter(warehouse_id=warehouse)
        
        start_date = request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        
        end_date = request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        queryset = queryset.order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = InventoryTransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = InventoryTransactionSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def lots(self, request, pk=None):
        """
        Lista lotes del producto.
        
        Propósito:
            Gestión de lotes para productos perecederos.
        """
        product = self.get_object()
        lots = Lot.objects.filter(
            product=product,
            quantity__gt=0
        ).select_related('warehouse')
        
        serializer = LotSerializer(lots, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def serial_numbers(self, request, pk=None):
        """
        Lista números de serie del producto.
        
        Propósito:
            Trazabilidad de productos serializados.
        """
        product = self.get_object()
        serials = SerialNumber.objects.filter(
            product=product
        ).select_related('warehouse', 'lot')
        
        # Filtro por estado
        serial_status = request.query_params.get('status')
        if serial_status:
            serials = serials.filter(status=serial_status)
        
        page = self.paginate_queryset(serials)
        if page is not None:
            serializer = SerialNumberSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SerialNumberSerializer(serials, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='adjust-stock')
    def adjust_stock(self, request, pk=None):
        """
        Ajusta stock de un producto.
        
        Propósito:
            Corregir discrepancias después de conteo físico.
        
        Body:
            {
                "warehouse": "uuid-almacen",
                "new_quantity": 100,
                "reason": "Conteo físico"
            }
        
        Returns:
            Transacción de ajuste creada.
        """
        product = self.get_object()
        warehouse_id = request.data.get('warehouse')
        new_quantity = request.data.get('new_quantity')
        reason = request.data.get('reason', 'Ajuste de inventario')
        
        if warehouse_id is None or new_quantity is None:
            return Response(
                {'error': 'Se requiere warehouse y new_quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            stock, transaction = InventoryService.adjust_stock(
                product_id=str(product.id),
                warehouse_id=warehouse_id,
                new_quantity=int(new_quantity),
                reason=reason,
                user=request.user
            )
            
            if transaction:
                return Response({
                    'message': 'Stock ajustado correctamente',
                    'stock': StockSerializer(stock).data,
                    'transaction': InventoryTransactionSerializer(transaction).data
                })
            else:
                return Response({
                    'message': 'El stock ya es igual a la cantidad especificada',
                    'stock': StockSerializer(stock).data
                })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """
        Lista productos con stock bajo.
        
        Propósito:
            Alertas de productos que necesitan reposición.
        
        Query Params:
            warehouse: Filtrar por almacén
        """
        warehouse_id = request.query_params.get('warehouse')
        result = InventoryService.get_low_stock_products(warehouse_id)
        return Response(result)


class StockViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de stock.
    
    Propósito:
        Consultar y gestionar niveles de stock.
        Operaciones de entrada, salida y transferencia.
    
    Endpoints Adicionales:
        POST /stock/add/ - Agregar stock
        POST /stock/remove/ - Remover stock
        POST /stock/reserve/ - Reservar stock
        POST /stock/release/ - Liberar reserva
    """
    queryset = Stock.objects.all().select_related('product', 'warehouse')
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'inventory'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['warehouse', 'product']
    search_fields = ['product__name', 'product__sku', 'warehouse__name']
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return StockDetailSerializer
        return StockSerializer
    
    @action(detail=False, methods=['post'])
    def add(self, request):
        """
        Agrega stock de un producto.
        
        Propósito:
            Registrar entrada de inventario.
        
        Body:
            {
                "product": "uuid-producto",
                "warehouse": "uuid-almacen",
                "quantity": 100,
                "reason": "purchase",
                "unit_cost": "25.50",
                "lot_number": "LOT-001",  # opcional
                "reference_type": "purchase_order",
                "reference_id": "uuid-orden",
                "notes": "Nota opcional"
            }
        """
        try:
            stock, transaction = InventoryService.add_stock(
                product_id=request.data.get('product'),
                warehouse_id=request.data.get('warehouse'),
                quantity=int(request.data.get('quantity', 0)),
                reason=request.data.get('reason', 'purchase'),
                unit_cost=Decimal(request.data['unit_cost']) if request.data.get('unit_cost') else None,
                lot_number=request.data.get('lot_number'),
                serial_numbers=request.data.get('serial_numbers'),
                reference_type=request.data.get('reference_type'),
                reference_id=request.data.get('reference_id'),
                notes=request.data.get('notes', ''),
                user=request.user
            )
            
            return Response({
                'message': 'Stock agregado correctamente',
                'stock': StockSerializer(stock).data,
                'transaction': InventoryTransactionSerializer(transaction).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def remove(self, request):
        """
        Remueve stock de un producto.
        
        Propósito:
            Registrar salida de inventario.
        """
        try:
            stock, transaction = InventoryService.remove_stock(
                product_id=request.data.get('product'),
                warehouse_id=request.data.get('warehouse'),
                quantity=int(request.data.get('quantity', 0)),
                reason=request.data.get('reason', 'sale'),
                lot_id=request.data.get('lot'),
                serial_numbers=request.data.get('serial_numbers'),
                reference_type=request.data.get('reference_type'),
                reference_id=request.data.get('reference_id'),
                notes=request.data.get('notes', ''),
                user=request.user
            )
            
            return Response({
                'message': 'Stock removido correctamente',
                'stock': StockSerializer(stock).data,
                'transaction': InventoryTransactionSerializer(transaction).data
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def reserve(self, request):
        """
        Reserva stock para una orden.
        
        Propósito:
            Evitar sobreventa reservando stock.
        
        Body:
            {
                "product": "uuid-producto",
                "warehouse": "uuid-almacen",
                "quantity": 10
            }
        """
        try:
            stock = InventoryService.reserve_stock(
                product_id=request.data.get('product'),
                warehouse_id=request.data.get('warehouse'),
                quantity=int(request.data.get('quantity', 0)),
                user=request.user
            )
            
            return Response({
                'message': 'Stock reservado correctamente',
                'stock': StockSerializer(stock).data
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def release(self, request):
        """
        Libera stock reservado.
        
        Propósito:
            Liberar reserva cuando una orden se cancela.
        """
        try:
            stock = InventoryService.release_reservation(
                product_id=request.data.get('product'),
                warehouse_id=request.data.get('warehouse'),
                quantity=int(request.data.get('quantity', 0))
            )
            
            return Response({
                'message': 'Reserva liberada correctamente',
                'stock': StockSerializer(stock).data
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class LotViewSet(BaseViewSet):
    """
    ViewSet para gestión de lotes.
    
    Propósito:
        Trazabilidad de lotes para productos perecederos.
    """
    queryset = Lot.objects.all().select_related('product', 'warehouse')
    serializer_class = LotSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'inventory'
    filterset_fields = ['product', 'warehouse', 'status']
    search_fields = ['lot_number', 'product__name']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def expiring(self, request):
        """
        Lista lotes próximos a vencer.
        
        Propósito:
            Alertas de productos por vencer.
        
        Query Params:
            days: Días para considerar "próximo a vencer" (default: 30)
        """
        days = int(request.query_params.get('days', 30))
        expiry_date = timezone.now().date() + timezone.timedelta(days=days)
        
        lots = Lot.objects.filter(
            expiry_date__lte=expiry_date,
            quantity__gt=0,
            status=Lot.LotStatus.ACTIVE
        ).select_related('product', 'warehouse').order_by('expiry_date')
        
        serializer = LotSerializer(lots, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """
        Lista lotes vencidos.
        
        Propósito:
            Control de productos vencidos para disposición.
        """
        today = timezone.now().date()
        
        lots = Lot.objects.filter(
            expiry_date__lt=today,
            quantity__gt=0
        ).select_related('product', 'warehouse').order_by('expiry_date')
        
        serializer = LotSerializer(lots, many=True)
        return Response(serializer.data)


class SerialNumberViewSet(BaseViewSet):
    """
    ViewSet para números de serie.
    
    Propósito:
        Trazabilidad de productos serializados.
    """
    queryset = SerialNumber.objects.all().select_related(
        'product', 'warehouse', 'lot'
    )
    serializer_class = SerialNumberSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'inventory'
    filterset_fields = ['product', 'warehouse', 'status']
    search_fields = ['serial', 'product__name']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'], url_path='lookup/(?P<serial>[^/.]+)')
    def lookup(self, request, serial=None):
        """
        Busca información de un número de serie.
        
        Propósito:
            Verificar estado y ubicación de un número de serie específico.
        """
        try:
            sn = SerialNumber.objects.select_related(
                'product', 'warehouse', 'lot'
            ).get(serial=serial)
            
            serializer = SerialNumberSerializer(sn)
            return Response(serializer.data)
        except SerialNumber.DoesNotExist:
            return Response(
                {'error': f'Número de serie no encontrado: {serial}'},
                status=status.HTTP_404_NOT_FOUND
            )


class InventoryTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para transacciones de inventario.
    
    Propósito:
        Consultar historial de movimientos (solo lectura).
        Las transacciones se crean automáticamente por el servicio.
    """
    queryset = InventoryTransaction.objects.all().select_related(
        'product', 'warehouse', 'lot', 'created_by'
    )
    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'inventory'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'warehouse', 'transaction_type', 'reason']
    search_fields = ['product__name', 'product__sku', 'reference_type', 'notes']
    ordering_fields = ['created_at', 'quantity']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Resumen de transacciones por período.
        
        Propósito:
            Dashboard y reportes de movimientos.
        
        Query Params:
            start_date: Fecha inicio
            end_date: Fecha fin
            warehouse: Filtrar por almacén
        """
        queryset = self.get_queryset()
        
        # Filtros
        start_date = request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        
        end_date = request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        warehouse = request.query_params.get('warehouse')
        if warehouse:
            queryset = queryset.filter(warehouse_id=warehouse)
        
        # Agregaciones
        summary = queryset.values('transaction_type').annotate(
            count=Sum('id'),
            total_quantity=Sum('quantity')
        )
        
        return Response({
            'summary': list(summary),
            'total_transactions': queryset.count()
        })


class StockTransferViewSet(BaseViewSet):
    """
    ViewSet para transferencias de inventario.
    
    Propósito:
        Gestionar transferencias entre almacenes.
    
    Endpoints Adicionales:
        POST /transfers/{id}/confirm/ - Confirmar transferencia
        POST /transfers/{id}/ship/ - Despachar transferencia
        POST /transfers/{id}/receive/ - Recibir transferencia
        POST /transfers/{id}/cancel/ - Cancelar transferencia
    """
    queryset = StockTransfer.objects.all().select_related(
        'source_warehouse', 'destination_warehouse',
        'created_by', 'approved_by'
    ).prefetch_related('items', 'items__product')
    serializer_class = StockTransferSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'inventory'
    filterset_fields = ['status', 'source_warehouse', 'destination_warehouse']
    search_fields = ['transfer_number', 'notes']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return StockTransferDetailSerializer
        return StockTransferSerializer
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirma una transferencia en borrador.
        
        Propósito:
            Validar y reservar stock antes del despacho.
        """
        transfer = self.get_object()
        try:
            updated = InventoryService.process_transfer(
                transfer, 'confirm', request.user
            )
            return Response({
                'message': 'Transferencia confirmada',
                'transfer': StockTransferDetailSerializer(updated).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """
        Marca la transferencia como despachada.
        
        Propósito:
            Registrar salida del almacén origen.
        """
        transfer = self.get_object()
        try:
            updated = InventoryService.process_transfer(
                transfer, 'ship', request.user
            )
            return Response({
                'message': 'Transferencia despachada',
                'transfer': StockTransferDetailSerializer(updated).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """
        Registra la recepción de la transferencia.
        
        Propósito:
            Registrar entrada en almacén destino.
        
        Body:
            {
                "items": [
                    {"item_id": "uuid", "received_quantity": 10}
                ]
            }
        """
        transfer = self.get_object()
        
        # Actualizar cantidades recibidas si se proporcionan
        items_data = request.data.get('items', [])
        for item_data in items_data:
            try:
                item = transfer.items.get(pk=item_data['item_id'])
                item.received_quantity = item_data.get('received_quantity', item.quantity)
                item.save()
            except StockTransferItem.DoesNotExist:
                pass
        
        try:
            updated = InventoryService.process_transfer(
                transfer, 'receive', request.user
            )
            return Response({
                'message': 'Transferencia recibida',
                'transfer': StockTransferDetailSerializer(updated).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancela una transferencia.
        
        Propósito:
            Cancelar y liberar reservas si corresponde.
        """
        transfer = self.get_object()
        try:
            updated = InventoryService.process_transfer(
                transfer, 'cancel', request.user
            )
            return Response({
                'message': 'Transferencia cancelada',
                'transfer': StockTransferDetailSerializer(updated).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
