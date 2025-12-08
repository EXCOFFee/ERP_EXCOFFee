# ========================================================
# SISTEMA ERP UNIVERSAL - Modelos de Ventas
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Definición de modelos para gestión de ventas.
# ========================================================

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from apps.core.models import BaseModel, SoftDeleteModel


# ========================================================
# Clientes
# ========================================================

class CustomerGroup(BaseModel):
    """
    Grupos de clientes para clasificación y descuentos.
    """
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Descuento %'
    )
    credit_limit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Límite de Crédito'
    )
    payment_term = models.ForeignKey(
        'finance.PaymentTerm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Término de Pago'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        db_table = 'sales_customer_group'
        verbose_name = 'Grupo de Clientes'
        verbose_name_plural = 'Grupos de Clientes'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Customer(BaseModel, SoftDeleteModel):
    """
    Modelo para clientes.
    """
    
    CUSTOMER_TYPES = [
        ('individual', 'Persona Natural'),
        ('company', 'Empresa'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('blocked', 'Bloqueado'),
        ('prospect', 'Prospecto'),
    ]
    
    # Información básica
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código'
    )
    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPES,
        default='company',
        verbose_name='Tipo'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre/Razón Social'
    )
    trade_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Nombre Comercial'
    )
    tax_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='RUC/NIT/RFC'
    )
    
    # Clasificación
    group = models.ForeignKey(
        CustomerGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers',
        verbose_name='Grupo'
    )
    
    # Contacto principal
    contact_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Contacto Principal'
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Correo'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    mobile = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Celular'
    )
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name='Sitio Web'
    )
    
    # Dirección principal
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='Dirección'
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Ciudad'
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Estado/Provincia'
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='País'
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Código Postal'
    )
    
    # Configuración financiera
    credit_limit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Límite de Crédito'
    )
    credit_used = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Crédito Usado'
    )
    payment_term = models.ForeignKey(
        'finance.PaymentTerm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Término de Pago'
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name='Moneda'
    )
    
    # Vendedor asignado
    sales_rep = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers',
        verbose_name='Vendedor Asignado'
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Estado'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    # Notas
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    class Meta:
        db_table = 'sales_customer'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def available_credit(self):
        """Crédito disponible."""
        return self.credit_limit - self.credit_used
    
    @property
    def display_name(self):
        """Nombre para mostrar."""
        return self.trade_name or self.name


class CustomerAddress(BaseModel):
    """
    Direcciones adicionales del cliente.
    """
    
    ADDRESS_TYPES = [
        ('billing', 'Facturación'),
        ('shipping', 'Envío'),
        ('both', 'Ambas'),
    ]
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name='Cliente'
    )
    address_type = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPES,
        default='both',
        verbose_name='Tipo'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre/Etiqueta'
    )
    contact_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Contacto'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    address = models.TextField(
        verbose_name='Dirección'
    )
    city = models.CharField(
        max_length=100,
        verbose_name='Ciudad'
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Estado/Provincia'
    )
    country = models.CharField(
        max_length=100,
        verbose_name='País'
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Código Postal'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='Por Defecto'
    )
    
    class Meta:
        db_table = 'sales_customer_address'
        verbose_name = 'Dirección de Cliente'
        verbose_name_plural = 'Direcciones de Clientes'
    
    def __str__(self):
        return f"{self.customer} - {self.name}"


class CustomerContact(BaseModel):
    """
    Contactos del cliente.
    """
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name='Cliente'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Cargo'
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Correo'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    mobile = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Celular'
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name='Contacto Principal'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    class Meta:
        db_table = 'sales_customer_contact'
        verbose_name = 'Contacto de Cliente'
        verbose_name_plural = 'Contactos de Clientes'
    
    def __str__(self):
        return f"{self.customer} - {self.name}"


# ========================================================
# Cotizaciones
# ========================================================

