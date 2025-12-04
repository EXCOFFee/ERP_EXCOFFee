# ========================================================
# SISTEMA ERP UNIVERSAL - Admin de Ventas
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Configuración del admin de Django para ventas.
# ========================================================

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum

from .models import (
    CustomerGroup,
    Customer,
    CustomerAddress,
    CustomerContact,
    Quotation,
    QuotationLine,
    SalesOrder,
    SalesOrderLine,
    Invoice,
    InvoiceLine,
    Payment,
    PaymentAllocation,
    Shipment,
    ShipmentLine,
    PriceList,
    PriceListItem,
    Promotion,
)


# ========================================================
# Inlines
# ========================================================

class CustomerAddressInline(admin.TabularInline):
    model = CustomerAddress
    extra = 0
    fields = ['address_type', 'name', 'contact_name', 'phone', 'address', 'city', 'is_default']


class CustomerContactInline(admin.TabularInline):
    model = CustomerContact
    extra = 0
    fields = ['name', 'position', 'email', 'phone', 'is_primary']


class QuotationLineInline(admin.TabularInline):
    model = QuotationLine
    extra = 0
    fields = ['line_number', 'product', 'description', 'quantity', 'unit_price', 'discount_percent', 'line_total']
    readonly_fields = ['line_total']


class SalesOrderLineInline(admin.TabularInline):
    model = SalesOrderLine
    extra = 0
    fields = ['line_number', 'product', 'quantity', 'quantity_shipped', 'quantity_invoiced', 'unit_price', 'line_total', 'status']
    readonly_fields = ['quantity_shipped', 'quantity_invoiced', 'line_total']


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 0
    fields = ['line_number', 'product', 'description', 'quantity', 'unit_price', 'line_total']
    readonly_fields = ['line_total']


class PaymentAllocationInline(admin.TabularInline):
    model = PaymentAllocation
    extra = 0
    fields = ['invoice', 'amount']


class ShipmentLineInline(admin.TabularInline):
    model = ShipmentLine
    extra = 0
    fields = ['order_line', 'quantity', 'lot']


class PriceListItemInline(admin.TabularInline):
    model = PriceListItem
    extra = 0
    fields = ['product', 'min_quantity', 'unit_price', 'discount_percent']


# ========================================================
# Grupos de Clientes
# ========================================================

@admin.register(CustomerGroup)
class CustomerGroupAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'discount_percentage', 'credit_limit', 'customers_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['name']
    
    def customers_count(self, obj):
        return obj.customers.count()
    customers_count.short_description = 'Clientes'


