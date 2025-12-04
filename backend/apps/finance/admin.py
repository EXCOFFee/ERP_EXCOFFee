# ========================================================
# SISTEMA ERP UNIVERSAL - Admin de Finanzas
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Configuración del administrador de Django
#            para el módulo de finanzas.
# ========================================================

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from decimal import Decimal

from .models import (
    AccountingPeriod,
    AccountType,
    Account,
    JournalEntry,
    JournalEntryLine,
    CostCenter,
    Budget,
    BudgetLine,
    Tax,
    PaymentTerm,
)


# ========================================================
# Inlines
# ========================================================

class JournalEntryLineInline(admin.TabularInline):
    """Inline para líneas de asiento contable."""
    
    model = JournalEntryLine
    extra = 2
    min_num = 2
    fields = ['account', 'description', 'debit', 'credit', 'cost_center']
    autocomplete_fields = ['account', 'cost_center']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('account', 'cost_center')


class BudgetLineInline(admin.TabularInline):
    """Inline para líneas de presupuesto."""
    
    model = BudgetLine
    extra = 1
    fields = ['account', 'budgeted_amount', 'notes']
    autocomplete_fields = ['account']


class AccountInline(admin.TabularInline):
    """Inline para subcuentas."""
    
    model = Account
    fk_name = 'parent'
    extra = 0
    fields = ['code', 'name', 'account_type', 'is_active']
    readonly_fields = ['code', 'name']
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        return False


# ========================================================
# Administradores
# ========================================================

@admin.register(AccountingPeriod)
class AccountingPeriodAdmin(admin.ModelAdmin):
    """Administrador de períodos contables."""
    
    list_display = [
        'code', 'name', 'start_date', 'end_date',
        'status_badge', 'is_current', 'created_at'
    ]
    list_filter = ['is_closed', 'is_current', 'fiscal_year']
    search_fields = ['code', 'name']
    ordering = ['-start_date']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Información General', {
            'fields': ('code', 'name', 'fiscal_year')
        }),
        ('Fechas', {
            'fields': ('start_date', 'end_date')
        }),
        ('Estado', {
            'fields': ('is_closed', 'is_current', 'closed_at', 'closed_by')
        }),
    )
    
    readonly_fields = ['closed_at', 'closed_by']
    
    def status_badge(self, obj):
        """Muestra badge de estado."""
        if obj.is_closed:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">Cerrado</span>'
            )
        return format_html(
            '<span style="background: #28a745; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">Abierto</span>'
        )
    status_badge.short_description = 'Estado'


