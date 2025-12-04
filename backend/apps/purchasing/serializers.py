# ========================================================
# SISTEMA ERP UNIVERSAL - Serializadores de Compras
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Serializadores para el módulo de compras.
# ========================================================

from rest_framework import serializers
from django.db import transaction
from decimal import Decimal

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
# Proveedores
# ========================================================

class SupplierCategorySerializer(serializers.ModelSerializer):
    """Serializador de categorías de proveedores."""
    
    suppliers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SupplierCategory
        fields = [
            'id', 'code', 'name', 'description', 'is_active', 'suppliers_count'
        ]
    
    def get_suppliers_count(self, obj):
        return obj.suppliers.filter(is_active=True).count()


class SupplierContactSerializer(serializers.ModelSerializer):
    """Serializador de contactos de proveedor."""
    
    class Meta:
        model = SupplierContact
        fields = [
            'id', 'name', 'position', 'department', 'email', 'phone',
            'mobile', 'is_primary', 'notes'
        ]


class SupplierAddressSerializer(serializers.ModelSerializer):
    """Serializador de direcciones de proveedor."""
    
    class Meta:
        model = SupplierAddress
        fields = [
            'id', 'address_type', 'name', 'address', 'city', 'state',
            'country', 'postal_code', 'is_default'
        ]


class SupplierProductSerializer(serializers.ModelSerializer):
    """Serializador de productos de proveedor."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = SupplierProduct
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'supplier_code',
            'supplier_name', 'unit_price', 'min_order_quantity', 'lead_time_days',
            'is_preferred', 'is_active', 'last_purchase_date', 'last_purchase_price'
        ]


class SupplierListSerializer(serializers.ModelSerializer):
    """Serializador de lista de proveedores."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    buyer_name = serializers.CharField(source='buyer.full_name', read_only=True)
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'code', 'name', 'supplier_type', 'category', 'category_name',
            'email', 'phone', 'city', 'country', 'rating', 'buyer', 'buyer_name',
            'status', 'is_active'
        ]


class SupplierDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado de proveedor."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    buyer_name = serializers.CharField(source='buyer.full_name', read_only=True)
    contacts = SupplierContactSerializer(many=True, read_only=True)
    addresses = SupplierAddressSerializer(many=True, read_only=True)
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'code', 'name', 'trade_name', 'tax_id', 'supplier_type',
            'category', 'category_name', 'contact_name', 'email', 'phone',
            'mobile', 'fax', 'website', 'address', 'city', 'state', 'country',
            'postal_code', 'payment_term', 'currency', 'credit_limit',
            'account_payable', 'buyer', 'buyer_name', 'rating', 'status',
            'is_active', 'tax_exempt', 'notes', 'contacts', 'addresses',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'rating', 'created_at', 'updated_at']


class SupplierCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializador para crear/actualizar proveedores."""
    
    contacts = SupplierContactSerializer(many=True, required=False)
    addresses = SupplierAddressSerializer(many=True, required=False)
    
    class Meta:
        model = Supplier
        fields = [
            'code', 'name', 'trade_name', 'tax_id', 'supplier_type', 'category',
            'contact_name', 'email', 'phone', 'mobile', 'fax', 'website',
            'address', 'city', 'state', 'country', 'postal_code', 'payment_term',
            'currency', 'credit_limit', 'account_payable', 'buyer', 'status',
            'is_active', 'tax_exempt', 'notes', 'contacts', 'addresses'
        ]
    
    @transaction.atomic
    def create(self, validated_data):
        contacts_data = validated_data.pop('contacts', [])
        addresses_data = validated_data.pop('addresses', [])
        
        supplier = Supplier.objects.create(**validated_data)
        
        for contact_data in contacts_data:
            SupplierContact.objects.create(supplier=supplier, **contact_data)
        
        for address_data in addresses_data:
            SupplierAddress.objects.create(supplier=supplier, **address_data)
        
        return supplier
    
    @transaction.atomic
    def update(self, instance, validated_data):
        contacts_data = validated_data.pop('contacts', None)
        addresses_data = validated_data.pop('addresses', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if contacts_data is not None:
            instance.contacts.all().delete()
            for contact_data in contacts_data:
                SupplierContact.objects.create(supplier=instance, **contact_data)
        
        if addresses_data is not None:
            instance.addresses.all().delete()
            for address_data in addresses_data:
                SupplierAddress.objects.create(supplier=instance, **address_data)
        
        return instance


# ========================================================
# Solicitudes de Compra
# ========================================================

class PurchaseRequisitionLineSerializer(serializers.ModelSerializer):
    """Serializador de líneas de solicitud de compra."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    supplier_name = serializers.CharField(
        source='suggested_supplier.name', read_only=True
    )
    quantity_pending = serializers.DecimalField(
        max_digits=14, decimal_places=4, read_only=True
    )
    
    class Meta:
        model = PurchaseRequisitionLine
        fields = [
            'id', 'line_number', 'product', 'product_name', 'product_sku',
            'description', 'quantity', 'unit', 'unit_name', 'estimated_unit_price',
            'quantity_ordered', 'quantity_pending', 'suggested_supplier',
            'supplier_name', 'notes'
        ]
        read_only_fields = ['id', 'quantity_ordered']


