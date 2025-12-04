# ========================================================
# SISTEMA ERP UNIVERSAL - Vistas de Ventas
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: ViewSets y vistas para el módulo de ventas.
# ========================================================

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from apps.core.views import BaseModelViewSet

from .models import (
    CustomerGroup,
    Customer,
    CustomerAddress,
    CustomerContact,
    Quotation,
    QuotationLine,
    SalesOrder,
    SalesOrderLine,
    Invoice,
    InvoiceLine,
    Payment,
    PaymentAllocation,
    Shipment,
    ShipmentLine,
    PriceList,
    PriceListItem,
    Promotion,
)

from .serializers import (
    CustomerGroupSerializer,
    CustomerListSerializer,
    CustomerDetailSerializer,
    CustomerCreateUpdateSerializer,
    CustomerAddressSerializer,
    CustomerContactSerializer,
    QuotationListSerializer,
    QuotationDetailSerializer,
    QuotationCreateSerializer,
    QuotationLineSerializer,
    SalesOrderListSerializer,
    SalesOrderDetailSerializer,
    SalesOrderCreateSerializer,
    SalesOrderLineSerializer,
    InvoiceListSerializer,
    InvoiceDetailSerializer,
    InvoiceLineSerializer,
    PaymentSerializer,
    PaymentCreateSerializer,
    PaymentAllocationSerializer,
    ShipmentListSerializer,
    ShipmentDetailSerializer,
    ShipmentLineSerializer,
    PriceListSerializer,
    PriceListItemSerializer,
    PromotionSerializer,
    SalesSummarySerializer,
    CustomerStatementSerializer,
)

from .services import SalesService


# ========================================================
# Grupos de Clientes
# ========================================================

class CustomerGroupViewSet(BaseModelViewSet):
    """ViewSet para grupos de clientes."""
    
    queryset = CustomerGroup.objects.all()
    serializer_class = CustomerGroupSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']
    ordering = ['name']


# ========================================================
# Clientes
# ========================================================

class CustomerViewSet(BaseModelViewSet):
    """ViewSet para clientes."""
    
    queryset = Customer.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer_type', 'group', 'status', 'is_active', 'sales_rep', 'country']
    search_fields = ['code', 'name', 'trade_name', 'tax_id', 'email']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CustomerCreateUpdateSerializer
        return CustomerDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('group', 'sales_rep')
        return queryset
    
    @action(detail=True, methods=['get'])
    def statement(self, request, pk=None):
        """Obtiene estado de cuenta del cliente."""
        customer = self.get_object()
        
        from_date = request.query_params.get(
            'from_date',
            (date.today() - timedelta(days=90)).isoformat()
        )
        to_date = request.query_params.get(
            'to_date',
            date.today().isoformat()
        )
        
        statement = SalesService.get_customer_statement(
            customer=customer,
            from_date=date.fromisoformat(from_date),
            to_date=date.fromisoformat(to_date)
        )
        
        serializer = CustomerStatementSerializer(statement)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def aging(self, request, pk=None):
        """Obtiene antigüedad de saldos del cliente."""
        customer = self.get_object()
        aging = SalesService.get_customer_aging(customer)
        return Response(aging)
    
    @action(detail=True, methods=['get'])
    def credit_status(self, request, pk=None):
        """Obtiene estado de crédito del cliente."""
        customer = self.get_object()
        return Response({
            'credit_limit': customer.credit_limit,
            'credit_used': customer.credit_used,
            'available_credit': customer.credit_limit - customer.credit_used,
            'utilization_percentage': (
                customer.credit_used / customer.credit_limit * 100
                if customer.credit_limit > 0 else 0
            )
        })
    
    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """Obtiene órdenes del cliente."""
        customer = self.get_object()
        orders = SalesOrder.objects.filter(customer=customer).order_by('-order_date')[:20]
        serializer = SalesOrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def invoices(self, request, pk=None):
        """Obtiene facturas del cliente."""
        customer = self.get_object()
        invoices = Invoice.objects.filter(customer=customer).order_by('-invoice_date')[:20]
        serializer = InvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)


class CustomerAddressViewSet(BaseModelViewSet):
    """ViewSet para direcciones de cliente."""
    
    queryset = CustomerAddress.objects.all()
    serializer_class = CustomerAddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        customer_id = self.request.query_params.get('customer')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        return queryset


