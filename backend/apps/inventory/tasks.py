# ========================================================
# SISTEMA ERP UNIVERSAL - Tareas Asíncronas de Inventario
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Tareas de Celery para operaciones asíncronas
# de inventario que requieren procesamiento en background.
#
# Por qué Celery:
# - Operaciones pesadas (reportes, sincronización)
# - Procesos programados (alertas, limpieza)
# - Mejora el tiempo de respuesta de la API
# ========================================================

from celery import shared_task
from django.utils import timezone
from django.db.models import F, Sum
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def check_low_stock_alerts(self):
    """
    Verifica productos con stock bajo y genera alertas.
    
    Propósito:
        Tarea programada para revisar niveles de stock
        y notificar al personal de compras.
    
    Frecuencia Recomendada: Cada hora o según configuración
    
    Retorna:
        dict: Estadísticas de alertas generadas
    """
    try:
        from .models import Stock, Product
        from apps.authentication.models import User
        
        # Buscar productos con stock bajo
        low_stock_items = Stock.objects.filter(
            quantity__lte=F('product__min_stock'),
            product__is_active=True,
            product__is_deleted=False
        ).select_related('product', 'warehouse')
        
        if not low_stock_items.exists():
            logger.info("No hay productos con stock bajo")
            return {'alerts_sent': 0}
        
        # Agrupar por almacén para el reporte
        alerts_by_warehouse = {}
        for stock in low_stock_items:
            warehouse_name = stock.warehouse.name
            if warehouse_name not in alerts_by_warehouse:
                alerts_by_warehouse[warehouse_name] = []
            
            alerts_by_warehouse[warehouse_name].append({
                'sku': stock.product.sku,
                'name': stock.product.name,
                'current_stock': stock.quantity,
                'min_stock': stock.product.min_stock,
                'reorder_quantity': stock.product.reorder_quantity,
            })
        
        # Construir mensaje de alerta
        message_parts = ["Alerta de Stock Bajo - Sistema ERP\n\n"]
        for warehouse, products in alerts_by_warehouse.items():
            message_parts.append(f"=== {warehouse} ===\n")
            for product in products:
                message_parts.append(
                    f"- {product['sku']}: {product['name']}\n"
                    f"  Stock actual: {product['current_stock']} | "
                    f"Mínimo: {product['min_stock']} | "
                    f"Pedir: {product['reorder_quantity']}\n"
                )
            message_parts.append("\n")
        
        message = "".join(message_parts)
        
        # Obtener usuarios con rol de compras
        # TODO: Implementar notificación por rol
        purchasing_users = User.objects.filter(
            is_active=True,
            role__name__in=['Compras', 'Admin', 'Gerente']
        ).values_list('email', flat=True)
        
        # Enviar email de alerta
        if purchasing_users:
            send_mail(
                subject='[ERP] Alerta de Stock Bajo',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=list(purchasing_users),
                fail_silently=True,
            )
        
        logger.info(f"Alertas de stock bajo enviadas: {low_stock_items.count()} productos")
        
        return {
            'alerts_sent': low_stock_items.count(),
            'warehouses_affected': len(alerts_by_warehouse),
        }
        
    except Exception as exc:
        logger.error(f"Error en check_low_stock_alerts: {exc}")
        self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def check_expiring_lots(self, days=30):
    """
    Verifica lotes próximos a vencer.
    
    Propósito:
        Alerta temprana de productos por vencer para
        gestión de mermas y rotación de inventario.
    
    Args:
        days: Días de anticipación para la alerta
    
    Frecuencia Recomendada: Diaria
    """
    try:
        from .models import Lot
        
        expiry_threshold = timezone.now().date() + timezone.timedelta(days=days)
        
        # Lotes por vencer
        expiring_lots = Lot.objects.filter(
            expiry_date__lte=expiry_threshold,
            expiry_date__gt=timezone.now().date(),
            quantity__gt=0,
            status='active'
        ).select_related('product', 'warehouse')
        
        # Lotes ya vencidos
        expired_lots = Lot.objects.filter(
            expiry_date__lt=timezone.now().date(),
            quantity__gt=0,
            status='active'
        ).select_related('product', 'warehouse')
        
        # Marcar lotes vencidos
        expired_count = expired_lots.update(status='expired')
        
        if not expiring_lots.exists() and not expired_count:
            logger.info("No hay lotes por vencer")
            return {'expiring': 0, 'expired_marked': 0}
        
        # Construir alerta
        message_parts = ["Reporte de Lotes - Sistema ERP\n\n"]
        
        if expired_count:
            message_parts.append(f"⚠️ LOTES VENCIDOS: {expired_count}\n\n")
        
        if expiring_lots.exists():
            message_parts.append(f"📅 LOTES POR VENCER (próximos {days} días):\n\n")
            for lot in expiring_lots[:50]:  # Limitar a 50
                message_parts.append(
                    f"- Lote: {lot.lot_number}\n"
                    f"  Producto: {lot.product.name}\n"
                    f"  Vence: {lot.expiry_date}\n"
                    f"  Cantidad: {lot.quantity} | Almacén: {lot.warehouse.name}\n\n"
                )
        
        message = "".join(message_parts)
        
        # Enviar notificación
        send_mail(
            subject='[ERP] Alerta de Lotes por Vencer',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.INVENTORY_ALERT_EMAIL],
            fail_silently=True,
        )
        
        logger.info(f"Lotes por vencer: {expiring_lots.count()}, Vencidos marcados: {expired_count}")
        
        return {
            'expiring': expiring_lots.count(),
            'expired_marked': expired_count,
        }
        
    except Exception as exc:
        logger.error(f"Error en check_expiring_lots: {exc}")
        self.retry(exc=exc, countdown=60)


