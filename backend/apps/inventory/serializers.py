# ========================================================
# SISTEMA ERP UNIVERSAL - Serializers de Inventario
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Serializers para la API de inventario.
# Manejan validación y transformación de datos.
# ========================================================

from rest_framework import serializers
from decimal import Decimal

from .models import (
    Category,
    Brand,
    UnitOfMeasure,
    Warehouse,
    WarehouseLocation,
    Product,
    Stock,
    Lot,
    SerialNumber,
    InventoryTransaction,
    StockTransfer,
    StockTransferItem,
)
from apps.core.validators import (
    DecimalValidator,
    IntegerValidator,
    StringValidator,
)
from apps.core.exceptions import (
    ValidationException,
    InsufficientStockException,
)


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer para categorías de productos.
    """
    
    # Ruta completa calculada
    full_path = serializers.CharField(
        source='get_full_path',
        read_only=True
    )
    
    # Nombre de categoría padre
    parent_name = serializers.CharField(
        source='parent.name',
        read_only=True,
        allow_null=True
    )
    
    # Cantidad de productos en la categoría
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'code', 'description',
            'parent', 'parent_name', 'full_path',
            'image', 'is_active', 'products_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_products_count(self, obj: Category) -> int:
        """Cuenta productos en la categoría."""
        return obj.products.filter(is_deleted=False).count()
    
    def validate_code(self, value: str) -> str:
        """Valida y normaliza el código."""
        return value.upper().strip()


class BrandSerializer(serializers.ModelSerializer):
    """
    Serializer para marcas de productos.
    """
    
    # Cantidad de productos de la marca
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'description', 'logo',
            'website', 'is_active', 'products_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_products_count(self, obj: Brand) -> int:
        """Cuenta productos de la marca."""
        return obj.products.filter(is_deleted=False).count()


class UnitOfMeasureSerializer(serializers.ModelSerializer):
    """
    Serializer para unidades de medida.
    """
    
    class Meta:
        model = UnitOfMeasure
        fields = [
            'id', 'name', 'abbreviation', 'is_base_unit', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WarehouseSerializer(serializers.ModelSerializer):
    """
    Serializer para almacenes.
    """
    
    # Nombre del responsable
    manager_name = serializers.CharField(
        source='manager.full_name',
        read_only=True,
        allow_null=True
    )
    
    # Nombre del tipo de almacén
    warehouse_type_display = serializers.CharField(
        source='get_warehouse_type_display',
        read_only=True
    )
    
    # Cantidad de productos en el almacén
    products_count = serializers.SerializerMethodField()
    
    # Valor total del inventario
    total_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Warehouse
        fields = [
            'id', 'name', 'code', 'address', 'city', 'state',
            'postal_code', 'country', 'phone', 'email',
            'manager', 'manager_name', 'warehouse_type',
            'warehouse_type_display', 'is_active',
            'products_count', 'total_value',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_products_count(self, obj: Warehouse) -> int:
        """Cuenta productos con stock en el almacén."""
        return obj.stocks.filter(quantity__gt=0).count()
    
    def get_total_value(self, obj: Warehouse) -> str:
        """Calcula el valor total del inventario en el almacén."""
        total = sum(
            stock.quantity * stock.product.cost_price
            for stock in obj.stocks.filter(quantity__gt=0).select_related('product')
        )
        return str(total)


class WarehouseLocationSerializer(serializers.ModelSerializer):
    """
    Serializer para ubicaciones de almacén.
    """
    
    warehouse_name = serializers.CharField(
        source='warehouse.name',
        read_only=True
    )
    
    location_type_display = serializers.CharField(
        source='get_location_type_display',
        read_only=True
    )
    
    parent_code = serializers.CharField(
        source='parent.code',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = WarehouseLocation
        fields = [
            'id', 'warehouse', 'warehouse_name', 'code', 'name',
            'location_type', 'location_type_display',
            'parent', 'parent_code',
            'max_weight', 'max_volume', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer ligero para listados de productos.
    
    Propósito:
        Retornar solo campos esenciales para listados,
        optimizando el rendimiento de las consultas.
    """
    
    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )
    
    unit_name = serializers.CharField(
        source='unit_of_measure.abbreviation',
        read_only=True
    )
    
    # Stock total en todos los almacenes
    total_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'barcode', 'name',
            'category', 'category_name',
            'unit_of_measure', 'unit_name',
            'cost_price', 'sale_price',
            'product_type', 'is_active',
            'image', 'total_stock'
        ]
    
    def get_total_stock(self, obj: Product) -> int:
        """Suma el stock de todos los almacenes."""
        return sum(stock.quantity for stock in obj.stocks.all())


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo para detalle de producto.
    
    Propósito:
        Retornar toda la información del producto incluyendo
        stock por almacén, margen de beneficio, etc.
    """
    
    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )
    
    category_path = serializers.CharField(
        source='category.get_full_path',
        read_only=True
    )
    
    unit_name = serializers.CharField(
        source='unit_of_measure.name',
        read_only=True
    )
    
    unit_abbreviation = serializers.CharField(
        source='unit_of_measure.abbreviation',
        read_only=True
    )
    
    # Campos calculados
    profit_margin = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    
    profit_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    
    # Stock por almacén
    stocks = serializers.SerializerMethodField()
    
    # Stock total
    total_stock = serializers.SerializerMethodField()
    
    # Stock disponible (total - reservado)
    available_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'barcode', 'qr_code', 'name', 'description',
            'category', 'category_name', 'category_path',
            'unit_of_measure', 'unit_name', 'unit_abbreviation',
            'brand', 'model',
            'cost_price', 'sale_price', 'min_sale_price',
            'profit_margin', 'profit_amount',
            'min_stock', 'max_stock', 'reorder_point', 'reorder_quantity',
            'product_type', 'track_lots', 'track_serial_numbers',
            'tax_rate', 'tax_exempt',
            'weight', 'length', 'width', 'height',
            'image', 'is_active', 'is_purchasable', 'is_sellable',
            'stocks', 'total_stock', 'available_stock',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
    
    def get_stocks(self, obj: Product) -> list:
        """Retorna stock por almacén."""
        return [
            {
                'warehouse_id': str(stock.warehouse.id),
                'warehouse_code': stock.warehouse.code,
                'warehouse_name': stock.warehouse.name,
                'quantity': stock.quantity,
                'reserved': stock.reserved_quantity,
                'available': stock.available_quantity,
                'location': stock.location,
                'is_low_stock': stock.is_low_stock,
            }
            for stock in obj.stocks.select_related('warehouse').all()
        ]
    
    def get_total_stock(self, obj: Product) -> int:
        """Suma el stock de todos los almacenes."""
        return sum(stock.quantity for stock in obj.stocks.all())
    
    def get_available_stock(self, obj: Product) -> int:
        """Suma el stock disponible de todos los almacenes."""
        return sum(stock.available_quantity for stock in obj.stocks.all())


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear/actualizar productos.
    
    Propósito:
        Validar datos de entrada y crear/actualizar productos.
        Implementa validación de Capa 2 (Service Layer).
    """
    
    class Meta:
        model = Product
        fields = [
            'sku', 'barcode', 'qr_code', 'name', 'description',
            'category', 'unit_of_measure', 'brand', 'model',
            'cost_price', 'sale_price', 'min_sale_price',
            'min_stock', 'max_stock', 'reorder_point', 'reorder_quantity',
            'product_type', 'track_lots', 'track_serial_numbers',
            'tax_rate', 'tax_exempt',
            'weight', 'length', 'width', 'height',
            'image', 'is_active', 'is_purchasable', 'is_sellable'
        ]
    
    def validate_sku(self, value: str) -> str:
        """
        Valida y normaliza el SKU.
        
        Args:
            value: SKU a validar
        
        Returns:
            str: SKU en mayúsculas
        """
        sku = value.upper().strip()
        
        # Verificar unicidad (excepto si es el mismo producto)
        instance = self.instance
        if Product.objects.filter(sku=sku).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError(
                f'Ya existe un producto con el SKU "{sku}"'
            )
        
        return sku
    
    def validate_barcode(self, value: str) -> str:
        """Valida el código de barras."""
        if not value:
            return value
        
        # Verificar que solo contenga dígitos (para EAN/UPC)
        # O caracteres alfanuméricos (para códigos internos)
        barcode = value.strip()
        if not barcode.isalnum():
            raise serializers.ValidationError(
                'El código de barras solo puede contener letras y números'
            )
        
        return barcode
    
    def validate_cost_price(self, value: Decimal) -> Decimal:
        """Valida que el precio de costo sea positivo."""
        if value < 0:
            raise serializers.ValidationError(
                'El precio de costo no puede ser negativo'
            )
        return value
    
    def validate_sale_price(self, value: Decimal) -> Decimal:
        """Valida que el precio de venta sea positivo."""
        if value < 0:
            raise serializers.ValidationError(
                'El precio de venta no puede ser negativo'
            )
        return value
    
    def validate(self, attrs: dict) -> dict:
        """
        Validaciones cruzadas.
        
        Args:
            attrs: Todos los campos
        
        Returns:
            dict: Campos validados
        """
        cost = attrs.get('cost_price', getattr(self.instance, 'cost_price', 0))
        sale = attrs.get('sale_price', getattr(self.instance, 'sale_price', 0))
        min_sale = attrs.get('min_sale_price')
        
        # Advertir si precio de venta es menor al costo (no bloquear)
        if sale and cost and sale < cost:
            # Solo advertir, no bloquear - puede haber promociones
            pass
        
        # Validar precio mínimo
        if min_sale is not None:
            if min_sale > sale:
                raise serializers.ValidationError({
                    'min_sale_price': 'El precio mínimo no puede ser mayor al precio de venta'
                })
            if min_sale < cost:
                raise serializers.ValidationError({
                    'min_sale_price': 'El precio mínimo no puede ser menor al costo'
                })
        
        return attrs
    
    def create(self, validated_data: dict) -> Product:
        """Crea el producto y registra el usuario creador."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)
    
    def update(self, instance: Product, validated_data: dict) -> Product:
        """Actualiza el producto y registra el usuario modificador."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class StockSerializer(serializers.ModelSerializer):
    """
    Serializer para stock de productos.
    """
    
    product_sku = serializers.CharField(
        source='product.sku',
        read_only=True
    )
    
    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )
    
    warehouse_code = serializers.CharField(
        source='warehouse.code',
        read_only=True
    )
    
    warehouse_name = serializers.CharField(
        source='warehouse.name',
        read_only=True
    )
    
    available_quantity = serializers.IntegerField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    needs_reorder = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Stock
        fields = [
            'id', 'product', 'product_sku', 'product_name',
            'warehouse', 'warehouse_code', 'warehouse_name',
            'quantity', 'reserved_quantity', 'available_quantity',
            'location', 'is_low_stock', 'needs_reorder',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at'
        ]