@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    """Administrador de tipos de cuenta."""
    
    list_display = ['code', 'name', 'classification', 'nature', 'is_active']
    list_filter = ['classification', 'nature', 'is_active']
    search_fields = ['code', 'name']
    ordering = ['code']
    
    fieldsets = (
        ('Información', {
            'fields': ('code', 'name', 'description')
        }),
        ('Clasificación', {
            'fields': ('classification', 'nature')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Administrador de cuentas contables."""
    
    list_display = [
        'code', 'name', 'account_type', 'parent',
        'balance_display', 'is_active', 'allows_movements'
    ]
    list_filter = ['account_type', 'is_active', 'allows_movements', 'level']
    search_fields = ['code', 'name']
    ordering = ['code']
    autocomplete_fields = ['parent', 'account_type']
    
    inlines = [AccountInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('code', 'name', 'description', 'account_type')
        }),
        ('Jerarquía', {
            'fields': ('parent', 'level')
        }),
        ('Configuración', {
            'fields': ('allows_movements', 'is_active')
        }),
        ('Saldos', {
            'fields': ('initial_balance', 'current_balance'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['current_balance', 'level']
    
    def balance_display(self, obj):
        """Muestra el saldo formateado."""
        balance = obj.current_balance or Decimal('0')
        color = 'green' if balance >= 0 else 'red'
        return format_html(
            '<span style="color: {};">${:,.2f}</span>',
            color, balance
        )
    balance_display.short_description = 'Saldo Actual'
    
    def get_search_results(self, request, queryset, search_term):
        """Búsqueda mejorada para autocomplete."""
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        if search_term:
            queryset = queryset.filter(allows_movements=True)
        return queryset, use_distinct


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    """Administrador de asientos contables."""
    
    list_display = [
        'reference', 'date', 'description_short', 'period',
        'total_display', 'status_badge', 'created_by'
    ]
    list_filter = ['status', 'entry_type', 'period', 'created_at']
    search_fields = ['reference', 'description']
    ordering = ['-date', '-created_at']
    date_hierarchy = 'date'
    autocomplete_fields = ['period']
    
    inlines = [JournalEntryLineInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('reference', 'date', 'description', 'period')
        }),
        ('Clasificación', {
            'fields': ('entry_type', 'status')
        }),
        ('Auditoría', {
            'fields': ('created_by', 'posted_by', 'posted_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['posted_by', 'posted_at']
    
    def description_short(self, obj):
        """Descripción truncada."""
        if len(obj.description) > 50:
            return f"{obj.description[:50]}..."
        return obj.description
    description_short.short_description = 'Descripción'
    
    def total_display(self, obj):
        """Muestra el total del asiento."""
        total = obj.lines.aggregate(total=Sum('debit'))['total'] or Decimal('0')
        return format_html('${:,.2f}', total)
    total_display.short_description = 'Total'
    
    def status_badge(self, obj):
        """Muestra badge de estado."""
        colors = {
            'draft': '#6c757d',
            'posted': '#28a745',
            'reversed': '#dc3545',
        }
        labels = {
            'draft': 'Borrador',
            'posted': 'Contabilizado',
            'reversed': 'Reversado',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            labels.get(obj.status, obj.status)
        )
    status_badge.short_description = 'Estado'
    
    def save_model(self, request, obj, form, change):
        """Asigna usuario al crear."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['post_entries', 'reverse_entries']
    
    @admin.action(description='Contabilizar asientos seleccionados')
    def post_entries(self, request, queryset):
        """Contabiliza asientos en borrador."""
        count = 0
        for entry in queryset.filter(status='draft'):
            # Validar cuadre
            totals = entry.lines.aggregate(
                total_debit=Sum('debit'),
                total_credit=Sum('credit')
            )
            if totals['total_debit'] == totals['total_credit']:
                entry.status = 'posted'
                entry.posted_by = request.user
                entry.save()
                count += 1
        
        self.message_user(request, f'{count} asientos contabilizados.')
    
    @admin.action(description='Reversar asientos seleccionados')
    def reverse_entries(self, request, queryset):
        """Reversa asientos contabilizados."""
        count = queryset.filter(status='posted').update(status='reversed')
        self.message_user(request, f'{count} asientos reversados.')


@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    """Administrador de centros de costo."""
    
    list_display = ['code', 'name', 'parent', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['code']
    autocomplete_fields = ['parent', 'responsible']
    
    fieldsets = (
        ('Información', {
            'fields': ('code', 'name', 'description')
        }),
        ('Jerarquía', {
            'fields': ('parent', 'responsible')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    """Administrador de presupuestos."""
    
    list_display = [
        'code', 'name', 'start_date', 'end_date',
        'total_display', 'status_badge', 'created_at'
    ]
    list_filter = ['status', 'budget_type', 'fiscal_year']
    search_fields = ['code', 'name']
    ordering = ['-start_date']
    date_hierarchy = 'start_date'
    
    inlines = [BudgetLineInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('code', 'name', 'description', 'fiscal_year')
        }),
        ('Período', {
            'fields': ('start_date', 'end_date')
        }),
        ('Configuración', {
            'fields': ('budget_type', 'cost_center', 'status')
        }),
        ('Aprobación', {
            'fields': ('approved_by', 'approved_at'),
            'classes': ('collapse',)
        }),
    )
    
    autocomplete_fields = ['cost_center', 'approved_by']
    readonly_fields = ['approved_at']
    
    def total_display(self, obj):
        """Muestra el total presupuestado."""
        total = obj.lines.aggregate(
            total=Sum('budgeted_amount')
        )['total'] or Decimal('0')
        return format_html('${:,.2f}', total)
    total_display.short_description = 'Total'
    
    def status_badge(self, obj):
        """Muestra badge de estado."""
        colors = {
            'draft': '#6c757d',
            'pending': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545',
        }
        labels = {
            'draft': 'Borrador',
            'pending': 'Pendiente',
            'approved': 'Aprobado',
            'rejected': 'Rechazado',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            labels.get(obj.status, obj.status)
        )
    status_badge.short_description = 'Estado'
    
    actions = ['approve_budgets', 'reject_budgets']
    
    @admin.action(description='Aprobar presupuestos seleccionados')
    def approve_budgets(self, request, queryset):
        """Aprueba presupuestos pendientes."""
        from django.utils import timezone
        count = queryset.filter(status='pending').update(
            status='approved',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{count} presupuestos aprobados.')
    
    @admin.action(description='Rechazar presupuestos seleccionados')
    def reject_budgets(self, request, queryset):
        """Rechaza presupuestos pendientes."""
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{count} presupuestos rechazados.')


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    """Administrador de impuestos."""
    
    list_display = ['code', 'name', 'rate_display', 'tax_type', 'is_active']
    list_filter = ['tax_type', 'is_active']
    search_fields = ['code', 'name']
    ordering = ['code']
    
    fieldsets = (
        ('Información', {
            'fields': ('code', 'name', 'description')
        }),
        ('Configuración', {
            'fields': ('tax_type', 'rate', 'is_percentage')
        }),
        ('Cuentas Contables', {
            'fields': ('sales_account', 'purchase_account')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )
    
    autocomplete_fields = ['sales_account', 'purchase_account']
    
    def rate_display(self, obj):
        """Muestra la tasa formateada."""
        if obj.is_percentage:
            return f"{obj.rate}%"
        return f"${obj.rate:,.2f}"
    rate_display.short_description = 'Tasa'


@admin.register(PaymentTerm)
class PaymentTermAdmin(admin.ModelAdmin):
    """Administrador de términos de pago."""
    
    list_display = ['code', 'name', 'days', 'discount_display', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['days']
    
    fieldsets = (
        ('Información', {
            'fields': ('code', 'name', 'description')
        }),
        ('Configuración', {
            'fields': ('days', 'discount_percentage', 'discount_days')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )
    
    def discount_display(self, obj):
        """Muestra descuento si aplica."""
        if obj.discount_percentage and obj.discount_days:
            return f"{obj.discount_percentage}% si paga en {obj.discount_days} días"
        return "Sin descuento"
    discount_display.short_description = 'Descuento'