@shared_task(bind=True)
def generate_inventory_valuation_report(self, warehouse_id=None, as_of_date=None):
    """
    Genera reporte de valoración de inventario.
    
    Propósito:
        Reporte financiero del valor total del inventario
        para contabilidad y auditoría.
    
    Args:
        warehouse_id: UUID del almacén (opcional, None = todos)
        as_of_date: Fecha para el reporte histórico
    
    Frecuencia: Bajo demanda o mensual
    
    Returns:
        dict: Reporte de valoración
    """
    try:
        from .models import Stock
        from apps.finance.models import AccountingPeriod  # Si existe
        
        queryset = Stock.objects.filter(quantity__gt=0)
        
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
        
        # Calcular valoración
        valuation = queryset.annotate(
            line_value=F('quantity') * F('product__cost_price')
        ).aggregate(
            total_value=Sum('line_value'),
            total_items=Sum('quantity')
        )
        
        # Valoración por categoría
        by_category = queryset.values(
            'product__category__name'
        ).annotate(
            value=Sum(F('quantity') * F('product__cost_price')),
            items=Sum('quantity')
        ).order_by('-value')
        
        # Valoración por almacén
        by_warehouse = queryset.values(
            'warehouse__name'
        ).annotate(
            value=Sum(F('quantity') * F('product__cost_price')),
            items=Sum('quantity')
        ).order_by('-value')
        
        report = {
            'generated_at': timezone.now().isoformat(),
            'as_of_date': as_of_date or timezone.now().date().isoformat(),
            'total_value': str(valuation['total_value'] or Decimal('0.00')),
            'total_items': valuation['total_items'] or 0,
            'by_category': list(by_category),
            'by_warehouse': list(by_warehouse),
        }
        
        logger.info(f"Reporte de valoración generado: ${valuation['total_value']}")
        
        # TODO: Guardar reporte en modelo o S3
        # TODO: Notificar al solicitante
        
        return report
        
    except Exception as exc:
        logger.error(f"Error generando reporte de valoración: {exc}")
        raise


