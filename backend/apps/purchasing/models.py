# ========================================================
# SISTEMA ERP UNIVERSAL - Modelos de Compras
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Definición de modelos para gestión de compras.
# ========================================================

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from apps.core.models import BaseModel, SoftDeleteModel


# ========================================================
# Proveedores
# ========================================================

class SupplierCategory(BaseModel):
    """
    Categorías de proveedores.
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
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        db_table = 'purchasing_supplier_category'
        verbose_name = 'Categoría de Proveedor'
        verbose_name_plural = 'Categorías de Proveedores'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Supplier(BaseModel, SoftDeleteModel):
    """
    Proveedores.
    """
    
    SUPPLIER_TYPES = [
        ('goods', 'Bienes'),
        ('services', 'Servicios'),
        ('both', 'Bienes y Servicios'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('blocked', 'Bloqueado'),
        ('pending', 'Pendiente Aprobación'),
    ]
    
    # Información básica
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código'
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
    supplier_type = models.CharField(
        max_length=20,
        choices=SUPPLIER_TYPES,
        default='goods',
        verbose_name='Tipo'
    )
    
    # Categoría
    category = models.ForeignKey(
        SupplierCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suppliers',
        verbose_name='Categoría'
    )
    
    # Contacto
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
    fax = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Fax'
    )
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name='Sitio Web'
    )
    
    # Dirección
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
    credit_limit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Límite de Crédito'
    )
    
    # Cuenta contable
    account_payable = models.ForeignKey(
        'finance.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suppliers_payable',
        verbose_name='Cuenta por Pagar'
    )
    
    # Comprador asignado
    buyer = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_suppliers',
        verbose_name='Comprador Asignado'
    )
    
    # Evaluación
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='Calificación'
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
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
    
    # Documentos y certificaciones
    tax_exempt = models.BooleanField(
        default=False,
        verbose_name='Exento de Impuestos'
    )
    
    class Meta:
        db_table = 'purchasing_supplier'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class SupplierContact(BaseModel):
    """
    Contactos del proveedor.
    """
    
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name='Proveedor'
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
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Departamento'
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
        db_table = 'purchasing_supplier_contact'
        verbose_name = 'Contacto de Proveedor'
        verbose_name_plural = 'Contactos de Proveedores'
    
    def __str__(self):
        return f"{self.supplier} - {self.name}"


class SupplierAddress(BaseModel):
    """
    Direcciones del proveedor.
    """
    
    ADDRESS_TYPES = [
        ('main', 'Principal'),
        ('billing', 'Facturación'),
        ('shipping', 'Envío'),
        ('warehouse', 'Almacén'),
    ]
    
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name='Proveedor'
    )
    address_type = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPES,
        default='main',
        verbose_name='Tipo'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre/Etiqueta'
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
        db_table = 'purchasing_supplier_address'
        verbose_name = 'Dirección de Proveedor'
        verbose_name_plural = 'Direcciones de Proveedores'
    
    def __str__(self):
        return f"{self.supplier} - {self.name}"


class SupplierProduct(BaseModel):
    """
    Productos que ofrece cada proveedor.
    """
    
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Proveedor'
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.CASCADE,
        related_name='suppliers',
        verbose_name='Producto'
    )
    supplier_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Código del Proveedor'
    )
    supplier_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Nombre del Proveedor'
    )
    unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        verbose_name='Precio Unitario'
    )
    min_order_quantity = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal('1'),
        verbose_name='Cantidad Mínima'
    )
    lead_time_days = models.PositiveIntegerField(
        default=0,
        verbose_name='Tiempo de Entrega (días)'
    )
    is_preferred = models.BooleanField(
        default=False,
        verbose_name='Proveedor Preferido'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    last_purchase_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Última Compra'
    )
    last_purchase_price = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name='Último Precio'
    )
    
    class Meta:
        db_table = 'purchasing_supplier_product'
        verbose_name = 'Producto de Proveedor'
        verbose_name_plural = 'Productos de Proveedores'
        unique_together = ['supplier', 'product']
    
    def __str__(self):
        return f"{self.supplier} - {self.product}"


# ========================================================
# Solicitudes de Compra
# ========================================================

class PurchaseRequisition(BaseModel, SoftDeleteModel):
    """
    Solicitudes de compra internas.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('submitted', 'Enviada'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
        ('converted', 'Convertida a OC'),
        ('cancelled', 'Cancelada'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número'
    )
    date = models.DateField(
        verbose_name='Fecha'
    )
    required_date = models.DateField(
        verbose_name='Fecha Requerida'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal',
        verbose_name='Prioridad'
    )
    
    # Departamento solicitante
    department = models.ForeignKey(
        'hr.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Departamento'
    )
    requested_by = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        related_name='purchase_requisitions',
        verbose_name='Solicitado Por'
    )
    
    # Almacén destino
    warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Almacén Destino'
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )
    
    # Aprobación
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_requisitions',
        verbose_name='Aprobado Por'
    )
    approved_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Aprobación'
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name='Motivo de Rechazo'
    )
    
    # Notas
    justification = models.TextField(
        blank=True,
        null=True,
        verbose_name='Justificación'
    )
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
        related_name='created_requisitions',
        verbose_name='Creado Por'
    )
    
    class Meta:
        db_table = 'purchasing_requisition'
        verbose_name = 'Solicitud de Compra'
        verbose_name_plural = 'Solicitudes de Compra'
        ordering = ['-date', '-number']
    
    def __str__(self):
        return f"{self.number}"


