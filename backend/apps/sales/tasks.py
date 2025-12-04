# ========================================================
# SISTEMA ERP UNIVERSAL - Tareas Celery de Ventas
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Tareas asíncronas para el módulo de ventas.
# ========================================================

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import date, timedelta
from decimal import Decimal

import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_quotation_email(self, quotation_id: int):
    """
    Envía cotización por email al cliente.
    
    Args:
        quotation_id: ID de la cotización
    """
    try:
        from .models import Quotation
        
        quotation = Quotation.objects.select_related(
            'customer', 'sales_rep'
        ).get(id=quotation_id)
        
        if not quotation.customer.email:
            logger.warning(
                f"Cliente {quotation.customer.code} sin email configurado"
            )
            return
        
        subject = f"Cotización {quotation.number}"
        message = f"""
Estimado {quotation.customer.contact_name or quotation.customer.name},

Adjunto encontrará la cotización {quotation.number} por un total de {quotation.currency} {quotation.total:,.2f}.

Esta cotización es válida hasta {quotation.valid_until}.

Líneas:
"""
        for line in quotation.lines.all():
            message += f"- {line.description}: {line.quantity} x {line.unit_price:,.2f} = {line.line_total:,.2f}\n"
        
        message += f"""
Subtotal: {quotation.subtotal:,.2f}
Impuestos: {quotation.tax_amount:,.2f}
Total: {quotation.total:,.2f}

Para cualquier consulta, no dude en contactarnos.

Atentamente,
{quotation.sales_rep.user.get_full_name() if quotation.sales_rep else 'Equipo de Ventas'}
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[quotation.customer.email],
            fail_silently=False
        )
        
        logger.info(f"Cotización {quotation.number} enviada a {quotation.customer.email}")
        
    except Exception as exc:
        logger.error(f"Error enviando cotización: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_invoice_email(self, invoice_id: int):
    """
    Envía factura por email al cliente.
    
    Args:
        invoice_id: ID de la factura
    """
    try:
        from .models import Invoice
        
        invoice = Invoice.objects.select_related('customer').get(id=invoice_id)
        
        if not invoice.customer.email:
            logger.warning(
                f"Cliente {invoice.customer.code} sin email configurado"
            )
            return
        
        subject = f"Factura {invoice.number}"
        message = f"""
Estimado {invoice.customer.contact_name or invoice.customer.name},

Adjunto encontrará la factura {invoice.number} por un total de {invoice.currency} {invoice.total:,.2f}.

Fecha de vencimiento: {invoice.due_date}

Forma de pago: {invoice.payment_term.name if invoice.payment_term else 'Según acuerdo'}

Para cualquier consulta sobre esta factura, no dude en contactarnos.

Atentamente,
Departamento de Cobranzas
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invoice.customer.email],
            fail_silently=False
        )
        
        logger.info(f"Factura {invoice.number} enviada a {invoice.customer.email}")
        
    except Exception as exc:
        logger.error(f"Error enviando factura: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def check_quotation_expiry():
    """
    Verifica cotizaciones próximas a vencer y notifica.
    """
    from .models import Quotation
    
    # Cotizaciones que vencen en los próximos 3 días
    warning_date = date.today() + timedelta(days=3)
    
    expiring = Quotation.objects.filter(
        status='sent',
        valid_until__lte=warning_date,
        valid_until__gte=date.today()
    ).select_related('customer', 'sales_rep')
    
    for quotation in expiring:
        # Notificar al vendedor
        if quotation.sales_rep and quotation.sales_rep.user.email:
            send_mail(
                subject=f"Cotización {quotation.number} próxima a vencer",
                message=f"""
La cotización {quotation.number} para {quotation.customer.name} 
vencerá el {quotation.valid_until}.

Total: {quotation.currency} {quotation.total:,.2f}

Por favor, haga seguimiento con el cliente.
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[quotation.sales_rep.user.email],
                fail_silently=True
            )
    
    # Marcar como vencidas las expiradas
    Quotation.objects.filter(
        status='sent',
        valid_until__lt=date.today()
    ).update(status='expired')
    
    logger.info(f"Verificación de vencimiento: {expiring.count()} cotizaciones próximas a vencer")


@shared_task
def check_overdue_invoices():
    """
    Verifica facturas vencidas y envía recordatorios.
    """
    from .models import Invoice
    
    today = date.today()
    
    # Facturas vencidas sin pago
    overdue = Invoice.objects.filter(
        status__in=['pending', 'partial'],
        due_date__lt=today
    ).select_related('customer')
    
    # Agrupar por días de mora
    reminder_1_day = []  # 1 día de mora
    reminder_7_days = []  # 7 días de mora
    reminder_30_days = []  # 30 días de mora
    
    for invoice in overdue:
        days_overdue = (today - invoice.due_date).days
        balance = invoice.total - invoice.amount_paid
        
        if days_overdue == 1:
            reminder_1_day.append((invoice, balance, days_overdue))
        elif days_overdue == 7:
            reminder_7_days.append((invoice, balance, days_overdue))
        elif days_overdue == 30:
            reminder_30_days.append((invoice, balance, days_overdue))
    
    # Enviar recordatorios
    for invoice, balance, days in reminder_1_day + reminder_7_days + reminder_30_days:
        if invoice.customer.email:
            urgency = "URGENTE: " if days >= 30 else ""
            send_mail(
                subject=f"{urgency}Recordatorio de pago - Factura {invoice.number}",
                message=f"""
Estimado {invoice.customer.name},

Le recordamos que la factura {invoice.number} con vencimiento 
{invoice.due_date} tiene un saldo pendiente de {invoice.currency} {balance:,.2f}.

Días de mora: {days}

Por favor, proceda con el pago a la brevedad posible.

Atentamente,
Departamento de Cobranzas
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invoice.customer.email],
                fail_silently=True
            )
    
    logger.info(
        f"Recordatorios enviados: 1 día={len(reminder_1_day)}, "
        f"7 días={len(reminder_7_days)}, 30 días={len(reminder_30_days)}"
    )


