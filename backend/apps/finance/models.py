# ========================================================
# SISTEMA ERP UNIVERSAL - Modelos de Finanzas
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Modelos para el módulo de contabilidad.
# Implementa RF3 - Gestión Financiera del SRS.
#
# Modelo contable:
# - Plan de cuentas jerárquico
# - Partida doble (débito = crédito)
# - Períodos contables
# - Libro mayor y balance
# ========================================================

from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from apps.core.models import BaseModel


class AccountingPeriod(BaseModel):
    """
    Período contable (ejercicio fiscal).
    
    Propósito:
        Definir períodos para agrupar transacciones contables.
        Normalmente corresponde a un año fiscal.
    
    Estados:
        - OPEN: Período activo, acepta transacciones
        - CLOSED: Período cerrado, no acepta cambios
    
    Por qué:
        - Organizar estados financieros por período
        - Controlar cierre de ejercicios
        - Cumplimiento fiscal y auditoría
    """
    
    class PeriodStatus(models.TextChoices):
        OPEN = 'open', 'Abierto'
        CLOSING = 'closing', 'En Cierre'
        CLOSED = 'closed', 'Cerrado'
    
    # Nombre del período
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        help_text='Ej: "Ejercicio 2025"'
    )
    
    # Código único
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código',
        help_text='Ej: "2025"'
    )
    
    # Fechas del período
    start_date = models.DateField(
        verbose_name='Fecha Inicio'
    )
    
    end_date = models.DateField(
        verbose_name='Fecha Fin'
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=PeriodStatus.choices,
        default=PeriodStatus.OPEN,
        verbose_name='Estado'
    )
    
    # Período activo (solo puede haber uno)
    is_current = models.BooleanField(
        default=False,
        verbose_name='Es Período Actual'
    )
    
    class Meta:
        db_table = 'finance_accounting_periods'
        verbose_name = 'Período Contable'
        verbose_name_plural = 'Períodos Contables'
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validaciones del modelo."""
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError({
                    'end_date': 'La fecha fin debe ser posterior a la fecha inicio'
                })
    
    def save(self, *args, **kwargs):
        # Si se marca como actual, desmarcar los demás
        if self.is_current:
            AccountingPeriod.objects.filter(
                is_current=True
            ).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class AccountType(BaseModel):
    """
    Tipo de cuenta contable.
    
    Propósito:
        Clasificar las cuentas según su naturaleza contable.
    
    Tipos estándar:
        - ASSET: Activo (débito aumenta)
        - LIABILITY: Pasivo (crédito aumenta)
        - EQUITY: Patrimonio (crédito aumenta)
        - INCOME: Ingreso (crédito aumenta)
        - EXPENSE: Gasto (débito aumenta)
    """
    
    class Nature(models.TextChoices):
        ASSET = 'asset', 'Activo'
        LIABILITY = 'liability', 'Pasivo'
        EQUITY = 'equity', 'Patrimonio'
        INCOME = 'income', 'Ingreso'
        EXPENSE = 'expense', 'Gasto'
    
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Nombre'
    )
    
    nature = models.CharField(
        max_length=20,
        choices=Nature.choices,
        verbose_name='Naturaleza'
    )
    
    # Indica si el saldo normal es débito
    debit_nature = models.BooleanField(
        default=True,
        verbose_name='Naturaleza Débito',
        help_text='True si el saldo normal es débito (Activos, Gastos)'
    )
    
    class Meta:
        db_table = 'finance_account_types'
        verbose_name = 'Tipo de Cuenta'
        verbose_name_plural = 'Tipos de Cuenta'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Account(BaseModel):
    """
    Cuenta contable (Plan de Cuentas).
    
    Propósito:
        Representar cada cuenta del plan contable.
        Soporta jerarquía para cuentas padre/hijo.
    
    Estructura típica:
        1 - Activo
            1.1 - Activo Corriente
                1.1.01 - Caja
                1.1.02 - Bancos
            1.2 - Activo No Corriente
        2 - Pasivo
        3 - Patrimonio
        4 - Ingresos
        5 - Gastos
    
    Por qué jerárquico:
        - Permite consolidar saldos
        - Facilita reportes por nivel
        - Cumple con estándares contables
    """
    
    # Código de cuenta (estructura jerárquica)
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código',
        help_text='Código jerárquico (ej. "1.1.01")'
    )
    
    # Nombre de la cuenta
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre',
        help_text='Nombre descriptivo de la cuenta'
    )
    
    # Tipo de cuenta
    account_type = models.ForeignKey(
        AccountType,
        on_delete=models.PROTECT,
        related_name='accounts',
        verbose_name='Tipo de Cuenta'
    )
    
    # Cuenta padre (para jerarquía)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='children',
        verbose_name='Cuenta Padre'
    )
    
    # Nivel en la jerarquía (calculado)
    level = models.PositiveIntegerField(
        default=1,
        verbose_name='Nivel'
    )
    
    # Indica si permite movimientos (cuentas de detalle)
    is_detail = models.BooleanField(
        default=True,
        verbose_name='Es Cuenta de Detalle',
        help_text='Solo las cuentas de detalle pueden tener movimientos'
    )
    
    # Estado
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    
    # Descripción
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    # Saldo actual (desnormalizado para consultas rápidas)
    current_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Saldo Actual'
    )
    
    class Meta:
        db_table = 'finance_accounts'
        verbose_name = 'Cuenta Contable'
        verbose_name_plural = 'Cuentas Contables'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def save(self, *args, **kwargs):
        # Calcular nivel automáticamente
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 1
        super().save(*args, **kwargs)
    
    @property
    def full_name(self) -> str:
        """Nombre completo incluyendo padres."""
        if self.parent:
            return f"{self.parent.full_name} > {self.name}"
        return self.name
    
    def get_balance(self, period: AccountingPeriod = None) -> Decimal:
        """
        Calcula el saldo de la cuenta.
        
        Args:
            period: Período contable (None = todos)
        
        Returns:
            Decimal: Saldo (débitos - créditos o viceversa según tipo)
        """
        from django.db.models import Sum
        
        entries = self.entries.all()
        if period:
            entries = entries.filter(journal_entry__period=period)
        
        totals = entries.aggregate(
            total_debit=Sum('debit'),
            total_credit=Sum('credit')
        )
        
        debit = totals['total_debit'] or Decimal('0.00')
        credit = totals['total_credit'] or Decimal('0.00')
        
        # El saldo depende de la naturaleza de la cuenta
        if self.account_type.debit_nature:
            return debit - credit
        else:
            return credit - debit


class JournalEntry(BaseModel):
    """
    Asiento contable.
    
    Propósito:
        Registrar transacciones contables siguiendo
        el principio de partida doble (débito = crédito).
    
    Flujo:
        1. Se crea en estado DRAFT
        2. Se valida que débitos = créditos
        3. Se posta (POSTED) para afectar saldos
        4. Puede revertirse con un asiento contrario
    
    Por qué:
        - Base del sistema contable
        - Trazabilidad de cada transacción
        - Cumplimiento con principios contables
    """
    
    class EntryStatus(models.TextChoices):
        DRAFT = 'draft', 'Borrador'
        POSTED = 'posted', 'Contabilizado'
        REVERSED = 'reversed', 'Reversado'
        CANCELLED = 'cancelled', 'Anulado'
    
    # Número de asiento (secuencial por período)
    entry_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de Asiento'
    )
    
    # Período contable
    period = models.ForeignKey(
        AccountingPeriod,
        on_delete=models.PROTECT,
        related_name='entries',
        verbose_name='Período'
    )
    
    # Fecha del asiento
    entry_date = models.DateField(
        verbose_name='Fecha'
    )
    
    # Descripción/Concepto
    description = models.CharField(
        max_length=500,
        verbose_name='Descripción',
        help_text='Concepto del asiento contable'
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=EntryStatus.choices,
        default=EntryStatus.DRAFT,
        verbose_name='Estado'
    )
    
    # Tipo de asiento
    class EntryType(models.TextChoices):
        STANDARD = 'standard', 'Estándar'
        OPENING = 'opening', 'Apertura'
        CLOSING = 'closing', 'Cierre'
        ADJUSTMENT = 'adjustment', 'Ajuste'
        REVERSAL = 'reversal', 'Reversión'
    
    entry_type = models.CharField(
        max_length=20,
        choices=EntryType.choices,
        default=EntryType.STANDARD,
        verbose_name='Tipo'
    )
    
    # Referencia al documento origen
    reference_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Tipo de Referencia',
        help_text='Tipo de documento (invoice, payment, etc.)'
    )
    
    reference_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name='ID de Referencia'
    )
    
    reference_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Número de Referencia'
    )
    
    # Totales (calculados pero almacenados para validación)
    total_debit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Débito'
    )
    
    total_credit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Crédito'
    )
    
    # Notas adicionales
    notes = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    # Fecha de contabilización
    posted_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha Contabilización'
    )
    
    # Asiento de reversión (si fue reversado)
    reversal_entry = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reversed_by',
        verbose_name='Asiento de Reversión'
    )
    
    class Meta:
        db_table = 'finance_journal_entries'
        verbose_name = 'Asiento Contable'
        verbose_name_plural = 'Asientos Contables'
        ordering = ['-entry_date', '-entry_number']
        indexes = [
            models.Index(fields=['entry_date', 'status']),
            models.Index(fields=['period', 'status']),
            models.Index(fields=['reference_type', 'reference_id']),
        ]
    
    def __str__(self):
        return f"{self.entry_number} - {self.description}"
    
    def clean(self):
        """Validaciones del asiento."""
        # Verificar que el período esté abierto
        if self.period and self.period.status == AccountingPeriod.PeriodStatus.CLOSED:
            raise ValidationError({
                'period': 'No se pueden crear asientos en un período cerrado'
            })
        
        # Verificar que la fecha esté dentro del período
        if self.period and self.entry_date:
            if not (self.period.start_date <= self.entry_date <= self.period.end_date):
                raise ValidationError({
                    'entry_date': 'La fecha debe estar dentro del período contable'
                })
    
    @property
    def is_balanced(self) -> bool:
        """Verifica si el asiento está balanceado."""
        return self.total_debit == self.total_credit and self.total_debit > 0
    
    def calculate_totals(self):
        """Recalcula los totales del asiento."""
        from django.db.models import Sum
        
        totals = self.lines.aggregate(
            total_debit=Sum('debit'),
            total_credit=Sum('credit')
        )
        
        self.total_debit = totals['total_debit'] or Decimal('0.00')
        self.total_credit = totals['total_credit'] or Decimal('0.00')
        self.save(update_fields=['total_debit', 'total_credit'])
    
    def post(self, user=None):
        """
        Contabiliza el asiento (actualiza saldos de cuentas).
        
        Propósito:
            Transicionar el asiento a POSTED y actualizar
            los saldos de las cuentas afectadas.
        
        Args:
            user: Usuario que contabiliza
        
        Raises:
            ValidationError: Si el asiento no está balanceado
        """
        from django.utils import timezone
        
        if self.status != self.EntryStatus.DRAFT:
            raise ValidationError('Solo se pueden contabilizar asientos en borrador')
        
        if not self.is_balanced:
            raise ValidationError(
                f'El asiento no está balanceado. '
                f'Débito: {self.total_debit}, Crédito: {self.total_credit}'
            )
        
        # Actualizar saldos de cuentas
        for line in self.lines.all():
            account = line.account
            if account.account_type.debit_nature:
                account.current_balance += (line.debit - line.credit)
            else:
                account.current_balance += (line.credit - line.debit)
            account.save(update_fields=['current_balance'])
        
        self.status = self.EntryStatus.POSTED
        self.posted_date = timezone.now()
        if user:
            self.updated_by = user
        self.save()
    
    def reverse(self, user=None, description=None):
        """
        Crea un asiento de reversión.
        
        Propósito:
            Anular un asiento contabilizado creando
            un asiento con valores invertidos.
        
        Args:
            user: Usuario que reversa
            description: Descripción del asiento de reversión
        
        Returns:
            JournalEntry: Asiento de reversión creado
        """
        if self.status != self.EntryStatus.POSTED:
            raise ValidationError('Solo se pueden reversar asientos contabilizados')
        
        # Crear asiento de reversión
        reversal = JournalEntry.objects.create(
            period=self.period,
            entry_date=self.entry_date,
            entry_type=self.EntryType.REVERSAL,
            description=description or f"Reversión de {self.entry_number}",
            created_by=user,
        )
        
        # Generar número de asiento
        import uuid
        reversal.entry_number = f"REV-{uuid.uuid4().hex[:8].upper()}"
        
        # Crear líneas invertidas
        for line in self.lines.all():
            JournalEntryLine.objects.create(
                journal_entry=reversal,
                account=line.account,
                debit=line.credit,  # Invertir
                credit=line.debit,
                description=f"Reversión: {line.description}",
            )
        
        reversal.calculate_totals()
        reversal.save()
        
        # Contabilizar reversión
        reversal.post(user)
        
        # Marcar asiento original como reversado
        self.status = self.EntryStatus.REVERSED
        self.reversal_entry = reversal
        self.save()
        
        return reversal


class JournalEntryLine(BaseModel):
    """
    Línea de asiento contable.
    
    Propósito:
        Cada línea representa un débito o crédito
        a una cuenta específica.
    
    Regla de partida doble:
        - Todo débito tiene un crédito correspondiente
        - Suma de débitos = Suma de créditos
    
    Por qué líneas separadas:
        - Un asiento puede afectar múltiples cuentas
        - Flexibilidad en la distribución
        - Detalle por cuenta
    """
    
    # Asiento al que pertenece
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='Asiento'
    )
    
    # Cuenta afectada
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='entries',
        verbose_name='Cuenta'
    )
    
    # Monto al débito
    debit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Débito'
    )
    
    # Monto al crédito
    credit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Crédito'
    )
    
    # Descripción de la línea
    description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Descripción'
    )
    
    # Centro de costo (opcional)
    cost_center = models.ForeignKey(
        'CostCenter',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='entries',
        verbose_name='Centro de Costo'
    )
    
    class Meta:
        db_table = 'finance_journal_entry_lines'
        verbose_name = 'Línea de Asiento'
        verbose_name_plural = 'Líneas de Asiento'
        ordering = ['id']
    
    def __str__(self):
        if self.debit > 0:
            return f"{self.account.code} - Débito: {self.debit}"
        return f"{self.account.code} - Crédito: {self.credit}"
    
    def clean(self):
        """Validaciones de la línea."""
        # Una línea debe tener débito O crédito, no ambos
        if self.debit > 0 and self.credit > 0:
            raise ValidationError(
                'Una línea no puede tener débito y crédito al mismo tiempo'
            )
        
        # Debe tener al menos uno
        if self.debit == 0 and self.credit == 0:
            raise ValidationError(
                'La línea debe tener un monto en débito o crédito'
            )
        
        # La cuenta debe ser de detalle
        if not self.account.is_detail:
            raise ValidationError({
                'account': 'Solo se pueden usar cuentas de detalle'
            })


class CostCenter(BaseModel):
    """
    Centro de costo.
    
    Propósito:
        Clasificar gastos e ingresos por área o proyecto
        para análisis gerencial.
    
    Ejemplos:
        - Departamentos: Ventas, Producción, Administración
        - Proyectos: Proyecto A, Proyecto B
        - Sucursales: Sucursal Norte, Sucursal Sur
    
    Por qué:
        - Permite análisis por área de negocio
        - Control de presupuestos por centro
        - Reportes gerenciales detallados
    """
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    # Centro padre (para jerarquía)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
        verbose_name='Centro Padre'
    )
    
    # Responsable
    manager = models.ForeignKey(
        'authentication.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='managed_cost_centers',
        verbose_name='Responsable'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        db_table = 'finance_cost_centers'
        verbose_name = 'Centro de Costo'
        verbose_name_plural = 'Centros de Costo'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Budget(BaseModel):
    """
    Presupuesto.
    
    Propósito:
        Definir presupuestos por cuenta y período
        para control de gastos.
    
    Por qué:
        - Control de gastos vs presupuesto
        - Alertas de sobregiro
        - Planificación financiera
    """
    
    # Período del presupuesto
    period = models.ForeignKey(
        AccountingPeriod,
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name='Período'
    )
    
    # Cuenta
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name='Cuenta'
    )
    
    # Centro de costo (opcional)
    cost_center = models.ForeignKey(
        CostCenter,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name='Centro de Costo'
    )
    
    # Monto presupuestado
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Monto Presupuestado'
    )
    
    # Notas
    notes = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    class Meta:
        db_table = 'finance_budgets'
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'
        unique_together = ['period', 'account', 'cost_center']
    
    def __str__(self):
        return f"{self.period.code} - {self.account.code}: {self.amount}"
    
    @property
    def executed_amount(self) -> Decimal:
        """Monto ejecutado (gastado/ingresado)."""
        return abs(self.account.get_balance(self.period))
    
    @property
    def remaining_amount(self) -> Decimal:
        """Monto disponible."""
        return self.amount - self.executed_amount
    
    @property
    def execution_percentage(self) -> Decimal:
        """Porcentaje de ejecución."""
        if self.amount == 0:
            return Decimal('0.00')
        return (self.executed_amount / self.amount) * 100


class TaxRate(BaseModel):
    """
    Tasa de impuesto.
    
    Propósito:
        Definir tasas impositivas aplicables a
        transacciones (ventas, compras).
    
    Ejemplos:
        - IVA 16%
        - IVA 0%
        - Retención ISR 10%
    """
    
    class TaxType(models.TextChoices):
        VAT = 'vat', 'IVA'
        WITHHOLDING = 'withholding', 'Retención'
        OTHER = 'other', 'Otro'
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    
    tax_type = models.CharField(
        max_length=20,
        choices=TaxType.choices,
        default=TaxType.VAT,
        verbose_name='Tipo'
    )
    
    rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Tasa (%)'
    )
    
    # Cuenta contable del impuesto
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='tax_rates',
        verbose_name='Cuenta Contable'
    )
    
    # Aplica a compras
    applies_to_purchases = models.BooleanField(
        default=True,
        verbose_name='Aplica a Compras'
    )
    
    # Aplica a ventas
    applies_to_sales = models.BooleanField(
        default=True,
        verbose_name='Aplica a Ventas'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        db_table = 'finance_tax_rates'
        verbose_name = 'Tasa de Impuesto'
        verbose_name_plural = 'Tasas de Impuesto'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.rate}%)"


class PaymentMethod(BaseModel):
    """
    Método de pago.
    
    Propósito:
        Definir métodos de pago disponibles.
    
    Ejemplos:
        - Efectivo
        - Transferencia Bancaria
        - Tarjeta de Crédito
        - Cheque
    """
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    
    # Cuenta contable asociada
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='payment_methods',
        verbose_name='Cuenta Contable'
    )
    
    # Requiere referencia (número de transferencia, cheque, etc.)
    requires_reference = models.BooleanField(
        default=False,
        verbose_name='Requiere Referencia'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        db_table = 'finance_payment_methods'
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BankAccount(BaseModel):
    """
    Cuenta bancaria de la empresa.
    
    Propósito:
        Registrar cuentas bancarias para conciliación
        y gestión de tesorería.
    """
    
    class AccountType(models.TextChoices):
        CHECKING = 'checking', 'Cuenta Corriente'
        SAVINGS = 'savings', 'Cuenta de Ahorro'
        CREDIT = 'credit', 'Línea de Crédito'
    
    # Nombre de la cuenta
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    
    # Número de cuenta
    account_number = models.CharField(
        max_length=50,
        verbose_name='Número de Cuenta'
    )
    
    # Banco
    bank_name = models.CharField(
        max_length=100,
        verbose_name='Banco'
    )
    
    # Tipo de cuenta
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.CHECKING,
        verbose_name='Tipo'
    )
    
    # Moneda
    currency = models.CharField(
        max_length=3,
        default='MXN',
        verbose_name='Moneda'
    )
    
    # Cuenta contable asociada
    ledger_account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='bank_accounts',
        verbose_name='Cuenta Contable'
    )
    
    # Saldo actual (para conciliación rápida)
    current_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Saldo Actual'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    
    class Meta:
        db_table = 'finance_bank_accounts'
        verbose_name = 'Cuenta Bancaria'
        verbose_name_plural = 'Cuentas Bancarias'
        ordering = ['bank_name', 'name']
    
    def __str__(self):
        return f"{self.bank_name} - {self.name}"