class PurchaseRequisitionLine(BaseModel):
    """
    Líneas de solicitud de compra.
    """
    
    requisition = models.ForeignKey(
        PurchaseRequisition,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='Solicitud'
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
    estimated_unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name='Precio Estimado'
    )
    quantity_ordered = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name='Cantidad Ordenada'
    )
    suggested_supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Proveedor Sugerido'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    class Meta:
        db_table = 'purchasing_requisition_line'
        verbose_name = 'Línea de Solicitud'
        verbose_name_plural = 'Líneas de Solicitud'
        ordering = ['requisition', 'line_number']
    
    def __str__(self):
        return f"{self.requisition.number} - {self.product}"
    
    @property
    def quantity_pending(self):
        """Cantidad pendiente de ordenar."""
        return self.quantity - self.quantity_ordered


# ========================================================
# Órdenes de Compra
# ========================================================

class PurchaseOrder(BaseModel, SoftDeleteModel):
    """
    Órdenes de compra.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('pending_approval', 'Pendiente Aprobación'),
        ('approved', 'Aprobada'),
        ('sent', 'Enviada a Proveedor'),
        ('confirmed', 'Confirmada por Proveedor'),
        ('partial', 'Recibida Parcial'),
        ('received', 'Recibida'),
        ('invoiced', 'Facturada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]
    
    ORDER_TYPES = [
        ('standard', 'Estándar'),
        ('blanket', 'Contrato Abierto'),
        ('dropship', 'Envío Directo'),
        ('consignment', 'Consignación'),
    ]
    
    number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchase_orders',
        verbose_name='Proveedor'
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
    
    # Tipo
    order_type = models.CharField(
        max_length=20,
        choices=ORDER_TYPES,
        default='standard',
        verbose_name='Tipo'
    )
    
    # Comprador
    buyer = models.ForeignKey(
        'hr.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_orders',
        verbose_name='Comprador'
    )
    
    # Almacén
    warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Almacén Destino'
    )
    
    # Dirección de entrega
    delivery_address = models.TextField(
        blank=True,
        null=True,
        verbose_name='Dirección de Entrega'
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
    freight_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Flete'
    )
    other_charges = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Otros Cargos'
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
    
    # Referencia del proveedor
    supplier_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Referencia del Proveedor'
    )
    
    # Solicitud origen
    requisition = models.ForeignKey(
        PurchaseRequisition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_orders',
        verbose_name='Solicitud Origen'
    )
    
    # Aprobación
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_purchase_orders',
        verbose_name='Aprobado Por'
    )
    approved_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Aprobación'
    )
    
    # Notas
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas Internas'
    )
    supplier_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas para Proveedor'
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
        related_name='created_purchase_orders',
        verbose_name='Creado Por'
    )
    
    class Meta:
        db_table = 'purchasing_order'
        verbose_name = 'Orden de Compra'
        verbose_name_plural = 'Órdenes de Compra'
        ordering = ['-order_date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.supplier}"


class PurchaseOrderLine(BaseModel):
    """
    Líneas de orden de compra.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('partial', 'Recibida Parcial'),
        ('received', 'Recibida'),
        ('cancelled', 'Cancelada'),
    ]
    
    order = models.ForeignKey(
        PurchaseOrder,
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
    quantity_received = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name='Cantidad Recibida'
    )
    quantity_invoiced = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal('0'),
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
        'finance.Tax',
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
    
    # Referencia a solicitud
    requisition_line = models.ForeignKey(
        PurchaseRequisitionLine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_lines',
        verbose_name='Línea de Solicitud'
    )
    
    # Almacén específico para la línea
    warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Almacén'
    )
    
    # Fecha de entrega específica
    required_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Requerida'
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    class Meta:
        db_table = 'purchasing_order_line'
        verbose_name = 'Línea de Orden'
        verbose_name_plural = 'Líneas de Orden'
        ordering = ['order', 'line_number']
    
    def __str__(self):
        return f"{self.order.number} - {self.product}"
    
    @property
    def quantity_pending(self):
        """Cantidad pendiente de recibir."""
        return self.quantity - self.quantity_received


