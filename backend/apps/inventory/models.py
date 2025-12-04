# ========================================================
# SISTEMA ERP UNIVERSAL - Modelos de Inventario
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Definir modelos para el módulo de inventario.
# Implementa el Diagrama de Clases (4.7) y DER (4.9) del SRS.
#
# Requisitos implementados:
# - RF2: Control de inventario multi-almacén
# - RF2: Gestión de lotes y números de serie
# - RU2: Escaneo de códigos de barras
# ========================================================

from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel, StatusChoices


class Category(BaseModel):
    """
    Categoría de productos.
    
    Propósito:
        Organizar productos en categorías jerárquicas.
    
    Estructura:
        Soporta categorías anidadas (árbol) mediante parent.
        Ej: Electrónica > Computadoras > Laptops
    
    Por qué categorías:
        - Facilita búsqueda y filtrado de productos
        - Permite aplicar reglas por categoría (descuentos, impuestos)
        - Mejora la organización del catálogo
    """
    
    # Nombre de la categoría
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        help_text='Nombre de la categoría (ej. "Electrónica")'
    )
    
    # Código único para referencia rápida
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código',
        help_text='Código único de la categoría (ej. "ELEC")'
    )
    
    # Descripción detallada
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    # Categoría padre (para jerarquía)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
        verbose_name='Categoría Padre',
        help_text='Categoría padre para crear jerarquías'
    )
    
    # Imagen representativa
    image = models.ImageField(
        upload_to='categories/',
        null=True,
        blank=True,
        verbose_name='Imagen'
    )
    
    # Estado activo/inactivo
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    
    class Meta:
        db_table = 'inventory_categories'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def get_full_path(self) -> str:
        """
        Obtiene la ruta completa de la categoría.
        
        Returns:
            str: Ruta completa (ej. "Electrónica > Computadoras > Laptops")
        """
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return ' > '.join(path)