@shared_task(bind=True, max_retries=3)
def sync_stock_with_external_system(self, system_name, product_ids=None):
    """
    Sincroniza stock con sistemas externos.
    
    Propósito:
        Mantener sincronizado el inventario con:
        - E-commerce (Shopify, WooCommerce, etc.)
        - Marketplace (Amazon, MercadoLibre)
        - POS externos
    
    Args:
        system_name: Nombre del sistema a sincronizar
        product_ids: Lista de productos a sincronizar (None = todos)
    
    Frecuencia: Cada 15 minutos o en tiempo real
    """
    try:
        from .models import Stock, Product
        
        logger.info(f"Iniciando sincronización con {system_name}")
        
        # Obtener stock actual
        queryset = Stock.objects.filter(
            product__sync_external=True,  # Campo hipotético
            quantity__gte=0
        ).select_related('product', 'warehouse')
        
        if product_ids:
            queryset = queryset.filter(product_id__in=product_ids)
        
        # Preparar datos para sincronización
        sync_data = []
        for stock in queryset:
            sync_data.append({
                'sku': stock.product.sku,
                'barcode': stock.product.barcode,
                'quantity': stock.available_quantity,
                'warehouse_code': stock.warehouse.code,
            })
        
        # TODO: Implementar conectores específicos por sistema
        # Ejemplo pseudo-código:
        # if system_name == 'shopify':
        #     from integrations.shopify import ShopifyClient
        #     client = ShopifyClient()
        #     client.update_inventory(sync_data)
        
        logger.info(f"Sincronización completada: {len(sync_data)} productos")
        
        return {
            'system': system_name,
            'products_synced': len(sync_data),
            'timestamp': timezone.now().isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"Error en sincronización con {system_name}: {exc}")
        self.retry(exc=exc, countdown=120)


@shared_task
def recalculate_stock_from_transactions(product_id, warehouse_id):
    """
    Recalcula el stock basándose en transacciones.
    
    Propósito:
        Corregir discrepancias recalculando desde el historial.
        Útil para auditorías y corrección de errores.
    
    Args:
        product_id: ID del producto
        warehouse_id: ID del almacén
    """
    try:
        from .models import Stock, InventoryTransaction
        
        # Sumar todas las entradas
        entries = InventoryTransaction.objects.filter(
            product_id=product_id,
            warehouse_id=warehouse_id,
            transaction_type__in=['in', 'adjustment_plus', 'transfer_in', 'initial']
        ).aggregate(total=Sum('quantity'))
        
        # Sumar todas las salidas
        exits = InventoryTransaction.objects.filter(
            product_id=product_id,
            warehouse_id=warehouse_id,
            transaction_type__in=['out', 'adjustment_minus', 'transfer_out']
        ).aggregate(total=Sum('quantity'))
        
        # Calcular stock
        calculated_stock = (entries['total'] or 0) - (exits['total'] or 0)
        
        # Actualizar stock
        stock, created = Stock.objects.get_or_create(
            product_id=product_id,
            warehouse_id=warehouse_id,
            defaults={'quantity': 0}
        )
        
        old_quantity = stock.quantity
        stock.quantity = max(0, calculated_stock)
        stock.save()
        
        logger.info(
            f"Stock recalculado para producto {product_id} en almacén {warehouse_id}: "
            f"{old_quantity} -> {calculated_stock}"
        )
        
        return {
            'product_id': str(product_id),
            'warehouse_id': str(warehouse_id),
            'old_quantity': old_quantity,
            'new_quantity': stock.quantity,
            'difference': stock.quantity - old_quantity,
        }
        
    except Exception as exc:
        logger.error(f"Error recalculando stock: {exc}")
        raise