class LotSerializer(serializers.ModelSerializer):
    """
    Serializer para lotes de productos.
    """
    
    product_sku = serializers.CharField(
        source='product.sku',
        read_only=True
    )
    
    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )
    
    warehouse_name = serializers.CharField(
        source='warehouse.name',
        read_only=True
    )
    
    is_expired = serializers.BooleanField(read_only=True)
    days_until_expiration = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Lot
        fields = [
            'id', 'product', 'product_sku', 'product_name',
            'warehouse', 'warehouse_name', 'lot_number',
            'production_date', 'expiration_date', 'quantity',
            'cost', 'notes', 'is_expired', 'days_until_expiration',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SerialNumberSerializer(serializers.ModelSerializer):
    """
    Serializer para números de serie.
    """
    
    product_sku = serializers.CharField(
        source='product.sku',
        read_only=True
    )
    
    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )
    
    warehouse_name = serializers.CharField(
        source='warehouse.name',
        read_only=True,
        allow_null=True
    )
    
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    class Meta:
        model = SerialNumber
        fields = [
            'id', 'product', 'product_sku', 'product_name',
            'warehouse', 'warehouse_name', 'serial', 'lot',
            'status', 'status_display', 'received_date',
            'sold_date', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'received_date', 'created_at', 'updated_at']


class InventoryTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer para transacciones de inventario.
    """
    
    product_sku = serializers.CharField(
        source='product.sku',
        read_only=True
    )
    
    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )
    
    warehouse_name = serializers.CharField(
        source='warehouse.name',
        read_only=True
    )
    
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display',
        read_only=True
    )
    
    reason_display = serializers.CharField(
        source='get_reason_display',
        read_only=True
    )
    
    created_by_name = serializers.CharField(
        source='created_by.full_name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'product', 'product_sku', 'product_name',
            'warehouse', 'warehouse_name',
            'transaction_type', 'transaction_type_display',
            'reason', 'reason_display',
            'quantity', 'stock_before', 'stock_after',
            'unit_cost', 'lot', 'serial_number',
            'reference_type', 'reference_id',
            'notes', 'created_by', 'created_by_name',
            'created_at'
        ]
        read_only_fields = [
            'id', 'stock_before', 'stock_after',
            'created_by', 'created_at'
        ]


class StockTransferItemSerializer(serializers.ModelSerializer):
    """
    Serializer para ítems de transferencia.
    """
    
    product_sku = serializers.CharField(
        source='product.sku',
        read_only=True
    )
    
    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )
    
    class Meta:
        model = StockTransferItem
        fields = [
            'id', 'product', 'product_sku', 'product_name',
            'quantity', 'received_quantity', 'lot', 'notes'
        ]
        read_only_fields = ['id']


class StockTransferSerializer(serializers.ModelSerializer):
    """
    Serializer para transferencias de inventario.
    """
    
    source_warehouse_name = serializers.CharField(
        source='source_warehouse.name',
        read_only=True
    )
    
    destination_warehouse_name = serializers.CharField(
        source='destination_warehouse.name',
        read_only=True
    )
    
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    items = StockTransferItemSerializer(many=True, read_only=True)
    
    created_by_name = serializers.CharField(
        source='created_by.full_name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = StockTransfer
        fields = [
            'id', 'transfer_number',
            'source_warehouse', 'source_warehouse_name',
            'destination_warehouse', 'destination_warehouse_name',
            'status', 'status_display',
            'scheduled_date', 'shipped_date', 'received_date',
            'notes', 'items',
            'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'transfer_number', 'shipped_date', 'received_date',
            'created_by', 'created_at', 'updated_at'
        ]


class StockTransferCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear transferencias con sus ítems.
    """
    
    items = StockTransferItemSerializer(many=True)
    
    class Meta:
        model = StockTransfer
        fields = [
            'source_warehouse', 'destination_warehouse',
            'scheduled_date', 'notes', 'items'
        ]
    
    def validate(self, attrs: dict) -> dict:
        """
        Valida la transferencia.
        """
        source = attrs.get('source_warehouse')
        destination = attrs.get('destination_warehouse')
        
        # No puede ser el mismo almacén
        if source == destination:
            raise serializers.ValidationError({
                'destination_warehouse': 'El almacén destino debe ser diferente al origen'
            })
        
        # Validar que hay items
        items = attrs.get('items', [])
        if not items:
            raise serializers.ValidationError({
                'items': 'La transferencia debe tener al menos un ítem'
            })
        
        # Validar stock disponible para cada ítem
        for item_data in items:
            product = item_data['product']
            quantity = item_data['quantity']
            
            try:
                stock = Stock.objects.get(product=product, warehouse=source)
                if stock.available_quantity < quantity:
                    raise InsufficientStockException(
                        product=product.name,
                        requested=quantity,
                        available=stock.available_quantity
                    )
            except Stock.DoesNotExist:
                raise serializers.ValidationError({
                    'items': f'No hay stock del producto {product.sku} en el almacén origen'
                })
        
        return attrs
    
    def create(self, validated_data: dict) -> StockTransfer:
        """
        Crea la transferencia con sus ítems.
        """
        items_data = validated_data.pop('items')
        
        # Generar número de transferencia
        import uuid
        validated_data['transfer_number'] = f"TRF-{uuid.uuid4().hex[:8].upper()}"
        
        # Crear transferencia
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        
        transfer = StockTransfer.objects.create(**validated_data)
        
        # Crear ítems
        for item_data in items_data:
            StockTransferItem.objects.create(transfer=transfer, **item_data)
        
        return transfer