# ========================================================
# Recepción de Mercancía
# ========================================================

class GoodsReceipt(BaseModel):
    """
    Recepción de mercancía.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmada'),
        ('in_inspection', 'En Inspección'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]
    
    number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número'
    )
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='receipts',
        verbose_name='Orden de Compra'
    )
    
    # Fechas
    receipt_date = models.DateField(
        verbose_name='Fecha de Recepción'
    )
    
    # Almacén
    warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Almacén'
    )
    
    # Documentos del proveedor
    supplier_delivery_note = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Guía de Remisión'
    )
    supplier_invoice_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Número de Factura'
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
    
    # Recibido por
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='goods_receipts',
        verbose_name='Recibido Por'
    )
    
    # Creación
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_goods_receipts',
        verbose_name='Creado Por'
    )
    
    class Meta:
        db_table = 'purchasing_goods_receipt'
        verbose_name = 'Recepción de Mercancía'
        verbose_name_plural = 'Recepciones de Mercancía'
        ordering = ['-receipt_date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.purchase_order}"


class GoodsReceiptLine(BaseModel):
    """
    Líneas de recepción de mercancía.
    """
    
    receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='Recepción'
    )
    order_line = models.ForeignKey(
        PurchaseOrderLine,
        on_delete=models.CASCADE,
        related_name='receipt_lines',
        verbose_name='Línea de Orden'
    )
    quantity_received = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        verbose_name='Cantidad Recibida'
    )
    quantity_accepted = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name='Cantidad Aceptada'
    )
    quantity_rejected = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name='Cantidad Rechazada'
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name='Motivo de Rechazo'
    )
    
    # Ubicación de destino
    location = models.ForeignKey(
        'inventory.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Ubicación'
    )
    
    # Lote
    lot = models.ForeignKey(
        'inventory.Lot',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Lote'
    )
    
    # Números de serie
    serial_numbers = models.ManyToManyField(
        'inventory.SerialNumber',
        blank=True,
        verbose_name='Números de Serie'
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    class Meta:
        db_table = 'purchasing_goods_receipt_line'
        verbose_name = 'Línea de Recepción'
        verbose_name_plural = 'Líneas de Recepción'
    
    def __str__(self):
        return f"{self.receipt.number} - {self.order_line.product}"


# ========================================================
# Facturas de Proveedor
# ========================================================

class SupplierInvoice(BaseModel, SoftDeleteModel):
    """
    Facturas de proveedores.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('validated', 'Validada'),
        ('approved', 'Aprobada'),
        ('partial', 'Pago Parcial'),
        ('paid', 'Pagada'),
        ('cancelled', 'Cancelada'),
    ]
    
    INVOICE_TYPES = [
        ('invoice', 'Factura'),
        ('credit_note', 'Nota de Crédito'),
        ('debit_note', 'Nota de Débito'),
    ]
    
    number = models.CharField(
        max_length=50,
        verbose_name='Número Interno'
    )
    supplier_invoice_number = models.CharField(
        max_length=100,
        verbose_name='Número de Factura Proveedor'
    )
    invoice_type = models.CharField(
        max_length=20,
        choices=INVOICE_TYPES,
        default='invoice',
        verbose_name='Tipo'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name='Proveedor'
    )
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name='Orden de Compra'
    )
    
    # Fechas
    invoice_date = models.DateField(
        verbose_name='Fecha de Factura'
    )
    received_date = models.DateField(
        verbose_name='Fecha de Recepción'
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
    
    # Contabilidad
    journal_entry = models.ForeignKey(
        'finance.JournalEntry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supplier_invoices',
        verbose_name='Asiento Contable'
    )
    
    # Notas
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    # Aprobación
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_supplier_invoices',
        verbose_name='Aprobado Por'
    )
    approved_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Aprobación'
    )
    
    # Creación
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_supplier_invoices',
        verbose_name='Creado Por'
    )
    
    class Meta:
        db_table = 'purchasing_supplier_invoice'
        verbose_name = 'Factura de Proveedor'
        verbose_name_plural = 'Facturas de Proveedores'
        ordering = ['-invoice_date', '-number']
        unique_together = ['supplier', 'supplier_invoice_number']
    
    def __str__(self):
        return f"{self.number} - {self.supplier}"
    
    @property
    def balance(self):
        """Saldo pendiente."""
        return self.total - self.amount_paid
    
    @property
    def is_overdue(self):
        """Indica si está vencida."""
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.balance > 0