class CustomerContactViewSet(BaseModelViewSet):
    """ViewSet para contactos de cliente."""
    
    queryset = CustomerContact.objects.all()
    serializer_class = CustomerContactSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        customer_id = self.request.query_params.get('customer')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        return queryset


# ========================================================
# Cotizaciones
# ========================================================

class QuotationViewSet(BaseModelViewSet):
    """ViewSet para cotizaciones."""
    
    queryset = Quotation.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'sales_rep', 'status']
    search_fields = ['number', 'customer__name']
    ordering_fields = ['number', 'date', 'total']
    ordering = ['-date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return QuotationListSerializer
        elif self.action == 'create':
            return QuotationCreateSerializer
        return QuotationDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('customer', 'sales_rep')
        
        # Filtrar por rango de fechas
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        if from_date and to_date:
            queryset = queryset.filter(date__range=[from_date, to_date])
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Marca cotización como enviada."""
        quotation = self.get_object()
        
        if quotation.status != 'draft':
            return Response(
                {'error': 'Solo se pueden enviar cotizaciones en borrador'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        quotation.status = 'sent'
        quotation.save()
        
        # TODO: Enviar email al cliente
        
        return Response({'status': 'Cotización enviada'})
    
    @action(detail=True, methods=['post'])
    def convert_to_order(self, request, pk=None):
        """Convierte cotización a orden de venta."""
        quotation = self.get_object()
        
        try:
            order = SalesService.convert_quotation_to_order(
                quotation=quotation,
                user=request.user
            )
            serializer = SalesOrderDetailSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplica cotización."""
        quotation = self.get_object()
        
        # Crear nueva cotización
        new_quotation = Quotation.objects.create(
            customer=quotation.customer,
            contact=quotation.contact,
            date=date.today(),
            valid_until=date.today() + timedelta(days=30),
            sales_rep=quotation.sales_rep,
            payment_term=quotation.payment_term,
            currency=quotation.currency,
            notes=quotation.notes,
            terms_conditions=quotation.terms_conditions,
            created_by=request.user
        )
        
        # Copiar líneas
        for line in quotation.lines.all():
            QuotationLine.objects.create(
                quotation=new_quotation,
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
        
        serializer = QuotationDetailSerializer(new_quotation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ========================================================
# Órdenes de Venta
# ========================================================

class SalesOrderViewSet(BaseModelViewSet):
    """ViewSet para órdenes de venta."""
    
    queryset = SalesOrder.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'sales_rep', 'status', 'order_type', 'priority', 'warehouse']
    search_fields = ['number', 'customer__name', 'customer_reference']
    ordering_fields = ['number', 'order_date', 'total', 'status']
    ordering = ['-order_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SalesOrderListSerializer
        elif self.action == 'create':
            return SalesOrderCreateSerializer
        return SalesOrderDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('customer', 'sales_rep', 'warehouse')
        
        # Filtrar por rango de fechas
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        if from_date and to_date:
            queryset = queryset.filter(order_date__range=[from_date, to_date])
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirma orden de venta."""
        order = self.get_object()
        
        try:
            SalesService.confirm_order(order, request.user)
            return Response({'status': 'Orden confirmada'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reserve_stock(self, request, pk=None):
        """Reserva inventario para la orden."""
        order = self.get_object()
        
        try:
            all_reserved = SalesService.reserve_stock(order)
            return Response({
                'status': 'Inventario reservado',
                'complete': all_reserved
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancela orden de venta."""
        order = self.get_object()
        reason = request.data.get('reason', 'Sin especificar')
        
        try:
            SalesService.cancel_order(order, reason, request.user)
            return Response({'status': 'Orden cancelada'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def create_shipment(self, request, pk=None):
        """Crea envío para la orden."""
        order = self.get_object()
        
        lines_data = request.data.get('lines', [])
        shipment_data = request.data.get('shipment', {})
        
        try:
            shipment = SalesService.create_shipment(
                order=order,
                lines_data=lines_data,
                shipment_data=shipment_data,
                user=request.user
            )
            serializer = ShipmentDetailSerializer(shipment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def create_invoice(self, request, pk=None):
        """Crea factura para la orden."""
        order = self.get_object()
        
        try:
            invoice = SalesService.create_invoice_from_order(order, request.user)
            serializer = InvoiceDetailSerializer(invoice)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ========================================================
# Facturas
# ========================================================

class InvoiceViewSet(BaseModelViewSet):
    """ViewSet para facturas."""
    
    queryset = Invoice.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'invoice_type', 'status']
    search_fields = ['number', 'customer__name']
    ordering_fields = ['number', 'invoice_date', 'due_date', 'total']
    ordering = ['-invoice_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        return InvoiceDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('customer', 'sales_order')
        
        # Filtrar por vencidas
        overdue = self.request.query_params.get('overdue')
        if overdue == 'true':
            queryset = queryset.filter(
                due_date__lt=date.today(),
                status__in=['pending', 'partial']
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def post(self, request, pk=None):
        """Contabiliza factura."""
        invoice = self.get_object()
        
        try:
            SalesService.post_invoice(invoice, request.user)
            return Response({'status': 'Factura contabilizada'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def void(self, request, pk=None):
        """Anula factura."""
        invoice = self.get_object()
        reason = request.data.get('reason', 'Sin especificar')
        
        if invoice.status == 'paid':
            return Response(
                {'error': 'No se puede anular una factura pagada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.status = 'void'
        invoice.notes = f"{invoice.notes or ''}\nAnulada: {reason}"
        invoice.save()
        
        return Response({'status': 'Factura anulada'})
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Lista facturas vencidas."""
        days = int(request.query_params.get('days', 0))
        
        invoices = SalesService.get_overdue_invoices(days_overdue=days)
        serializer = InvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)


# ========================================================
# Pagos
# ========================================================

class PaymentViewSet(BaseModelViewSet):
    """ViewSet para pagos."""
    
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'payment_method', 'status']
    search_fields = ['number', 'customer__name', 'reference']
    ordering_fields = ['number', 'payment_date', 'amount']
    ordering = ['-payment_date']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('customer')
        queryset = queryset.prefetch_related('allocations__invoice')
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Aplica pago a facturas."""
        payment = self.get_object()
        allocations = request.data.get('allocations', [])
        
        try:
            SalesService.apply_payment(payment, allocations)
            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirma pago."""
        payment = self.get_object()
        
        if payment.status != 'pending':
            return Response(
                {'error': 'Solo se pueden confirmar pagos pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = 'confirmed'
        payment.save()
        
        return Response({'status': 'Pago confirmado'})


# ========================================================
# Envíos
# ========================================================

class ShipmentViewSet(BaseModelViewSet):
    """ViewSet para envíos."""
    
    queryset = Shipment.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sales_order', 'status', 'carrier', 'warehouse']
    search_fields = ['number', 'tracking_number', 'sales_order__number']
    ordering_fields = ['number', 'shipment_date', 'estimated_delivery']
    ordering = ['-shipment_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ShipmentListSerializer
        return ShipmentDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('sales_order', 'sales_order__customer', 'warehouse')
        queryset = queryset.prefetch_related('lines__order_line__product')
        return queryset
    
    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """Marca envío como en tránsito."""
        shipment = self.get_object()
        
        if shipment.status != 'pending':
            return Response(
                {'error': 'El envío ya está en proceso'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        shipment.status = 'in_transit'
        shipment.shipment_date = date.today()
        shipment.tracking_number = request.data.get(
            'tracking_number',
            shipment.tracking_number
        )
        shipment.save()
        
        return Response({'status': 'Envío en tránsito'})
    
    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        """Confirma entrega de envío."""
        shipment = self.get_object()
        delivery_date = request.data.get('delivery_date')
        
        try:
            SalesService.confirm_delivery(
                shipment=shipment,
                delivery_date=date.fromisoformat(delivery_date) if delivery_date else None
            )
            return Response({'status': 'Entrega confirmada'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ========================================================
# Listas de Precios
# ========================================================

class PriceListViewSet(BaseModelViewSet):
    """ViewSet para listas de precios."""
    
    queryset = PriceList.objects.all()
    serializer_class = PriceListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active', 'is_default', 'currency']
    search_fields = ['code', 'name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('items__product')
        return queryset
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Establece lista de precios como predeterminada."""
        price_list = self.get_object()
        
        # Quitar default de otras
        PriceList.objects.filter(is_default=True).update(is_default=False)
        
        price_list.is_default = True
        price_list.save()
        
        return Response({'status': 'Lista establecida como predeterminada'})
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Agrega item a lista de precios."""
        price_list = self.get_object()
        
        serializer = PriceListItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(price_list=price_list)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ========================================================
# Promociones
# ========================================================

class PromotionViewSet(BaseModelViewSet):
    """ViewSet para promociones."""
    
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['promotion_type', 'is_active']
    search_fields = ['code', 'name']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Lista promociones activas."""
        today = date.today()
        promotions = Promotion.objects.filter(
            is_active=True,
            valid_from__lte=today
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gte=today)
        )
        serializer = PromotionSerializer(promotions, many=True)
        return Response(serializer.data)


# ========================================================
# Reportes
# ========================================================

class SalesReportViewSet(viewsets.ViewSet):
    """ViewSet para reportes de ventas."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Resumen de ventas."""
        from_date = request.query_params.get(
            'from_date',
            (date.today() - timedelta(days=30)).isoformat()
        )
        to_date = request.query_params.get(
            'to_date',
            date.today().isoformat()
        )
        warehouse_id = request.query_params.get('warehouse')
        
        from apps.inventory.models import Warehouse
        warehouse = None
        if warehouse_id:
            warehouse = Warehouse.objects.filter(id=warehouse_id).first()
        
        summary = SalesService.get_sales_summary(
            from_date=date.fromisoformat(from_date),
            to_date=date.fromisoformat(to_date),
            warehouse=warehouse
        )
        
        serializer = SalesSummarySerializer(summary)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def forecast(self, request):
        """Pronóstico de ventas."""
        months = int(request.query_params.get('months', 3))
        forecast = SalesService.get_sales_forecast(months=months)
        return Response(forecast)
    
    @action(detail=False, methods=['get'])
    def aging(self, request):
        """Antigüedad global de cuentas por cobrar."""
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
            status__in=['pending', 'partial']
        ).select_related('customer')
        
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
        
        return Response(aging)
    
    @action(detail=False, methods=['get'])
    def top_customers(self, request):
        """Top clientes por ventas."""
        from_date = request.query_params.get(
            'from_date',
            (date.today() - timedelta(days=365)).isoformat()
        )
        to_date = request.query_params.get(
            'to_date',
            date.today().isoformat()
        )
        limit = int(request.query_params.get('limit', 10))
        
        top_customers = SalesOrder.objects.filter(
            order_date__range=[from_date, to_date],
            status__in=['delivered', 'invoiced']
        ).values(
            'customer__id',
            'customer__code',
            'customer__name'
        ).annotate(
            total_orders=Count('id'),
            total_value=Sum('total')
        ).order_by('-total_value')[:limit]
        
        return Response(list(top_customers))
    
    @action(detail=False, methods=['get'])
    def top_products(self, request):
        """Top productos vendidos."""
        from_date = request.query_params.get(
            'from_date',
            (date.today() - timedelta(days=365)).isoformat()
        )
        to_date = request.query_params.get(
            'to_date',
            date.today().isoformat()
        )
        limit = int(request.query_params.get('limit', 10))
        
        top_products = SalesOrderLine.objects.filter(
            order__order_date__range=[from_date, to_date],
            order__status__in=['delivered', 'invoiced']
        ).values(
            'product__id',
            'product__sku',
            'product__name'
        ).annotate(
            quantity_sold=Sum('quantity'),
            total_value=Sum('line_total')
        ).order_by('-total_value')[:limit]
        
        return Response(list(top_products))
    
    @action(detail=False, methods=['get'])
    def sales_by_rep(self, request):
        """Ventas por vendedor."""
        from_date = request.query_params.get(
            'from_date',
            (date.today() - timedelta(days=30)).isoformat()
        )
        to_date = request.query_params.get(
            'to_date',
            date.today().isoformat()
        )
        
        sales_by_rep = SalesOrder.objects.filter(
            order_date__range=[from_date, to_date]
        ).exclude(
            status='cancelled'
        ).values(
            'sales_rep__id',
            'sales_rep__user__first_name',
            'sales_rep__user__last_name'
        ).annotate(
            total_orders=Count('id'),
            total_value=Sum('total'),
            avg_order_value=Avg('total')
        ).order_by('-total_value')
        
        return Response(list(sales_by_rep))