class BarcodeSearchSerializer(serializers.Serializer):
    """
    Serializer para búsqueda por código de barras.
    
    Propósito:
        Validar la entrada del escáner de códigos.
        Implementa RU2 - Escaneo de códigos de barras.
    """
    
    code = serializers.CharField(
        max_length=100,
        help_text='Código de barras o QR escaneado'
    )
    
    warehouse = serializers.UUIDField(
        required=False,
        help_text='ID del almacén para filtrar stock'
    )


class StockDetailSerializer(StockSerializer):
    """
    Serializer detallado para stock con información de producto.
    """
    
    product_category = serializers.CharField(
        source='product.category.name',
        read_only=True
    )
    
    product_cost_price = serializers.DecimalField(
        source='product.cost_price',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    
    product_sale_price = serializers.DecimalField(
        source='product.sale_price',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    
    stock_value = serializers.SerializerMethodField()
    
    class Meta(StockSerializer.Meta):
        fields = StockSerializer.Meta.fields + [
            'product_category', 'product_cost_price', 
            'product_sale_price', 'stock_value'
        ]
    
    def get_stock_value(self, obj: Stock) -> str:
        """Calcula el valor del stock."""
        return str(obj.quantity * obj.product.cost_price)


class StockTransferDetailSerializer(StockTransferSerializer):
    """
    Serializer detallado para transferencias con items expandidos.
    """
    
    items = StockTransferItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    
    class Meta(StockTransferSerializer.Meta):
        fields = StockTransferSerializer.Meta.fields + ['total_items']
    
    def get_total_items(self, obj: StockTransfer) -> int:
        """Cuenta el total de items en la transferencia."""
        return obj.items.count()


# Alias para ProductSerializer - usa el de creación/actualización
ProductSerializer = ProductCreateUpdateSerializer
