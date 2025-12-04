# ========================================================
# SISTEMA ERP UNIVERSAL - Tareas Asíncronas de Compras
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Tareas Celery para el módulo de compras.
# ========================================================

from celery import shared_task
from django.utils import timezone
from django.db.models import Sum, F, Q
from django.core.mail import send_mail
from django.conf import settings
from datetime import date, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


# ========================================================
# Tareas de Notificación
# ========================================================

@shared_task(bind=True, max_retries=3)
def send_overdue_invoice_alerts(self):
    """
    Envía alertas de facturas vencidas a proveedores.
    Se ejecuta diariamente.
    """
    from .models import SupplierInvoice
    
    try:
        today = date.today()
        overdue_invoices = SupplierInvoice.objects.filter(
            status__in=['approved', 'partial'],
            due_date__lt=today
        ).select_related('supplier')
        
        alerts_sent = 0
        
        for invoice in overdue_invoices:
            days_overdue = (today - invoice.due_date).days
            balance = invoice.total - invoice.amount_paid
            
            # Enviar alerta solo cada ciertos días
            if days_overdue in [1, 7, 15, 30]:
                try:
                    # Aquí iría la lógica de envío de correo
                    logger.info(
                        f"Alerta de factura vencida: {invoice.number} - "
                        f"{invoice.supplier.name} - {days_overdue} días - ${balance}"
                    )
                    alerts_sent += 1
                except Exception as e:
                    logger.error(f"Error enviando alerta para factura {invoice.number}: {e}")
        
        return {'alerts_sent': alerts_sent}
    
    except Exception as e:
        logger.error(f"Error en send_overdue_invoice_alerts: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_order_reminder_to_supplier(self, order_id):
    """
    Envía recordatorio de orden de compra a proveedor.
    """
    from .models import PurchaseOrder
    
    try:
        order = PurchaseOrder.objects.select_related('supplier').get(id=order_id)
        
        if order.status == 'sent':
            # Enviar email al proveedor
            subject = f"Recordatorio: Orden de Compra {order.number}"
            message = f"""
            Estimado {order.supplier.name},
            
            Le recordamos que tiene una orden de compra pendiente de confirmación:
            
            Número: {order.number}
            Fecha: {order.order_date}
            Total: ${order.total}
            Fecha requerida: {order.required_date or 'No especificada'}
            
            Por favor, confirme la recepción y fecha estimada de entrega.
            
            Saludos,
            Departamento de Compras
            """
            
            if order.supplier.email:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [order.supplier.email],
                    fail_silently=True
                )
                logger.info(f"Recordatorio enviado para orden {order.number}")
            
            return {'order_id': order_id, 'status': 'sent'}
        
        return {'order_id': order_id, 'status': 'skipped', 'reason': 'Order not in sent status'}
    
    except PurchaseOrder.DoesNotExist:
        logger.error(f"Orden de compra no encontrada: {order_id}")
        return {'order_id': order_id, 'status': 'error', 'reason': 'Order not found'}
    except Exception as e:
        logger.error(f"Error en send_order_reminder_to_supplier: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_requisition_approval_notification(self, requisition_id):
    """
    Envía notificación de solicitud pendiente de aprobación.
    """
    from .models import PurchaseRequisition
    
    try:
        requisition = PurchaseRequisition.objects.select_related(
            'requested_by', 'department'
        ).get(id=requisition_id)
        
        if requisition.status == 'submitted':
            # Notificar a los aprobadores
            logger.info(
                f"Notificación de aprobación: Solicitud {requisition.number} "
                f"del departamento {requisition.department.name if requisition.department else 'N/A'}"
            )
            
            return {'requisition_id': requisition_id, 'status': 'notified'}
        
        return {'requisition_id': requisition_id, 'status': 'skipped'}
    
    except PurchaseRequisition.DoesNotExist:
        return {'requisition_id': requisition_id, 'status': 'error'}
    except Exception as e:
        logger.error(f"Error en send_requisition_approval_notification: {e}")
        raise self.retry(exc=e, countdown=60)


# ========================================================
# Tareas de Procesamiento
# ========================================================

@shared_task(bind=True, max_retries=3)
def process_scheduled_orders(self):
    """
    Procesa órdenes de compra programadas.
    Se ejecuta diariamente.
    """
    from .models import PurchaseOrder
    
    try:
        today = date.today()
        
        # Buscar órdenes programadas para hoy
        orders = PurchaseOrder.objects.filter(
            status='approved',
            required_date=today
        )
        
        processed = 0
        
        for order in orders:
            try:
                # Enviar al proveedor
                order.status = 'sent'
                order.sent_date = timezone.now()
                order.save()
                
                # Enviar email
                send_order_reminder_to_supplier.delay(order.id)
                
                processed += 1
                logger.info(f"Orden {order.number} enviada automáticamente")
                
            except Exception as e:
                logger.error(f"Error procesando orden {order.number}: {e}")
        
        return {'orders_processed': processed}
    
    except Exception as e:
        logger.error(f"Error en process_scheduled_orders: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def update_supplier_ratings(self):
    """
    Actualiza calificaciones de proveedores basado en evaluaciones.
    Se ejecuta semanalmente.
    """
    from .models import Supplier, SupplierEvaluation
    from django.db.models import Avg
    
    try:
        updated = 0
        
        suppliers = Supplier.objects.filter(is_active=True)
        
        for supplier in suppliers:
            # Calcular promedio de últimas evaluaciones (máximo 12 meses)
            one_year_ago = date.today() - timedelta(days=365)
            
            avg_rating = SupplierEvaluation.objects.filter(
                supplier=supplier,
                evaluation_date__gte=one_year_ago
            ).aggregate(
                avg=Avg('overall_rating')
            )['avg']
            
            if avg_rating:
                supplier.rating = round(avg_rating, 2)
                supplier.save(update_fields=['rating'])
                updated += 1
        
        logger.info(f"Calificaciones actualizadas para {updated} proveedores")
        return {'suppliers_updated': updated}
    
    except Exception as e:
        logger.error(f"Error en update_supplier_ratings: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def check_reorder_points(self):
    """
    Verifica puntos de reorden y genera solicitudes automáticas.
    Se ejecuta diariamente.
    """
    from apps.inventory.models import Product, ProductWarehouse
    from .models import PurchaseRequisition, PurchaseRequisitionLine
    from apps.core.models import Company
    
    try:
        # Buscar productos bajo punto de reorden
        low_stock = ProductWarehouse.objects.filter(
            quantity__lte=F('reorder_point'),
            product__is_active=True,
            warehouse__is_active=True
        ).select_related('product', 'warehouse')
        
        requisitions_created = 0
        
        # Agrupar por almacén
        warehouse_products = {}
        for pw in low_stock:
            wh_id = pw.warehouse_id
            if wh_id not in warehouse_products:
                warehouse_products[wh_id] = {
                    'warehouse': pw.warehouse,
                    'products': []
                }
            warehouse_products[wh_id]['products'].append(pw)
        
        for wh_id, data in warehouse_products.items():
            try:
                # Generar número de solicitud
                from apps.core.utils import generate_document_number
                company = Company.objects.first()
                
                requisition = PurchaseRequisition.objects.create(
                    company=company,
                    number=generate_document_number('REQ'),
                    date=date.today(),
                    required_date=date.today() + timedelta(days=7),
                    warehouse=data['warehouse'],
                    status='draft',
                    notes='Generada automáticamente por punto de reorden'
                )
                
                for pw in data['products']:
                    qty_needed = max(0, pw.reorder_point - pw.quantity) + pw.reorder_quantity
                    
                    PurchaseRequisitionLine.objects.create(
                        requisition=requisition,
                        product=pw.product,
                        quantity=qty_needed,
                        unit=pw.product.unit,
                        notes=f'Stock actual: {pw.quantity}, Punto reorden: {pw.reorder_point}'
                    )
                
                requisitions_created += 1
                logger.info(
                    f"Solicitud {requisition.number} creada para almacén {data['warehouse'].name}"
                )
                
            except Exception as e:
                logger.error(f"Error creando solicitud para almacén {wh_id}: {e}")
        
        return {'requisitions_created': requisitions_created}
    
    except Exception as e:
        logger.error(f"Error en check_reorder_points: {e}")
        raise self.retry(exc=e, countdown=60)


# ========================================================
# Tareas de Reportes
# ========================================================

@shared_task(bind=True, max_retries=3)
def generate_purchasing_report(self, report_type='daily', email_to=None):
    """
    Genera reportes de compras.
    """
    from .models import PurchaseOrder, SupplierInvoice, SupplierPayment
    
    try:
        today = date.today()
        
        if report_type == 'daily':
            from_date = today
        elif report_type == 'weekly':
            from_date = today - timedelta(days=7)
        elif report_type == 'monthly':
            from_date = today.replace(day=1)
        else:
            from_date = today - timedelta(days=30)
        
        # Recopilar datos
        orders = PurchaseOrder.objects.filter(
            order_date__range=[from_date, today]
        ).aggregate(
            total_orders=Sum('id'),
            total_amount=Sum('total')
        )
        
        invoices = SupplierInvoice.objects.filter(
            invoice_date__range=[from_date, today]
        ).aggregate(
            total_invoices=Sum('id'),
            total_amount=Sum('total')
        )
        
        payments = SupplierPayment.objects.filter(
            payment_date__range=[from_date, today],
            status='approved'
        ).aggregate(
            total_payments=Sum('id'),
            total_amount=Sum('amount')
        )
        
        report_data = {
            'report_type': report_type,
            'from_date': from_date.isoformat(),
            'to_date': today.isoformat(),
            'orders': orders,
            'invoices': invoices,
            'payments': payments
        }
        
        logger.info(f"Reporte de compras {report_type} generado")
        
        if email_to:
            # Enviar por correo
            subject = f"Reporte de Compras - {report_type.capitalize()}"
            message = f"""
            Reporte de Compras
            Período: {from_date} a {today}
            
            Órdenes de Compra:
            - Cantidad: {orders['total_orders'] or 0}
            - Total: ${orders['total_amount'] or 0}
            
            Facturas de Proveedor:
            - Cantidad: {invoices['total_invoices'] or 0}
            - Total: ${invoices['total_amount'] or 0}
            
            Pagos Realizados:
            - Cantidad: {payments['total_payments'] or 0}
            - Total: ${payments['total_amount'] or 0}
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email_to],
                fail_silently=True
            )
        
        return report_data
    
    except Exception as e:
        logger.error(f"Error en generate_purchasing_report: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def generate_supplier_analysis(self):
    """
    Genera análisis de proveedores (ABC, rendimiento).
    Se ejecuta mensualmente.
    """
    from .models import Supplier, PurchaseOrder
    from django.db.models import Sum, Count
    
    try:
        # Análisis ABC de proveedores
        one_year_ago = date.today() - timedelta(days=365)
        
        suppliers_data = PurchaseOrder.objects.filter(
            order_date__gte=one_year_ago,
            status__in=['received', 'invoiced', 'completed']
        ).values('supplier_id').annotate(
            total=Sum('total'),
            orders=Count('id')
        ).order_by('-total')
        
        total_purchases = sum(s['total'] or 0 for s in suppliers_data)
        
        cumulative = Decimal('0')
        classification = {'A': [], 'B': [], 'C': []}
        
        for supplier in suppliers_data:
            if total_purchases > 0:
                cumulative += (supplier['total'] or 0)
                percentage = (cumulative / total_purchases) * 100
                
                if percentage <= 80:
                    classification['A'].append(supplier['supplier_id'])
                elif percentage <= 95:
                    classification['B'].append(supplier['supplier_id'])
                else:
                    classification['C'].append(supplier['supplier_id'])
        
        # Actualizar clasificación en proveedores
        Supplier.objects.filter(id__in=classification['A']).update(
            classification='A'
        )
        Supplier.objects.filter(id__in=classification['B']).update(
            classification='B'
        )
        Supplier.objects.filter(id__in=classification['C']).update(
            classification='C'
        )
        
        result = {
            'total_purchases': str(total_purchases),
            'suppliers_class_A': len(classification['A']),
            'suppliers_class_B': len(classification['B']),
            'suppliers_class_C': len(classification['C'])
        }
        
        logger.info(f"Análisis ABC de proveedores completado: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Error en generate_supplier_analysis: {e}")
        raise self.retry(exc=e, countdown=60)


# ========================================================
# Tareas de Sincronización
# ========================================================

@shared_task(bind=True, max_retries=3)
def sync_supplier_prices(self, supplier_id=None):
    """
    Sincroniza precios con proveedores externos (si tienen integración).
    """
    from .models import Supplier, SupplierProduct
    
    try:
        if supplier_id:
            suppliers = Supplier.objects.filter(id=supplier_id)
        else:
            # Solo proveedores con integración activa
            suppliers = Supplier.objects.filter(
                is_active=True,
                integration_enabled=True
            )
        
        updated = 0
        
        for supplier in suppliers:
            # Aquí iría la lógica de integración con el proveedor
            # (API, EDI, etc.)
            logger.info(f"Sincronizando precios con proveedor {supplier.name}")
            updated += 1
        
        return {'suppliers_synced': updated}
    
    except Exception as e:
        logger.error(f"Error en sync_supplier_prices: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def process_supplier_edi(self, supplier_id, document_type, data):
    """
    Procesa documentos EDI de proveedores.
    """
    try:
        # Implementación de procesamiento EDI
        logger.info(
            f"Procesando EDI {document_type} del proveedor {supplier_id}"
        )
        
        # Lógica según tipo de documento
        if document_type == 'ORDER_RESPONSE':
            # Procesar confirmación de orden
            pass
        elif document_type == 'SHIP_NOTICE':
            # Procesar aviso de embarque
            pass
        elif document_type == 'INVOICE':
            # Procesar factura electrónica
            pass
        
        return {'status': 'processed', 'document_type': document_type}
    
    except Exception as e:
        logger.error(f"Error en process_supplier_edi: {e}")
        raise self.retry(exc=e, countdown=60)


# ========================================================
# Tareas de Limpieza
# ========================================================

@shared_task(bind=True, max_retries=3)
def cleanup_old_requisitions(self, days=90):
    """
    Limpia solicitudes de compra antiguas en borrador.
    Se ejecuta mensualmente.
    """
    from .models import PurchaseRequisition
    
    try:
        cutoff_date = date.today() - timedelta(days=days)
        
        # Eliminar solicitudes en borrador más antiguas que el límite
        deleted, _ = PurchaseRequisition.objects.filter(
            status='draft',
            date__lt=cutoff_date
        ).delete()
        
        logger.info(f"Eliminadas {deleted} solicitudes de compra antiguas")
        return {'requisitions_deleted': deleted}
    
    except Exception as e:
        logger.error(f"Error en cleanup_old_requisitions: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def archive_completed_orders(self, days=365):
    """
    Archiva órdenes de compra completadas antiguas.
    Se ejecuta mensualmente.
    """
    from .models import PurchaseOrder
    
    try:
        cutoff_date = date.today() - timedelta(days=days)
        
        # Marcar como archivadas
        updated = PurchaseOrder.objects.filter(
            status='completed',
            order_date__lt=cutoff_date,
            is_archived=False
        ).update(is_archived=True)
        
        logger.info(f"Archivadas {updated} órdenes de compra")
        return {'orders_archived': updated}
    
    except Exception as e:
        logger.error(f"Error en archive_completed_orders: {e}")
        raise self.retry(exc=e, countdown=60)