class PurchaseRequisitionListSerializer(serializers.ModelSerializer):
    """Serializador de lista de solicitudes de compra."""
    
    department_name = serializers.CharField(
        source='department.name', read_only=True
    )
    requested_by_name = serializers.CharField(
        source='requested_by.full_name', read_only=True
    )
    lines_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseRequisition
        fields = [
            'id', 'number', 'date', 'required_date', 'priority', 'department',
            'department_name', 'requested_by', 'requested_by_name',
            'warehouse', 'status', 'lines_count'
        ]
    
    def get_lines_count(self, obj):
        return obj.lines.count()


class PurchaseRequisitionDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado de solicitud de compra."""
    
    department_name = serializers.CharField(
        source='department.name', read_only=True
    )
    requested_by_name = serializers.CharField(
        source='requested_by.full_name', read_only=True
    )
    lines = PurchaseRequisitionLineSerializer(many=True, read_only=True)
    
    class Meta:
        model = PurchaseRequisition
        fields = [
            'id', 'number', 'date', 'required_date', 'priority', 'department',
            'department_name', 'requested_by', 'requested_by_name', 'warehouse',
            'status', 'approved_by', 'approved_date', 'rejection_reason',
            'justification', 'notes', 'lines', 'created_by', 'created_at'
        ]
        read_only_fields = [
            'id', 'approved_by', 'approved_date', 'created_by', 'created_at'
        ]


class PurchaseRequisitionCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear solicitudes de compra."""
    
    lines = PurchaseRequisitionLineSerializer(many=True)
    
    class Meta:
        model = PurchaseRequisition
        fields = [
            'number', 'date', 'required_date', 'priority', 'department',
            'requested_by', 'warehouse', 'justification', 'notes', 'lines'
        ]
    
    @transaction.atomic
    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        requisition = PurchaseRequisition.objects.create(**validated_data)
        
        for i, line_data in enumerate(lines_data, 1):
            line_data['line_number'] = i
            PurchaseRequisitionLine.objects.create(
                requisition=requisition, **line_data
            )
        
        return requisition


# ========================================================
# Órdenes de Compra
# ========================================================