class Quotation(BaseModel, SoftDeleteModel):
    """
    Cotizaciones de venta.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('sent', 'Enviada'),
        ('accepted', 'Aceptada'),
        ('rejected', 'Rechazada'),
        ('expired', 'Expirada'),
        ('converted', 'Convertida'),
    ]
    
    number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='quotations',
        verbose_name='Cliente'
    )
    contact = models.ForeignKey(
        CustomerContact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Contacto'
    )
    date = models.DateField(
        verbose_name='Fecha'
    )
    valid_until = models.DateField(
        verbose_name='Válida Hasta'
    )
    
    # Vendedor
    sales_rep = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotations',
        verbose_name='Vendedor'
    )
    
    # Términos
    payment_term = models.ForeignKey(
        'finance.PaymentTerm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Término de Pago'
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name='Moneda'
    )
    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal('1.00'),
        verbose_name='Tipo de Cambio'
    )
    
    # Totales
    subtotal = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Subtotal'
    )
    discount_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Descuento'
    )
    tax_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Impuestos'
    )
    total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total'
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )
    
    # Notas
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas Internas'
    )
    terms_conditions = models.TextField(
        blank=True,
        null=True,
        verbose_name='Términos y Condiciones'
    )
    
    # Creación
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_quotations',
        verbose_name='Creado Por'
    )
    
    class Meta:
        db_table = 'sales_quotation'
        verbose_name = 'Cotización'
        verbose_name_plural = 'Cotizaciones'
        ordering = ['-date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.customer}"


class QuotationLine(BaseModel):
    """
    Líneas de cotización.
    """
    
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='Cotización'
    )
    line_number = models.PositiveIntegerField(
        default=1,
        verbose_name='Línea'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.PROTECT,
        verbose_name='Producto'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name='Cantidad'
    )
    unit = models.ForeignKey(
        'inventory.UnitOfMeasure',
        on_delete=models.PROTECT,
        verbose_name='Unidad'
    )
    unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        verbose_name='Precio Unitario'
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Descuento %'
    )
    discount_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Descuento'
    )
    tax = models.ForeignKey(
        'finance.TaxRate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Impuesto'
    )
    tax_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto Impuesto'
    )
    line_total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Línea'
    )
    
    class Meta:
        db_table = 'sales_quotation_line'
        verbose_name = 'Línea de Cotización'
        verbose_name_plural = 'Líneas de Cotización'
        ordering = ['quotation', 'line_number']
    
    def __str__(self):
        return f"{self.quotation.number} - {self.product}"


# ========================================================
# Órdenes de Venta
# ========================================================

class SalesOrder(BaseModel, SoftDeleteModel):
    """
    Órdenes de venta.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmada'),
        ('processing', 'En Proceso'),
        ('shipped', 'Enviada'),
        ('delivered', 'Entregada'),
        ('invoiced', 'Facturada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]
    
    ORDER_TYPES = [
        ('standard', 'Estándar'),
        ('backorder', 'Pedido Pendiente'),
        ('dropship', 'Envío Directo'),
        ('return', 'Devolución'),
    ]
    
    number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='sales_orders',
        verbose_name='Cliente'
    )
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_orders',
        verbose_name='Cotización Origen'
    )
    
    # Fechas
    order_date = models.DateField(
        verbose_name='Fecha de Orden'
    )
    required_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Requerida'
    )
    promised_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Prometida'
    )
    shipped_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Envío'
    )
    
    # Tipo y clasificación
    order_type = models.CharField(
        max_length=20,
        choices=ORDER_TYPES,
        default='standard',
        verbose_name='Tipo'
    )
    priority = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Prioridad'
    )
    
    # Vendedor
    sales_rep = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_orders',
        verbose_name='Vendedor'
    )
    
    # Direcciones
    billing_address = models.ForeignKey(
        CustomerAddress,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='billing_orders',
        verbose_name='Dirección de Facturación'
    )
    shipping_address = models.ForeignKey(
        CustomerAddress,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shipping_orders',
        verbose_name='Dirección de Envío'
    )
    
    # Almacén
    warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Almacén'
    )
    
    # Términos
    payment_term = models.ForeignKey(
        'finance.PaymentTerm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Término de Pago'
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name='Moneda'
    )
    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal('1.00'),
        verbose_name='Tipo de Cambio'
    )
    
    # Totales
    subtotal = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Subtotal'
    )
    discount_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Descuento'
    )
    tax_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Impuestos'
    )
    shipping_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Envío'
    )
    total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total'
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )
    
    # Referencia del cliente
    customer_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Referencia del Cliente'
    )
    
    # Notas
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas Internas'
    )
    customer_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas para el Cliente'
    )
    
    # Creación
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_sales_orders',
        verbose_name='Creado Por'
    )
    
    class Meta:
        db_table = 'sales_order'
        verbose_name = 'Orden de Venta'
        verbose_name_plural = 'Órdenes de Venta'
        ordering = ['-order_date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.customer}"


class SalesOrderLine(BaseModel):
    """
    Líneas de orden de venta.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('reserved', 'Reservada'),
        ('picked', 'Preparada'),
        ('shipped', 'Enviada'),
        ('delivered', 'Entregada'),
        ('cancelled', 'Cancelada'),
    ]
    
    order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='Orden'
    )
    line_number = models.PositiveIntegerField(
        default=1,
        verbose_name='Línea'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.PROTECT,
        verbose_name='Producto'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name='Cantidad'
    )
    quantity_reserved = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal('0.00'),
        verbose_name='Cantidad Reservada'
    )
    quantity_shipped = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal('0.00'),
        verbose_name='Cantidad Enviada'
    )
    quantity_delivered = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal('0.00'),
        verbose_name='Cantidad Entregada'
    )
    quantity_invoiced = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal('0.00'),
        verbose_name='Cantidad Facturada'
    )
    unit = models.ForeignKey(
        'inventory.UnitOfMeasure',
        on_delete=models.PROTECT,
        verbose_name='Unidad'
    )
    unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        verbose_name='Precio Unitario'
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Descuento %'
    )
    discount_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Descuento'
    )
    tax = models.ForeignKey(
        'finance.TaxRate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Impuesto'
    )
    tax_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto Impuesto'
    )
    line_total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Línea'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Almacén'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    class Meta:
        db_table = 'sales_order_line'
        verbose_name = 'Línea de Orden'
        verbose_name_plural = 'Líneas de Orden'
        ordering = ['order', 'line_number']
    
    def __str__(self):
        return f"{self.order.number} - {self.product}"
    
    @property
    def quantity_pending(self):
        """Cantidad pendiente de enviar."""
        return self.quantity - self.quantity_shipped


# ========================================================
# Facturas
# ========================================================

class Invoice(BaseModel, SoftDeleteModel):
    """
    Facturas de venta.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('validated', 'Validada'),
        ('sent', 'Enviada'),
        ('partial', 'Pago Parcial'),
        ('paid', 'Pagada'),
        ('overdue', 'Vencida'),
        ('cancelled', 'Cancelada'),
    ]
    
    INVOICE_TYPES = [
        ('invoice', 'Factura'),
        ('credit_note', 'Nota de Crédito'),
        ('debit_note', 'Nota de Débito'),
    ]
    
    number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número'
    )
    invoice_type = models.CharField(
        max_length=20,
        choices=INVOICE_TYPES,
        default='invoice',
        verbose_name='Tipo'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name='Cliente'
    )
    sales_order = models.ForeignKey(
        SalesOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name='Orden de Venta'
    )
    
    # Fechas
    invoice_date = models.DateField(
        verbose_name='Fecha de Factura'
    )
    due_date = models.DateField(
        verbose_name='Fecha de Vencimiento'
    )
    
    # Términos
    payment_term = models.ForeignKey(
        'finance.PaymentTerm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Término de Pago'
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name='Moneda'
    )
    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal('1.00'),
        verbose_name='Tipo de Cambio'
    )
    
    # Totales
    subtotal = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Subtotal'
    )
    discount_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Descuento'
    )
    tax_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Impuestos'
    )
    total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total'
    )
    
    # Pagos
    amount_paid = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto Pagado'
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )
    
    # Dirección
    billing_address = models.TextField(
        blank=True,
        null=True,
        verbose_name='Dirección de Facturación'
    )
    
    # Notas
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    # Contabilidad
    journal_entry = models.ForeignKey(
        'finance.JournalEntry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name='Asiento Contable'
    )
    
    # Creación
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invoices',
        verbose_name='Creado Por'
    )
    
    class Meta:
        db_table = 'sales_invoice'
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-invoice_date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.customer}"
    
    @property
    def balance(self):
        """Saldo pendiente."""
        return self.total - self.amount_paid
    
    @property
    def is_overdue(self):
        """Indica si está vencida."""
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.balance > 0


