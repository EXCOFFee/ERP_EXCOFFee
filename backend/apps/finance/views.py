# ========================================================
# SISTEMA ERP UNIVERSAL - Vistas de Finanzas
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Vistas (ViewSets) para el módulo de finanzas.
# Implementa RF3 del SRS - Gestión Financiera.
# ========================================================

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from apps.core.views import BaseViewSet
from apps.authentication.permissions import HasModulePermission

from .models import (
    AccountingPeriod,
    AccountType,
    Account,
    JournalEntry,
    JournalEntryLine,
    CostCenter,
    Budget,
    TaxRate,
    PaymentMethod,
    BankAccount,
)
from .serializers import (
    AccountingPeriodSerializer,
    AccountTypeSerializer,
    AccountSerializer,
    AccountListSerializer,
    JournalEntrySerializer,
    JournalEntryListSerializer,
    JournalEntryCreateSerializer,
    JournalEntryLineSerializer,
    CostCenterSerializer,
    BudgetSerializer,
    TaxRateSerializer,
    PaymentMethodSerializer,
    BankAccountSerializer,
)
from .services import AccountingService, BudgetService


class AccountingPeriodViewSet(BaseViewSet):
    """
    ViewSet para períodos contables.
    
    Endpoints adicionales:
        POST /periods/{id}/close/ - Cerrar período
        POST /periods/{id}/set-current/ - Marcar como actual
    """
    queryset = AccountingPeriod.objects.all()
    serializer_class = AccountingPeriodSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'finance'
    search_fields = ['name', 'code']
    ordering = ['-start_date']
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """
        Cierra un período contable.
        """
        period = self.get_object()
        try:
            AccountingService.close_period(period, request.user)
            return Response({
                'message': 'Período cerrado exitosamente',
                'period': AccountingPeriodSerializer(period).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='set-current')
    def set_current(self, request, pk=None):
        """
        Marca un período como el actual.
        """
        period = self.get_object()
        if period.status != AccountingPeriod.PeriodStatus.OPEN:
            return Response(
                {'error': 'Solo se puede marcar como actual un período abierto'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        period.is_current = True
        period.save()
        
        return Response({
            'message': 'Período marcado como actual',
            'period': AccountingPeriodSerializer(period).data
        })


class AccountTypeViewSet(BaseViewSet):
    """
    ViewSet para tipos de cuenta.
    """
    queryset = AccountType.objects.all()
    serializer_class = AccountTypeSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'finance'
    ordering = ['name']


class AccountViewSet(BaseViewSet):
    """
    ViewSet para cuentas contables (Plan de Cuentas).
    
    Endpoints adicionales:
        GET /accounts/tree/ - Árbol de cuentas
        GET /accounts/{id}/balance/ - Saldo de la cuenta
        GET /accounts/{id}/ledger/ - Libro mayor
    """
    queryset = Account.objects.filter(is_active=True)
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'finance'
    search_fields = ['code', 'name', 'description']
    filterset_fields = ['account_type', 'parent', 'level', 'is_detail']
    ordering = ['code']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AccountListSerializer
        return AccountSerializer
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        Retorna el plan de cuentas en estructura de árbol.
        """
        def build_tree(account):
            children = account.children.filter(is_active=True)
            return {
                'id': str(account.id),
                'code': account.code,
                'name': account.name,
                'level': account.level,
                'is_detail': account.is_detail,
                'current_balance': str(account.current_balance),
                'children': [build_tree(child) for child in children]
            }
        
        root_accounts = Account.objects.filter(
            parent__isnull=True,
            is_active=True
        ).order_by('code')
        
        tree = [build_tree(acc) for acc in root_accounts]
        return Response(tree)
    
    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        """
        Obtiene el saldo de una cuenta.
        """
        account = self.get_object()
        period_id = request.query_params.get('period')
        
        period = None
        if period_id:
            try:
                period = AccountingPeriod.objects.get(pk=period_id)
            except AccountingPeriod.DoesNotExist:
                pass
        
        balance = AccountingService.get_account_balance(str(account.id), period)
        
        return Response({
            'account_code': account.code,
            'account_name': account.name,
            'balance': str(balance),
            'period': period.name if period else 'Todos los períodos'
        })
    
    @action(detail=True, methods=['get'])
    def ledger(self, request, pk=None):
        """
        Obtiene el libro mayor de una cuenta.
        """
        account = self.get_object()
        period_id = request.query_params.get('period')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        period = None
        if period_id:
            try:
                period = AccountingPeriod.objects.get(pk=period_id)
            except AccountingPeriod.DoesNotExist:
                pass
        
        ledger = AccountingService.get_account_ledger(
            str(account.id),
            period,
            start_date,
            end_date
        )
        
        return Response({
            'account_code': account.code,
            'account_name': account.name,
            'entries': ledger
        })


class JournalEntryViewSet(BaseViewSet):
    """
    ViewSet para asientos contables.
    
    Endpoints adicionales:
        POST /entries/{id}/post/ - Contabilizar asiento
        POST /entries/{id}/reverse/ - Reversar asiento
    """
    queryset = JournalEntry.objects.all().select_related(
        'period', 'created_by'
    ).prefetch_related('lines', 'lines__account')
    serializer_class = JournalEntrySerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'finance'
    search_fields = ['entry_number', 'description', 'notes']
    filterset_fields = ['status', 'entry_type', 'period']
    ordering = ['-entry_date', '-entry_number']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return JournalEntryListSerializer
        if self.action == 'create':
            return JournalEntryCreateSerializer
        return JournalEntrySerializer
    
    @action(detail=True, methods=['post'])
    def post(self, request, pk=None):
        """
        Contabiliza un asiento (cambia estado a POSTED).
        """
        entry = self.get_object()
        try:
            entry.post(request.user)
            return Response({
                'message': 'Asiento contabilizado exitosamente',
                'entry': JournalEntrySerializer(entry).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reverse(self, request, pk=None):
        """
        Reversa un asiento contabilizado.
        """
        entry = self.get_object()
        description = request.data.get('description')
        
        try:
            reversal = entry.reverse(request.user, description)
            return Response({
                'message': 'Asiento reversado exitosamente',
                'original_entry': JournalEntrySerializer(entry).data,
                'reversal_entry': JournalEntrySerializer(reversal).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CostCenterViewSet(BaseViewSet):
    """
    ViewSet para centros de costo.
    """
    queryset = CostCenter.objects.filter(is_active=True)
    serializer_class = CostCenterSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'finance'
    search_fields = ['code', 'name', 'description']
    ordering = ['code']


class BudgetViewSet(BaseViewSet):
    """
    ViewSet para presupuestos.
    
    Endpoints adicionales:
        GET /budgets/execution-report/ - Reporte de ejecución
    """
    queryset = Budget.objects.all().select_related(
        'period', 'account', 'cost_center'
    )
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'finance'
    filterset_fields = ['period', 'account', 'cost_center']
    ordering = ['account__code']
    
    @action(detail=False, methods=['get'], url_path='execution-report')
    def execution_report(self, request):
        """
        Genera reporte de ejecución presupuestal.
        """
        period_id = request.query_params.get('period')
        cost_center_id = request.query_params.get('cost_center')
        
        period = None
        if period_id:
            try:
                period = AccountingPeriod.objects.get(pk=period_id)
            except AccountingPeriod.DoesNotExist:
                pass
        
        report = BudgetService.get_budget_execution_report(
            period, cost_center_id
        )
        
        return Response({
            'period': period.name if period else 'Período Actual',
            'report': report
        })


class TaxRateViewSet(BaseViewSet):
    """
    ViewSet para tasas de impuesto.
    """
    queryset = TaxRate.objects.filter(is_active=True)
    serializer_class = TaxRateSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'finance'
    search_fields = ['code', 'name']
    filterset_fields = ['tax_type', 'applies_to_purchases', 'applies_to_sales']
    ordering = ['name']


class PaymentMethodViewSet(BaseViewSet):
    """
    ViewSet para métodos de pago.
    """
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'finance'
    ordering = ['name']


class BankAccountViewSet(BaseViewSet):
    """
    ViewSet para cuentas bancarias.
    """
    queryset = BankAccount.objects.filter(is_active=True)
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'finance'
    search_fields = ['name', 'account_number', 'bank_name']
    ordering = ['bank_name', 'name']


class ReportsViewSet(viewsets.ViewSet):
    """
    ViewSet para reportes financieros.
    
    Endpoints:
        GET /reports/trial-balance/ - Balance de comprobación
        GET /reports/income-statement/ - Estado de resultados
        GET /reports/balance-sheet/ - Balance general
    """
    permission_classes = [IsAuthenticated, HasModulePermission]
    module_name = 'finance'
    
    @action(detail=False, methods=['get'], url_path='trial-balance')
    def trial_balance(self, request):
        """
        Genera el balance de comprobación.
        """
        period_id = request.query_params.get('period')
        
        period = None
        if period_id:
            try:
                period = AccountingPeriod.objects.get(pk=period_id)
            except AccountingPeriod.DoesNotExist:
                pass
        
        data = AccountingService.get_trial_balance(period)
        
        # Calcular totales
        total_debit = sum(row['debit_balance'] for row in data)
        total_credit = sum(row['credit_balance'] for row in data)
        
        return Response({
            'period': period.name if period else 'Todos los períodos',
            'generated_at': timezone.now().isoformat(),
            'accounts': data,
            'total_debit': str(total_debit),
            'total_credit': str(total_credit),
            'is_balanced': total_debit == total_credit
        })
    
    @action(detail=False, methods=['get'], url_path='income-statement')
    def income_statement(self, request):
        """
        Genera el estado de resultados.
        """
        period_id = request.query_params.get('period')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        period = None
        if period_id:
            try:
                period = AccountingPeriod.objects.get(pk=period_id)
            except AccountingPeriod.DoesNotExist:
                pass
        
        data = AccountingService.get_income_statement(
            period, start_date, end_date
        )
        
        return Response({
            'period': period.name if period else 'Período personalizado',
            'start_date': start_date,
            'end_date': end_date,
            'generated_at': timezone.now().isoformat(),
            **data
        })
    
    @action(detail=False, methods=['get'], url_path='balance-sheet')
    def balance_sheet(self, request):
        """
        Genera el balance general.
        """
        as_of_date = request.query_params.get('as_of_date')
        
        data = AccountingService.get_balance_sheet(as_of_date)
        
        return Response({
            'as_of_date': as_of_date or timezone.now().date().isoformat(),
            'generated_at': timezone.now().isoformat(),
            **data
        })