class PurchaseOrderLineSerializer(serializers.ModelSerializer):
    """Serializador de líneas de orden de compra."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    quantity_pending = serializers.DecimalField(
        max_digits=14, decimal_places=4, read_only=True
    )
    
    class Meta:
        model = PurchaseOrderLine
        fields = [
            'id', 'line_number', 'product', 'product_name', 'product_sku',
            'description', 'quantity', 'quantity_received', 'quantity_invoiced',
            'quantity_pending', 'unit', 'unit_name', 'unit_price',
            'discount_percent', 'discount_amount', 'tax', 'tax_amount',
            'line_total', 'status', 'warehouse', 'required_date', 'notes'
        ]
        read_only_fields = [
            'id', 'quantity_received', 'quantity_invoiced',
            'discount_amount', 'tax_amount', 'line_total'
        ]


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    """Serializador de lista de órdenes de compra."""
    
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    buyer_name = serializers.CharField(source='buyer.full_name', read_only=True)
    lines_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'number', 'supplier', 'supplier_name', 'order_date',
            'required_date', 'order_type', 'buyer', 'buyer_name',
            'currency', 'total', 'status', 'lines_count'
        ]
    
    def get_lines_count(self, obj):
        return obj.lines.count()


class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado de orden de compra."""
    
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    buyer_name = serializers.CharField(source='buyer.full_name', read_only=True)
    lines = PurchaseOrderLineSerializer(many=True, read_only=True)
    receipts_count = serializers.SerializerMethodField()
    invoices_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'number', 'supplier', 'supplier_name', 'order_date',
            'required_date', 'promised_date', 'order_type', 'buyer', 'buyer_name',
            'warehouse', 'delivery_address', 'payment_term', 'currency',
            'exchange_rate', 'subtotal', 'discount_amount', 'tax_amount',
            'freight_amount', 'other_charges', 'total', 'status', 'requisition',
            'supplier_reference', 'notes', 'supplier_notes', 'terms_conditions',
            'approved_by', 'approved_date', 'lines', 'receipts_count',
            'invoices_count', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'subtotal', 'discount_amount', 'tax_amount', 'total',
            'approved_by', 'approved_date', 'created_by', 'created_at', 'updated_at'
        ]
    
    def get_receipts_count(self, obj):
        return obj.receipts.count()
    
    def get_invoices_count(self, obj):
        return obj.invoices.count()


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear órdenes de compra."""
    
    lines = PurchaseOrderLineSerializer(many=True)
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'number', 'supplier', 'order_date', 'required_date', 'promised_date',
            'order_type', 'buyer', 'warehouse', 'delivery_address', 'payment_term',
            'currency', 'exchange_rate', 'freight_amount', 'other_charges',
            'requisition', 'supplier_reference', 'notes', 'supplier_notes',
            'terms_conditions', 'lines'
        ]
    
    @transaction.atomic
    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        order = PurchaseOrder.objects.create(**validated_data)
        
        for i, line_data in enumerate(lines_data, 1):
            line_data['line_number'] = i
            self._calculate_line_totals(line_data)
            PurchaseOrderLine.objects.create(order=order, **line_data)
        
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
            order.subtotal - order.discount_amount + order.tax_amount +
            order.freight_amount + order.other_charges
        )
        order.save()


# ========================================================
# Recepción de Mercancía
# ========================================================

class GoodsReceiptLineSerializer(serializers.ModelSerializer):
    """Serializador de líneas de recepción."""
    
    product_name = serializers.CharField(
        source='order_line.product.name', read_only=True
    )
    product_sku = serializers.CharField(
        source='order_line.product.sku', read_only=True
    )
    
    class Meta:
        model = GoodsReceiptLine
        fields = [
            'id', 'order_line', 'product_name', 'product_sku', 'quantity_received',
            'quantity_accepted', 'quantity_rejected', 'rejection_reason',
            'location', 'lot', 'notes'
        ]


class GoodsReceiptListSerializer(serializers.ModelSerializer):
    """Serializador de lista de recepciones."""
    
    order_number = serializers.CharField(
        source='purchase_order.number', read_only=True
    )
    supplier_name = serializers.CharField(
        source='purchase_order.supplier.name', read_only=True
    )
    
    class Meta:
        model = GoodsReceipt
        fields = [
            'id', 'number', 'purchase_order', 'order_number', 'supplier_name',
            'receipt_date', 'warehouse', 'supplier_delivery_note', 'status'
        ]


class GoodsReceiptDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado de recepción."""
    
    order_number = serializers.CharField(
        source='purchase_order.number', read_only=True
    )
    supplier_name = serializers.CharField(
        source='purchase_order.supplier.name', read_only=True
    )
    lines = GoodsReceiptLineSerializer(many=True, read_only=True)
    
    class Meta:
        model = GoodsReceipt
        fields = [
            'id', 'number', 'purchase_order', 'order_number', 'supplier_name',
            'receipt_date', 'warehouse', 'supplier_delivery_note',
            'supplier_invoice_number', 'status', 'notes', 'received_by',
            'lines', 'created_by', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


# ========================================================
# Facturas de Proveedor
# ========================================================

class SupplierInvoiceLineSerializer(serializers.ModelSerializer):
    """Serializador de líneas de factura de proveedor."""
    
    product_name = serializers.CharField(
        source='product.name', read_only=True, allow_null=True
    )
    unit_name = serializers.CharField(
        source='unit.name', read_only=True, allow_null=True
    )
    
    class Meta:
        model = SupplierInvoiceLine
        fields = [
            'id', 'line_number', 'product', 'product_name', 'order_line',
            'description', 'quantity', 'unit', 'unit_name', 'unit_price',
            'discount_percent', 'discount_amount', 'tax', 'tax_amount',
            'line_total', 'account'
        ]
        read_only_fields = ['id', 'discount_amount', 'tax_amount', 'line_total']


class SupplierInvoiceListSerializer(serializers.ModelSerializer):
    """Serializador de lista de facturas de proveedor."""
    
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    balance = serializers.DecimalField(
        max_digits=18, decimal_places=2, read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = SupplierInvoice
        fields = [
            'id', 'number', 'supplier_invoice_number', 'invoice_type',
            'supplier', 'supplier_name', 'invoice_date', 'due_date',
            'currency', 'total', 'amount_paid', 'balance', 'status', 'is_overdue'
        ]


class SupplierInvoiceDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado de factura de proveedor."""
    
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    balance = serializers.DecimalField(
        max_digits=18, decimal_places=2, read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)
    lines = SupplierInvoiceLineSerializer(many=True, read_only=True)
    
    class Meta:
        model = SupplierInvoice
        fields = [
            'id', 'number', 'supplier_invoice_number', 'invoice_type', 'supplier',
            'supplier_name', 'purchase_order', 'invoice_date', 'received_date',
            'due_date', 'payment_term', 'currency', 'exchange_rate', 'subtotal',
            'discount_amount', 'tax_amount', 'total', 'amount_paid', 'balance',
            'status', 'is_overdue', 'journal_entry', 'notes', 'approved_by',
            'approved_date', 'lines', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'subtotal', 'discount_amount', 'tax_amount', 'total',
            'amount_paid', 'journal_entry', 'approved_by', 'approved_date',
            'created_by', 'created_at', 'updated_at'
        ]


# ========================================================
# Pagos a Proveedores
# ========================================================

class SupplierPaymentAllocationSerializer(serializers.ModelSerializer):
    """Serializador de aplicación de pagos a proveedor."""
    
    invoice_number = serializers.CharField(source='invoice.number', read_only=True)
    invoice_total = serializers.DecimalField(
        source='invoice.total', max_digits=18, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = SupplierPaymentAllocation
        fields = ['id', 'invoice', 'invoice_number', 'invoice_total', 'amount']


class SupplierPaymentSerializer(serializers.ModelSerializer):
    """Serializador de pagos a proveedor."""
    
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    allocations = SupplierPaymentAllocationSerializer(many=True, read_only=True)
    allocated_amount = serializers.SerializerMethodField()
    unallocated_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = SupplierPayment
        fields = [
            'id', 'number', 'supplier', 'supplier_name', 'payment_date',
            'payment_method', 'reference', 'amount', 'currency', 'exchange_rate',
            'status', 'bank_account', 'check_number', 'journal_entry', 'notes',
            'allocations', 'allocated_amount', 'unallocated_amount',
            'approved_by', 'created_by', 'created_at'
        ]
        read_only_fields = [
            'id', 'journal_entry', 'approved_by', 'created_by', 'created_at'
        ]
    
    def get_allocated_amount(self, obj):
        return sum(a.amount for a in obj.allocations.all())
    
    def get_unallocated_amount(self, obj):
        allocated = sum(a.amount for a in obj.allocations.all())
        return obj.amount - allocated


# ========================================================
# Evaluación de Proveedores
# ========================================================

class SupplierEvaluationSerializer(serializers.ModelSerializer):
    """Serializador de evaluación de proveedores."""
    
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = SupplierEvaluation
        fields = [
            'id', 'supplier', 'supplier_name', 'evaluation_date', 'period_start',
            'period_end', 'quality_rating', 'delivery_rating', 'price_rating',
            'service_rating', 'communication_rating', 'overall_rating',
            'total_orders', 'on_time_deliveries', 'quality_issues', 'total_spend',
            'strengths', 'weaknesses', 'recommendations', 'evaluated_by'
        ]
        read_only_fields = ['id', 'overall_rating']


# ========================================================
# Reportes
# ========================================================

class PurchaseSummarySerializer(serializers.Serializer):
    """Serializador para resumen de compras."""
    
    period = serializers.CharField()
    total_orders = serializers.IntegerField()
    total_received = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_invoiced = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=18, decimal_places=2)
    pending_payment = serializers.DecimalField(max_digits=18, decimal_places=2)
    by_supplier = serializers.ListField()
    by_category = serializers.ListField()
    top_products = serializers.ListField()


class SupplierStatementSerializer(serializers.Serializer):
    """Serializador para estado de cuenta de proveedor."""
    
    supplier = serializers.DictField()
    opening_balance = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_invoiced = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=18, decimal_places=2)
    closing_balance = serializers.DecimalField(max_digits=18, decimal_places=2)
    transactions = serializers.ListField()
    aging = serializers.DictField()