class InvoiceLine(BaseModel):
    """
    Líneas de factura.
    """
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='Factura'
    )
    line_number = models.PositiveIntegerField(
        default=1,
        verbose_name='Línea'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Producto'
    )
    sales_order_line = models.ForeignKey(
        SalesOrderLine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoice_lines',
        verbose_name='Línea de Orden'
    )
    description = models.TextField(
        verbose_name='Descripción'
    )
    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name='Cantidad'
    )
    unit = models.ForeignKey(
        'inventory.UnitOfMeasure',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Unidad'
    )
    unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        verbose_name='Precio Unitario'
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Descuento %'
    )
    discount_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Descuento'
    )
    tax = models.ForeignKey(
        'finance.TaxRate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Impuesto'
    )
    tax_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto Impuesto'
    )
    line_total = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Línea'
    )
    account = models.ForeignKey(
        'finance.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Cuenta Contable'
    )
    
    class Meta:
        db_table = 'sales_invoice_line'
        verbose_name = 'Línea de Factura'
        verbose_name_plural = 'Líneas de Factura'
        ordering = ['invoice', 'line_number']
    
    def __str__(self):
        return f"{self.invoice.number} - {self.description[:50]}"


# ========================================================
# Pagos
# ========================================================

class Payment(BaseModel):
    """
    Pagos recibidos de clientes.
    """
    
    PAYMENT_METHODS = [
        ('cash', 'Efectivo'),
        ('check', 'Cheque'),
        ('transfer', 'Transferencia'),
        ('credit_card', 'Tarjeta de Crédito'),
        ('debit_card', 'Tarjeta de Débito'),
        ('other', 'Otro'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('reconciled', 'Conciliado'),
        ('cancelled', 'Cancelado'),
    ]
    
    number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='Cliente'
    )
    payment_date = models.DateField(
        verbose_name='Fecha de Pago'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='transfer',
        verbose_name='Método de Pago'
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Referencia'
    )
    
    # Montos
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name='Monto'
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name='Moneda'
    )
    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal('1.00'),
        verbose_name='Tipo de Cambio'
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )
    
    # Banco
    bank_account = models.ForeignKey(
        'finance.BankAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Cuenta Bancaria'
    )
    
    # Contabilidad
    journal_entry = models.ForeignKey(
        'finance.JournalEntry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_payments',
        verbose_name='Asiento Contable'
    )
    
    # Notas
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    # Creación
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_payments',
        verbose_name='Creado Por'
    )
    
    class Meta:
        db_table = 'sales_payment'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-payment_date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.customer}"


