# ========================================================
# SISTEMA ERP UNIVERSAL - Admin de Compras
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Configuración del admin de Django para compras.
# ========================================================

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum

from .models import (
    SupplierCategory,
    Supplier,
    SupplierContact,
    SupplierAddress,
    SupplierProduct,
    PurchaseRequisition,
    PurchaseRequisitionLine,
    PurchaseOrder,
    PurchaseOrderLine,
    GoodsReceipt,
    GoodsReceiptLine,
    SupplierInvoice,
    SupplierInvoiceLine,
    SupplierPayment,
    SupplierPaymentAllocation,
    SupplierEvaluation,
)


# ========================================================
# Categorías de Proveedores
# ========================================================

@admin.register(SupplierCategory)
class SupplierCategoryAdmin(admin.ModelAdmin):
    """Admin para categorías de proveedores."""
    
    list_display = ['code', 'name', 'suppliers_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['name']
    
    def suppliers_count(self, obj):
        return obj.suppliers.count()
    suppliers_count.short_description = 'Proveedores'


# ========================================================
# Proveedores
# ========================================================

class SupplierContactInline(admin.TabularInline):
    """Inline para contactos de proveedor."""
    model = SupplierContact
    extra = 0
    fields = ['contact_name', 'position', 'phone', 'mobile', 'email', 'is_primary']


class SupplierAddressInline(admin.TabularInline):
    """Inline para direcciones de proveedor."""
    model = SupplierAddress
    extra = 0
    fields = ['address_type', 'street', 'city', 'state', 'country', 'is_default']


class SupplierProductInline(admin.TabularInline):
    """Inline para productos de proveedor."""
    model = SupplierProduct
    extra = 0
    fields = ['product', 'supplier_code', 'unit_price', 'lead_time_days', 'is_preferred']
    raw_id_fields = ['product']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Admin para proveedores."""
    
    list_display = [
        'code', 'name', 'category', 'supplier_type', 
        'rating_display', 'status', 'is_active'
    ]
    list_filter = ['supplier_type', 'category', 'status', 'is_active', 'country']
    search_fields = ['code', 'name', 'trade_name', 'tax_id', 'email']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Información General', {
            'fields': ('code', 'name', 'trade_name', 'supplier_type', 'category')
        }),
        ('Datos Fiscales', {
            'fields': ('tax_id', 'tax_regime', 'tax_residence')
        }),
        ('Contacto', {
            'fields': ('email', 'phone', 'mobile', 'website')
        }),
        ('Ubicación', {
            'fields': ('country', 'currency')
        }),
        ('Condiciones Comerciales', {
            'fields': ('payment_term', 'credit_limit', 'credit_days', 'discount_percent')
        }),
        ('Estado', {
            'fields': ('status', 'rating', 'classification', 'is_active')
        }),
        ('Responsables', {
            'fields': ('buyer', 'accounting_account')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [SupplierContactInline, SupplierAddressInline, SupplierProductInline]
    
    def rating_display(self, obj):
        if obj.rating:
            stars = '★' * int(obj.rating) + '☆' * (5 - int(obj.rating))
            return f'{stars} ({obj.rating})'
        return '-'
    rating_display.short_description = 'Calificación'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SupplierProduct)
class SupplierProductAdmin(admin.ModelAdmin):
    """Admin para productos de proveedor."""
    
    list_display = [
        'supplier', 'product', 'supplier_code', 
        'unit_price', 'lead_time_days', 'is_preferred', 'is_active'
    ]
    list_filter = ['is_preferred', 'is_active', 'supplier']
    search_fields = ['supplier__name', 'product__name', 'supplier_code']
    raw_id_fields = ['supplier', 'product']


# ========================================================
# Solicitudes de Compra
# ========================================================

class PurchaseRequisitionLineInline(admin.TabularInline):
    """Inline para líneas de solicitud de compra."""
    model = PurchaseRequisitionLine
    extra = 0
    fields = ['product', 'description', 'quantity', 'unit', 'suggested_supplier', 'notes']
    raw_id_fields = ['product', 'suggested_supplier']


@admin.register(PurchaseRequisition)
class PurchaseRequisitionAdmin(admin.ModelAdmin):
    """Admin para solicitudes de compra."""
    
    list_display = [
        'number', 'date', 'department', 'requested_by', 
        'priority', 'status', 'lines_count'
    ]
    list_filter = ['status', 'priority', 'department']
    search_fields = ['number', 'requested_by__username']
    date_hierarchy = 'date'
    ordering = ['-date']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('General', {
            'fields': ('company', 'number', 'date', 'required_date')
        }),
        ('Origen', {
            'fields': ('department', 'requested_by', 'project', 'cost_center')
        }),
        ('Destino', {
            'fields': ('warehouse',)
        }),
        ('Estado', {
            'fields': ('status', 'priority', 'approved_by', 'approved_date', 'rejection_reason')
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PurchaseRequisitionLineInline]
    
    def lines_count(self, obj):
        return obj.lines.count()
    lines_count.short_description = 'Líneas'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ========================================================
# Órdenes de Compra
# ========================================================

class PurchaseOrderLineInline(admin.TabularInline):
    """Inline para líneas de orden de compra."""
    model = PurchaseOrderLine
    extra = 0
    fields = [
        'product', 'description', 'quantity', 'unit', 
        'unit_price', 'discount_percent', 'tax_percent', 'line_total',
        'quantity_received', 'quantity_invoiced'
    ]
    readonly_fields = ['line_total', 'quantity_received', 'quantity_invoiced']
    raw_id_fields = ['product']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    """Admin para órdenes de compra."""
    
    list_display = [
        'number', 'supplier', 'order_date', 'order_type',
        'total_display', 'status', 'buyer'
    ]
    list_filter = ['status', 'order_type', 'supplier', 'buyer']
    search_fields = ['number', 'supplier__name', 'supplier_reference']
    date_hierarchy = 'order_date'
    ordering = ['-order_date']
    readonly_fields = [
        'subtotal', 'discount_amount', 'tax_amount', 'total',
        'created_at', 'updated_at', 'created_by'
    ]
    raw_id_fields = ['supplier', 'requisition']
    
    fieldsets = (
        ('General', {
            'fields': ('company', 'number', 'order_date', 'required_date', 'order_type')
        }),
        ('Proveedor', {
            'fields': ('supplier', 'supplier_reference', 'requisition')
        }),
        ('Destino', {
            'fields': ('warehouse', 'delivery_address')
        }),
        ('Condiciones', {
            'fields': ('payment_term', 'currency', 'exchange_rate', 'incoterm')
        }),
        ('Totales', {
            'fields': ('subtotal', 'discount_amount', 'tax_amount', 'total')
        }),
        ('Estado', {
            'fields': (
                'status', 'approved_by', 'approved_date', 
                'sent_date', 'confirmed_date', 'promised_date'
            )
        }),
        ('Responsables', {
            'fields': ('buyer',)
        }),
        ('Notas', {
            'fields': ('notes', 'internal_notes')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PurchaseOrderLineInline]
    
    def total_display(self, obj):
        return f'${obj.total:,.2f}'
    total_display.short_description = 'Total'
    total_display.admin_order_field = 'total'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ========================================================
# Recepción de Mercancía
# ========================================================

class GoodsReceiptLineInline(admin.TabularInline):
    """Inline para líneas de recepción."""
    model = GoodsReceiptLine
    extra = 0
    fields = [
        'order_line', 'product', 'quantity_received', 
        'quantity_accepted', 'quantity_rejected', 'rejection_reason'
    ]
    raw_id_fields = ['order_line', 'product']


@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    """Admin para recepciones de mercancía."""
    
    list_display = [
        'number', 'purchase_order', 'receipt_date', 
        'supplier_delivery_note', 'status', 'warehouse'
    ]
    list_filter = ['status', 'warehouse']
    search_fields = ['number', 'purchase_order__number', 'supplier_delivery_note']
    date_hierarchy = 'receipt_date'
    ordering = ['-receipt_date']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    raw_id_fields = ['purchase_order']
    
    fieldsets = (
        ('General', {
            'fields': ('company', 'number', 'receipt_date', 'purchase_order')
        }),
        ('Recepción', {
            'fields': ('warehouse', 'received_by', 'supplier_delivery_note')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [GoodsReceiptLineInline]
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ========================================================
# Facturas de Proveedor
# ========================================================

class SupplierInvoiceLineInline(admin.TabularInline):
    """Inline para líneas de factura de proveedor."""
    model = SupplierInvoiceLine
    extra = 0
    fields = [
        'order_line', 'product', 'description', 'quantity',
        'unit_price', 'discount_percent', 'tax_percent', 'line_total'
    ]
    readonly_fields = ['line_total']
    raw_id_fields = ['order_line', 'product']


class SupplierPaymentAllocationInline(admin.TabularInline):
    """Inline para asignaciones de pago."""
    model = SupplierPaymentAllocation
    extra = 0
    fields = ['payment', 'amount', 'allocation_date']
    readonly_fields = ['allocation_date']
    raw_id_fields = ['payment']


@admin.register(SupplierInvoice)
class SupplierInvoiceAdmin(admin.ModelAdmin):
    """Admin para facturas de proveedor."""
    
    list_display = [
        'number', 'supplier', 'supplier_invoice_number', 'invoice_date',
        'due_date', 'total_display', 'balance_display', 'status'
    ]
    list_filter = ['invoice_type', 'status', 'supplier']
    search_fields = ['number', 'supplier_invoice_number', 'supplier__name']
    date_hierarchy = 'invoice_date'
    ordering = ['-invoice_date']
    readonly_fields = [
        'subtotal', 'discount_amount', 'tax_amount', 'total', 
        'amount_paid', 'created_at', 'updated_at', 'created_by'
    ]
    raw_id_fields = ['supplier', 'purchase_order', 'goods_receipt']
    
    fieldsets = (
        ('General', {
            'fields': (
                'company', 'number', 'invoice_type', 
                'supplier_invoice_number', 'invoice_date', 'due_date'
            )
        }),
        ('Proveedor', {
            'fields': ('supplier', 'purchase_order', 'goods_receipt')
        }),
        ('Totales', {
            'fields': ('subtotal', 'discount_amount', 'tax_amount', 'total', 'amount_paid')
        }),
        ('Estado', {
            'fields': ('status', 'validated_by', 'validated_date', 'approved_by', 'approved_date')
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [SupplierInvoiceLineInline, SupplierPaymentAllocationInline]
    
    def total_display(self, obj):
        return f'${obj.total:,.2f}'
    total_display.short_description = 'Total'
    total_display.admin_order_field = 'total'
    
    def balance_display(self, obj):
        balance = obj.total - obj.amount_paid
        if balance > 0:
            return format_html('<span style="color: red;">${:,.2f}</span>', balance)
        return format_html('<span style="color: green;">${:,.2f}</span>', balance)
    balance_display.short_description = 'Saldo'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ========================================================
# Pagos a Proveedores
# ========================================================

class PaymentAllocationInline(admin.TabularInline):
    """Inline para asignaciones de pago a facturas."""
    model = SupplierPaymentAllocation
    extra = 0
    fields = ['invoice', 'amount', 'allocation_date']
    readonly_fields = ['allocation_date']
    raw_id_fields = ['invoice']


@admin.register(SupplierPayment)
class SupplierPaymentAdmin(admin.ModelAdmin):
    """Admin para pagos a proveedores."""
    
    list_display = [
        'number', 'supplier', 'payment_date', 'payment_method',
        'amount_display', 'allocated_display', 'status'
    ]
    list_filter = ['payment_method', 'status', 'supplier']
    search_fields = ['number', 'supplier__name', 'reference', 'check_number']
    date_hierarchy = 'payment_date'
    ordering = ['-payment_date']
    readonly_fields = ['amount_allocated', 'created_at', 'updated_at', 'created_by']
    raw_id_fields = ['supplier', 'bank_account']
    
    fieldsets = (
        ('General', {
            'fields': ('company', 'number', 'payment_date', 'supplier')
        }),
        ('Pago', {
            'fields': ('payment_method', 'amount', 'currency', 'bank_account')
        }),
        ('Referencias', {
            'fields': ('reference', 'check_number', 'transaction_id')
        }),
        ('Asignación', {
            'fields': ('amount_allocated',)
        }),
        ('Estado', {
            'fields': ('status', 'approved_by', 'approved_date')
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PaymentAllocationInline]
    
    def amount_display(self, obj):
        return f'${obj.amount:,.2f}'
    amount_display.short_description = 'Monto'
    amount_display.admin_order_field = 'amount'
    
    def allocated_display(self, obj):
        return f'${obj.amount_allocated:,.2f}'
    allocated_display.short_description = 'Asignado'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ========================================================
# Evaluación de Proveedores
# ========================================================

@admin.register(SupplierEvaluation)
class SupplierEvaluationAdmin(admin.ModelAdmin):
    """Admin para evaluaciones de proveedores."""
    
    list_display = [
        'supplier', 'evaluation_date', 'quality_rating', 
        'delivery_rating', 'price_rating', 'service_rating',
        'overall_rating_display', 'evaluated_by'
    ]
    list_filter = ['supplier', 'evaluation_date']
    search_fields = ['supplier__name', 'evaluated_by__username']
    date_hierarchy = 'evaluation_date'
    ordering = ['-evaluation_date']
    raw_id_fields = ['supplier']
    
    fieldsets = (
        ('General', {
            'fields': ('supplier', 'evaluation_date', 'period_start', 'period_end')
        }),
        ('Calificaciones', {
            'fields': (
                'quality_rating', 'delivery_rating', 
                'price_rating', 'service_rating', 'overall_rating'
            )
        }),
        ('Métricas', {
            'fields': (
                'on_time_delivery_percent', 'quality_acceptance_percent',
                'response_time_hours', 'orders_evaluated'
            )
        }),
        ('Observaciones', {
            'fields': ('strengths', 'weaknesses', 'recommendations', 'notes')
        }),
        ('Auditoría', {
            'fields': ('evaluated_by',)
        }),
    )
    
    def overall_rating_display(self, obj):
        if obj.overall_rating:
            stars = '★' * int(obj.overall_rating) + '☆' * (5 - int(obj.overall_rating))
            return f'{stars} ({obj.overall_rating})'
        return '-'
    overall_rating_display.short_description = 'Calificación General'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.evaluated_by = request.user
        super().save_model(request, obj, form, change)