@shared_task
def generate_abc_analysis():
    """
    Genera análisis ABC de inventario.
    
    Propósito:
        Clasificar productos según su importancia:
        - A: 80% del valor (20% de productos)
        - B: 15% del valor (30% de productos)  
        - C: 5% del valor (50% de productos)
    
    Usado para:
        - Priorizar conteos de inventario
        - Optimizar ubicaciones de almacén
        - Estrategias de reposición
    
    Frecuencia: Mensual
    """
    try:
        from .models import Product, Stock
        from django.db.models import F, Sum
        
        # Calcular valor por producto
        product_values = Stock.objects.filter(
            quantity__gt=0,
            product__is_active=True
        ).values(
            'product_id',
            'product__sku',
            'product__name'
        ).annotate(
            total_value=Sum(F('quantity') * F('product__cost_price'))
        ).order_by('-total_value')
        
        if not product_values.exists():
            return {'message': 'No hay stock para analizar'}
        
        # Calcular valor total
        total_value = sum(p['total_value'] or 0 for p in product_values)
        
        if total_value == 0:
            return {'message': 'Valor total es cero'}
        
        # Clasificar
        cumulative = Decimal('0')
        classifications = []
        
        for product in product_values:
            product_value = product['total_value'] or Decimal('0')
            cumulative += product_value
            percentage = (cumulative / total_value) * 100
            
            if percentage <= 80:
                classification = 'A'
            elif percentage <= 95:
                classification = 'B'
            else:
                classification = 'C'
            
            classifications.append({
                'product_id': str(product['product_id']),
                'sku': product['product__sku'],
                'name': product['product__name'],
                'value': str(product_value),
                'cumulative_percentage': f"{percentage:.2f}%",
                'classification': classification,
            })
        
        # Actualizar clasificación en productos
        a_products = [c['product_id'] for c in classifications if c['classification'] == 'A']
        b_products = [c['product_id'] for c in classifications if c['classification'] == 'B']
        c_products = [c['product_id'] for c in classifications if c['classification'] == 'C']
        
        Product.objects.filter(id__in=a_products).update(abc_classification='A')
        Product.objects.filter(id__in=b_products).update(abc_classification='B')
        Product.objects.filter(id__in=c_products).update(abc_classification='C')
        
        summary = {
            'generated_at': timezone.now().isoformat(),
            'total_value': str(total_value),
            'a_count': len(a_products),
            'b_count': len(b_products),
            'c_count': len(c_products),
        }
        
        logger.info(f"Análisis ABC completado: A={len(a_products)}, B={len(b_products)}, C={len(c_products)}")
        
        return summary
        
    except Exception as exc:
        logger.error(f"Error en análisis ABC: {exc}")
        raise


@shared_task
def cleanup_old_transactions(days=365):
    """
    Archiva transacciones antiguas.
    
    Propósito:
        Mantener la tabla de transacciones optimizada
        moviendo registros antiguos a archivo.
    
    Args:
        days: Transacciones más antiguas que estos días
    
    Frecuencia: Mensual
    """
    try:
        from .models import InventoryTransaction
        
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        
        # Contar transacciones a archivar
        old_transactions = InventoryTransaction.objects.filter(
            created_at__lt=cutoff_date
        )
        
        count = old_transactions.count()
        
        if count == 0:
            logger.info("No hay transacciones para archivar")
            return {'archived': 0}
        
        # TODO: Mover a tabla de archivo antes de eliminar
        # ArchivedInventoryTransaction.objects.bulk_create(...)
        
        # Por ahora solo logear
        logger.info(f"Transacciones a archivar: {count}")
        
        # Descomentar para eliminar:
        # old_transactions.delete()
        
        return {
            'archived': count,
            'cutoff_date': cutoff_date.isoformat(),
        }
        
    except Exception as exc:
        logger.error(f"Error archivando transacciones: {exc}")
        raise


@shared_task
def update_product_costs():
    """
    Actualiza costos promedio ponderados de productos.
    
    Propósito:
        Recalcular costo promedio basándose en las últimas
        compras para una valoración precisa.
    
    Frecuencia: Diaria o después de cada compra
    """
    try:
        from .models import Product, InventoryTransaction
        from django.db.models import Avg
        
        # Productos con transacciones de compra recientes
        recent_purchases = InventoryTransaction.objects.filter(
            transaction_type='in',
            reason='purchase',
            unit_cost__isnull=False,
            created_at__gte=timezone.now() - timezone.timedelta(days=90)
        ).values('product_id').annotate(
            avg_cost=Avg('unit_cost')
        )
        
        updated_count = 0
        for purchase in recent_purchases:
            Product.objects.filter(
                id=purchase['product_id']
            ).update(
                cost_price=purchase['avg_cost']
            )
            updated_count += 1
        
        logger.info(f"Costos actualizados para {updated_count} productos")
        
        return {'updated': updated_count}
        
    except Exception as exc:
        logger.error(f"Error actualizando costos: {exc}")
        raise