class SupplierInvoiceLine(BaseModel):
    """
    Líneas de factura de proveedor.
    """
    
    invoice = models.ForeignKey(
        SupplierInvoice,
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
    order_line = models.ForeignKey(
        PurchaseOrderLine,
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
        'finance.Tax',
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
        db_table = 'purchasing_supplier_invoice_line'
        verbose_name = 'Línea de Factura'
        verbose_name_plural = 'Líneas de Factura'
        ordering = ['invoice', 'line_number']
    
    def __str__(self):
        return f"{self.invoice.number} - {self.description[:50]}"


# ========================================================
# Pagos a Proveedores
# ========================================================

class SupplierPayment(BaseModel):
    """
    Pagos a proveedores.
    """
    
    PAYMENT_METHODS = [
        ('check', 'Cheque'),
        ('transfer', 'Transferencia'),
        ('cash', 'Efectivo'),
        ('other', 'Otro'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('approved', 'Aprobado'),
        ('sent', 'Enviado'),
        ('cleared', 'Cobrado'),
        ('cancelled', 'Cancelado'),
    ]
    
    number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='Proveedor'
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
    check_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Número de Cheque'
    )
    
    # Contabilidad
    journal_entry = models.ForeignKey(
        'finance.JournalEntry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supplier_payments',
        verbose_name='Asiento Contable'
    )
    
    # Notas
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    # Aprobación
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_supplier_payments',
        verbose_name='Aprobado Por'
    )
    
    # Creación
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_supplier_payments',
        verbose_name='Creado Por'
    )
    
    class Meta:
        db_table = 'purchasing_supplier_payment'
        verbose_name = 'Pago a Proveedor'
        verbose_name_plural = 'Pagos a Proveedores'
        ordering = ['-payment_date', '-number']
    
    def __str__(self):
        return f"{self.number} - {self.supplier}"


class SupplierPaymentAllocation(BaseModel):
    """
    Aplicación de pagos a facturas de proveedor.
    """
    
    payment = models.ForeignKey(
        SupplierPayment,
        on_delete=models.CASCADE,
        related_name='allocations',
        verbose_name='Pago'
    )
    invoice = models.ForeignKey(
        SupplierInvoice,
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
        db_table = 'purchasing_supplier_payment_allocation'
        verbose_name = 'Aplicación de Pago'
        verbose_name_plural = 'Aplicaciones de Pago'
        unique_together = ['payment', 'invoice']
    
    def __str__(self):
        return f"{self.payment.number} -> {self.invoice.number}"


# ========================================================
# Evaluación de Proveedores
# ========================================================

class SupplierEvaluation(BaseModel):
    """
    Evaluación periódica de proveedores.
    """
    
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='evaluations',
        verbose_name='Proveedor'
    )
    evaluation_date = models.DateField(
        verbose_name='Fecha de Evaluación'
    )
    period_start = models.DateField(
        verbose_name='Período Inicio'
    )
    period_end = models.DateField(
        verbose_name='Período Fin'
    )
    
    # Criterios de evaluación (1-5)
    quality_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='Calidad'
    )
    delivery_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='Entrega'
    )
    price_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='Precio'
    )
    service_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='Servicio'
    )
    communication_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='Comunicación'
    )
    
    # Rating promedio
    overall_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='Calificación General'
    )
    
    # Estadísticas del período
    total_orders = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de Órdenes'
    )
    on_time_deliveries = models.PositiveIntegerField(
        default=0,
        verbose_name='Entregas a Tiempo'
    )
    quality_issues = models.PositiveIntegerField(
        default=0,
        verbose_name='Problemas de Calidad'
    )
    total_spend = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='Gasto Total'
    )
    
    # Comentarios
    strengths = models.TextField(
        blank=True,
        null=True,
        verbose_name='Fortalezas'
    )
    weaknesses = models.TextField(
        blank=True,
        null=True,
        verbose_name='Debilidades'
    )
    recommendations = models.TextField(
        blank=True,
        null=True,
        verbose_name='Recomendaciones'
    )
    
    # Evaluado por
    evaluated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='supplier_evaluations',
        verbose_name='Evaluado Por'
    )
    
    class Meta:
        db_table = 'purchasing_supplier_evaluation'
        verbose_name = 'Evaluación de Proveedor'
        verbose_name_plural = 'Evaluaciones de Proveedores'
        ordering = ['-evaluation_date']
    
    def __str__(self):
        return f"{self.supplier} - {self.evaluation_date}"
    
    def save(self, *args, **kwargs):
        # Calcular rating promedio
        self.overall_rating = (
            self.quality_rating +
            self.delivery_rating +
            self.price_rating +
            self.service_rating +
            self.communication_rating
        ) / 5
        
        super().save(*args, **kwargs)
        
        # Actualizar rating del proveedor
        self.supplier.rating = self.overall_rating
        self.supplier.save(update_fields=['rating'])
