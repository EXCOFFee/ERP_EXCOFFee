# ========================================================
# SISTEMA ERP UNIVERSAL - Serializadores de Ventas
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Serializadores para el módulo de ventas.
# ========================================================

from rest_framework import serializers
from django.db import transaction
from decimal import Decimal

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
# Clientes
# ========================================================

class CustomerGroupSerializer(serializers.ModelSerializer):
    """Serializador de grupos de clientes."""
    
    customers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerGroup
        fields = [
            'id', 'code', 'name', 'description', 'discount_percentage',
            'credit_limit', 'payment_term', 'is_active', 'customers_count'
        ]
    
    def get_customers_count(self, obj):
        return obj.customers.filter(is_active=True).count()


class CustomerAddressSerializer(serializers.ModelSerializer):
    """Serializador de direcciones de cliente."""
    
    class Meta:
        model = CustomerAddress
        fields = [
            'id', 'address_type', 'name', 'contact_name', 'phone',
            'address', 'city', 'state', 'country', 'postal_code', 'is_default'
        ]


class CustomerContactSerializer(serializers.ModelSerializer):
    """Serializador de contactos de cliente."""
    
    class Meta:
        model = CustomerContact
        fields = [
            'id', 'name', 'position', 'email', 'phone', 'mobile',
            'is_primary', 'notes'
        ]


class CustomerListSerializer(serializers.ModelSerializer):
    """Serializador de lista de clientes."""
    
    group_name = serializers.CharField(source='group.name', read_only=True)
    sales_rep_name = serializers.CharField(
        source='sales_rep.full_name',
        read_only=True
    )
    available_credit = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = Customer
        fields = [
            'id', 'code', 'name', 'trade_name', 'customer_type',
            'group', 'group_name', 'email', 'phone', 'city', 'country',
            'credit_limit', 'credit_used', 'available_credit',
            'sales_rep', 'sales_rep_name', 'status', 'is_active'
        ]


class CustomerDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado de cliente."""
    
    group_name = serializers.CharField(source='group.name', read_only=True)
    sales_rep_name = serializers.CharField(
        source='sales_rep.full_name',
        read_only=True
    )
    available_credit = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )
    addresses = CustomerAddressSerializer(many=True, read_only=True)
    contacts = CustomerContactSerializer(many=True, read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id', 'code', 'customer_type', 'name', 'trade_name', 'tax_id',
            'group', 'group_name', 'contact_name', 'email', 'phone', 'mobile',
            'website', 'address', 'city', 'state', 'country', 'postal_code',
            'credit_limit', 'credit_used', 'available_credit', 'payment_term',
            'currency', 'sales_rep', 'sales_rep_name', 'status', 'is_active',
            'notes', 'addresses', 'contacts', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'credit_used', 'created_at', 'updated_at']


class CustomerCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializador para crear/actualizar clientes."""
    
    addresses = CustomerAddressSerializer(many=True, required=False)
    contacts = CustomerContactSerializer(many=True, required=False)
    
    class Meta:
        model = Customer
        fields = [
            'code', 'customer_type', 'name', 'trade_name', 'tax_id', 'group',
            'contact_name', 'email', 'phone', 'mobile', 'website', 'address',
            'city', 'state', 'country', 'postal_code', 'credit_limit',
            'payment_term', 'currency', 'sales_rep', 'status', 'is_active',
            'notes', 'addresses', 'contacts'
        ]
    
    @transaction.atomic
    def create(self, validated_data):
        addresses_data = validated_data.pop('addresses', [])
        contacts_data = validated_data.pop('contacts', [])
        
        customer = Customer.objects.create(**validated_data)
        
        for address_data in addresses_data:
            CustomerAddress.objects.create(customer=customer, **address_data)
        
        for contact_data in contacts_data:
            CustomerContact.objects.create(customer=customer, **contact_data)
        
        return customer
    
    @transaction.atomic
    def update(self, instance, validated_data):
        addresses_data = validated_data.pop('addresses', None)
        contacts_data = validated_data.pop('contacts', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if addresses_data is not None:
            instance.addresses.all().delete()
            for address_data in addresses_data:
                CustomerAddress.objects.create(customer=instance, **address_data)
        
        if contacts_data is not None:
            instance.contacts.all().delete()
            for contact_data in contacts_data:
                CustomerContact.objects.create(customer=instance, **contact_data)
        
        return instance


# ========================================================
# Cotizaciones
# ========================================================

class QuotationLineSerializer(serializers.ModelSerializer):
    """Serializador de líneas de cotización."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    
    class Meta:
        model = QuotationLine
        fields = [
            'id', 'line_number', 'product', 'product_name', 'product_sku',
            'description', 'quantity', 'unit', 'unit_name', 'unit_price',
            'discount_percent', 'discount_amount', 'tax', 'tax_amount',
            'line_total'
        ]
        read_only_fields = ['id', 'discount_amount', 'tax_amount', 'line_total']


class QuotationListSerializer(serializers.ModelSerializer):
    """Serializador de lista de cotizaciones."""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    sales_rep_name = serializers.CharField(
        source='sales_rep.full_name',
        read_only=True
    )
    lines_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quotation
        fields = [
            'id', 'number', 'customer', 'customer_name', 'date', 'valid_until',
            'sales_rep', 'sales_rep_name', 'currency', 'total', 'status',
            'lines_count'
        ]
    
    def get_lines_count(self, obj):
        return obj.lines.count()


class QuotationDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado de cotización."""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    sales_rep_name = serializers.CharField(
        source='sales_rep.full_name',
        read_only=True
    )
    lines = QuotationLineSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quotation
        fields = [
            'id', 'number', 'customer', 'customer_name', 'contact', 'date',
            'valid_until', 'sales_rep', 'sales_rep_name', 'payment_term',
            'currency', 'exchange_rate', 'subtotal', 'discount_amount',
            'tax_amount', 'total', 'status', 'notes', 'terms_conditions',
            'lines', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'subtotal', 'discount_amount', 'tax_amount', 'total',
            'created_by', 'created_at', 'updated_at'
        ]


class QuotationCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear cotizaciones."""
    
    lines = QuotationLineSerializer(many=True)
    
    class Meta:
        model = Quotation
        fields = [
            'number', 'customer', 'contact', 'date', 'valid_until',
            'sales_rep', 'payment_term', 'currency', 'exchange_rate',
            'notes', 'terms_conditions', 'lines'
        ]
    
    @transaction.atomic
    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        quotation = Quotation.objects.create(**validated_data)
        
        for i, line_data in enumerate(lines_data, 1):
            line_data['line_number'] = i
            self._calculate_line_totals(line_data)
            QuotationLine.objects.create(quotation=quotation, **line_data)
        
        self._calculate_quotation_totals(quotation)
        return quotation
    
    def _calculate_line_totals(self, line_data):
        """Calcula totales de línea."""
        quantity = line_data['quantity']
        unit_price = line_data['unit_price']
        discount_percent = line_data.get('discount_percent', Decimal('0'))
        
        subtotal = quantity * unit_price
        discount_amount = subtotal * (discount_percent / 100)
        line_data['discount_amount'] = discount_amount
        
        taxable_amount = subtotal - discount_amount
        tax = line_data.get('tax')
        if tax:
            line_data['tax_amount'] = taxable_amount * (tax.rate / 100)
        else:
            line_data['tax_amount'] = Decimal('0')
        
        line_data['line_total'] = taxable_amount + line_data['tax_amount']
    
    def _calculate_quotation_totals(self, quotation):
        """Calcula totales de cotización."""
        lines = quotation.lines.all()
        
        quotation.subtotal = sum(
            l.quantity * l.unit_price for l in lines
        )
        quotation.discount_amount = sum(l.discount_amount for l in lines)
        quotation.tax_amount = sum(l.tax_amount for l in lines)
        quotation.total = sum(l.line_total for l in lines)
        quotation.save()


# ========================================================
# Órdenes de Venta
# ========================================================

class SalesOrderLineSerializer(serializers.ModelSerializer):
    """Serializador de líneas de orden de venta."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    quantity_pending = serializers.DecimalField(
        max_digits=14, decimal_places=4, read_only=True
    )
    
    class Meta:
        model = SalesOrderLine
        fields = [
            'id', 'line_number', 'product', 'product_name', 'product_sku',
            'description', 'quantity', 'quantity_reserved', 'quantity_shipped',
            'quantity_delivered', 'quantity_invoiced', 'quantity_pending',
            'unit', 'unit_name', 'unit_price', 'discount_percent',
            'discount_amount', 'tax', 'tax_amount', 'line_total', 'status',
            'warehouse', 'notes'
        ]
        read_only_fields = [
            'id', 'quantity_reserved', 'quantity_shipped', 'quantity_delivered',
            'quantity_invoiced', 'discount_amount', 'tax_amount', 'line_total'
        ]


