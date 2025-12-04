# ========================================================
# SISTEMA ERP UNIVERSAL - Vistas de Compras
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: ViewSets y vistas para el módulo de compras.
# ========================================================

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, Avg
from datetime import date, timedelta
from decimal import Decimal

from apps.core.views import BaseModelViewSet

from .models import (
    SupplierCategory,
    Supplier,
    SupplierContact,
    SupplierAddress,
    SupplierProduct,
    PurchaseRequisition,
    PurchaseRequisitionLine,
    PurchaseOrder,
    PurchaseOrderLine,
    GoodsReceipt,
    GoodsReceiptLine,
    SupplierInvoice,
    SupplierInvoiceLine,
    SupplierPayment,
    SupplierPaymentAllocation,
    SupplierEvaluation,
)

from .serializers import (
    SupplierCategorySerializer,
    SupplierListSerializer,
    SupplierDetailSerializer,
    SupplierCreateUpdateSerializer,
    SupplierContactSerializer,
    SupplierAddressSerializer,
    SupplierProductSerializer,
    PurchaseRequisitionListSerializer,
    PurchaseRequisitionDetailSerializer,
    PurchaseRequisitionCreateSerializer,
    PurchaseRequisitionLineSerializer,
    PurchaseOrderListSerializer,
    PurchaseOrderDetailSerializer,
    PurchaseOrderCreateSerializer,
    PurchaseOrderLineSerializer,
    GoodsReceiptListSerializer,
    GoodsReceiptDetailSerializer,
    GoodsReceiptLineSerializer,
    SupplierInvoiceListSerializer,
    SupplierInvoiceDetailSerializer,
    SupplierInvoiceLineSerializer,
    SupplierPaymentSerializer,
    SupplierPaymentAllocationSerializer,
    SupplierEvaluationSerializer,
    PurchaseSummarySerializer,
    SupplierStatementSerializer,
)

from .services import PurchasingService


# ========================================================
# Categorías de Proveedores
# ========================================================

class SupplierCategoryViewSet(BaseModelViewSet):
    """ViewSet para categorías de proveedores."""
    
    queryset = SupplierCategory.objects.all()
    serializer_class = SupplierCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['code', 'name']


# ========================================================
# Proveedores
# ========================================================