class PaymentAllocation(BaseModel):
    """
    Aplicación de pagos a facturas.
    """
    
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='allocations',
        verbose_name='Pago'
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payment_allocations',
        verbose_name='Factura'
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name='Monto Aplicado'
    )
    
    class Meta:
        db_table = 'sales_payment_allocation'
        verbose_name = 'Aplicación de Pago'
        verbose_name_plural = 'Aplicaciones de Pago'
        unique_together = ['payment', 'invoice']
    
    def __str__(self):
        return f"{self.payment.number} -> {self.invoice.number}"


# ========================================================
# Envíos
# ========================================================

class Shipment(BaseModel):
    """
    Envíos de mercadería.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('picking', 'En Preparación'),
        ('packed', 'Empacado'),
        ('shipped', 'Enviado'),
        ('in_transit', 'En Tránsito'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ]
    
    number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número'
    )
    sales_order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name='shipments',
        verbose_name='Orden de Venta'
    )
    
    # Fechas
    shipment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Envío'
    )
    estimated_delivery = models.DateField(
        null=True,
        blank=True,
        verbose_name='Entrega Estimada'
    )
    actual_delivery = models.DateField(
        null=True,
        blank=True,
        verbose_name='Entrega Real'
    )
    
    # Transportista
    carrier = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Transportista'
    )
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Número de Guía'
    )
    tracking_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='URL de Rastreo'
    )
    
    # Almacén
    warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Almacén'
    )
    
    # Dirección de envío
    shipping_address = models.TextField(
        verbose_name='Dirección de Envío'
    )
    
    # Peso y dimensiones
    total_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Peso Total'
    )
    total_packages = models.PositiveIntegerField(
        default=1,
        verbose_name='Total Paquetes'
    )
    
    # Costos
    shipping_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Costo de Envío'
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )
    
    # Notas
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    # Creación
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_shipments',
        verbose_name='Creado Por'
    )
    
    class Meta:
        db_table = 'sales_shipment'
        verbose_name = 'Envío'
        verbose_name_plural = 'Envíos'
        ordering = ['-shipment_date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.sales_order}"


class ShipmentLine(BaseModel):
    """
    Líneas de envío.
    """
    
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='Envío'
    )
    order_line = models.ForeignKey(
        SalesOrderLine,
        on_delete=models.CASCADE,
        related_name='shipment_lines',
        verbose_name='Línea de Orden'
    )
    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        verbose_name='Cantidad'
    )
    lot = models.ForeignKey(
        'inventory.Lot',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Lote'
    )
    serial_numbers = models.ManyToManyField(
        'inventory.SerialNumber',
        blank=True,
        verbose_name='Números de Serie'
    )
    
    class Meta:
        db_table = 'sales_shipment_line'
        verbose_name = 'Línea de Envío'
        verbose_name_plural = 'Líneas de Envío'
    
    def __str__(self):
        return f"{self.shipment.number} - {self.order_line.product}"


# ========================================================
# Precios y Promociones
# ========================================================

class PriceList(BaseModel):
    """
    Listas de precios.
    """
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name='Moneda'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='Por Defecto'
    )
    valid_from = models.DateField(
        null=True,
        blank=True,
        verbose_name='Válida Desde'
    )
    valid_until = models.DateField(
        null=True,
        blank=True,
        verbose_name='Válida Hasta'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    
    class Meta:
        db_table = 'sales_price_list'
        verbose_name = 'Lista de Precios'
        verbose_name_plural = 'Listas de Precios'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class PriceListItem(BaseModel):
    """
    Items de lista de precios.
    """
    
    price_list = models.ForeignKey(
        PriceList,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Lista de Precios'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.CASCADE,
        related_name='price_list_items',
        verbose_name='Producto'
    )
    min_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal('1'),
        verbose_name='Cantidad Mínima'
    )
    unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        verbose_name='Precio Unitario'
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Descuento %'
    )
    
    class Meta:
        db_table = 'sales_price_list_item'
        verbose_name = 'Item de Lista de Precios'
        verbose_name_plural = 'Items de Lista de Precios'
        unique_together = ['price_list', 'product', 'min_quantity']
    
    def __str__(self):
        return f"{self.price_list} - {self.product}"


class Promotion(BaseModel):
    """
    Promociones y descuentos.
    """
    
    PROMOTION_TYPES = [
        ('percentage', 'Porcentaje'),
        ('fixed', 'Monto Fijo'),
        ('buy_x_get_y', 'Compre X Lleve Y'),
        ('bundle', 'Paquete'),
    ]
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    promotion_type = models.CharField(
        max_length=20,
        choices=PROMOTION_TYPES,
        default='percentage',
        verbose_name='Tipo'
    )
    discount_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Valor del Descuento'
    )
    min_purchase_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto Mínimo de Compra'
    )
    max_discount_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Descuento Máximo'
    )
    valid_from = models.DateTimeField(
        verbose_name='Válida Desde'
    )
    valid_until = models.DateTimeField(
        verbose_name='Válida Hasta'
    )
    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Límite de Uso'
    )
    usage_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Veces Usado'
    )
    products = models.ManyToManyField(
        'inventory.Product',
        blank=True,
        related_name='promotions',
        verbose_name='Productos'
    )
    categories = models.ManyToManyField(
        'inventory.Category',
        blank=True,
        related_name='promotions',
        verbose_name='Categorías'
    )
    customer_groups = models.ManyToManyField(
        CustomerGroup,
        blank=True,
        related_name='promotions',
        verbose_name='Grupos de Clientes'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    
    class Meta:
        db_table = 'sales_promotion'
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'
        ordering = ['-valid_from']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def is_valid(self):
        """Verifica si la promoción está vigente."""
        from django.utils import timezone
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from > now or self.valid_until < now:
            return False
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        return True
