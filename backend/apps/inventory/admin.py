# ========================================================
# SISTEMA ERP UNIVERSAL - Admin de Inventario
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Configuración del panel de administración
# de Django para el módulo de inventario.
# ========================================================

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, F

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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Administración de categorías de productos.
    """
    list_display = ['name', 'code', 'parent', 'is_active', 'product_count']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'code']
    prepopulated_fields = {'code': ('name',)}
    raw_id_fields = ['parent']
    ordering = ['name']
    
    def product_count(self, obj):
        """Cuenta productos en la categoría."""
        return obj.products.filter(is_deleted=False).count()
    product_count.short_description = 'Productos'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """
    Administración de marcas.
    """
    list_display = ['name', 'is_active', 'product_count']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['name']
    
    def product_count(self, obj):
        return obj.products.filter(is_deleted=False).count()
    product_count.short_description = 'Productos'


@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    """
    Administración de unidades de medida.
    """
    list_display = ['name', 'abbreviation', 'is_base_unit', 'is_active']
    list_filter = ['is_active', 'is_base_unit']
    search_fields = ['name', 'abbreviation']
    ordering = ['name']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    """
    Administración de almacenes.
    """
    list_display = ['name', 'code', 'warehouse_type', 'is_active', 'location_count', 'total_value']
    list_filter = ['is_active', 'warehouse_type']
    search_fields = ['name', 'code', 'address']
    ordering = ['name']
    
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'code', 'warehouse_type', 'is_active')
        }),
        ('Dirección', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Contacto', {
            'fields': ('manager_name', 'phone', 'email')
        }),
        ('Configuración', {
            'fields': ('is_default', 'allows_negative_stock')
        }),
    )
    
    def location_count(self, obj):
        return obj.locations.filter(is_active=True).count()
    location_count.short_description = 'Ubicaciones'
    
    def total_value(self, obj):
        value = Stock.objects.filter(
            warehouse=obj
        ).aggregate(
            total=Sum(F('quantity') * F('product__cost_price'))
        )['total']
        return f"${value or 0:,.2f}"
    total_value.short_description = 'Valor Total'


@admin.register(WarehouseLocation)
class WarehouseLocationAdmin(admin.ModelAdmin):
    """
    Administración de ubicaciones de almacén.
    """
    list_display = ['code', 'name', 'warehouse', 'location_type', 'is_active']
    list_filter = ['warehouse', 'location_type', 'is_active']
    search_fields = ['code', 'name']
    raw_id_fields = ['warehouse', 'parent']
    ordering = ['warehouse__name', 'code']


class StockInline(admin.TabularInline):
    """
    Stock del producto inline.
    """
    model = Stock
    extra = 0
    readonly_fields = ['warehouse', 'quantity', 'reserved_quantity', 'available_quantity']
    can_delete = False
    
    def available_quantity(self, obj):
        return obj.available_quantity
    available_quantity.short_description = 'Disponible'
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Administración de productos.
    
    Propósito:
        Panel completo para gestión de productos con
        visualización de stock y configuración avanzada.
    """
    list_display = [
        'sku', 'name', 'category', 'brand', 'cost_price', 
        'sale_price', 'total_stock', 'is_active', 'stock_status'
    ]
    list_filter = [
        'is_active', 'product_type', 'category', 'brand',
        'track_lots', 'track_serial_numbers'
    ]
    search_fields = ['sku', 'barcode', 'name', 'description']
    raw_id_fields = ['category', 'brand', 'default_supplier']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['name']
    inlines = [StockInline]
    
    fieldsets = (
        ('Identificación', {
            'fields': ('id', 'sku', 'barcode', 'qr_code', 'name')
        }),
        ('Clasificación', {
            'fields': ('product_type', 'category', 'brand', 'unit_of_measure')
        }),
        ('Descripción', {
            'fields': ('description', 'short_description', 'image'),
            'classes': ('collapse',)
        }),
        ('Precios', {
            'fields': ('cost_price', 'sale_price', 'tax_rate')
        }),
        ('Control de Stock', {
            'fields': ('min_stock', 'max_stock', 'reorder_point', 'reorder_quantity')
        }),
        ('Trazabilidad', {
            'fields': ('track_lots', 'track_serial_numbers', 'shelf_life_days')
        }),
        ('Dimensiones y Peso', {
            'fields': ('weight', 'length', 'width', 'height'),
            'classes': ('collapse',)
        }),
        ('Proveedor', {
            'fields': ('default_supplier',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_active', 'is_purchasable', 'is_sellable', 'abc_classification')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_stock(self, obj):
        """Stock total en todos los almacenes."""
        total = Stock.objects.filter(product=obj).aggregate(
            total=Sum('quantity')
        )['total']
        return total or 0
    total_stock.short_description = 'Stock Total'
    
    def stock_status(self, obj):
        """Estado del stock con indicador visual."""
        total = self.total_stock(obj)
        
        if total <= 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ Sin Stock</span>'
            )
        elif total <= obj.min_stock:
            return format_html(
                '<span style="color: orange;">⚠️ Bajo ({0})</span>',
                total
            )
        else:
            return format_html(
                '<span style="color: green;">✅ OK ({0})</span>',
                total
            )
    stock_status.short_description = 'Estado'


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """
    Administración de niveles de stock.
    """
    list_display = [
        'product', 'warehouse', 'quantity', 'reserved_quantity',
        'available', 'location', 'last_count_date'
    ]
    list_filter = ['warehouse']
    search_fields = ['product__name', 'product__sku', 'location']
    raw_id_fields = ['product', 'warehouse']
    readonly_fields = ['available']
    ordering = ['product__name']
    
    def available(self, obj):
        return obj.available_quantity
    available.short_description = 'Disponible'


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    """
    Administración de lotes.
    """
    list_display = [
        'lot_number', 'product', 'warehouse', 'quantity', 
        'manufacturing_date', 'expiry_date', 'status', 'days_to_expiry'
    ]
    list_filter = ['status', 'warehouse', 'expiry_date']
    search_fields = ['lot_number', 'product__name', 'product__sku']
    raw_id_fields = ['product', 'warehouse']
    date_hierarchy = 'expiry_date'
    ordering = ['expiry_date']
    
    def days_to_expiry(self, obj):
        """Días restantes para vencimiento."""
        if obj.expiry_date:
            from django.utils import timezone
            days = (obj.expiry_date - timezone.now().date()).days
            if days < 0:
                return format_html(
                    '<span style="color: red; font-weight: bold;">VENCIDO ({0}d)</span>',
                    days
                )
            elif days <= 30:
                return format_html(
                    '<span style="color: orange;">⚠️ {0} días</span>',
                    days
                )
            else:
                return f"{days} días"
        return "-"
    days_to_expiry.short_description = 'Días para Vencer'


@admin.register(SerialNumber)
class SerialNumberAdmin(admin.ModelAdmin):
    """
    Administración de números de serie.
    """
    list_display = ['serial', 'product', 'warehouse', 'status', 'sold_date']
    list_filter = ['status', 'warehouse']
    search_fields = ['serial', 'product__name', 'product__sku']
    raw_id_fields = ['product', 'warehouse', 'lot']
    readonly_fields = ['sold_date']
    ordering = ['-created_at']


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    """
    Administración de transacciones de inventario (solo lectura).
    """
    list_display = [
        'created_at', 'product', 'warehouse', 'transaction_type',
        'reason', 'quantity', 'stock_before', 'stock_after', 'created_by'
    ]
    list_filter = ['transaction_type', 'reason', 'warehouse', 'created_at']
    search_fields = ['product__name', 'product__sku', 'reference_type', 'notes']
    raw_id_fields = ['product', 'warehouse', 'lot', 'created_by']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = [
        'product', 'warehouse', 'transaction_type', 'reason', 'quantity',
        'stock_before', 'stock_after', 'unit_cost', 'lot', 'reference_type',
        'reference_id', 'notes', 'created_by', 'created_at'
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


class StockTransferItemInline(admin.TabularInline):
    """
    Items de transferencia inline.
    """
    model = StockTransferItem
    extra = 1
    raw_id_fields = ['product', 'lot']
    readonly_fields = ['received_quantity']


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    """
    Administración de transferencias de inventario.
    """
    list_display = [
        'transfer_number', 'source_warehouse', 'destination_warehouse',
        'status', 'created_at', 'shipped_date', 'received_date', 'item_count'
    ]
    list_filter = ['status', 'source_warehouse', 'destination_warehouse']
    search_fields = ['transfer_number', 'notes']
    raw_id_fields = ['source_warehouse', 'destination_warehouse', 'created_by', 'approved_by']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    inlines = [StockTransferItemInline]
    readonly_fields = ['transfer_number', 'shipped_date', 'received_date']
    
    fieldsets = (
        ('Transferencia', {
            'fields': ('transfer_number', 'status')
        }),
        ('Almacenes', {
            'fields': ('source_warehouse', 'destination_warehouse')
        }),
        ('Fechas', {
            'fields': ('expected_date', 'shipped_date', 'received_date')
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'approved_by'),
            'classes': ('collapse',)
        }),
    )
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'
