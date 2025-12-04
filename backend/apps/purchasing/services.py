# ========================================================
# SISTEMA ERP UNIVERSAL - Servicio de Compras
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Lógica de negocio para el módulo de compras.
# ========================================================

from decimal import Decimal
from datetime import date, timedelta
from typing import Dict, List, Optional, Any, Tuple

from django.db import transaction
from django.db.models import Sum, Count, Avg, F, Q
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.core.services import BaseService


class PurchasingService(BaseService):
    """Servicio para gestión de compras."""
    
    # ====================================================
    # Solicitudes de Compra
    # ====================================================
    
    @classmethod
    @transaction.atomic
    def approve_requisition(cls, requisition, user):
        """
        Aprueba una solicitud de compra.
        
        Args:
            requisition: Solicitud de compra
            user: Usuario que aprueba
        """
        if requisition.status != 'submitted':
            raise ValidationError(
                "Solo se pueden aprobar solicitudes enviadas"
            )
        
        requisition.status = 'approved'
        requisition.approved_by = user
        requisition.approved_date = timezone.now()
        requisition.save()
    
    @classmethod
    @transaction.atomic
    def reject_requisition(cls, requisition, user, reason: str):
        """
        Rechaza una solicitud de compra.
        
        Args:
            requisition: Solicitud de compra
            user: Usuario que rechaza
            reason: Motivo del rechazo
        """
        if requisition.status != 'submitted':
            raise ValidationError(
                "Solo se pueden rechazar solicitudes enviadas"
            )
        
        requisition.status = 'rejected'
        requisition.approved_by = user
        requisition.approved_date = timezone.now()
        requisition.rejection_reason = reason
        requisition.save()
    
    @classmethod
    @transaction.atomic
    def convert_requisition_to_order(
        cls,
        requisition,
        supplier,
        user,
        lines_map: Dict = None
    ):
        """
        Convierte solicitud de compra a orden de compra.
        
        Args:
            requisition: Solicitud de compra
            supplier: Proveedor seleccionado
            user: Usuario
            lines_map: Mapeo de líneas (opcional)
            
        Returns:
            Orden de compra creada
        """
        from .models import PurchaseOrder, PurchaseOrderLine
        
        if requisition.status != 'approved':
            raise ValidationError(
                "Solo se pueden convertir solicitudes aprobadas"
            )
        
        # Crear orden
        order = PurchaseOrder.objects.create(
            supplier=supplier,
            order_date=date.today(),
            required_date=requisition.required_date,
            warehouse=requisition.warehouse,
            requisition=requisition,
            created_by=user
        )
        
        # Crear líneas
        for line in requisition.lines.all():
            if line.quantity_pending <= 0:
                continue
            
            # Obtener precio del proveedor
            from .models import SupplierProduct
            supplier_product = SupplierProduct.objects.filter(
                supplier=supplier,
                product=line.product,
                is_active=True
            ).first()
            
            unit_price = (
                supplier_product.unit_price if supplier_product
                else line.estimated_unit_price or line.product.cost_price
            )
            
            PurchaseOrderLine.objects.create(
                order=order,
                line_number=line.line_number,
                product=line.product,
                description=line.description,
                quantity=line.quantity_pending,
                unit=line.unit,
                unit_price=unit_price,
                requisition_line=line,
                warehouse=order.warehouse
            )
            
            # Actualizar cantidad ordenada en solicitud
            line.quantity_ordered += line.quantity_pending
            line.save()
        
        # Calcular totales
        cls._calculate_order_totals(order)
        
        # Verificar si la solicitud está completamente convertida
        pending = sum(l.quantity_pending for l in requisition.lines.all())
        if pending <= 0:
            requisition.status = 'converted'
            requisition.save()
        
        return order
    
    # ====================================================
    # Órdenes de Compra
    # ====================================================
    
    @classmethod
    @transaction.atomic
    def approve_order(cls, order, user):
        """
        Aprueba una orden de compra.
        
        Args:
            order: Orden de compra
            user: Usuario que aprueba
        """
        if order.status != 'pending_approval':
            raise ValidationError(
                "Solo se pueden aprobar órdenes pendientes de aprobación"
            )
        
        order.status = 'approved'
        order.approved_by = user
        order.approved_date = timezone.now()
        order.save()
    
    @classmethod
    @transaction.atomic
    def send_order_to_supplier(cls, order, user):
        """
        Marca la orden como enviada al proveedor.
        
        Args:
            order: Orden de compra
            user: Usuario
        """
        if order.status not in ['draft', 'approved']:
            raise ValidationError(
                "Solo se pueden enviar órdenes en borrador o aprobadas"
            )
        
        order.status = 'sent'
        order.save()
        
        # TODO: Enviar email al proveedor
    
    @classmethod
    @transaction.atomic
    def confirm_order(cls, order, promised_date: date = None, reference: str = None):
        """
        Confirma la orden por parte del proveedor.
        
        Args:
            order: Orden de compra
            promised_date: Fecha prometida por proveedor
            reference: Referencia del proveedor
        """
        if order.status != 'sent':
            raise ValidationError(
                "Solo se pueden confirmar órdenes enviadas"
            )
        
        order.status = 'confirmed'
        if promised_date:
            order.promised_date = promised_date
        if reference:
            order.supplier_reference = reference
        order.save()
    
    @classmethod
    @transaction.atomic
    def cancel_order(cls, order, reason: str, user):
        """
        Cancela una orden de compra.
        
        Args:
            order: Orden de compra
            reason: Motivo
            user: Usuario
        """
        if order.status in ['received', 'invoiced', 'completed', 'cancelled']:
            raise ValidationError(
                "No se puede cancelar la orden en este estado"
            )
        
        # Revertir cantidades ordenadas en solicitud
        if order.requisition:
            for line in order.lines.all():
                if line.requisition_line:
                    line.requisition_line.quantity_ordered -= line.quantity
                    line.requisition_line.save()
        
        order.status = 'cancelled'
        order.notes = f"{order.notes or ''}\nCancelado: {reason}"
        order.save()
    
    @classmethod
    def _calculate_order_totals(cls, order):
        """Calcula totales de la orden."""
        lines = order.lines.all()
        
        subtotal = Decimal('0')
        discount = Decimal('0')
        tax = Decimal('0')
        
        for line in lines:
            line_subtotal = line.quantity * line.unit_price
            line_discount = line_subtotal * (line.discount_percent / 100)
            taxable = line_subtotal - line_discount
            line_tax = taxable * (line.tax.rate / 100 if line.tax else 0)
            
            line.discount_amount = line_discount
            line.tax_amount = line_tax
            line.line_total = taxable + line_tax
            line.save()
            
            subtotal += line_subtotal
            discount += line_discount
            tax += line_tax
        
        order.subtotal = subtotal
        order.discount_amount = discount
        order.tax_amount = tax
        order.total = (
            subtotal - discount + tax +
            order.freight_amount + order.other_charges
        )
        order.save()
    
    # ====================================================
    # Recepción de Mercancía
    # ====================================================
    
    @classmethod
    @transaction.atomic
    def create_goods_receipt(
        cls,
        order,
        lines_data: List[Dict],
        receipt_data: Dict,
        user
    ):
        """
        Crea recepción de mercancía.
        
        Args:
            order: Orden de compra
            lines_data: Datos de líneas a recibir
            receipt_data: Datos de la recepción
            user: Usuario
            
        Returns:
            Recepción creada
        """
        from .models import GoodsReceipt, GoodsReceiptLine
        
        if order.status not in ['confirmed', 'partial']:
            raise ValidationError(
                "Solo se puede recibir de órdenes confirmadas"
            )
        
        # Crear recepción
        receipt = GoodsReceipt.objects.create(
            purchase_order=order,
            receipt_date=receipt_data.get('receipt_date', date.today()),
            warehouse=receipt_data.get('warehouse', order.warehouse),
            supplier_delivery_note=receipt_data.get('supplier_delivery_note'),
            supplier_invoice_number=receipt_data.get('supplier_invoice_number'),
            notes=receipt_data.get('notes'),
            received_by=user,
            created_by=user
        )
        
        # Crear líneas
        for line_data in lines_data:
            order_line = line_data['order_line']
            quantity_received = line_data['quantity_received']
            
            # Validar cantidad
            pending = order_line.quantity - order_line.quantity_received
            if quantity_received > pending:
                raise ValidationError(
                    f"Cantidad excede pendiente para {order_line.product}"
                )
            
            GoodsReceiptLine.objects.create(
                receipt=receipt,
                order_line=order_line,
                quantity_received=quantity_received,
                quantity_accepted=line_data.get('quantity_accepted', quantity_received),
                quantity_rejected=line_data.get('quantity_rejected', Decimal('0')),
                rejection_reason=line_data.get('rejection_reason'),
                location=line_data.get('location'),
                lot=line_data.get('lot'),
                notes=line_data.get('notes')
            )
        
        return receipt
    
    @classmethod
    @transaction.atomic
    def confirm_goods_receipt(cls, receipt):
        """
        Confirma recepción de mercancía.
        
        Args:
            receipt: Recepción de mercancía
        """
        from apps.inventory.services import InventoryService
        
        if receipt.status != 'draft':
            raise ValidationError("Solo se pueden confirmar recepciones en borrador")
        
        for line in receipt.lines.all():
            order_line = line.order_line
            
            # Actualizar cantidad recibida en orden
            order_line.quantity_received += line.quantity_accepted
            if order_line.quantity_received >= order_line.quantity:
                order_line.status = 'received'
            else:
                order_line.status = 'partial'
            order_line.save()
            
            # Crear movimiento de inventario
            if line.quantity_accepted > 0:
                InventoryService.receive_stock(
                    product=order_line.product,
                    warehouse=receipt.warehouse,
                    quantity=line.quantity_accepted,
                    unit_cost=order_line.unit_price,
                    reference=f"GR-{receipt.number}",
                    lot=line.lot,
                    location=line.location
                )
            
            # Actualizar precio de costo del producto
            order_line.product.cost_price = order_line.unit_price
            order_line.product.save(update_fields=['cost_price'])
            
            # Actualizar último precio del proveedor
            from .models import SupplierProduct
            supplier_product = SupplierProduct.objects.filter(
                supplier=receipt.purchase_order.supplier,
                product=order_line.product
            ).first()
            
            if supplier_product:
                supplier_product.last_purchase_date = receipt.receipt_date
                supplier_product.last_purchase_price = order_line.unit_price
                supplier_product.save()
        
        receipt.status = 'completed'
        receipt.save()
        
        # Actualizar estado de la orden
        cls._update_order_status(receipt.purchase_order)
    
    @classmethod
    def _update_order_status(cls, order):
        """Actualiza estado de orden basado en líneas."""
        lines = order.lines.all()
        
        total_qty = sum(l.quantity for l in lines)
        received_qty = sum(l.quantity_received for l in lines)
        
        if received_qty >= total_qty:
            order.status = 'received'
        elif received_qty > 0:
            order.status = 'partial'
        
        order.save()
    
    # ====================================================
    # Facturas de Proveedor
    # ====================================================
    
    @classmethod
    @transaction.atomic
    def create_invoice_from_receipt(cls, receipt, user):
        """
        Crea factura de proveedor desde recepción.
        
        Args:
            receipt: Recepción de mercancía
            user: Usuario
            
        Returns:
            Factura creada
        """
        from .models import SupplierInvoice, SupplierInvoiceLine
        
        order = receipt.purchase_order
        
        # Crear factura
        due_date = date.today()
        if order.payment_term:
            due_date += timedelta(days=order.payment_term.days)
        else:
            due_date += timedelta(days=30)
        
        invoice = SupplierInvoice.objects.create(
            supplier_invoice_number=receipt.supplier_invoice_number or f"SI-{receipt.number}",
            supplier=order.supplier,
            purchase_order=order,
            invoice_date=date.today(),
            received_date=receipt.receipt_date,
            due_date=due_date,
            payment_term=order.payment_term,
            currency=order.currency,
            exchange_rate=order.exchange_rate,
            created_by=user
        )
        
        # Crear líneas
        for line in receipt.lines.all():
            order_line = line.order_line
            qty_to_invoice = line.quantity_accepted
            
            if qty_to_invoice > 0:
                SupplierInvoiceLine.objects.create(
                    invoice=invoice,
                    line_number=order_line.line_number,
                    product=order_line.product,
                    order_line=order_line,
                    description=order_line.description or order_line.product.name,
                    quantity=qty_to_invoice,
                    unit=order_line.unit,
                    unit_price=order_line.unit_price,
                    discount_percent=order_line.discount_percent,
                    tax=order_line.tax
                )
                
                # Actualizar cantidad facturada
                order_line.quantity_invoiced += qty_to_invoice
                order_line.save()
        
        # Calcular totales
        cls._calculate_invoice_totals(invoice)
        
        return invoice
    
    @classmethod
    def _calculate_invoice_totals(cls, invoice):
        """Calcula totales de factura."""
        lines = invoice.lines.all()
        
        subtotal = Decimal('0')
        discount = Decimal('0')
        tax = Decimal('0')
        
        for line in lines:
            line_subtotal = line.quantity * line.unit_price
            line_discount = line_subtotal * (line.discount_percent / 100)
            taxable = line_subtotal - line_discount
            line_tax = taxable * (line.tax.rate / 100 if line.tax else 0)
            
            line.discount_amount = line_discount
            line.tax_amount = line_tax
            line.line_total = taxable + line_tax
            line.save()
            
            subtotal += line_subtotal
            discount += line_discount
            tax += line_tax
        
        invoice.subtotal = subtotal
        invoice.discount_amount = discount
        invoice.tax_amount = tax
        invoice.total = subtotal - discount + tax
        invoice.save()
    
    @classmethod
    @transaction.atomic
    def approve_invoice(cls, invoice, user):
        """
        Aprueba factura de proveedor.
        
        Args:
            invoice: Factura
            user: Usuario
        """
        if invoice.status != 'validated':
            raise ValidationError(
                "Solo se pueden aprobar facturas validadas"
            )
        
        invoice.status = 'approved'
        invoice.approved_by = user
        invoice.approved_date = timezone.now()
        invoice.save()
    
    @classmethod
    @transaction.atomic
    def post_invoice(cls, invoice, user):
        """
        Contabiliza factura de proveedor.
        
        Args:
            invoice: Factura
            user: Usuario
        """
        from apps.finance.services import FinanceService
        
        if invoice.status not in ['validated', 'approved']:
            raise ValidationError(
                "Solo se pueden contabilizar facturas validadas o aprobadas"
            )
        
        # Crear asiento contable
        journal_entry = FinanceService.create_purchase_invoice_entry(
            invoice=invoice,
            user=user
        )
        
        invoice.status = 'approved'
        invoice.journal_entry = journal_entry
        invoice.save()
    
    # ====================================================
    # Pagos a Proveedores
    # ====================================================
    
    @classmethod
    @transaction.atomic
    def apply_payment(cls, payment, allocations: List[Dict]):
        """
        Aplica pago a facturas de proveedor.
        
        Args:
            payment: Pago
            allocations: Lista de asignaciones
        """
        from .models import SupplierPaymentAllocation, SupplierInvoice
        
        total_allocated = Decimal('0')
        
        for alloc in allocations:
            invoice = alloc['invoice']
            amount = alloc['amount']
            
            # Validar
            balance = invoice.total - invoice.amount_paid
            if amount > balance:
                raise ValidationError(
                    f"El monto excede el balance de {invoice.number}"
                )
            
            if total_allocated + amount > payment.amount:
                raise ValidationError("El total excede el monto del pago")
            
            # Crear asignación
            SupplierPaymentAllocation.objects.create(
                payment=payment,
                invoice=invoice,
                amount=amount
            )
            
            # Actualizar factura
            invoice.amount_paid += amount
            if invoice.amount_paid >= invoice.total:
                invoice.status = 'paid'
            else:
                invoice.status = 'partial'
            invoice.save()
            
            total_allocated += amount
        
        # Actualizar estado del pago
        payment.status = 'approved'
        payment.save()
    
    # ====================================================
    # Proveedores
    # ====================================================
    
    @classmethod
    def get_supplier_statement(
        cls,
        supplier,
        from_date: date,
        to_date: date
    ) -> Dict[str, Any]:
        """
        Genera estado de cuenta del proveedor.
        
        Args:
            supplier: Proveedor
            from_date: Fecha inicial
            to_date: Fecha final
            
        Returns:
            Estado de cuenta
        """
        from .models import SupplierInvoice, SupplierPayment
        
        # Balance inicial
        opening_invoices = SupplierInvoice.objects.filter(
            supplier=supplier,
            invoice_date__lt=from_date,
            status__in=['approved', 'partial']
        ).aggregate(total=Sum('total'))['total'] or Decimal('0')
        
        opening_payments = SupplierPayment.objects.filter(
            supplier=supplier,
            payment_date__lt=from_date,
            status__in=['approved', 'cleared']
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        opening_balance = opening_invoices - opening_payments
        
        # Transacciones del período
        invoices = SupplierInvoice.objects.filter(
            supplier=supplier,
            invoice_date__range=[from_date, to_date]
        ).order_by('invoice_date')
        
        payments = SupplierPayment.objects.filter(
            supplier=supplier,
            payment_date__range=[from_date, to_date],
            status__in=['approved', 'cleared']
        ).order_by('payment_date')
        
        transactions = []
        running_balance = opening_balance
        
        for inv in invoices:
            running_balance += inv.total
            transactions.append({
                'date': inv.invoice_date,
                'type': 'invoice',
                'reference': inv.supplier_invoice_number,
                'debit': inv.total,
                'credit': Decimal('0'),
                'balance': running_balance
            })
        
        for pay in payments:
            running_balance -= pay.amount
            transactions.append({
                'date': pay.payment_date,
                'type': 'payment',
                'reference': pay.number,
                'debit': Decimal('0'),
                'credit': pay.amount,
                'balance': running_balance
            })
        
        # Ordenar por fecha
        transactions.sort(key=lambda x: x['date'])
        
        # Recalcular balance acumulado
        running_balance = opening_balance
        for txn in transactions:
            running_balance += txn['debit'] - txn['credit']
            txn['balance'] = running_balance
        
        # Totales
        total_invoiced = sum(t['debit'] for t in transactions)
        total_paid = sum(t['credit'] for t in transactions)
        
        # Antigüedad
        aging = cls.get_supplier_aging(supplier)
        
        return {
            'supplier': {
                'id': supplier.id,
                'code': supplier.code,
                'name': supplier.name
            },
            'from_date': from_date,
            'to_date': to_date,
            'opening_balance': opening_balance,
            'total_invoiced': total_invoiced,
            'total_paid': total_paid,
            'closing_balance': running_balance,
            'transactions': transactions,
            'aging': aging
        }
    
    @classmethod
    def get_supplier_aging(cls, supplier) -> Dict[str, Decimal]:
        """
        Calcula antigüedad de saldos del proveedor.
        
        Args:
            supplier: Proveedor
            
        Returns:
            Dict con rangos de antigüedad
        """
        from .models import SupplierInvoice
        
        today = date.today()
        
        aging = {
            'current': Decimal('0'),
            '1_30': Decimal('0'),
            '31_60': Decimal('0'),
            '61_90': Decimal('0'),
            'over_90': Decimal('0'),
            'total': Decimal('0')
        }
        
        invoices = SupplierInvoice.objects.filter(
            supplier=supplier,
            status__in=['approved', 'partial']
        )
        
        for inv in invoices:
            balance = inv.total - inv.amount_paid
            days_overdue = (today - inv.due_date).days
            
            if days_overdue <= 0:
                aging['current'] += balance
            elif days_overdue <= 30:
                aging['1_30'] += balance
            elif days_overdue <= 60:
                aging['31_60'] += balance
            elif days_overdue <= 90:
                aging['61_90'] += balance
            else:
                aging['over_90'] += balance
            
            aging['total'] += balance
        
        return aging
    
    # ====================================================
    # Reportes
    # ====================================================
    
    @classmethod
    def get_purchase_summary(
        cls,
        from_date: date,
        to_date: date,
        warehouse=None
    ) -> Dict[str, Any]:
        """
        Genera resumen de compras.
        
        Args:
            from_date: Fecha inicial
            to_date: Fecha final
            warehouse: Almacén (opcional)
            
        Returns:
            Resumen de compras
        """
        from .models import PurchaseOrder, SupplierInvoice, SupplierPayment
        
        # Filtros
        order_filter = Q(order_date__range=[from_date, to_date])
        invoice_filter = Q(invoice_date__range=[from_date, to_date])
        payment_filter = Q(payment_date__range=[from_date, to_date])
        
        if warehouse:
            order_filter &= Q(warehouse=warehouse)
        
        # Totales
        orders = PurchaseOrder.objects.filter(order_filter).exclude(
            status='cancelled'
        )
        invoices = SupplierInvoice.objects.filter(invoice_filter)
        payments = SupplierPayment.objects.filter(
            payment_filter,
            status__in=['approved', 'cleared']
        )
        
        total_orders = orders.count()
        total_order_value = orders.aggregate(
            total=Sum('total')
        )['total'] or Decimal('0')
        
        total_invoiced = invoices.aggregate(
            total=Sum('total')
        )['total'] or Decimal('0')
        
        total_paid = payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        pending = SupplierInvoice.objects.filter(
            status__in=['approved', 'partial']
        ).aggregate(
            total=Sum('total'),
            paid=Sum('amount_paid')
        )
        pending_payment = (
            (pending['total'] or Decimal('0')) -
            (pending['paid'] or Decimal('0'))
        )
        
        # Por proveedor
        by_supplier = list(orders.values(
            'supplier__code',
            'supplier__name'
        ).annotate(
            total_orders=Count('id'),
            total_value=Sum('total')
        ).order_by('-total_value')[:10])
        
        # Por categoría
        by_category = list(orders.values(
            'supplier__category__name'
        ).annotate(
            total_orders=Count('id'),
            total_value=Sum('total')
        ).order_by('-total_value'))
        
        # Top productos
        from .models import PurchaseOrderLine
        top_products = list(PurchaseOrderLine.objects.filter(
            order__in=orders
        ).values(
            'product__name',
            'product__sku'
        ).annotate(
            quantity_purchased=Sum('quantity'),
            total_value=Sum('line_total')
        ).order_by('-total_value')[:10])
        
        return {
            'period': f"{from_date} - {to_date}",
            'total_orders': total_orders,
            'total_order_value': total_order_value,
            'total_invoiced': total_invoiced,
            'total_paid': total_paid,
            'pending_payment': pending_payment,
            'by_supplier': by_supplier,
            'by_category': by_category,
            'top_products': top_products
        }
    
    @classmethod
    def get_pending_orders(cls, supplier=None) -> List[Any]:
        """
        Obtiene órdenes de compra pendientes.
        
        Args:
            supplier: Proveedor específico (opcional)
            
        Returns:
            Lista de órdenes pendientes
        """
        from .models import PurchaseOrder
        
        query = PurchaseOrder.objects.filter(
            status__in=['confirmed', 'partial']
        ).select_related('supplier')
        
        if supplier:
            query = query.filter(supplier=supplier)
        
        return query.order_by('required_date')
    
    @classmethod
    def get_overdue_invoices(
        cls,
        days_overdue: int = 0,
        supplier=None
    ) -> List[Any]:
        """
        Obtiene facturas vencidas.
        
        Args:
            days_overdue: Días de mora mínimos
            supplier: Proveedor específico
            
        Returns:
            Lista de facturas vencidas
        """
        from .models import SupplierInvoice
        
        cutoff_date = date.today() - timedelta(days=days_overdue)
        
        query = SupplierInvoice.objects.filter(
            due_date__lte=cutoff_date,
            status__in=['approved', 'partial']
        ).select_related('supplier')
        
        if supplier:
            query = query.filter(supplier=supplier)
        
        return query.order_by('due_date')
    
    @classmethod
    def suggest_supplier_for_product(cls, product) -> List[Dict]:
        """
        Sugiere proveedores para un producto.
        
        Args:
            product: Producto
            
        Returns:
            Lista de proveedores sugeridos con precios
        """
        from .models import SupplierProduct
        
        suppliers = SupplierProduct.objects.filter(
            product=product,
            is_active=True,
            supplier__is_active=True,
            supplier__status='active'
        ).select_related('supplier').order_by(
            '-is_preferred', 'unit_price', 'lead_time_days'
        )
        
        return [
            {
                'supplier': sp.supplier,
                'unit_price': sp.unit_price,
                'min_order_quantity': sp.min_order_quantity,
                'lead_time_days': sp.lead_time_days,
                'is_preferred': sp.is_preferred,
                'last_purchase_date': sp.last_purchase_date,
                'last_purchase_price': sp.last_purchase_price,
                'rating': sp.supplier.rating
            }
            for sp in suppliers
        ]