# ========================================================
# Clientes
# ========================================================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'customer_type', 'group', 'email', 'phone', 
                    'credit_display', 'status', 'is_active']
    list_filter = ['customer_type', 'group', 'status', 'is_active', 'country']
    search_fields = ['code', 'name', 'trade_name', 'tax_id', 'email']
    ordering = ['name']
    readonly_fields = ['credit_used', 'created_at', 'updated_at']
    inlines = [CustomerAddressInline, CustomerContactInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('code', 'customer_type', 'name', 'trade_name', 'tax_id', 'group')
        }),
        ('Contacto', {
            'fields': ('contact_name', 'email', 'phone', 'mobile', 'website')
        }),
        ('Dirección', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Crédito y Pagos', {
            'fields': ('credit_limit', 'credit_used', 'payment_term', 'currency')
        }),
        ('Comercial', {
            'fields': ('sales_rep', 'status', 'is_active', 'notes')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def credit_display(self, obj):
        available = obj.credit_limit - obj.credit_used
        if available < 0:
            color = 'red'
        elif available < obj.credit_limit * 0.2:
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {};">{:,.2f} / {:,.2f}</span>',
            color, obj.credit_used, obj.credit_limit
        )
    credit_display.short_description = 'Crédito (Usado/Límite)'


# ========================================================
# Cotizaciones
# ========================================================

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['number', 'customer', 'date', 'valid_until', 'total_display', 'status', 'sales_rep']
    list_filter = ['status', 'date', 'sales_rep']
    search_fields = ['number', 'customer__name', 'customer__code']
    date_hierarchy = 'date'
    ordering = ['-date']
    readonly_fields = ['number', 'subtotal', 'discount_amount', 'tax_amount', 'total', 'created_at', 'created_by']
    inlines = [QuotationLineInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('number', 'customer', 'contact', 'date', 'valid_until', 'sales_rep')
        }),
        ('Condiciones', {
            'fields': ('payment_term', 'currency', 'exchange_rate')
        }),
        ('Totales', {
            'fields': ('subtotal', 'discount_amount', 'tax_amount', 'total')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Notas', {
            'fields': ('notes', 'terms_conditions'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_display(self, obj):
        return format_html('{} {:,.2f}', obj.currency, obj.total)
    total_display.short_description = 'Total'
    
    actions = ['mark_as_sent', 'mark_as_expired']
    
    @admin.action(description='Marcar como enviadas')
    def mark_as_sent(self, request, queryset):
        updated = queryset.filter(status='draft').update(status='sent')
        self.message_user(request, f'{updated} cotizaciones marcadas como enviadas.')
    
    @admin.action(description='Marcar como expiradas')
    def mark_as_expired(self, request, queryset):
        updated = queryset.filter(status='sent').update(status='expired')
        self.message_user(request, f'{updated} cotizaciones marcadas como expiradas.')


# ========================================================
# Órdenes de Venta
# ========================================================

@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ['number', 'customer', 'order_date', 'required_date', 'total_display', 
                    'status', 'priority', 'sales_rep']
    list_filter = ['status', 'order_type', 'priority', 'order_date', 'warehouse']
    search_fields = ['number', 'customer__name', 'customer__code', 'customer_reference']
    date_hierarchy = 'order_date'
    ordering = ['-order_date']
    readonly_fields = ['number', 'subtotal', 'discount_amount', 'tax_amount', 'total', 
                       'created_at', 'created_by']
    inlines = [SalesOrderLineInline]
    raw_id_fields = ['customer', 'quotation']
    
    fieldsets = (
        ('Información General', {
            'fields': ('number', 'customer', 'quotation', 'order_date', 'required_date', 
                       'promised_date', 'order_type', 'priority')
        }),
        ('Comercial', {
            'fields': ('sales_rep', 'customer_reference')
        }),
        ('Direcciones', {
            'fields': ('billing_address', 'shipping_address', 'warehouse')
        }),
        ('Condiciones', {
            'fields': ('payment_term', 'currency', 'exchange_rate')
        }),
        ('Totales', {
            'fields': ('subtotal', 'discount_amount', 'tax_amount', 'shipping_amount', 'total')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Notas', {
            'fields': ('notes', 'customer_notes'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_display(self, obj):
        return format_html('{} {:,.2f}', obj.currency, obj.total)
    total_display.short_description = 'Total'
    
    actions = ['confirm_orders', 'cancel_orders']
    
    @admin.action(description='Confirmar órdenes seleccionadas')
    def confirm_orders(self, request, queryset):
        from .services import SalesService
        confirmed = 0
        for order in queryset.filter(status='draft'):
            try:
                SalesService.confirm_order(order, request.user)
                confirmed += 1
            except Exception:
                pass
        self.message_user(request, f'{confirmed} órdenes confirmadas.')
    
    @admin.action(description='Cancelar órdenes seleccionadas')
    def cancel_orders(self, request, queryset):
        from .services import SalesService
        cancelled = 0
        for order in queryset.exclude(status__in=['shipped', 'delivered', 'invoiced', 'cancelled']):
            try:
                SalesService.cancel_order(order, 'Cancelación masiva desde admin', request.user)
                cancelled += 1
            except Exception:
                pass
        self.message_user(request, f'{cancelled} órdenes canceladas.')


# ========================================================
# Facturas
# ========================================================

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['number', 'invoice_type', 'customer', 'invoice_date', 'due_date',
                    'total_display', 'amount_paid', 'balance_display', 'status', 'is_overdue']
    list_filter = ['invoice_type', 'status', 'invoice_date', 'due_date']
    search_fields = ['number', 'customer__name', 'customer__code']
    date_hierarchy = 'invoice_date'
    ordering = ['-invoice_date']
    readonly_fields = ['number', 'subtotal', 'discount_amount', 'tax_amount', 'total',
                       'amount_paid', 'journal_entry', 'created_at', 'created_by']
    inlines = [InvoiceLineInline]
    raw_id_fields = ['customer', 'sales_order']
    
    fieldsets = (
        ('Información General', {
            'fields': ('number', 'invoice_type', 'customer', 'sales_order', 'invoice_date', 'due_date')
        }),
        ('Condiciones', {
            'fields': ('payment_term', 'currency', 'exchange_rate')
        }),
        ('Totales', {
            'fields': ('subtotal', 'discount_amount', 'tax_amount', 'total', 'amount_paid')
        }),
        ('Estado', {
            'fields': ('status', 'journal_entry')
        }),
        ('Dirección de Facturación', {
            'fields': ('billing_address',),
            'classes': ('collapse',)
        }),
        ('Notas', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_display(self, obj):
        return format_html('{} {:,.2f}', obj.currency, obj.total)
    total_display.short_description = 'Total'
    
    def balance_display(self, obj):
        balance = obj.total - obj.amount_paid
        if balance > 0:
            color = 'red' if obj.is_overdue else 'orange'
        else:
            color = 'green'
        return format_html('<span style="color: {};">{:,.2f}</span>', color, balance)
    balance_display.short_description = 'Saldo'
    
    def is_overdue(self, obj):
        from datetime import date
        if obj.status in ['paid', 'void']:
            return False
        return obj.due_date < date.today()
    is_overdue.boolean = True
    is_overdue.short_description = 'Vencida'


# ========================================================
# Pagos
# ========================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['number', 'customer', 'payment_date', 'payment_method', 
                    'amount_display', 'allocated_amount', 'status']
    list_filter = ['payment_method', 'status', 'payment_date']
    search_fields = ['number', 'customer__name', 'reference']
    date_hierarchy = 'payment_date'
    ordering = ['-payment_date']
    readonly_fields = ['number', 'journal_entry', 'created_at', 'created_by']
    inlines = [PaymentAllocationInline]
    raw_id_fields = ['customer']
    
    def amount_display(self, obj):
        return format_html('{} {:,.2f}', obj.currency, obj.amount)
    amount_display.short_description = 'Monto'
    
    def allocated_amount(self, obj):
        total = obj.allocations.aggregate(total=Sum('amount'))['total'] or 0
        return format_html('{:,.2f}', total)
    allocated_amount.short_description = 'Aplicado'


# ========================================================
# Envíos
# ========================================================

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['number', 'sales_order', 'shipment_date', 'estimated_delivery',
                    'carrier', 'tracking_number', 'status']
    list_filter = ['status', 'carrier', 'shipment_date', 'warehouse']
    search_fields = ['number', 'tracking_number', 'sales_order__number']
    date_hierarchy = 'shipment_date'
    ordering = ['-shipment_date']
    readonly_fields = ['number', 'created_at', 'created_by']
    inlines = [ShipmentLineInline]
    raw_id_fields = ['sales_order']
    
    def get_customer(self, obj):
        return obj.sales_order.customer.name
    get_customer.short_description = 'Cliente'


# ========================================================
# Listas de Precios
# ========================================================

@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'currency', 'is_default', 'valid_from', 
                    'valid_until', 'items_count', 'is_active']
    list_filter = ['is_active', 'is_default', 'currency']
    search_fields = ['code', 'name']
    ordering = ['name']
    inlines = [PriceListItemInline]
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Items'


# ========================================================
# Promociones
# ========================================================

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'promotion_type', 'discount_value', 
                    'valid_from', 'valid_until', 'usage_display', 'is_active']
    list_filter = ['promotion_type', 'is_active', 'valid_from']
    search_fields = ['code', 'name']
    filter_horizontal = ['products', 'categories', 'customer_groups']
    ordering = ['-valid_from']
    
    def usage_display(self, obj):
        if obj.usage_limit:
            return f'{obj.usage_count} / {obj.usage_limit}'
        return str(obj.usage_count)
    usage_display.short_description = 'Uso'
