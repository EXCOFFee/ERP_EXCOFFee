# ========================================================
# SISTEMA ERP UNIVERSAL - Serializers de Finanzas
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Serializers para la API de finanzas.
# ========================================================

from rest_framework import serializers
from decimal import Decimal

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


class AccountingPeriodSerializer(serializers.ModelSerializer):
    """
    Serializer para períodos contables.
    """
    
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    entries_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AccountingPeriod
        fields = [
            'id', 'name', 'code', 'start_date', 'end_date',
            'status', 'status_display', 'is_current',
            'entries_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_entries_count(self, obj: AccountingPeriod) -> int:
        """Cuenta asientos en el período."""
        return obj.entries.count()


class AccountTypeSerializer(serializers.ModelSerializer):
    """
    Serializer para tipos de cuenta.
    """
    
    nature_display = serializers.CharField(
        source='get_nature_display',
        read_only=True
    )
    
    class Meta:
        model = AccountType
        fields = [
            'id', 'name', 'nature', 'nature_display',
            'debit_nature', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AccountListSerializer(serializers.ModelSerializer):
    """
    Serializer ligero para listados de cuentas.
    """
    
    account_type_name = serializers.CharField(
        source='account_type.name',
        read_only=True
    )
    
    class Meta:
        model = Account
        fields = [
            'id', 'code', 'name', 'account_type',
            'account_type_name', 'level', 'is_detail',
            'is_active', 'current_balance'
        ]


class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer completo para cuentas contables.
    """
    
    account_type_name = serializers.CharField(
        source='account_type.name',
        read_only=True
    )
    
    parent_code = serializers.CharField(
        source='parent.code',
        read_only=True,
        allow_null=True
    )
    
    parent_name = serializers.CharField(
        source='parent.name',
        read_only=True,
        allow_null=True
    )
    
    full_name = serializers.CharField(read_only=True)
    
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'code', 'name', 'description',
            'account_type', 'account_type_name',
            'parent', 'parent_code', 'parent_name',
            'level', 'is_detail', 'is_active',
            'current_balance', 'full_name', 'children',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'level', 'current_balance', 'created_at', 'updated_at']
    
    def get_children(self, obj: Account) -> list:
        """Retorna hijos de la cuenta."""
        return AccountListSerializer(
            obj.children.filter(is_active=True),
            many=True
        ).data


class JournalEntryLineSerializer(serializers.ModelSerializer):
    """
    Serializer para líneas de asiento.
    """
    
    account_code = serializers.CharField(
        source='account.code',
        read_only=True
    )
    
    account_name = serializers.CharField(
        source='account.name',
        read_only=True
    )
    
    cost_center_name = serializers.CharField(
        source='cost_center.name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = JournalEntryLine
        fields = [
            'id', 'account', 'account_code', 'account_name',
            'debit', 'credit', 'description',
            'cost_center', 'cost_center_name'
        ]
        read_only_fields = ['id']
    
    def validate(self, attrs):
        """Validar que tenga débito O crédito."""
        debit = attrs.get('debit', Decimal('0.00'))
        credit = attrs.get('credit', Decimal('0.00'))
        
        if debit > 0 and credit > 0:
            raise serializers.ValidationError(
                'Una línea no puede tener débito y crédito al mismo tiempo'
            )
        
        if debit == 0 and credit == 0:
            raise serializers.ValidationError(
                'Debe especificar un monto en débito o crédito'
            )
        
        return attrs


class JournalEntryListSerializer(serializers.ModelSerializer):
    """
    Serializer ligero para listado de asientos.
    """
    
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    entry_type_display = serializers.CharField(
        source='get_entry_type_display',
        read_only=True
    )
    
    is_balanced = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = JournalEntry
        fields = [
            'id', 'entry_number', 'entry_date', 'description',
            'status', 'status_display', 'entry_type', 'entry_type_display',
            'total_debit', 'total_credit', 'is_balanced'
        ]


class JournalEntrySerializer(serializers.ModelSerializer):
    """
    Serializer completo para asientos contables.
    """
    
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    entry_type_display = serializers.CharField(
        source='get_entry_type_display',
        read_only=True
    )
    
    period_name = serializers.CharField(
        source='period.name',
        read_only=True
    )
    
    lines = JournalEntryLineSerializer(many=True, read_only=True)
    
    is_balanced = serializers.BooleanField(read_only=True)
    
    created_by_name = serializers.CharField(
        source='created_by.full_name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = JournalEntry
        fields = [
            'id', 'entry_number', 'period', 'period_name',
            'entry_date', 'description',
            'status', 'status_display',
            'entry_type', 'entry_type_display',
            'reference_type', 'reference_id', 'reference_number',
            'total_debit', 'total_credit', 'is_balanced',
            'notes', 'posted_date', 'reversal_entry',
            'lines', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'entry_number', 'total_debit', 'total_credit',
            'posted_date', 'reversal_entry',
            'created_by', 'created_at', 'updated_at'
        ]


class JournalEntryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear asientos con sus líneas.
    """
    
    lines = JournalEntryLineSerializer(many=True)
    
    class Meta:
        model = JournalEntry
        fields = [
            'period', 'entry_date', 'description', 'entry_type',
            'reference_type', 'reference_id', 'reference_number',
            'notes', 'lines'
        ]
    
    def validate_lines(self, value):
        """Validar que las líneas estén balanceadas."""
        if not value or len(value) < 2:
            raise serializers.ValidationError(
                'Un asiento debe tener al menos 2 líneas'
            )
        
        total_debit = sum(line.get('debit', Decimal('0.00')) for line in value)
        total_credit = sum(line.get('credit', Decimal('0.00')) for line in value)
        
        if total_debit != total_credit:
            raise serializers.ValidationError(
                f'El asiento no está balanceado. Débito: {total_debit}, Crédito: {total_credit}'
            )
        
        return value
    
    def create(self, validated_data):
        """Crear asiento con sus líneas."""
        lines_data = validated_data.pop('lines')
        
        # Generar número de asiento
        import uuid
        validated_data['entry_number'] = f"AST-{uuid.uuid4().hex[:8].upper()}"
        
        # Crear asiento
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        
        entry = JournalEntry.objects.create(**validated_data)
        
        # Crear líneas
        for line_data in lines_data:
            JournalEntryLine.objects.create(journal_entry=entry, **line_data)
        
        # Calcular totales
        entry.calculate_totals()
        
        return entry


class CostCenterSerializer(serializers.ModelSerializer):
    """
    Serializer para centros de costo.
    """
    
    parent_name = serializers.CharField(
        source='parent.name',
        read_only=True,
        allow_null=True
    )
    
    manager_name = serializers.CharField(
        source='manager.full_name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = CostCenter
        fields = [
            'id', 'code', 'name', 'description',
            'parent', 'parent_name',
            'manager', 'manager_name', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BudgetSerializer(serializers.ModelSerializer):
    """
    Serializer para presupuestos.
    """
    
    period_name = serializers.CharField(
        source='period.name',
        read_only=True
    )
    
    account_code = serializers.CharField(
        source='account.code',
        read_only=True
    )
    
    account_name = serializers.CharField(
        source='account.name',
        read_only=True
    )
    
    cost_center_name = serializers.CharField(
        source='cost_center.name',
        read_only=True,
        allow_null=True
    )
    
    executed_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    
    remaining_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    
    execution_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Budget
        fields = [
            'id', 'period', 'period_name',
            'account', 'account_code', 'account_name',
            'cost_center', 'cost_center_name',
            'amount', 'executed_amount', 'remaining_amount',
            'execution_percentage', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaxRateSerializer(serializers.ModelSerializer):
    """
    Serializer para tasas de impuesto.
    """
    
    tax_type_display = serializers.CharField(
        source='get_tax_type_display',
        read_only=True
    )
    
    account_name = serializers.CharField(
        source='account.name',
        read_only=True
    )
    
    class Meta:
        model = TaxRate
        fields = [
            'id', 'code', 'name', 'tax_type', 'tax_type_display',
            'rate', 'account', 'account_name',
            'applies_to_purchases', 'applies_to_sales',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentMethodSerializer(serializers.ModelSerializer):
    """
    Serializer para métodos de pago.
    """
    
    account_name = serializers.CharField(
        source='account.name',
        read_only=True
    )
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'code', 'name', 'account', 'account_name',
            'requires_reference', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BankAccountSerializer(serializers.ModelSerializer):
    """
    Serializer para cuentas bancarias.
    """
    
    account_type_display = serializers.CharField(
        source='get_account_type_display',
        read_only=True
    )
    
    ledger_account_name = serializers.CharField(
        source='ledger_account.name',
        read_only=True
    )
    
    class Meta:
        model = BankAccount
        fields = [
            'id', 'name', 'account_number', 'bank_name',
            'account_type', 'account_type_display',
            'currency', 'ledger_account', 'ledger_account_name',
            'current_balance', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TrialBalanceSerializer(serializers.Serializer):
    """
    Serializer para balance de comprobación.
    """
    
    account_code = serializers.CharField()
    account_name = serializers.CharField()
    account_type = serializers.CharField()
    initial_debit = serializers.DecimalField(max_digits=15, decimal_places=2)
    initial_credit = serializers.DecimalField(max_digits=15, decimal_places=2)
    period_debit = serializers.DecimalField(max_digits=15, decimal_places=2)
    period_credit = serializers.DecimalField(max_digits=15, decimal_places=2)
    final_debit = serializers.DecimalField(max_digits=15, decimal_places=2)
    final_credit = serializers.DecimalField(max_digits=15, decimal_places=2)


class IncomeStatementSerializer(serializers.Serializer):
    """
    Serializer para estado de resultados.
    """
    
    category = serializers.CharField()
    accounts = serializers.ListField()
    subtotal = serializers.DecimalField(max_digits=15, decimal_places=2)


class BalanceSheetSerializer(serializers.Serializer):
    """
    Serializer para balance general.
    """
    
    assets = serializers.ListField()
    liabilities = serializers.ListField()
    equity = serializers.ListField()
    total_assets = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_liabilities = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_equity = serializers.DecimalField(max_digits=15, decimal_places=2)
