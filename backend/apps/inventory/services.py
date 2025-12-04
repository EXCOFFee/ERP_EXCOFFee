# ========================================================
# SISTEMA ERP UNIVERSAL - Servicios de Inventario
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Encapsular la lógica de negocio del módulo de inventario.
# Implementa el patrón Service Layer para separar la lógica
# de las vistas y serializers.
#
# Por qué Service Layer:
# - Reutilización de lógica desde diferentes endpoints
# - Facilita testing unitario
# - Mantiene las vistas simples
# ========================================================

from decimal import Decimal
from typing import Optional, Tuple, List
from django.db import transaction
from django.utils import timezone

from .models import (
    Product,
    Stock,
    Lot,
    SerialNumber,
    InventoryTransaction,
    Warehouse,
    StockTransfer,
    StockTransferItem,
)
from apps.core.exceptions import (
    InsufficientStockException,
    ProductNotFoundException,
    WarehouseNotFoundException,
    InvalidTransferException,
    ValidationException,
)


class InventoryService:
    """
    Servicio para operaciones de inventario.
    
    Propósito:
        Centralizar la lógica de negocio relacionada con
        movimientos de inventario, validaciones de stock,
        y operaciones complejas.
    
    Uso:
        service = InventoryService()
        service.add_stock(product_id, warehouse_id, quantity, ...)
    """
    
    @staticmethod
    @transaction.atomic
    def add_stock(
        product_id: str,
        warehouse_id: str,
        quantity: int,
        reason: str = InventoryTransaction.TransactionReason.PURCHASE,
        unit_cost: Decimal = None,
        lot_number: str = None,
        serial_numbers: List[str] = None,
        reference_type: str = None,
        reference_id: str = None,
        notes: str = '',
        user=None
    ) -> Tuple[Stock, InventoryTransaction]:
        """
        Agrega stock de un producto a un almacén.
        
        Propósito:
            Registrar entrada de inventario con trazabilidad completa.
        
        Args:
            product_id: ID del producto
            warehouse_id: ID del almacén
            quantity: Cantidad a agregar (debe ser positiva)
            reason: Razón de la entrada (compra, devolución, etc.)
            unit_cost: Costo unitario (para actualizar promedio)
            lot_number: Número de lote si el producto lo requiere
            serial_numbers: Lista de números de serie si aplica
            reference_type: Tipo de documento origen (purchase_order, etc.)
            reference_id: ID del documento origen
            notes: Notas adicionales
            user: Usuario que realiza la operación
        
        Returns:
            Tuple[Stock, InventoryTransaction]: Stock actualizado y transacción creada
        
        Raises:
            ProductNotFoundException: Si el producto no existe
            WarehouseNotFoundException: Si el almacén no existe
            ValidationException: Si los datos son inválidos
        
        Ejemplo:
            stock, transaction = InventoryService.add_stock(
                product_id='uuid-del-producto',
                warehouse_id='uuid-del-almacen',
                quantity=100,
                reason='purchase',
                unit_cost=Decimal('25.50'),
                reference_type='purchase_order',
                reference_id='uuid-de-la-orden'
            )
        """
        # Validar cantidad
        if quantity <= 0:
            raise ValidationException(
                message='La cantidad debe ser mayor a cero',
                field='quantity',
                source='InventoryService.add_stock'
            )
        
        # Obtener producto
        try:
            product = Product.objects.get(pk=product_id, is_deleted=False)
        except Product.DoesNotExist:
            raise ProductNotFoundException(product_id=product_id)
        
        # Obtener almacén
        try:
            warehouse = Warehouse.objects.get(pk=warehouse_id, is_active=True)
        except Warehouse.DoesNotExist:
            raise WarehouseNotFoundException(warehouse_id=warehouse_id)
        
        # Validar lotes si el producto los requiere
        lot = None
        if product.track_lots:
            if not lot_number:
                raise ValidationException(
                    message='Este producto requiere número de lote',
                    field='lot_number',
                    source='InventoryService.add_stock'
                )
            # Crear o obtener lote
            lot, _ = Lot.objects.get_or_create(
                product=product,
                warehouse=warehouse,
                lot_number=lot_number,
                defaults={'quantity': 0, 'cost': unit_cost}
            )
            lot.quantity += quantity
            lot.save()
        
        # Validar números de serie si el producto los requiere
        if product.track_serial_numbers:
            if not serial_numbers or len(serial_numbers) != quantity:
                raise ValidationException(
                    message=f'Se requieren {quantity} números de serie',
                    field='serial_numbers',
                    source='InventoryService.add_stock'
                )
            # Crear números de serie
            for serial in serial_numbers:
                SerialNumber.objects.create(
                    product=product,
                    warehouse=warehouse,
                    serial=serial,
                    lot=lot,
                    status=SerialNumber.SerialStatus.AVAILABLE
                )
        
        # Obtener o crear stock
        stock, created = Stock.objects.get_or_create(
            product=product,
            warehouse=warehouse,
            defaults={'quantity': 0}
        )
        
        # Guardar stock anterior para la transacción
        stock_before = stock.quantity
        
        # Actualizar stock
        stock.quantity += quantity
        stock.save()
        
        # Crear transacción
        transaction_record = InventoryTransaction.objects.create(
            product=product,
            warehouse=warehouse,
            transaction_type=InventoryTransaction.TransactionType.IN,
            reason=reason,
            quantity=quantity,
            stock_before=stock_before,
            stock_after=stock.quantity,
            unit_cost=unit_cost,
            lot=lot,
            reference_type=reference_type or '',
            reference_id=reference_id,
            notes=notes,
            created_by=user
        )
        
        return stock, transaction_record
    
    @staticmethod
    @transaction.atomic
    def remove_stock(
        product_id: str,
        warehouse_id: str,
        quantity: int,
        reason: str = InventoryTransaction.TransactionReason.SALE,
        lot_id: str = None,
        serial_numbers: List[str] = None,
        reference_type: str = None,
        reference_id: str = None,
        notes: str = '',
        user=None
    ) -> Tuple[Stock, InventoryTransaction]:
        """
        Remueve stock de un producto de un almacén.
        
        Propósito:
            Registrar salida de inventario con validación de disponibilidad.
        
        Args:
            product_id: ID del producto
            warehouse_id: ID del almacén
            quantity: Cantidad a remover
            reason: Razón de la salida
            lot_id: ID del lote específico (si aplica)
            serial_numbers: Números de serie a sacar
            reference_type: Tipo de documento origen
            reference_id: ID del documento origen
            notes: Notas adicionales
            user: Usuario que realiza la operación
        
        Returns:
            Tuple[Stock, InventoryTransaction]: Stock actualizado y transacción
        
        Raises:
            InsufficientStockException: Si no hay suficiente stock
        """
        # Validar cantidad
        if quantity <= 0:
            raise ValidationException(
                message='La cantidad debe ser mayor a cero',
                field='quantity',
                source='InventoryService.remove_stock'
            )
        
        # Obtener producto
        try:
            product = Product.objects.get(pk=product_id, is_deleted=False)
        except Product.DoesNotExist:
            raise ProductNotFoundException(product_id=product_id)
        
        # Obtener stock
        try:
            stock = Stock.objects.get(
                product_id=product_id,
                warehouse_id=warehouse_id
            )
        except Stock.DoesNotExist:
            raise InsufficientStockException(
                product=product.name,
                requested=quantity,
                available=0
            )
        
        # Verificar disponibilidad
        if stock.available_quantity < quantity:
            raise InsufficientStockException(
                product=product.name,
                requested=quantity,
                available=stock.available_quantity
            )
        
        # Manejar lotes si aplica
        lot = None
        if product.track_lots:
            if lot_id:
                try:
                    lot = Lot.objects.get(pk=lot_id, product=product)
                    if lot.quantity < quantity:
                        raise InsufficientStockException(
                            product=f"{product.name} (Lote: {lot.lot_number})",
                            requested=quantity,
                            available=lot.quantity
                        )
                    lot.quantity -= quantity
                    lot.save()
                except Lot.DoesNotExist:
                    raise ValidationException(
                        message=f'Lote no encontrado: {lot_id}',
                        source='InventoryService.remove_stock'
                    )
            else:
                # Usar FIFO (First In, First Out) - lotes más antiguos primero
                raise ValidationException(
                    message='Debe especificar el lote para este producto',
                    field='lot_id',
                    source='InventoryService.remove_stock'
                )
        
        # Manejar números de serie si aplica
        if product.track_serial_numbers:
            if not serial_numbers or len(serial_numbers) != quantity:
                raise ValidationException(
                    message=f'Se requieren {quantity} números de serie',
                    field='serial_numbers',
                    source='InventoryService.remove_stock'
                )
            # Actualizar estado de números de serie
            for serial in serial_numbers:
                try:
                    sn = SerialNumber.objects.get(
                        product=product,
                        serial=serial,
                        status=SerialNumber.SerialStatus.AVAILABLE
                    )
                    sn.status = SerialNumber.SerialStatus.SOLD
                    sn.sold_date = timezone.now().date()
                    sn.save()
                except SerialNumber.DoesNotExist:
                    raise ValidationException(
                        message=f'Número de serie no disponible: {serial}',
                        source='InventoryService.remove_stock'
                    )
        
        # Guardar stock anterior
        stock_before = stock.quantity
        
        # Actualizar stock
        stock.quantity -= quantity
        stock.save()
        
        # Crear transacción
        transaction_record = InventoryTransaction.objects.create(
            product=product,
            warehouse_id=warehouse_id,
            transaction_type=InventoryTransaction.TransactionType.OUT,
            reason=reason,
            quantity=quantity,
            stock_before=stock_before,
            stock_after=stock.quantity,
            lot=lot,
            reference_type=reference_type or '',
            reference_id=reference_id,
            notes=notes,
            created_by=user
        )
        
        return stock, transaction_record
    
    @staticmethod
    @transaction.atomic
    def reserve_stock(
        product_id: str,
        warehouse_id: str,
        quantity: int,
        user=None
    ) -> Stock:
        """
        Reserva stock para una orden pendiente.
        
        Propósito:
            Marcar stock como reservado para evitar sobreventa.
            El stock reservado no está disponible para otras ventas.
        
        Args:
            product_id: ID del producto
            warehouse_id: ID del almacén
            quantity: Cantidad a reservar
        
        Returns:
            Stock: Stock actualizado
        
        Raises:
            InsufficientStockException: Si no hay suficiente disponible
        """
        try:
            stock = Stock.objects.select_for_update().get(
                product_id=product_id,
                warehouse_id=warehouse_id
            )
        except Stock.DoesNotExist:
            product = Product.objects.get(pk=product_id)
            raise InsufficientStockException(
                product=product.name,
                requested=quantity,
                available=0
            )
        
        if stock.available_quantity < quantity:
            raise InsufficientStockException(
                product=stock.product.name,
                requested=quantity,
                available=stock.available_quantity
            )
        
        stock.reserved_quantity += quantity
        stock.save()
        
        return stock
    
    @staticmethod
    @transaction.atomic
    def release_reservation(
        product_id: str,
        warehouse_id: str,
        quantity: int
    ) -> Stock:
        """
        Libera stock previamente reservado.
        
        Propósito:
            Cuando una orden es cancelada, liberar el stock reservado.
        
        Args:
            product_id: ID del producto
            warehouse_id: ID del almacén
            quantity: Cantidad a liberar
        
        Returns:
            Stock: Stock actualizado
        """
        stock = Stock.objects.select_for_update().get(
            product_id=product_id,
            warehouse_id=warehouse_id
        )
        
        # No liberar más de lo reservado
        release_qty = min(quantity, stock.reserved_quantity)
        stock.reserved_quantity -= release_qty
        stock.save()
        
        return stock
    
    @staticmethod
    @transaction.atomic
    def adjust_stock(
        product_id: str,
        warehouse_id: str,
        new_quantity: int,
        reason: str = 'Ajuste de inventario físico',
        user=None
    ) -> Tuple[Stock, InventoryTransaction]:
        """
        Ajusta el stock a una cantidad específica.
        
        Propósito:
            Corregir discrepancias entre stock en sistema y físico.
            Usado después de un conteo de inventario.
        
        Args:
            product_id: ID del producto
            warehouse_id: ID del almacén
            new_quantity: Nueva cantidad absoluta
            reason: Razón del ajuste
            user: Usuario que realiza el ajuste
        
        Returns:
            Tuple[Stock, InventoryTransaction]: Stock y transacción de ajuste
        """
        try:
            product = Product.objects.get(pk=product_id, is_deleted=False)
        except Product.DoesNotExist:
            raise ProductNotFoundException(product_id=product_id)
        
        stock, created = Stock.objects.get_or_create(
            product=product,
            warehouse_id=warehouse_id,
            defaults={'quantity': 0}
        )
        
        stock_before = stock.quantity
        difference = new_quantity - stock_before
        
        if difference == 0:
            # No hay cambio
            return stock, None
        
        # Determinar tipo de transacción
        if difference > 0:
            transaction_type = InventoryTransaction.TransactionType.ADJUSTMENT_PLUS
        else:
            transaction_type = InventoryTransaction.TransactionType.ADJUSTMENT_MINUS
        
        # Actualizar stock
        stock.quantity = new_quantity
        stock.save()
        
        # Crear transacción de ajuste
        transaction_record = InventoryTransaction.objects.create(
            product=product,
            warehouse_id=warehouse_id,
            transaction_type=transaction_type,
            reason=InventoryTransaction.TransactionReason.PHYSICAL_COUNT,
            quantity=abs(difference),
            stock_before=stock_before,
            stock_after=new_quantity,
            notes=reason,
            created_by=user
        )
        
        return stock, transaction_record
    
    @staticmethod
    @transaction.atomic
    def process_transfer(
        transfer: StockTransfer,
        action: str,
        user=None
    ) -> StockTransfer:
        """
        Procesa una transferencia de inventario.
        
        Propósito:
            Manejar el flujo completo de una transferencia:
            confirm -> ship -> receive
        
        Args:
            transfer: Objeto StockTransfer
            action: 'confirm', 'ship', 'receive', 'cancel'
            user: Usuario que realiza la acción
        
        Returns:
            StockTransfer: Transferencia actualizada
        """
        if action == 'confirm':
            if transfer.status != StockTransfer.TransferStatus.DRAFT:
                raise InvalidTransferException(
                    reason='Solo se pueden confirmar transferencias en borrador'
                )
            
            # Validar y reservar stock
            for item in transfer.items.all():
                try:
                    stock = Stock.objects.get(
                        product=item.product,
                        warehouse=transfer.source_warehouse
                    )
                    if stock.available_quantity < item.quantity:
                        raise InsufficientStockException(
                            product=item.product.name,
                            requested=item.quantity,
                            available=stock.available_quantity
                        )
                    # Reservar stock
                    stock.reserved_quantity += item.quantity
                    stock.save()
                except Stock.DoesNotExist:
                    raise InsufficientStockException(
                        product=item.product.name,
                        requested=item.quantity,
                        available=0
                    )
            
            transfer.status = StockTransfer.TransferStatus.CONFIRMED
            transfer.save()
        
        elif action == 'ship':
            if transfer.status != StockTransfer.TransferStatus.CONFIRMED:
                raise InvalidTransferException(
                    reason='Solo se pueden despachar transferencias confirmadas'
                )
            
            # Sacar del almacén origen
            for item in transfer.items.all():
                stock = Stock.objects.get(
                    product=item.product,
                    warehouse=transfer.source_warehouse
                )
                stock.quantity -= item.quantity
                stock.reserved_quantity -= item.quantity
                stock.save()
                
                # Registrar transacción de salida
                InventoryTransaction.objects.create(
                    product=item.product,
                    warehouse=transfer.source_warehouse,
                    transaction_type=InventoryTransaction.TransactionType.TRANSFER_OUT,
                    reason=InventoryTransaction.TransactionReason.TRANSFER,
                    quantity=item.quantity,
                    stock_before=stock.quantity + item.quantity,
                    stock_after=stock.quantity,
                    reference_type='stock_transfer',
                    reference_id=transfer.id,
                    created_by=user
                )
            
            transfer.status = StockTransfer.TransferStatus.IN_TRANSIT
            transfer.shipped_date = timezone.now()
            transfer.save()
        
        elif action == 'receive':
            if transfer.status != StockTransfer.TransferStatus.IN_TRANSIT:
                raise InvalidTransferException(
                    reason='Solo se pueden recibir transferencias en tránsito'
                )
            
            # Agregar al almacén destino
            for item in transfer.items.all():
                received_qty = item.received_quantity or item.quantity
                
                stock, _ = Stock.objects.get_or_create(
                    product=item.product,
                    warehouse=transfer.destination_warehouse,
                    defaults={'quantity': 0}
                )
                
                stock_before = stock.quantity
                stock.quantity += received_qty
                stock.save()
                
                # Registrar transacción de entrada
                InventoryTransaction.objects.create(
                    product=item.product,
                    warehouse=transfer.destination_warehouse,
                    transaction_type=InventoryTransaction.TransactionType.TRANSFER_IN,
                    reason=InventoryTransaction.TransactionReason.TRANSFER,
                    quantity=received_qty,
                    stock_before=stock_before,
                    stock_after=stock.quantity,
                    reference_type='stock_transfer',
                    reference_id=transfer.id,
                    created_by=user
                )
            
            transfer.status = StockTransfer.TransferStatus.COMPLETED
            transfer.received_date = timezone.now()
            transfer.save()
        
        elif action == 'cancel':
            if transfer.status in [
                StockTransfer.TransferStatus.COMPLETED,
                StockTransfer.TransferStatus.CANCELLED
            ]:
                raise InvalidTransferException(
                    reason='No se puede cancelar esta transferencia'
                )
            
            # Liberar reservas si estaba confirmada
            if transfer.status == StockTransfer.TransferStatus.CONFIRMED:
                for item in transfer.items.all():
                    try:
                        stock = Stock.objects.get(
                            product=item.product,
                            warehouse=transfer.source_warehouse
                        )
                        stock.reserved_quantity -= item.quantity
                        stock.save()
                    except Stock.DoesNotExist:
                        pass
            
            transfer.status = StockTransfer.TransferStatus.CANCELLED
            transfer.save()
        
        return transfer
    
    @staticmethod
    def get_stock_valuation(warehouse_id: str = None) -> dict:
        """
        Calcula la valoración del inventario.
        
        Propósito:
            Obtener el valor total del inventario para reportes financieros.
        
        Args:
            warehouse_id: Opcional, para filtrar por almacén
        
        Returns:
            dict: {
                'total_value': Decimal,
                'total_items': int,
                'by_category': [...]
            }
        """
        from django.db.models import Sum, F, DecimalField
        from django.db.models.functions import Coalesce
        
        queryset = Stock.objects.filter(quantity__gt=0)
        
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
        
        # Valor total
        total = queryset.annotate(
            line_value=F('quantity') * F('product__cost_price')
        ).aggregate(
            total_value=Coalesce(Sum('line_value'), Decimal('0.00')),
            total_items=Coalesce(Sum('quantity'), 0)
        )
        
        # Por categoría
        by_category = queryset.values(
            'product__category__name'
        ).annotate(
            category_value=Sum(F('quantity') * F('product__cost_price')),
            category_items=Sum('quantity')
        ).order_by('-category_value')
        
        return {
            'total_value': total['total_value'],
            'total_items': total['total_items'],
            'by_category': list(by_category)
        }
    
    @staticmethod
    def get_low_stock_products(warehouse_id: str = None) -> List[dict]:
        """
        Obtiene productos con stock bajo.
        
        Propósito:
            Generar alertas de productos que necesitan reposición.
        
        Args:
            warehouse_id: Opcional, para filtrar por almacén
        
        Returns:
            Lista de productos con stock bajo
        """
        from django.db.models import F
        
        queryset = Stock.objects.filter(
            quantity__lte=F('product__min_stock'),
            quantity__gt=0,
            product__is_active=True
        ).select_related('product', 'warehouse')
        
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
        
        return [
            {
                'product_id': str(stock.product.id),
                'product_sku': stock.product.sku,
                'product_name': stock.product.name,
                'warehouse_id': str(stock.warehouse.id),
                'warehouse_name': stock.warehouse.name,
                'current_stock': stock.quantity,
                'min_stock': stock.product.min_stock,
                'reorder_point': stock.product.reorder_point,
                'reorder_quantity': stock.product.reorder_quantity,
            }
            for stock in queryset
        ]
    
    @staticmethod
    def search_by_barcode(
        code: str,
        warehouse_id: str = None
    ) -> Optional[dict]:
        """
        Busca un producto por código de barras o QR.
        
        Propósito:
            Implementa RU2 - Escaneo de códigos de barras.
        
        Args:
            code: Código escaneado
            warehouse_id: Almacén para obtener stock específico
        
        Returns:
            dict: Información del producto o None
        """
        # Buscar por código de barras
        product = Product.objects.filter(
            barcode=code,
            is_deleted=False
        ).first()
        
        # Si no encuentra, buscar por QR
        if not product:
            product = Product.objects.filter(
                qr_code=code,
                is_deleted=False
            ).first()
        
        # Si no encuentra, buscar por SKU
        if not product:
            product = Product.objects.filter(
                sku__iexact=code,
                is_deleted=False
            ).first()
        
        if not product:
            return None
        
        result = {
            'id': str(product.id),
            'sku': product.sku,
            'barcode': product.barcode,
            'name': product.name,
            'category': product.category.name,
            'cost_price': str(product.cost_price),
            'sale_price': str(product.sale_price),
            'image': product.image.url if product.image else None,
        }
        
        # Agregar stock si se especifica almacén
        if warehouse_id:
            try:
                stock = Stock.objects.get(
                    product=product,
                    warehouse_id=warehouse_id
                )
                result['stock'] = {
                    'quantity': stock.quantity,
                    'reserved': stock.reserved_quantity,
                    'available': stock.available_quantity,
                    'location': stock.location,
                }
            except Stock.DoesNotExist:
                result['stock'] = {
                    'quantity': 0,
                    'reserved': 0,
                    'available': 0,
                    'location': '',
                }
        
        return result
