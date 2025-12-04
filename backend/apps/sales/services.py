# ========================================================
# SISTEMA ERP UNIVERSAL - Servicio de Ventas
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Lógica de negocio para el módulo de ventas.
# ========================================================

from decimal import Decimal
from datetime import date, timedelta
from typing import Dict, List, Optional, Any, Tuple

from django.db import transaction
from django.db.models import Sum, Count, Avg, F, Q
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.core.services import BaseService


class SalesService(BaseService):
    """Servicio para gestión de ventas."""
    
    # ====================================================
    # Gestión de Clientes
    # ====================================================
    
    @classmethod
    def check_customer_credit(
        cls,
        customer,
        amount: Decimal
    ) -> Tuple[bool, Decimal]:
        """
        Verifica crédito disponible del cliente.
        
        Args:
            customer: Cliente
            amount: Monto requerido
            
        Returns:
            Tuple con (aprobado, disponible)
        """
        available_credit = customer.credit_limit - customer.credit_used
        is_approved = amount <= available_credit
        return is_approved, available_credit
    
    @classmethod
    def update_customer_credit(
        cls,
        customer,
        amount: Decimal,
        operation: str = 'add'
    ):
        """
        Actualiza crédito usado del cliente.
        
        Args:
            customer: Cliente
            amount: Monto
            operation: 'add' o 'subtract'
        """
        if operation == 'add':
            customer.credit_used += amount
        else:
            customer.credit_used -= amount
            if customer.credit_used < 0:
                customer.credit_used = Decimal('0')
        customer.save(update_fields=['credit_used'])
    
    @classmethod
    def get_customer_statement(
        cls,
        customer,
        from_date: date,
        to_date: date
    ) -> Dict[str, Any]:
        """
        Genera estado de cuenta del cliente.
        
        Args:
            customer: Cliente
            from_date: Fecha inicial
            to_date: Fecha final
            
        Returns:
            Estado de cuenta
        """
        from .models import Invoice, Payment
        
        # Balance inicial (facturas anteriores no pagadas)
        opening_invoices = Invoice.objects.filter(
            customer=customer,
            invoice_date__lt=from_date,
            status__in=['pending', 'partial']
        ).aggregate(total=Sum('total'))['total'] or Decimal('0')
        
        opening_payments = Payment.objects.filter(
            customer=customer,
            payment_date__lt=from_date,
            status='confirmed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        opening_balance = opening_invoices - opening_payments
        
        # Transacciones del período
        invoices = Invoice.objects.filter(
            customer=customer,
            invoice_date__range=[from_date, to_date]
        ).order_by('invoice_date')
        
        payments = Payment.objects.filter(
            customer=customer,
            payment_date__range=[from_date, to_date],
            status='confirmed'
        ).order_by('payment_date')
        
        transactions = []
        running_balance = opening_balance
        
        # Combinar facturas y pagos
        for inv in invoices:
            running_balance += inv.total
            transactions.append({
                'date': inv.invoice_date,
                'type': 'invoice',
                'reference': inv.number,
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
        
        # Antigüedad de saldos
        aging = cls.get_customer_aging(customer)
        
        return {
            'customer': {
                'id': customer.id,
                'code': customer.code,
                'name': customer.name,
                'credit_limit': customer.credit_limit,
                'credit_used': customer.credit_used
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
    def get_customer_aging(cls, customer) -> Dict[str, Decimal]:
        """
        Calcula antigüedad de saldos del cliente.
        
        Args:
            customer: Cliente
            
        Returns:
            Dict con rangos de antigüedad
        """
        from .models import Invoice
        
        today = date.today()
        
        aging = {
            'current': Decimal('0'),
            '1_30': Decimal('0'),
            '31_60': Decimal('0'),
            '61_90': Decimal('0'),
            'over_90': Decimal('0'),
            'total': Decimal('0')
        }
        
        invoices = Invoice.objects.filter(
            customer=customer,
            status__in=['pending', 'partial']
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
    # Cotizaciones
    # ====================================================
    
    @classmethod
    @transaction.atomic
    def convert_quotation_to_order(cls, quotation, user) -> Any:
        """
        Convierte cotización a orden de venta.
        
        Args:
            quotation: Cotización
            user: Usuario
            
        Returns:
            Orden de venta creada
        """
        from .models import SalesOrder, SalesOrderLine
        
        if quotation.status != 'sent':
            raise ValidationError(
                "Solo se pueden convertir cotizaciones enviadas"
            )
        
        # Crear orden
        order = SalesOrder.objects.create(
            customer=quotation.customer,
            quotation=quotation,
            order_date=date.today(),
            sales_rep=quotation.sales_rep,
            payment_term=quotation.payment_term,
            currency=quotation.currency,
            exchange_rate=quotation.exchange_rate,
            subtotal=quotation.subtotal,
            discount_amount=quotation.discount_amount,
            tax_amount=quotation.tax_amount,
            total=quotation.total,
            notes=quotation.notes,
            created_by=user
        )
        
        # Copiar líneas
        for line in quotation.lines.all():
            SalesOrderLine.objects.create(
                order=order,
                line_number=line.line_number,
                product=line.product,
                description=line.description,
                quantity=line.quantity,
                unit=line.unit,
                unit_price=line.unit_price,
                discount_percent=line.discount_percent,
                discount_amount=line.discount_amount,
                tax=line.tax,
                tax_amount=line.tax_amount,
                line_total=line.line_total
            )
        
        # Actualizar cotización
        quotation.status = 'accepted'
        quotation.save()
        
        return order
    
    # ====================================================
    # Órdenes de Venta
    # ====================================================
    
    @classmethod
    @transaction.atomic
    def confirm_order(cls, order, user) -> bool:
        """
        Confirma una orden de venta.
        
        Args:
            order: Orden de venta
            user: Usuario
            
        Returns:
            True si se confirma
        """
        if order.status != 'draft':
            raise ValidationError("Solo se pueden confirmar órdenes en borrador")
        
        # Verificar crédito del cliente
        is_approved, available = cls.check_customer_credit(
            order.customer,
            order.total
        )
        
        if not is_approved:
            raise ValidationError(
                f"Crédito insuficiente. Disponible: {available}"
            )
        
        # Actualizar crédito usado
        cls.update_customer_credit(order.customer, order.total, 'add')
        
        # Actualizar estado
        order.status = 'confirmed'
        order.save()
        
        return True
    
    @classmethod
    @transaction.atomic
    def reserve_stock(cls, order) -> bool:
        """
        Reserva inventario para la orden.
        
        Args:
            order: Orden de venta
            
        Returns:
            True si se reserva todo
        """
        from apps.inventory.services import InventoryService
        
        all_reserved = True
        
        for line in order.lines.filter(status='pending'):
            pending_qty = line.quantity - line.quantity_reserved
            
            if pending_qty > 0:
                # Intentar reservar
                reserved = InventoryService.reserve_stock(
                    product=line.product,
                    warehouse=line.warehouse or order.warehouse,
                    quantity=pending_qty,
                    reference=f"SO-{order.number}-{line.line_number}"
                )
                
                line.quantity_reserved += reserved
                line.save()
                
                if reserved < pending_qty:
                    all_reserved = False
        
        if all_reserved:
            order.status = 'ready'
        else:
            order.status = 'partial'
        order.save()
        
        return all_reserved
    
    @classmethod
    @transaction.atomic
    def cancel_order(cls, order, reason: str, user):
        """
        Cancela una orden de venta.
        
        Args:
            order: Orden de venta
            reason: Motivo
            user: Usuario
        """
        if order.status in ['shipped', 'delivered', 'invoiced', 'cancelled']:
            raise ValidationError(
                "No se puede cancelar la orden en este estado"
            )
        
        # Liberar reservas
        for line in order.lines.all():
            if line.quantity_reserved > 0:
                from apps.inventory.services import InventoryService
                InventoryService.release_reservation(
                    product=line.product,
                    warehouse=line.warehouse or order.warehouse,
                    quantity=line.quantity_reserved,
                    reference=f"SO-{order.number}-{line.line_number}"
                )
        
        # Liberar crédito
        if order.status in ['confirmed', 'ready', 'partial', 'processing']:
            cls.update_customer_credit(order.customer, order.total, 'subtract')
        
        order.status = 'cancelled'
        order.notes = f"{order.notes or ''}\nCancelado: {reason}"
        order.save()
    
    # ====================================================
    # Envíos
    # ====================================================
    
    @classmethod
    @transaction.atomic
    def create_shipment(
        cls,
        order,
        lines_data: List[Dict],
        shipment_data: Dict,
        user
    ):
        """
        Crea envío para orden de venta.
        
        Args:
            order: Orden de venta
            lines_data: Líneas a enviar
            shipment_data: Datos del envío
            user: Usuario
            
        Returns:
            Envío creado
        """
        from .models import Shipment, ShipmentLine
        from apps.inventory.services import InventoryService
        
        # Crear envío
        shipment = Shipment.objects.create(
            sales_order=order,
            warehouse=shipment_data.get('warehouse', order.warehouse),
            shipping_address=shipment_data.get(
                'shipping_address',
                order.shipping_address
            ),
            carrier=shipment_data.get('carrier'),
            tracking_number=shipment_data.get('tracking_number'),
            total_weight=shipment_data.get('total_weight', Decimal('0')),
            total_packages=shipment_data.get('total_packages', 1),
            shipping_cost=shipment_data.get('shipping_cost', Decimal('0')),
            notes=shipment_data.get('notes'),
            created_by=user
        )
        
        # Crear líneas y descontar inventario
        for line_data in lines_data:
            order_line = line_data['order_line']
            quantity = line_data['quantity']
            
            # Validar cantidad
            available_to_ship = (
                order_line.quantity_reserved - order_line.quantity_shipped
            )
            if quantity > available_to_ship:
                raise ValidationError(
                    f"Cantidad excede lo reservado para {order_line.product}"
                )
            
            # Crear línea de envío
            ShipmentLine.objects.create(
                shipment=shipment,
                order_line=order_line,
                quantity=quantity,
                lot=line_data.get('lot'),
                serial_numbers=line_data.get('serial_numbers')
            )
            
            # Actualizar línea de orden
            order_line.quantity_shipped += quantity
            order_line.save()
            
            # Descontar inventario
            InventoryService.ship_stock(
                product=order_line.product,
                warehouse=shipment.warehouse,
                quantity=quantity,
                reference=f"SHIP-{shipment.number}"
            )
        
        # Actualizar estado de orden
        cls._update_order_status(order)
        
        return shipment
    
    @classmethod
    def confirm_delivery(cls, shipment, delivery_date: date = None):
        """
        Confirma entrega de envío.
        
        Args:
            shipment: Envío
            delivery_date: Fecha de entrega
        """
        if shipment.status not in ['pending', 'in_transit']:
            raise ValidationError("El envío no está en tránsito")
        
        shipment.status = 'delivered'
        shipment.actual_delivery = delivery_date or date.today()
        shipment.save()
        
        # Actualizar líneas de orden
        for line in shipment.lines.all():
            order_line = line.order_line
            order_line.quantity_delivered += line.quantity
            order_line.save()
        
        # Actualizar estado de orden
        cls._update_order_status(shipment.sales_order)
    
    @classmethod
    def _update_order_status(cls, order):
        """Actualiza estado de orden basado en líneas."""
        lines = order.lines.all()
        
        total_qty = sum(l.quantity for l in lines)
        shipped_qty = sum(l.quantity_shipped for l in lines)
        delivered_qty = sum(l.quantity_delivered for l in lines)
        
        if delivered_qty >= total_qty:
            order.status = 'delivered'
        elif shipped_qty >= total_qty:
            order.status = 'shipped'
        elif shipped_qty > 0:
            order.status = 'processing'
        
        order.save()
    
    # ====================================================
    # Facturación
    # ====================================================
    
    @classmethod
    @transaction.atomic
    def create_invoice_from_order(cls, order, user) -> Any:
        """
        Crea factura desde orden de venta.
        
        Args:
            order: Orden de venta
            user: Usuario
            
        Returns:
            Factura creada
        """
        from .models import Invoice, InvoiceLine
        
        if order.status not in ['shipped', 'delivered']:
            raise ValidationError(
                "Solo se pueden facturar órdenes enviadas o entregadas"
            )
        
        # Calcular fecha de vencimiento
        due_date = date.today()
        if order.payment_term:
            due_date += timedelta(days=order.payment_term.days)
        else:
            due_date += timedelta(days=30)
        
        # Crear factura
        invoice = Invoice.objects.create(
            customer=order.customer,
            sales_order=order,
            invoice_date=date.today(),
            due_date=due_date,
            payment_term=order.payment_term,
            currency=order.currency,
            exchange_rate=order.exchange_rate,
            subtotal=order.subtotal,
            discount_amount=order.discount_amount,
            tax_amount=order.tax_amount,
            total=order.total,
            billing_address=order.billing_address,
            notes=order.notes,
            created_by=user
        )
        
        # Crear líneas
        for line in order.lines.all():
            qty_to_invoice = line.quantity_delivered - line.quantity_invoiced
            
            if qty_to_invoice > 0:
                InvoiceLine.objects.create(
                    invoice=invoice,
                    line_number=line.line_number,
                    product=line.product,
                    sales_order_line=line,
                    description=line.description,
                    quantity=qty_to_invoice,
                    unit=line.unit,
                    unit_price=line.unit_price,
                    discount_percent=line.discount_percent,
                    discount_amount=line.discount_amount * (
                        qty_to_invoice / line.quantity
                    ),
                    tax=line.tax,
                    tax_amount=line.tax_amount * (
                        qty_to_invoice / line.quantity
                    ),
                    line_total=line.line_total * (
                        qty_to_invoice / line.quantity
                    )
                )
                
                # Actualizar cantidad facturada
                line.quantity_invoiced += qty_to_invoice
                line.save()
        
        # Actualizar crédito del cliente
        cls.update_customer_credit(order.customer, invoice.total, 'add')
        
        # Actualizar estado de orden
        order.status = 'invoiced'
        order.save()
        
        return invoice
    
    @classmethod
    @transaction.atomic
    def post_invoice(cls, invoice, user):
        """
        Contabiliza factura.
        
        Args:
            invoice: Factura
            user: Usuario
        """
        from apps.finance.services import FinanceService
        
        if invoice.status != 'draft':
            raise ValidationError("Solo se pueden contabilizar facturas en borrador")
        
        # Crear asiento contable
        journal_entry = FinanceService.create_sales_invoice_entry(
            invoice=invoice,
            user=user
        )
        
        invoice.status = 'posted'
        invoice.journal_entry = journal_entry
        invoice.save()
    
    @classmethod
    @transaction.atomic
    def apply_payment(
        cls,
        payment,
        allocations: List[Dict]
    ):
        """
        Aplica pago a facturas.
        
        Args:
            payment: Pago
            allocations: Lista de asignaciones
        """
        from .models import PaymentAllocation, Invoice
        
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
            PaymentAllocation.objects.create(
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
            
            # Liberar crédito
            cls.update_customer_credit(invoice.customer, amount, 'subtract')
            
            total_allocated += amount
        
        # Actualizar estado del pago
        if total_allocated >= payment.amount:
            payment.status = 'allocated'
        payment.save()
    
    # ====================================================
    # Precios
    # ====================================================
    
    @classmethod
    def get_product_price(
        cls,
        product,
        customer=None,
        quantity: Decimal = Decimal('1'),
        price_list=None
    ) -> Decimal:
        """
        Obtiene precio de producto para cliente.
        
        Args:
            product: Producto
            customer: Cliente (opcional)
            quantity: Cantidad
            price_list: Lista de precios específica
            
        Returns:
            Precio unitario
        """
        from .models import PriceList, PriceListItem, Promotion
        
        base_price = product.sale_price
        
        # Buscar lista de precios
        if price_list is None and customer:
            # Lista del cliente o grupo
            price_list = PriceList.objects.filter(
                Q(customers=customer) | Q(customer_groups=customer.group),
                is_active=True,
                valid_from__lte=date.today()
            ).filter(
                Q(valid_until__isnull=True) | Q(valid_until__gte=date.today())
            ).first()
        
        if price_list is None:
            # Lista por defecto
            price_list = PriceList.objects.filter(
                is_default=True,
                is_active=True
            ).first()
        
        if price_list:
            # Buscar precio en lista
            price_item = PriceListItem.objects.filter(
                price_list=price_list,
                product=product,
                min_quantity__lte=quantity
            ).order_by('-min_quantity').first()
            
            if price_item:
                if price_item.discount_percent > 0:
                    base_price = base_price * (
                        1 - price_item.discount_percent / 100
                    )
                else:
                    base_price = price_item.unit_price
        
        # Aplicar promociones activas
        promotions = Promotion.objects.filter(
            is_active=True,
            valid_from__lte=date.today()
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gte=date.today())
        ).filter(
            Q(products=product) | Q(categories=product.category)
        )
        
        for promo in promotions:
            if promo.usage_limit and promo.usage_count >= promo.usage_limit:
                continue
            
            if promo.promotion_type == 'percentage':
                discount = base_price * (promo.discount_value / 100)
                if promo.max_discount_amount:
                    discount = min(discount, promo.max_discount_amount)
                base_price -= discount
            elif promo.promotion_type == 'fixed':
                base_price -= promo.discount_value
        
        return max(base_price, Decimal('0'))
    
    # ====================================================
    # Reportes y Análisis
    # ====================================================
    
    @classmethod
    def get_sales_summary(
        cls,
        from_date: date,
        to_date: date,
        warehouse=None
    ) -> Dict[str, Any]:
        """
        Genera resumen de ventas.
        
        Args:
            from_date: Fecha inicial
            to_date: Fecha final
            warehouse: Almacén (opcional)
            
        Returns:
            Resumen de ventas
        """
        from .models import SalesOrder, Invoice, Payment
        
        # Filtros base
        order_filter = Q(order_date__range=[from_date, to_date])
        invoice_filter = Q(invoice_date__range=[from_date, to_date])
        payment_filter = Q(payment_date__range=[from_date, to_date])
        
        if warehouse:
            order_filter &= Q(warehouse=warehouse)
        
        # Totales
        orders = SalesOrder.objects.filter(order_filter).exclude(
            status='cancelled'
        )
        invoices = Invoice.objects.filter(invoice_filter)
        payments = Payment.objects.filter(
            payment_filter,
            status='confirmed'
        )
        
        total_orders = orders.count()
        total_order_value = orders.aggregate(
            total=Sum('total')
        )['total'] or Decimal('0')
        
        total_invoiced = invoices.aggregate(
            total=Sum('total')
        )['total'] or Decimal('0')
        
        total_collected = payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        avg_order_value = (
            total_order_value / total_orders if total_orders > 0
            else Decimal('0')
        )
        
        # Por vendedor
        by_sales_rep = list(orders.values(
            'sales_rep__user__first_name',
            'sales_rep__user__last_name'
        ).annotate(
            total_orders=Count('id'),
            total_value=Sum('total')
        ).order_by('-total_value')[:10])
        
        # Por grupo de cliente
        by_customer_group = list(orders.values(
            'customer__group__name'
        ).annotate(
            total_orders=Count('id'),
            total_value=Sum('total')
        ).order_by('-total_value'))
        
        # Top productos
        from .models import SalesOrderLine
        top_products = list(SalesOrderLine.objects.filter(
            order__in=orders
        ).values(
            'product__name',
            'product__sku'
        ).annotate(
            quantity_sold=Sum('quantity'),
            total_value=Sum('line_total')
        ).order_by('-total_value')[:10])
        
        # Top clientes
        top_customers = list(orders.values(
            'customer__code',
            'customer__name'
        ).annotate(
            total_orders=Count('id'),
            total_value=Sum('total')
        ).order_by('-total_value')[:10])
        
        return {
            'period': f"{from_date} - {to_date}",
            'total_orders': total_orders,
            'total_order_value': total_order_value,
            'total_invoiced': total_invoiced,
            'total_collected': total_collected,
            'average_order_value': avg_order_value,
            'collection_rate': (
                total_collected / total_invoiced * 100
                if total_invoiced > 0 else Decimal('0')
            ),
            'by_sales_rep': by_sales_rep,
            'by_customer_group': by_customer_group,
            'top_products': top_products,
            'top_customers': top_customers
        }
    
    @classmethod
    def get_sales_forecast(
        cls,
        months: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Genera pronóstico de ventas.
        
        Args:
            months: Meses a pronosticar
            
        Returns:
            Pronóstico
        """
        from .models import SalesOrder
        
        # Obtener histórico
        today = date.today()
        start_date = today - timedelta(days=365)
        
        historical = SalesOrder.objects.filter(
            order_date__range=[start_date, today],
            status__in=['delivered', 'invoiced']
        ).values(
            month=F('order_date__month'),
            year=F('order_date__year')
        ).annotate(
            total=Sum('total')
        ).order_by('year', 'month')
        
        # Calcular promedio móvil simple
        history = list(historical)
        if len(history) < 3:
            return []
        
        last_3_months = [h['total'] for h in history[-3:]]
        avg = sum(last_3_months) / 3
        
        # Generar pronóstico
        forecast = []
        current_month = today.month
        current_year = today.year
        
        for i in range(months):
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
            
            # Aplicar tendencia simple
            trend = 1 + (i * 0.02)  # 2% crecimiento mensual
            
            forecast.append({
                'year': current_year,
                'month': current_month,
                'forecast': avg * Decimal(str(trend)),
                'confidence_low': avg * Decimal(str(trend * 0.85)),
                'confidence_high': avg * Decimal(str(trend * 1.15))
            })
        
        return forecast
    
    @classmethod
    def get_overdue_invoices(
        cls,
        days_overdue: int = 0,
        customer=None
    ) -> List[Any]:
        """
        Obtiene facturas vencidas.
        
        Args:
            days_overdue: Días de mora mínimos
            customer: Cliente específico
            
        Returns:
            Lista de facturas vencidas
        """
        from .models import Invoice
        
        cutoff_date = date.today() - timedelta(days=days_overdue)
        
        query = Invoice.objects.filter(
            due_date__lte=cutoff_date,
            status__in=['pending', 'partial']
        ).select_related('customer')
        
        if customer:
            query = query.filter(customer=customer)
        
        return query.order_by('due_date')