class SalesOrderListSerializer(serializers.ModelSerializer):
    """Serializador de lista de órdenes de venta."""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    sales_rep_name = serializers.CharField(
        source='sales_rep.full_name',
        read_only=True
    )
    lines_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SalesOrder
        fields = [
            'id', 'number', 'customer', 'customer_name', 'order_date',
            'required_date', 'order_type', 'priority', 'sales_rep',
            'sales_rep_name', 'currency', 'total', 'status', 'lines_count'
        ]
    
    def get_lines_count(self, obj):
        return obj.lines.count()


class SalesOrderDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado de orden de venta."""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    sales_rep_name = serializers.CharField(
        source='sales_rep.full_name',
        read_only=True
    )
    lines = SalesOrderLineSerializer(many=True, read_only=True)
    shipments_count = serializers.SerializerMethodField()
    invoices_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SalesOrder
        fields = [
            'id', 'number', 'customer', 'customer_name', 'quotation',
            'order_date', 'required_date', 'promised_date', 'shipped_date',
            'order_type', 'priority', 'sales_rep', 'sales_rep_name',
            'billing_address', 'shipping_address', 'warehouse', 'payment_term',
            'currency', 'exchange_rate', 'subtotal', 'discount_amount',
            'tax_amount', 'shipping_amount', 'total', 'status',
            'customer_reference', 'notes', 'customer_notes', 'lines',
            'shipments_count', 'invoices_count', 'created_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'subtotal', 'discount_amount', 'tax_amount', 'total',
            'created_by', 'created_at', 'updated_at'
        ]
    
    def get_shipments_count(self, obj):
        return obj.shipments.count()
    
    def get_invoices_count(self, obj):
        return obj.invoices.count()


class SalesOrderCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear órdenes de venta."""
    
    lines = SalesOrderLineSerializer(many=True)
    
    class Meta:
        model = SalesOrder
        fields = [
            'number', 'customer', 'quotation', 'order_date', 'required_date',
            'promised_date', 'order_type', 'priority', 'sales_rep',
            'billing_address', 'shipping_address', 'warehouse', 'payment_term',
            'currency', 'exchange_rate', 'shipping_amount', 'customer_reference',
            'notes', 'customer_notes', 'lines'
        ]
    
    @transaction.atomic
    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        order = SalesOrder.objects.create(**validated_data)
        
        for i, line_data in enumerate(lines_data, 1):
            line_data['line_number'] = i
            self._calculate_line_totals(line_data)
            SalesOrderLine.objects.create(order=order, **line_data)
        
        self._calculate_order_totals(order)
        return order
    
    def _calculate_line_totals(self, line_data):
        """Calcula totales de línea."""
        quantity = line_data['quantity']
        unit_price = line_data['unit_price']
        discount_percent = line_data.get('discount_percent', Decimal('0'))
        
        subtotal = quantity * unit_price
        discount_amount = subtotal * (discount_percent / 100)
        line_data['discount_amount'] = discount_amount
        
        taxable_amount = subtotal - discount_amount
        tax = line_data.get('tax')
        if tax:
            line_data['tax_amount'] = taxable_amount * (tax.rate / 100)
        else:
            line_data['tax_amount'] = Decimal('0')
        
        line_data['line_total'] = taxable_amount + line_data['tax_amount']
    
    def _calculate_order_totals(self, order):
        """Calcula totales de orden."""
        lines = order.lines.all()
        
        order.subtotal = sum(l.quantity * l.unit_price for l in lines)
        order.discount_amount = sum(l.discount_amount for l in lines)
        order.tax_amount = sum(l.tax_amount for l in lines)
        order.total = (
            order.subtotal - order.discount_amount +
            order.tax_amount + order.shipping_amount
        )
        order.save()