class SupplierViewSet(BaseModelViewSet):
    """ViewSet para proveedores."""
    
    queryset = Supplier.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['supplier_type', 'category', 'status', 'is_active', 'buyer', 'country']
    search_fields = ['code', 'name', 'trade_name', 'tax_id', 'email']
    ordering_fields = ['code', 'name', 'rating', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SupplierListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SupplierCreateUpdateSerializer
        return SupplierDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('category', 'buyer')
        return queryset
    
    @action(detail=True, methods=['get'])
    def statement(self, request, pk=None):
        """Obtiene estado de cuenta del proveedor."""
        supplier = self.get_object()
        
        from_date = request.query_params.get(
            'from_date',
            (date.today() - timedelta(days=90)).isoformat()
        )
        to_date = request.query_params.get(
            'to_date',
            date.today().isoformat()
        )
        
        statement = PurchasingService.get_supplier_statement(
            supplier=supplier,
            from_date=date.fromisoformat(from_date),
            to_date=date.fromisoformat(to_date)
        )
        
        serializer = SupplierStatementSerializer(statement)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def aging(self, request, pk=None):
        """Obtiene antigüedad de saldos del proveedor."""
        supplier = self.get_object()
        aging = PurchasingService.get_supplier_aging(supplier)
        return Response(aging)
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Obtiene productos del proveedor."""
        supplier = self.get_object()
        products = SupplierProduct.objects.filter(
            supplier=supplier, is_active=True
        ).select_related('product')
        serializer = SupplierProductSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """Obtiene órdenes del proveedor."""
        supplier = self.get_object()
        orders = PurchaseOrder.objects.filter(
            supplier=supplier
        ).order_by('-order_date')[:20]
        serializer = PurchaseOrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def invoices(self, request, pk=None):
        """Obtiene facturas del proveedor."""
        supplier = self.get_object()
        invoices = SupplierInvoice.objects.filter(
            supplier=supplier
        ).order_by('-invoice_date')[:20]
        serializer = SupplierInvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def evaluations(self, request, pk=None):
        """Obtiene evaluaciones del proveedor."""
        supplier = self.get_object()
        evaluations = SupplierEvaluation.objects.filter(
            supplier=supplier
        ).order_by('-evaluation_date')
        serializer = SupplierEvaluationSerializer(evaluations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprueba un proveedor."""
        supplier = self.get_object()
        
        if supplier.status != 'pending':
            return Response(
                {'error': 'Solo se pueden aprobar proveedores pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        supplier.status = 'active'
        supplier.save()
        
        return Response({'status': 'Proveedor aprobado'})


class SupplierContactViewSet(BaseModelViewSet):
    """ViewSet para contactos de proveedor."""
    
    queryset = SupplierContact.objects.all()
    serializer_class = SupplierContactSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        supplier_id = self.request.query_params.get('supplier')
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        return queryset


class SupplierProductViewSet(BaseModelViewSet):
    """ViewSet para productos de proveedor."""
    
    queryset = SupplierProduct.objects.all()
    serializer_class = SupplierProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['supplier', 'product', 'is_preferred', 'is_active']
    search_fields = ['supplier_code', 'supplier_name', 'product__name', 'product__sku']


# ========================================================
# Solicitudes de Compra
# ========================================================

class PurchaseRequisitionViewSet(BaseModelViewSet):
    """ViewSet para solicitudes de compra."""
    
    queryset = PurchaseRequisition.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'department', 'requested_by', 'warehouse']
    search_fields = ['number']
    ordering_fields = ['number', 'date', 'required_date']
    ordering = ['-date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseRequisitionListSerializer
        elif self.action == 'create':
            return PurchaseRequisitionCreateSerializer
        return PurchaseRequisitionDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('department', 'requested_by', 'warehouse')
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Envía solicitud para aprobación."""
        requisition = self.get_object()
        
        if requisition.status != 'draft':
            return Response(
                {'error': 'Solo se pueden enviar solicitudes en borrador'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        requisition.status = 'submitted'
        requisition.save()
        
        return Response({'status': 'Solicitud enviada para aprobación'})
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprueba solicitud de compra."""
        requisition = self.get_object()
        
        try:
            PurchasingService.approve_requisition(requisition, request.user)
            return Response({'status': 'Solicitud aprobada'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rechaza solicitud de compra."""
        requisition = self.get_object()
        reason = request.data.get('reason', 'Sin especificar')
        
        try:
            PurchasingService.reject_requisition(requisition, request.user, reason)
            return Response({'status': 'Solicitud rechazada'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def convert_to_order(self, request, pk=None):
        """Convierte solicitud a orden de compra."""
        requisition = self.get_object()
        supplier_id = request.data.get('supplier_id')
        
        if not supplier_id:
            return Response(
                {'error': 'Se requiere el ID del proveedor'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            supplier = Supplier.objects.get(id=supplier_id)
            order = PurchasingService.convert_requisition_to_order(
                requisition=requisition,
                supplier=supplier,
                user=request.user
            )
            serializer = PurchaseOrderDetailSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ========================================================
# Órdenes de Compra
# ========================================================

class PurchaseOrderViewSet(BaseModelViewSet):
    """ViewSet para órdenes de compra."""
    
    queryset = PurchaseOrder.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['supplier', 'status', 'order_type', 'buyer', 'warehouse']
    search_fields = ['number', 'supplier__name', 'supplier_reference']
    ordering_fields = ['number', 'order_date', 'total', 'status']
    ordering = ['-order_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseOrderListSerializer
        elif self.action == 'create':
            return PurchaseOrderCreateSerializer
        return PurchaseOrderDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('supplier', 'buyer', 'warehouse')
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def submit_for_approval(self, request, pk=None):
        """Envía orden para aprobación."""
        order = self.get_object()
        
        if order.status != 'draft':
            return Response(
                {'error': 'Solo se pueden enviar órdenes en borrador'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'pending_approval'
        order.save()
        
        return Response({'status': 'Orden enviada para aprobación'})
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprueba orden de compra."""
        order = self.get_object()
        
        try:
            PurchasingService.approve_order(order, request.user)
            return Response({'status': 'Orden aprobada'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def send_to_supplier(self, request, pk=None):
        """Envía orden al proveedor."""
        order = self.get_object()
        
        try:
            PurchasingService.send_order_to_supplier(order, request.user)
            return Response({'status': 'Orden enviada al proveedor'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirma orden por parte del proveedor."""
        order = self.get_object()
        promised_date = request.data.get('promised_date')
        reference = request.data.get('reference')
        
        try:
            PurchasingService.confirm_order(
                order,
                promised_date=date.fromisoformat(promised_date) if promised_date else None,
                reference=reference
            )
            return Response({'status': 'Orden confirmada'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancela orden de compra."""
        order = self.get_object()
        reason = request.data.get('reason', 'Sin especificar')
        
        try:
            PurchasingService.cancel_order(order, reason, request.user)
            return Response({'status': 'Orden cancelada'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def create_receipt(self, request, pk=None):
        """Crea recepción de mercancía."""
        order = self.get_object()
        
        lines_data = request.data.get('lines', [])
        receipt_data = request.data.get('receipt', {})
        
        try:
            receipt = PurchasingService.create_goods_receipt(
                order=order,
                lines_data=lines_data,
                receipt_data=receipt_data,
                user=request.user
            )
            serializer = GoodsReceiptDetailSerializer(receipt)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ========================================================
# Recepción de Mercancía
# ========================================================

class GoodsReceiptViewSet(BaseModelViewSet):
    """ViewSet para recepciones de mercancía."""
    
    queryset = GoodsReceipt.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['purchase_order', 'status', 'warehouse']
    search_fields = ['number', 'supplier_delivery_note', 'purchase_order__number']
    ordering_fields = ['number', 'receipt_date']
    ordering = ['-receipt_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return GoodsReceiptListSerializer
        return GoodsReceiptDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'purchase_order', 'purchase_order__supplier', 'warehouse'
        )
        return queryset
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirma recepción de mercancía."""
        receipt = self.get_object()
        
        try:
            PurchasingService.confirm_goods_receipt(receipt)
            return Response({'status': 'Recepción confirmada'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def create_invoice(self, request, pk=None):
        """Crea factura desde recepción."""
        receipt = self.get_object()
        
        try:
            invoice = PurchasingService.create_invoice_from_receipt(
                receipt, request.user
            )
            serializer = SupplierInvoiceDetailSerializer(invoice)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ========================================================
# Facturas de Proveedor
# ========================================================

class SupplierInvoiceViewSet(BaseModelViewSet):
    """ViewSet para facturas de proveedor."""
    
    queryset = SupplierInvoice.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['supplier', 'invoice_type', 'status']
    search_fields = ['number', 'supplier_invoice_number', 'supplier__name']
    ordering_fields = ['number', 'invoice_date', 'due_date', 'total']
    ordering = ['-invoice_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SupplierInvoiceListSerializer
        return SupplierInvoiceDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('supplier', 'purchase_order')
        
        # Filtrar por vencidas
        overdue = self.request.query_params.get('overdue')
        if overdue == 'true':
            queryset = queryset.filter(
                due_date__lt=date.today(),
                status__in=['approved', 'partial']
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Valida factura de proveedor."""
        invoice = self.get_object()
        
        if invoice.status != 'draft':
            return Response(
                {'error': 'Solo se pueden validar facturas en borrador'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.status = 'validated'
        invoice.save()
        
        return Response({'status': 'Factura validada'})
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprueba factura de proveedor."""
        invoice = self.get_object()
        
        try:
            PurchasingService.approve_invoice(invoice, request.user)
            return Response({'status': 'Factura aprobada'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def post(self, request, pk=None):
        """Contabiliza factura."""
        invoice = self.get_object()
        
        try:
            PurchasingService.post_invoice(invoice, request.user)
            return Response({'status': 'Factura contabilizada'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Lista facturas vencidas."""
        days = int(request.query_params.get('days', 0))
        
        invoices = PurchasingService.get_overdue_invoices(days_overdue=days)
        serializer = SupplierInvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)


# ========================================================
# Pagos a Proveedores
# ========================================================

class SupplierPaymentViewSet(BaseModelViewSet):
    """ViewSet para pagos a proveedores."""
    
    queryset = SupplierPayment.objects.all()
    serializer_class = SupplierPaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['supplier', 'payment_method', 'status']
    search_fields = ['number', 'supplier__name', 'reference', 'check_number']
    ordering_fields = ['number', 'payment_date', 'amount']
    ordering = ['-payment_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('supplier')
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
            PurchasingService.apply_payment(payment, allocations)
            serializer = SupplierPaymentSerializer(payment)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprueba pago."""
        payment = self.get_object()
        
        if payment.status != 'draft':
            return Response(
                {'error': 'Solo se pueden aprobar pagos en borrador'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment.status = 'approved'
        payment.approved_by = request.user
        payment.save()
        
        return Response({'status': 'Pago aprobado'})


# ========================================================
# Evaluación de Proveedores
# ========================================================

class SupplierEvaluationViewSet(BaseModelViewSet):
    """ViewSet para evaluaciones de proveedores."""
    
    queryset = SupplierEvaluation.objects.all()
    serializer_class = SupplierEvaluationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['supplier']
    ordering_fields = ['evaluation_date', 'overall_rating']
    ordering = ['-evaluation_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('supplier')
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(evaluated_by=self.request.user)


# ========================================================
# Reportes
# ========================================================

class PurchaseReportViewSet(viewsets.ViewSet):
    """ViewSet para reportes de compras."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Resumen de compras."""
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
        
        summary = PurchasingService.get_purchase_summary(
            from_date=date.fromisoformat(from_date),
            to_date=date.fromisoformat(to_date),
            warehouse=warehouse
        )
        
        serializer = PurchaseSummarySerializer(summary)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_orders(self, request):
        """Órdenes de compra pendientes."""
        supplier_id = request.query_params.get('supplier')
        supplier = None
        if supplier_id:
            supplier = Supplier.objects.filter(id=supplier_id).first()
        
        orders = PurchasingService.get_pending_orders(supplier=supplier)
        serializer = PurchaseOrderListSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def aging(self, request):
        """Antigüedad global de cuentas por pagar."""
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
            status__in=['approved', 'partial']
        ).select_related('supplier')
        
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
    def top_suppliers(self, request):
        """Top proveedores por compras."""
        from_date = request.query_params.get(
            'from_date',
            (date.today() - timedelta(days=365)).isoformat()
        )
        to_date = request.query_params.get(
            'to_date',
            date.today().isoformat()
        )
        limit = int(request.query_params.get('limit', 10))
        
        top_suppliers = PurchaseOrder.objects.filter(
            order_date__range=[from_date, to_date],
            status__in=['received', 'invoiced', 'completed']
        ).values(
            'supplier__id',
            'supplier__code',
            'supplier__name'
        ).annotate(
            total_orders=Count('id'),
            total_value=Sum('total')
        ).order_by('-total_value')[:limit]
        
        return Response(list(top_suppliers))
    
    @action(detail=False, methods=['get'])
    def top_products(self, request):
        """Top productos comprados."""
        from_date = request.query_params.get(
            'from_date',
            (date.today() - timedelta(days=365)).isoformat()
        )
        to_date = request.query_params.get(
            'to_date',
            date.today().isoformat()
        )
        limit = int(request.query_params.get('limit', 10))
        
        top_products = PurchaseOrderLine.objects.filter(
            order__order_date__range=[from_date, to_date],
            order__status__in=['received', 'invoiced', 'completed']
        ).values(
            'product__id',
            'product__sku',
            'product__name'
        ).annotate(
            quantity_purchased=Sum('quantity'),
            total_value=Sum('line_total')
        ).order_by('-total_value')[:limit]
        
        return Response(list(top_products))
    
    @action(detail=False, methods=['get'])
    def supplier_performance(self, request):
        """Rendimiento de proveedores."""
        evaluations = SupplierEvaluation.objects.values(
            'supplier__id',
            'supplier__code',
            'supplier__name'
        ).annotate(
            avg_quality=Avg('quality_rating'),
            avg_delivery=Avg('delivery_rating'),
            avg_price=Avg('price_rating'),
            avg_service=Avg('service_rating'),
            avg_overall=Avg('overall_rating'),
            total_evaluations=Count('id')
        ).order_by('-avg_overall')
        
        return Response(list(evaluations))