class Brand(BaseModel):
    """
    Marca de productos.
    
    Propósito:
        Clasificar productos por fabricante o marca comercial.
    
    Por qué:
        - Facilita filtrado por marca
        - Reportes de ventas por marca
        - Negociación con proveedores
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre',
        help_text='Nombre de la marca (ej. "Samsung")'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    logo = models.ImageField(
        upload_to='brands/',
        null=True,
        blank=True,
        verbose_name='Logo'
    )
    
    website = models.URLField(
        blank=True,
        verbose_name='Sitio Web'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    
    class Meta:
        db_table = 'inventory_brands'
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UnitOfMeasure(BaseModel):
    """
    Unidad de medida para productos.
    
    Propósito:
        Estandarizar las unidades de medida utilizadas en productos.
    
    Ejemplos:
        - Unidad (UND)
        - Kilogramo (KG)
        - Metro (M)
        - Caja (CJ)
        - Pallet (PLT)
    """
    
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Nombre',
        help_text='Nombre de la unidad (ej. "Kilogramo")'
    )
    
    abbreviation = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Abreviatura',
        help_text='Abreviatura (ej. "KG")'
    )
    
    # Indica si es la unidad base (para conversiones)
    is_base_unit = models.BooleanField(
        default=False,
        verbose_name='Es Unidad Base'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    
    class Meta:
        db_table = 'inventory_units_of_measure'
        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medida'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


class Warehouse(BaseModel):
    """
    Almacén o bodega.
    
    Propósito:
        Representar ubicaciones físicas donde se almacena inventario.
        Implementa RF2 - Control multi-almacén.
    
    Por qué multi-almacén:
        - Empresas tienen múltiples ubicaciones
        - Permite transferencias entre almacenes
        - Cada almacén puede tener su propio stock
    """
    
    # Nombre del almacén
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        help_text='Nombre del almacén (ej. "Almacén Central")'
    )
    
    # Código único
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código',
        help_text='Código único del almacén (ej. "ALM-001")'
    )
    
    # Dirección
    address = models.TextField(
        verbose_name='Dirección',
        help_text='Dirección física del almacén'
    )
    
    city = models.CharField(
        max_length=100,
        verbose_name='Ciudad'
    )
    
    state = models.CharField(
        max_length=100,
        verbose_name='Estado/Provincia'
    )
    
    postal_code = models.CharField(
        max_length=20,
        verbose_name='Código Postal'
    )
    
    country = models.CharField(
        max_length=100,
        default='México',
        verbose_name='País'
    )
    
    # Contacto
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono'
    )
    
    email = models.EmailField(
        blank=True,
        verbose_name='Email'
    )
    
    # Responsable del almacén
    manager = models.ForeignKey(
        'authentication.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='managed_warehouses',
        verbose_name='Responsable'
    )
    
    # Tipo de almacén
    class WarehouseType(models.TextChoices):
        MAIN = 'main', 'Principal'
        BRANCH = 'branch', 'Sucursal'
        VIRTUAL = 'virtual', 'Virtual'
        TRANSIT = 'transit', 'En Tránsito'
    
    warehouse_type = models.CharField(
        max_length=20,
        choices=WarehouseType.choices,
        default=WarehouseType.BRANCH,
        verbose_name='Tipo'
    )
    
    # Estado
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        db_table = 'inventory_warehouses'
        verbose_name = 'Almacén'
        verbose_name_plural = 'Almacenes'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class WarehouseLocation(BaseModel):
    """
    Ubicación dentro de un almacén.
    
    Propósito:
        Definir ubicaciones específicas dentro de un almacén
        para organizar el inventario físicamente.
    
    Estructura:
        Almacén > Zona > Pasillo > Estante > Nivel
        Ejemplo: ALM-001 > A > 01 > 03 = Zona A, Pasillo 1, Nivel 3
    
    Por qué:
        - Localización rápida de productos
        - Optimización de rutas de picking
        - Organización por tipo de producto o rotación
    """
    
    class LocationType(models.TextChoices):
        ZONE = 'zone', 'Zona'
        AISLE = 'aisle', 'Pasillo'
        RACK = 'rack', 'Estante'
        SHELF = 'shelf', 'Nivel'
        BIN = 'bin', 'Casillero'
    
    # Almacén al que pertenece
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='locations',
        verbose_name='Almacén'
    )
    
    # Código de ubicación
    code = models.CharField(
        max_length=50,
        verbose_name='Código',
        help_text='Código de ubicación (ej. "A-01-03")'
    )
    
    # Nombre descriptivo
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        help_text='Nombre descriptivo (ej. "Zona A, Pasillo 1, Nivel 3")'
    )
    
    # Tipo de ubicación
    location_type = models.CharField(
        max_length=20,
        choices=LocationType.choices,
        default=LocationType.BIN,
        verbose_name='Tipo'
    )
    
    # Ubicación padre (para jerarquía)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='Ubicación Padre'
    )
    
    # Capacidad máxima
    max_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Peso Máximo (kg)'
    )
    
    max_volume = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Volumen Máximo (m³)'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    
    class Meta:
        db_table = 'inventory_warehouse_locations'
        verbose_name = 'Ubicación de Almacén'
        verbose_name_plural = 'Ubicaciones de Almacén'
        unique_together = ['warehouse', 'code']
        ordering = ['warehouse__name', 'code']
    
    def __str__(self):
        return f"{self.warehouse.code} - {self.code}"


class Product(BaseModel):
    """
    Producto del inventario.
    
    Propósito:
        Representar los productos que maneja la empresa.
        Es la entidad central del módulo de inventario.
    
    Campos principales:
        - Identificación: SKU, códigos de barras
        - Descripción: nombre, categoría
        - Precios: costo, precio de venta
        - Control: stock mínimo, máximo
    
    Por qué SKU:
        Stock Keeping Unit - identificador interno único.
        Diferente del código de barras (puede haber varios productos
        con el mismo UPC en diferentes presentaciones).
    """
    
    # ========================================================
    # IDENTIFICACIÓN
    # ========================================================
    
    # SKU - Código interno único
    sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='SKU',
        help_text='Stock Keeping Unit - Código interno único'
    )
    
    # Código de barras (EAN/UPC)
    barcode = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_index=True,
        verbose_name='Código de Barras',
        help_text='EAN-13, UPC-A o código interno para escaneo'
    )
    
    # Código QR (opcional, puede ser diferente al barcode)
    qr_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Código QR'
    )
    
    # ========================================================
    # DESCRIPCIÓN
    # ========================================================
    
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre',
        help_text='Nombre del producto'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción detallada del producto'
    )
    
    # Categoría
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Categoría'
    )
    
    # Unidad de medida
    unit_of_measure = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Unidad de Medida'
    )
    
    # Marca
    brand = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Marca'
    )
    
    # Modelo
    model = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Modelo'
    )
    
    # ========================================================
    # PRECIOS (usando Decimal para precisión financiera)
    # ========================================================
    
    # Costo unitario (precio de compra)
    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Precio de Costo',
        help_text='Costo unitario de adquisición'
    )
    
    # Precio de venta
    sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Precio de Venta',
        help_text='Precio de venta al público'
    )
    
    # Precio mínimo de venta (para descuentos)
    min_sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Precio Mínimo',
        help_text='Precio mínimo permitido (para control de descuentos)'
    )
    
    # ========================================================
    # CONTROL DE INVENTARIO
    # ========================================================
    
    # Stock mínimo (para alertas)
    min_stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Stock Mínimo',
        help_text='Cantidad mínima antes de generar alerta'
    )
    
    # Stock máximo recomendado
    max_stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Stock Máximo',
        help_text='Cantidad máxima recomendada'
    )
    
    # Punto de reorden (cuando pedir más)
    reorder_point = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Punto de Reorden',
        help_text='Cantidad a la cual generar orden de compra'
    )
    
    # Cantidad de reorden
    reorder_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Cantidad de Reorden',
        help_text='Cantidad a ordenar cuando se alcanza el punto de reorden'
    )
    
    # ========================================================
    # TIPO DE PRODUCTO
    # ========================================================
    
    class ProductType(models.TextChoices):
        """
        Tipos de producto.
        
        STORABLE: Producto físico con inventario
        SERVICE: Servicio (no tiene inventario)
        CONSUMABLE: Consumible (no se rastrea inventario)
        """
        STORABLE = 'storable', 'Almacenable'
        SERVICE = 'service', 'Servicio'
        CONSUMABLE = 'consumable', 'Consumible'
    
    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.STORABLE,
        verbose_name='Tipo de Producto'
    )
    
    # ========================================================
    # CONTROL DE LOTES Y SERIES
    # ========================================================
    
    # Requiere control por lotes
    track_lots = models.BooleanField(
        default=False,
        verbose_name='Control por Lotes',
        help_text='Activar para productos con fecha de vencimiento o lotes de producción'
    )
    
    # Requiere control por número de serie
    track_serial_numbers = models.BooleanField(
        default=False,
        verbose_name='Control por Número de Serie',
        help_text='Activar para productos individuales con números de serie únicos'
    )
    
    # ========================================================
    # IMPUESTOS
    # ========================================================
    
    # Porcentaje de IVA
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('16.00'),
        verbose_name='Tasa de Impuesto (%)',
        help_text='Porcentaje de IVA aplicable'
    )
    
    # Exento de impuesto
    tax_exempt = models.BooleanField(
        default=False,
        verbose_name='Exento de Impuesto'
    )
    
    # ========================================================
    # CARACTERÍSTICAS FÍSICAS
    # ========================================================
    
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name='Peso (kg)'
    )
    
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Largo (cm)'
    )
    
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Ancho (cm)'
    )
    
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Alto (cm)'
    )
    
    # ========================================================
    # IMÁGENES
    # ========================================================
    
    image = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True,
        verbose_name='Imagen Principal'
    )
    
    # ========================================================
    # ESTADO
    # ========================================================
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Si está disponible para venta'
    )
    
    is_purchasable = models.BooleanField(
        default=True,
        verbose_name='Se puede comprar',
        help_text='Si puede ser incluido en órdenes de compra'
    )
    
    is_sellable = models.BooleanField(
        default=True,
        verbose_name='Se puede vender',
        help_text='Si puede ser incluido en órdenes de venta'
    )
    
    class Meta:
        db_table = 'inventory_products'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['name']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['barcode']),
            models.Index(fields=['name']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"[{self.sku}] {self.name}"
    
    @property
    def profit_margin(self) -> Decimal:
        """
        Calcula el margen de beneficio.
        
        Returns:
            Decimal: Porcentaje de margen sobre el precio de venta
        
        Fórmula:
            ((Precio Venta - Costo) / Precio Venta) * 100
        
        Por qué:
            RU1 - Gerente necesita ver márgenes en tiempo real.
        """
        if self.sale_price > 0:
            margin = ((self.sale_price - self.cost_price) / self.sale_price) * 100
            return round(margin, 2)
        return Decimal('0.00')
    
    @property
    def profit_amount(self) -> Decimal:
        """
        Calcula la ganancia unitaria.
        
        Returns:
            Decimal: Ganancia por unidad vendida
        """
        return self.sale_price - self.cost_price


class Stock(BaseModel):
    """
    Stock de un producto en un almacén específico.
    
    Propósito:
        Registrar la cantidad disponible de cada producto
        en cada almacén. Implementa RF2 - Control multi-almacén.
    
    Relación:
        Producto (1) --- (N) Stock (N) --- (1) Almacén
        Un producto puede estar en múltiples almacenes.
    
    Por qué tabla separada:
        - Permite saber stock por ubicación
        - Facilita transferencias entre almacenes
        - Optimiza consultas de disponibilidad
    """
    
    # Producto
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name='Producto'
    )
    
    # Almacén
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name='Almacén'
    )
    
    # Cantidad disponible
    quantity = models.IntegerField(
        default=0,
        verbose_name='Cantidad Disponible',
        help_text='Cantidad física en el almacén'
    )
    
    # Cantidad reservada (para órdenes pendientes)
    reserved_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Cantidad Reservada',
        help_text='Cantidad reservada para órdenes de venta pendientes'
    )
    
    # Ubicación dentro del almacén
    location = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Ubicación',
        help_text='Ubicación específica (ej. "A-01-03" = Pasillo A, Estante 1, Nivel 3)'
    )
    
    class Meta:
        db_table = 'inventory_stock'
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'
        # Un producto solo puede tener un registro de stock por almacén
        unique_together = ['product', 'warehouse']
        ordering = ['product__name', 'warehouse__name']
    
    def __str__(self):
        return f"{self.product.sku} @ {self.warehouse.code}: {self.quantity}"
    
    @property
    def available_quantity(self) -> int:
        """
        Calcula la cantidad disponible para venta.
        
        Returns:
            int: Cantidad total menos reservada
        
        Por qué:
            La cantidad reservada está comprometida para órdenes
            pendientes, no se puede vender de nuevo.
        """
        return max(0, self.quantity - self.reserved_quantity)
    
    @property
    def is_low_stock(self) -> bool:
        """
        Indica si el stock está por debajo del mínimo.
        
        Returns:
            bool: True si está bajo el mínimo del producto
        """
        return self.quantity <= self.product.min_stock
    
    @property
    def needs_reorder(self) -> bool:
        """
        Indica si se necesita hacer un pedido de reposición.
        
        Returns:
            bool: True si está en o bajo el punto de reorden
        """
        return self.quantity <= self.product.reorder_point


class Lot(BaseModel):
    """
    Lote de producto.
    
    Propósito:
        Rastrear productos por lote de producción o importación.
        Implementa RF2 - Gestión de lotes.
    
    Uso:
        - Productos perecederos con fecha de vencimiento
        - Control de calidad por lote de producción
        - Trazabilidad para recalls
    
    Por qué:
        Permite rastrear de dónde vino cada unidad vendida
        y gestionar productos que vencen.
    """
    
    # Producto al que pertenece el lote
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='lots',
        verbose_name='Producto'
    )
    
    # Almacén donde está el lote
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='lots',
        verbose_name='Almacén'
    )
    
    # Número de lote (único por producto)
    lot_number = models.CharField(
        max_length=50,
        verbose_name='Número de Lote',
        help_text='Identificador único del lote'
    )
    
    # Fecha de producción/entrada
    production_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Producción'
    )
    
    # Fecha de vencimiento
    expiration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Vencimiento',
        help_text='Fecha de caducidad del lote'
    )
    
    # Cantidad en el lote
    quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Cantidad'
    )
    
    # Costo del lote (puede variar por lote)
    cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Costo'
    )
    
    # Notas
    notes = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    class Meta:
        db_table = 'inventory_lots'
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        unique_together = ['product', 'warehouse', 'lot_number']
        ordering = ['expiration_date', 'production_date']
    
    def __str__(self):
        return f"{self.product.sku} - Lote: {self.lot_number}"
    
    @property
    def is_expired(self) -> bool:
        """
        Indica si el lote está vencido.
        
        Returns:
            bool: True si pasó la fecha de vencimiento
        """
        if self.expiration_date:
            from django.utils import timezone
            return self.expiration_date < timezone.now().date()
        return False
    
    @property
    def days_until_expiration(self) -> int:
        """
        Calcula días hasta el vencimiento.
        
        Returns:
            int: Días restantes (negativo si ya venció)
        """
        if self.expiration_date:
            from django.utils import timezone
            delta = self.expiration_date - timezone.now().date()
            return delta.days
        return 999  # Sin fecha de vencimiento


class SerialNumber(BaseModel):
    """
    Número de serie de producto individual.
    
    Propósito:
        Rastrear productos individuales por número de serie único.
        Implementa RF2 - Gestión de números de serie.
    
    Uso:
        - Electrónicos con números de serie
        - Equipos con garantía individual
        - Productos de alto valor
    
    Por qué:
        Permite saber exactamente qué unidad específica
        se vendió a cada cliente (para garantías, devoluciones).
    """
    
    class SerialStatus(models.TextChoices):
        """
        Estados posibles de un número de serie.
        """
        AVAILABLE = 'available', 'Disponible'
        RESERVED = 'reserved', 'Reservado'
        SOLD = 'sold', 'Vendido'
        RETURNED = 'returned', 'Devuelto'
        DEFECTIVE = 'defective', 'Defectuoso'
    
    # Producto
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='serial_numbers',
        verbose_name='Producto'
    )
    
    # Almacén actual
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='serial_numbers',
        verbose_name='Almacén'
    )
    
    # Número de serie único
    serial = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Número de Serie'
    )
    
    # Lote asociado (opcional)
    lot = models.ForeignKey(
        Lot,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='serial_numbers',
        verbose_name='Lote'
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=SerialStatus.choices,
        default=SerialStatus.AVAILABLE,
        verbose_name='Estado'
    )
    
    # Fecha de entrada al inventario
    received_date = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha de Recepción'
    )
    
    # Fecha de venta (si aplica)
    sold_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Venta'
    )
    
    # Referencia a la venta (si fue vendido)
    # Se relacionará con OrderItem cuando se implemente
    
    # Notas
    notes = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    class Meta:
        db_table = 'inventory_serial_numbers'
        verbose_name = 'Número de Serie'
        verbose_name_plural = 'Números de Serie'
        ordering = ['product__sku', 'serial']
    
    def __str__(self):
        return f"{self.product.sku} - S/N: {self.serial}"


class InventoryTransaction(BaseModel):
    """
    Transacción/Movimiento de inventario.
    
    Propósito:
        Registrar todos los movimientos de inventario.
        Proporciona trazabilidad completa del stock.
    
    Tipos de transacción:
        - IN: Entrada (compra, devolución de cliente)
        - OUT: Salida (venta, devolución a proveedor)
        - TRANSFER: Transferencia entre almacenes
        - ADJUSTMENT: Ajuste por inventario físico
    
    Por qué:
        - Auditoría: Saber cuándo, quién y por qué cambió el stock
        - Trazabilidad: Reconstruir el historial de un producto
        - Conciliación: Comparar sistema vs físico
    """
    
    class TransactionType(models.TextChoices):
        """
        Tipos de transacción de inventario.
        """
        IN = 'in', 'Entrada'
        OUT = 'out', 'Salida'
        TRANSFER_IN = 'transfer_in', 'Transferencia Entrada'
        TRANSFER_OUT = 'transfer_out', 'Transferencia Salida'
        ADJUSTMENT_PLUS = 'adj_plus', 'Ajuste Positivo'
        ADJUSTMENT_MINUS = 'adj_minus', 'Ajuste Negativo'
        RETURN_FROM_CUSTOMER = 'return_customer', 'Devolución de Cliente'
        RETURN_TO_SUPPLIER = 'return_supplier', 'Devolución a Proveedor'
    
    class TransactionReason(models.TextChoices):
        """
        Razones de la transacción.
        """
        PURCHASE = 'purchase', 'Compra'
        SALE = 'sale', 'Venta'
        TRANSFER = 'transfer', 'Transferencia'
        PHYSICAL_COUNT = 'physical_count', 'Inventario Físico'
        DAMAGE = 'damage', 'Daño/Rotura'
        THEFT = 'theft', 'Robo'
        EXPIRED = 'expired', 'Vencimiento'
        PRODUCTION = 'production', 'Producción'
        OTHER = 'other', 'Otro'
    
    # Producto afectado
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name='Producto'
    )
    
    # Almacén
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name='Almacén'
    )
    
    # Tipo de transacción
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        verbose_name='Tipo de Transacción'
    )
    
    # Razón
    reason = models.CharField(
        max_length=20,
        choices=TransactionReason.choices,
        verbose_name='Razón'
    )
    
    # Cantidad (siempre positiva, el tipo indica dirección)
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Cantidad'
    )
    
    # Stock antes de la transacción
    stock_before = models.IntegerField(
        verbose_name='Stock Antes'
    )
    
    # Stock después de la transacción
    stock_after = models.IntegerField(
        verbose_name='Stock Después'
    )
    
    # Costo unitario al momento de la transacción
    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Costo Unitario'
    )
    
    # Lote relacionado (si aplica)
    lot = models.ForeignKey(
        Lot,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='transactions',
        verbose_name='Lote'
    )
    
    # Número de serie (si aplica)
    serial_number = models.ForeignKey(
        SerialNumber,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='transactions',
        verbose_name='Número de Serie'
    )
    
    # Referencia al documento origen (orden de compra, venta, etc.)
    reference_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Tipo de Referencia',
        help_text='Tipo de documento origen (purchase_order, sale_order, etc.)'
    )
    
    reference_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name='ID de Referencia',
        help_text='ID del documento origen'
    )
    
    # Notas adicionales
    notes = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    class Meta:
        db_table = 'inventory_transactions'
        verbose_name = 'Transacción de Inventario'
        verbose_name_plural = 'Transacciones de Inventario'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['warehouse', '-created_at']),
            models.Index(fields=['reference_type', 'reference_id']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.product.sku}: {self.quantity}"


class StockTransfer(BaseModel):
    """
    Transferencia de inventario entre almacenes.
    
    Propósito:
        Gestionar el movimiento de productos entre ubicaciones.
        Implementa funcionalidad multi-almacén del RF2.
    
    Flujo:
        1. Se crea transferencia (DRAFT)
        2. Se confirma (CONFIRMED)
        3. Se despacha desde origen (IN_TRANSIT)
        4. Se recibe en destino (COMPLETED)
    
    Por qué estados:
        Permite rastrear dónde está físicamente la mercancía
        en cada momento del proceso.
    """
    
    class TransferStatus(models.TextChoices):
        DRAFT = 'draft', 'Borrador'
        CONFIRMED = 'confirmed', 'Confirmado'
        IN_TRANSIT = 'in_transit', 'En Tránsito'
        COMPLETED = 'completed', 'Completado'
        CANCELLED = 'cancelled', 'Cancelado'
    
    # Número de transferencia único
    transfer_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de Transferencia'
    )
    
    # Almacén origen
    source_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name='outgoing_transfers',
        verbose_name='Almacén Origen'
    )
    
    # Almacén destino
    destination_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name='incoming_transfers',
        verbose_name='Almacén Destino'
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=TransferStatus.choices,
        default=TransferStatus.DRAFT,
        verbose_name='Estado'
    )
    
    # Fecha programada
    scheduled_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Programada'
    )
    
    # Fecha de despacho real
    shipped_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Despacho'
    )
    
    # Fecha de recepción real
    received_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Recepción'
    )
    
    # Notas
    notes = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    class Meta:
        db_table = 'inventory_transfers'
        verbose_name = 'Transferencia'
        verbose_name_plural = 'Transferencias'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transfer_number}: {self.source_warehouse.code} -> {self.destination_warehouse.code}"


class StockTransferItem(BaseModel):
    """
    Línea de detalle de una transferencia.
    
    Propósito:
        Especificar qué productos y cantidades se transfieren.
    """
    
    # Transferencia padre
    transfer = models.ForeignKey(
        StockTransfer,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Transferencia'
    )
    
    # Producto
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='transfer_items',
        verbose_name='Producto'
    )
    
    # Cantidad a transferir
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Cantidad'
    )
    
    # Cantidad recibida (puede ser diferente a la enviada)
    received_quantity = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='Cantidad Recibida'
    )
    
    # Lote específico (si aplica)
    lot = models.ForeignKey(
        Lot,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Lote'
    )
    
    # Notas por línea
    notes = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Notas'
    )
    
    class Meta:
        db_table = 'inventory_transfer_items'
        verbose_name = 'Ítem de Transferencia'
        verbose_name_plural = 'Ítems de Transferencia'
    
    def __str__(self):
        return f"{self.transfer.transfer_number} - {self.product.sku}: {self.quantity}"