@shared_task
def generate_daily_sales_report():
    """
    Genera reporte diario de ventas.
    """
    from .models import SalesOrder, Invoice, Payment
    from .services import SalesService
    
    yesterday = date.today() - timedelta(days=1)
    
    # Órdenes del día
    orders = SalesOrder.objects.filter(
        order_date=yesterday
    ).exclude(status='cancelled')
    
    # Facturas del día
    invoices = Invoice.objects.filter(invoice_date=yesterday)
    
    # Pagos del día
    payments = Payment.objects.filter(
        payment_date=yesterday,
        status='confirmed'
    )
    
    # Totales
    order_total = sum(o.total for o in orders)
    invoice_total = sum(i.total for i in invoices)
    payment_total = sum(p.amount for p in payments)
    
    report = f"""
REPORTE DIARIO DE VENTAS - {yesterday}
{'='*50}

ÓRDENES DE VENTA
- Cantidad: {orders.count()}
- Total: ${order_total:,.2f}

FACTURAS EMITIDAS
- Cantidad: {invoices.count()}
- Total: ${invoice_total:,.2f}

PAGOS RECIBIDOS
- Cantidad: {payments.count()}
- Total: ${payment_total:,.2f}

DETALLE DE ÓRDENES:
"""
    
    for order in orders:
        report += f"  - {order.number}: {order.customer.name} - ${order.total:,.2f}\n"
    
    # Enviar reporte
    send_mail(
        subject=f"Reporte Diario de Ventas - {yesterday}",
        message=report,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.SALES_REPORT_EMAIL] if hasattr(settings, 'SALES_REPORT_EMAIL') else [],
        fail_silently=True
    )
    
    logger.info(f"Reporte diario generado para {yesterday}")


@shared_task
def sync_customer_balances():
    """
    Sincroniza saldos de crédito de clientes.
    """
    from .models import Customer, Invoice
    from django.db.models import Sum
    
    customers = Customer.objects.all()
    updated = 0
    
    for customer in customers:
        # Calcular crédito usado basado en facturas pendientes
        pending = Invoice.objects.filter(
            customer=customer,
            status__in=['pending', 'partial']
        ).aggregate(
            total=Sum('total'),
            paid=Sum('amount_paid')
        )
        
        credit_used = (pending['total'] or Decimal('0')) - (pending['paid'] or Decimal('0'))
        
        if customer.credit_used != credit_used:
            customer.credit_used = credit_used
            customer.save(update_fields=['credit_used'])
            updated += 1
    
    logger.info(f"Sincronización de saldos: {updated} clientes actualizados")


@shared_task
def process_recurring_orders():
    """
    Procesa órdenes recurrentes programadas.
    """
    # TODO: Implementar lógica de órdenes recurrentes
    logger.info("Procesamiento de órdenes recurrentes ejecutado")


@shared_task
def update_price_lists():
    """
    Actualiza listas de precios basado en reglas configuradas.
    """
    from .models import PriceList
    
    today = date.today()
    
    # Desactivar listas expiradas
    expired = PriceList.objects.filter(
        is_active=True,
        valid_until__lt=today
    ).update(is_active=False)
    
    # Activar listas que inician hoy
    activated = PriceList.objects.filter(
        is_active=False,
        valid_from=today,
        valid_until__gte=today
    ).update(is_active=True)
    
    logger.info(f"Listas de precios: {expired} expiradas, {activated} activadas")


@shared_task
def calculate_sales_commissions(period_start: str, period_end: str):
    """
    Calcula comisiones de ventas para un período.
    
    Args:
        period_start: Fecha inicio (ISO format)
        period_end: Fecha fin (ISO format)
    """
    from .models import SalesOrder, Invoice
    from apps.hr.models import Employee
    from django.db.models import Sum
    
    start_date = date.fromisoformat(period_start)
    end_date = date.fromisoformat(period_end)
    
    # Obtener facturas pagadas en el período
    invoices = Invoice.objects.filter(
        invoice_date__range=[start_date, end_date],
        status='paid'
    ).select_related('sales_order__sales_rep')
    
    commissions = {}
    
    for invoice in invoices:
        if invoice.sales_order and invoice.sales_order.sales_rep:
            rep = invoice.sales_order.sales_rep
            
            if rep.id not in commissions:
                commissions[rep.id] = {
                    'employee': rep,
                    'total_sales': Decimal('0'),
                    'commission_rate': Decimal('0.05'),  # 5% default
                    'commission_amount': Decimal('0')
                }
            
            commissions[rep.id]['total_sales'] += invoice.total
    
    # Calcular comisiones
    for rep_id, data in commissions.items():
        data['commission_amount'] = data['total_sales'] * data['commission_rate']
        
        # TODO: Crear registro de comisión en sistema de nómina
        logger.info(
            f"Comisión calculada para {data['employee'].user.get_full_name()}: "
            f"${data['commission_amount']:,.2f}"
        )
    
    logger.info(
        f"Comisiones calculadas: {len(commissions)} vendedores, "
        f"período {start_date} a {end_date}"
    )
    
    return commissions