# ========================================================
# Facturas
# ========================================================

class InvoiceLineSerializer(serializers.ModelSerializer):
    """Serializador de líneas de factura."""
    
    product_name = serializers.CharField(
        source='product.name',
        read_only=True,
        allow_null=True
    )
    unit_name = serializers.CharField(
        source='unit.name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = InvoiceLine
        fields = [
            'id', 'line_number', 'product', 'product_name', 'sales_order_line',
            'description', 'quantity', 'unit', 'unit_name', 'unit_price',
            'discount_percent', 'discount_amount', 'tax', 'tax_amount',
            'line_total', 'account'
        ]
        read_only_fields = ['id', 'discount_amount', 'tax_amount', 'line_total']


class InvoiceListSerializer(serializers.ModelSerializer):
    """Serializador de lista de facturas."""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    balance = serializers.DecimalField(
        max_digits=18, decimal_places=2, read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'number', 'invoice_type', 'customer', 'customer_name',
            'invoice_date', 'due_date', 'currency', 'total', 'amount_paid',
            'balance', 'status', 'is_overdue'
        ]


class InvoiceDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado de factura."""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    balance = serializers.DecimalField(
        max_digits=18, decimal_places=2, read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)
    lines = InvoiceLineSerializer(many=True, read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'number', 'invoice_type', 'customer', 'customer_name',
            'sales_order', 'invoice_date', 'due_date', 'payment_term',
            'currency', 'exchange_rate', 'subtotal', 'discount_amount',
            'tax_amount', 'total', 'amount_paid', 'balance', 'status',
            'is_overdue', 'billing_address', 'notes', 'journal_entry',
            'lines', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'subtotal', 'discount_amount', 'tax_amount', 'total',
            'amount_paid', 'journal_entry', 'created_by', 'created_at',
            'updated_at'
        ]


# ========================================================
# Pagos
# ========================================================

class PaymentAllocationSerializer(serializers.ModelSerializer):
    """Serializador de aplicación de pagos."""
    
    invoice_number = serializers.CharField(
        source='invoice.number',
        read_only=True
    )
    invoice_total = serializers.DecimalField(
        source='invoice.total',
        max_digits=18,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = PaymentAllocation
        fields = ['id', 'invoice', 'invoice_number', 'invoice_total', 'amount']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializador de pagos."""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    allocations = PaymentAllocationSerializer(many=True, read_only=True)
    allocated_amount = serializers.SerializerMethodField()
    unallocated_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'number', 'customer', 'customer_name', 'payment_date',
            'payment_method', 'reference', 'amount', 'currency', 'exchange_rate',
            'status', 'bank_account', 'journal_entry', 'notes', 'allocations',
            'allocated_amount', 'unallocated_amount', 'created_by', 'created_at'
        ]
        read_only_fields = ['id', 'journal_entry', 'created_by', 'created_at']
    
    def get_allocated_amount(self, obj):
        return sum(a.amount for a in obj.allocations.all())
    
    def get_unallocated_amount(self, obj):
        allocated = sum(a.amount for a in obj.allocations.all())
        return obj.amount - allocated


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear pagos."""
    
    allocations = PaymentAllocationSerializer(many=True, required=False)
    
    class Meta:
        model = Payment
        fields = [
            'number', 'customer', 'payment_date', 'payment_method',
            'reference', 'amount', 'currency', 'exchange_rate',
            'bank_account', 'notes', 'allocations'
        ]
    
    @transaction.atomic
    def create(self, validated_data):
        allocations_data = validated_data.pop('allocations', [])
        payment = Payment.objects.create(**validated_data)
        
        for allocation_data in allocations_data:
            PaymentAllocation.objects.create(
                payment=payment,
                **allocation_data
            )
            
            # Actualizar factura
            invoice = allocation_data['invoice']
            invoice.amount_paid += allocation_data['amount']
            if invoice.amount_paid >= invoice.total:
                invoice.status = 'paid'
            else:
                invoice.status = 'partial'
            invoice.save()
        
        return payment


# ========================================================
# Envíos
# ========================================================

class ShipmentLineSerializer(serializers.ModelSerializer):
    """Serializador de líneas de envío."""
    
    product_name = serializers.CharField(
        source='order_line.product.name',
        read_only=True
    )
    product_sku = serializers.CharField(
        source='order_line.product.sku',
        read_only=True
    )
    
    class Meta:
        model = ShipmentLine
        fields = [
            'id', 'order_line', 'product_name', 'product_sku',
            'quantity', 'lot', 'serial_numbers'
        ]


class ShipmentListSerializer(serializers.ModelSerializer):
    """Serializador de lista de envíos."""
    
    order_number = serializers.CharField(
        source='sales_order.number',
        read_only=True
    )
    customer_name = serializers.CharField(
        source='sales_order.customer.name',
        read_only=True
    )
    
    class Meta:
        model = Shipment
        fields = [
            'id', 'number', 'sales_order', 'order_number', 'customer_name',
            'shipment_date', 'estimated_delivery', 'carrier', 'tracking_number',
            'status', 'total_packages'
        ]


class ShipmentDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado de envío."""
    
    order_number = serializers.CharField(
        source='sales_order.number',
        read_only=True
    )
    customer_name = serializers.CharField(
        source='sales_order.customer.name',
        read_only=True
    )
    lines = ShipmentLineSerializer(many=True, read_only=True)
    
    class Meta:
        model = Shipment
        fields = [
            'id', 'number', 'sales_order', 'order_number', 'customer_name',
            'shipment_date', 'estimated_delivery', 'actual_delivery',
            'carrier', 'tracking_number', 'tracking_url', 'warehouse',
            'shipping_address', 'total_weight', 'total_packages',
            'shipping_cost', 'status', 'notes', 'lines',
            'created_by', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


# ========================================================
# Precios y Promociones
# ========================================================

class PriceListItemSerializer(serializers.ModelSerializer):
    """Serializador de items de lista de precios."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = PriceListItem
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'min_quantity', 'unit_price', 'discount_percent'
        ]


class PriceListSerializer(serializers.ModelSerializer):
    """Serializador de lista de precios."""
    
    items = PriceListItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PriceList
        fields = [
            'id', 'code', 'name', 'description', 'currency', 'is_default',
            'valid_from', 'valid_until', 'is_active', 'items', 'items_count'
        ]
    
    def get_items_count(self, obj):
        return obj.items.count()


class PromotionSerializer(serializers.ModelSerializer):
    """Serializador de promociones."""
    
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Promotion
        fields = [
            'id', 'code', 'name', 'description', 'promotion_type',
            'discount_value', 'min_purchase_amount', 'max_discount_amount',
            'valid_from', 'valid_until', 'usage_limit', 'usage_count',
            'products', 'categories', 'customer_groups', 'is_active', 'is_valid'
        ]
        read_only_fields = ['usage_count']


# ========================================================
# Reportes
# ========================================================

class SalesSummarySerializer(serializers.Serializer):
    """Serializador para resumen de ventas."""
    
    period = serializers.CharField()
    total_orders = serializers.IntegerField()
    total_invoiced = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_collected = serializers.DecimalField(max_digits=18, decimal_places=2)
    average_order_value = serializers.DecimalField(max_digits=18, decimal_places=2)
    by_sales_rep = serializers.ListField()
    by_customer_group = serializers.ListField()
    top_products = serializers.ListField()
    top_customers = serializers.ListField()


class CustomerStatementSerializer(serializers.Serializer):
    """Serializador para estado de cuenta de cliente."""
    
    customer = serializers.DictField()
    opening_balance = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_invoiced = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=18, decimal_places=2)
    closing_balance = serializers.DecimalField(max_digits=18, decimal_places=2)
    transactions = serializers.ListField()
    aging = serializers.DictField()
