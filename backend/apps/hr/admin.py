# ========================================================
# SISTEMA ERP UNIVERSAL - Admin de RRHH
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Configuración del administrador de Django
#            para el módulo de Recursos Humanos.
# ========================================================

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from decimal import Decimal

from .models import (
    Department,
    Position,
    Employee,
    EmergencyContact,
    EmployeeDocument,
    LeaveType,
    LeaveRequest,
    LeaveBalance,
    Attendance,
    WorkSchedule,
    Holiday,
    PayrollPeriod,
    SalaryComponent,
    Payslip,
    PayslipLine,
    Loan,
    LoanPayment,
    PerformanceReviewTemplate,
    PerformanceCriteria,
    PerformanceReview,
    PerformanceScore,
    Training,
    TrainingParticipant,
)


# ========================================================
# Inlines
# ========================================================

class EmergencyContactInline(admin.TabularInline):
    """Inline para contactos de emergencia."""
    
    model = EmergencyContact
    extra = 1
    fields = ['name', 'relationship', 'phone', 'mobile', 'is_primary']


class EmployeeDocumentInline(admin.TabularInline):
    """Inline para documentos de empleado."""
    
    model = EmployeeDocument
    extra = 0
    fields = ['document_type', 'name', 'file', 'expiry_date']
    readonly_fields = ['file']


class PayslipLineInline(admin.TabularInline):
    """Inline para líneas de nómina."""
    
    model = PayslipLine
    extra = 0
    fields = ['component', 'quantity', 'rate', 'amount', 'notes']
    readonly_fields = ['amount']


class LoanPaymentInline(admin.TabularInline):
    """Inline para pagos de préstamo."""
    
    model = LoanPayment
    extra = 0
    fields = ['payment_date', 'installment_number', 'principal_amount', 'interest_amount', 'total_amount']
    readonly_fields = ['payment_date', 'installment_number', 'principal_amount', 'interest_amount', 'total_amount']


class PerformanceCriteriaInline(admin.TabularInline):
    """Inline para criterios de evaluación."""
    
    model = PerformanceCriteria
    extra = 1
    fields = ['name', 'description', 'weight', 'order']


class PerformanceScoreInline(admin.TabularInline):
    """Inline para puntuaciones."""
    
    model = PerformanceScore
    extra = 0
    fields = ['criteria', 'score', 'comments']
    readonly_fields = ['criteria']


class TrainingParticipantInline(admin.TabularInline):
    """Inline para participantes de capacitación."""
    
    model = TrainingParticipant
    extra = 0
    fields = ['employee', 'status', 'score', 'attendance_percentage', 'certificate_issued']
    autocomplete_fields = ['employee']


# ========================================================
# Estructura Organizacional
# ========================================================

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Administrador de departamentos."""
    
    list_display = ['code', 'name', 'parent', 'manager', 'employee_count', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['code', 'name']
    ordering = ['code']
    autocomplete_fields = ['parent', 'manager', 'cost_center']
    
    fieldsets = (
        ('Información General', {
            'fields': ('code', 'name', 'description')
        }),
        ('Jerarquía', {
            'fields': ('parent', 'manager')
        }),
        ('Configuración', {
            'fields': ('cost_center', 'is_active')
        }),
    )
    
    def employee_count(self, obj):
        return obj.employees.filter(status='active').count()
    employee_count.short_description = 'Empleados'


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    """Administrador de puestos."""
    
    list_display = ['code', 'name', 'department', 'level', 'salary_range', 'is_active']
    list_filter = ['department', 'level', 'is_active']
    search_fields = ['code', 'name']
    ordering = ['department', 'level', 'code']
    autocomplete_fields = ['department', 'reports_to']
    
    fieldsets = (
        ('Información General', {
            'fields': ('code', 'name', 'description', 'department')
        }),
        ('Jerarquía', {
            'fields': ('level', 'reports_to')
        }),
        ('Salario', {
            'fields': ('min_salary', 'max_salary')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )
    
    def salary_range(self, obj):
        return f"${obj.min_salary:,.0f} - ${obj.max_salary:,.0f}"
    salary_range.short_description = 'Rango Salarial'


# ========================================================
# Empleados
# ========================================================

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Administrador de empleados."""
    
    list_display = [
        'employee_code', 'full_name_display', 'department', 'position',
        'status_badge', 'hire_date', 'salary_display'
    ]
    list_filter = ['status', 'department', 'contract_type', 'is_active']
    search_fields = ['employee_code', 'first_name', 'last_name', 'id_number', 'email']
    ordering = ['last_name', 'first_name']
    date_hierarchy = 'hire_date'
    autocomplete_fields = ['department', 'position', 'manager', 'user']
    
    inlines = [EmergencyContactInline, EmployeeDocumentInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'employee_code', 'user', ('first_name', 'last_name'),
                ('id_type', 'id_number'), 'photo'
            )
        }),
        ('Información Personal', {
            'fields': (
                ('gender', 'birth_date'), 'marital_status', 'nationality'
            ),
            'classes': ('collapse',)
        }),
        ('Contacto', {
            'fields': (
                ('email', 'work_email'), ('phone', 'mobile'),
                'address', ('city', 'country')
            )
        }),
        ('Información Laboral', {
            'fields': (
                ('department', 'position'), 'manager',
                ('hire_date', 'termination_date'),
                ('contract_type', 'contract_end_date')
            )
        }),
        ('Información Salarial', {
            'fields': (
                ('salary', 'salary_currency'), 'payment_frequency',
                ('bank_name', 'bank_account')
            ),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('status', 'is_active')
        }),
    )
    
    def full_name_display(self, obj):
        return obj.full_name
    full_name_display.short_description = 'Nombre Completo'
    
    def status_badge(self, obj):
        colors = {
            'active': '#28a745',
            'inactive': '#6c757d',
            'on_leave': '#ffc107',
            'terminated': '#dc3545',
            'suspended': '#fd7e14',
        }
        labels = {
            'active': 'Activo',
            'inactive': 'Inactivo',
            'on_leave': 'En Licencia',
            'terminated': 'Terminado',
            'suspended': 'Suspendido',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            labels.get(obj.status, obj.status)
        )
    status_badge.short_description = 'Estado'
    
    def salary_display(self, obj):
        return f"${obj.salary:,.2f}"
    salary_display.short_description = 'Salario'


# ========================================================
# Gestión de Tiempo
# ========================================================

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    """Administrador de tipos de ausencia."""
    
    list_display = ['code', 'name', 'is_paid', 'max_days_per_year', 'requires_approval', 'is_active']
    list_filter = ['is_paid', 'requires_approval', 'is_active']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    """Administrador de solicitudes de ausencia."""
    
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'days_display', 'status_badge', 'approved_by']
    list_filter = ['status', 'leave_type', 'start_date']
    search_fields = ['employee__first_name', 'employee__last_name']
    ordering = ['-start_date']
    date_hierarchy = 'start_date'
    autocomplete_fields = ['employee', 'leave_type', 'approved_by']
    
    fieldsets = (
        ('Solicitud', {
            'fields': ('employee', 'leave_type', ('start_date', 'end_date'), ('start_half_day', 'end_half_day'), 'reason')
        }),
        ('Estado', {
            'fields': ('status', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Adjuntos', {
            'fields': ('attachment',)
        }),
    )
    
    readonly_fields = ['approved_at']
    
    def days_display(self, obj):
        return f"{obj.days} días"
    days_display.short_description = 'Días'
    
    def status_badge(self, obj):
        colors = {
            'draft': '#6c757d',
            'pending': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545',
            'cancelled': '#17a2b8',
        }
        labels = {
            'draft': 'Borrador',
            'pending': 'Pendiente',
            'approved': 'Aprobado',
            'rejected': 'Rechazado',
            'cancelled': 'Cancelado',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            labels.get(obj.status, obj.status)
        )
    status_badge.short_description = 'Estado'
    
    actions = ['approve_requests', 'reject_requests']
    
    @admin.action(description='Aprobar solicitudes seleccionadas')
    def approve_requests(self, request, queryset):
        from django.utils import timezone
        count = queryset.filter(status='pending').update(
            status='approved',
            approved_by=request.user.employee_profile if hasattr(request.user, 'employee_profile') else None,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{count} solicitudes aprobadas.')
    
    @admin.action(description='Rechazar solicitudes seleccionadas')
    def reject_requests(self, request, queryset):
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{count} solicitudes rechazadas.')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Administrador de asistencia."""
    
    list_display = ['employee', 'date', 'check_in', 'check_out', 'worked_hours', 'overtime_hours', 'status']
    list_filter = ['status', 'date']
    search_fields = ['employee__first_name', 'employee__last_name']
    ordering = ['-date']
    date_hierarchy = 'date'
    autocomplete_fields = ['employee']


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    """Administrador de horarios."""
    
    list_display = ['name', 'is_default', 'is_active']
    list_filter = ['is_default', 'is_active']
    search_fields = ['name']


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    """Administrador de feriados."""
    
    list_display = ['name', 'date', 'is_recurring', 'is_half_day', 'applies_to_all']
    list_filter = ['is_recurring', 'applies_to_all', 'date']
    search_fields = ['name']
    ordering = ['date']
    filter_horizontal = ['departments']


# ========================================================
# Nómina
# ========================================================

@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    """Administrador de períodos de nómina."""
    
    list_display = ['code', 'name', 'start_date', 'end_date', 'payment_date', 'status_badge', 'totals_display']
    list_filter = ['status']
    search_fields = ['code', 'name']
    ordering = ['-start_date']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Información', {
            'fields': ('code', 'name')
        }),
        ('Fechas', {
            'fields': (('start_date', 'end_date'), 'payment_date')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Totales', {
            'fields': (('total_gross', 'total_deductions', 'total_net'),),
            'classes': ('collapse',)
        }),
        ('Procesamiento', {
            'fields': ('processed_by', 'processed_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['total_gross', 'total_deductions', 'total_net', 'processed_by', 'processed_at']
    
    def status_badge(self, obj):
        colors = {
            'draft': '#6c757d',
            'processing': '#17a2b8',
            'approved': '#28a745',
            'paid': '#28a745',
            'closed': '#6c757d',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def totals_display(self, obj):
        return format_html(
            '<strong>Bruto:</strong> ${:,.2f}<br>'
            '<strong>Deduc:</strong> ${:,.2f}<br>'
            '<strong>Neto:</strong> ${:,.2f}',
            obj.total_gross, obj.total_deductions, obj.total_net
        )
    totals_display.short_description = 'Totales'


@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    """Administrador de componentes salariales."""
    
    list_display = ['code', 'name', 'component_type', 'calculation_type', 'amount_display', 'is_taxable', 'is_active']
    list_filter = ['component_type', 'calculation_type', 'is_taxable', 'is_active']
    search_fields = ['code', 'name']
    ordering = ['component_type', 'code']
    autocomplete_fields = ['base_component', 'account']
    
    def amount_display(self, obj):
        if obj.calculation_type == 'fixed':
            return f"${obj.default_amount:,.2f}"
        elif obj.calculation_type == 'percentage':
            return f"{obj.percentage}%"
        return "Fórmula"
    amount_display.short_description = 'Monto/Tasa'


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    """Administrador de recibos de nómina."""
    
    list_display = ['employee', 'period', 'gross_salary', 'total_deductions', 'net_salary', 'status']
    list_filter = ['status', 'period']
    search_fields = ['employee__first_name', 'employee__last_name']
    ordering = ['-period__start_date', 'employee__last_name']
    autocomplete_fields = ['employee', 'period']
    
    inlines = [PayslipLineInline]
    
    readonly_fields = ['gross_salary', 'total_deductions', 'net_salary']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    """Administrador de préstamos."""
    
    list_display = ['employee', 'loan_type', 'amount', 'installments', 'remaining', 'status_badge']
    list_filter = ['status', 'loan_type']
    search_fields = ['employee__first_name', 'employee__last_name']
    ordering = ['-start_date']
    autocomplete_fields = ['employee', 'approved_by']
    
    inlines = [LoanPaymentInline]
    
    def remaining(self, obj):
        return f"${obj.remaining_amount:,.2f} ({obj.installments - obj.paid_installments} cuotas)"
    remaining.short_description = 'Pendiente'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'approved': '#17a2b8',
            'active': '#28a745',
            'paid': '#6c757d',
            'cancelled': '#dc3545',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'


# ========================================================
# Evaluaciones de Desempeño
# ========================================================

@admin.register(PerformanceReviewTemplate)
class PerformanceReviewTemplateAdmin(admin.ModelAdmin):
    """Administrador de plantillas de evaluación."""
    
    list_display = ['name', 'criteria_count', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    
    inlines = [PerformanceCriteriaInline]
    
    def criteria_count(self, obj):
        return obj.criteria.count()
    criteria_count.short_description = 'Criterios'


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    """Administrador de evaluaciones."""
    
    list_display = ['employee', 'reviewer', 'review_date', 'overall_score', 'status_badge']
    list_filter = ['status', 'review_date']
    search_fields = ['employee__first_name', 'employee__last_name']
    ordering = ['-review_date']
    date_hierarchy = 'review_date'
    autocomplete_fields = ['employee', 'reviewer', 'template']
    
    inlines = [PerformanceScoreInline]
    
    def status_badge(self, obj):
        colors = {
            'draft': '#6c757d',
            'in_progress': '#17a2b8',
            'pending_approval': '#ffc107',
            'completed': '#28a745',
            'cancelled': '#dc3545',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'


# ========================================================
# Capacitación
# ========================================================

@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    """Administrador de capacitaciones."""
    
    list_display = ['code', 'name', 'training_type', 'start_date', 'end_date', 'participants_count', 'status_badge']
    list_filter = ['status', 'training_type', 'start_date']
    search_fields = ['code', 'name', 'provider', 'instructor']
    ordering = ['-start_date']
    date_hierarchy = 'start_date'
    
    inlines = [TrainingParticipantInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('code', 'name', 'description', 'training_type')
        }),
        ('Instructor/Proveedor', {
            'fields': ('provider', 'instructor')
        }),
        ('Fechas', {
            'fields': (('start_date', 'end_date'), 'duration_hours', 'location')
        }),
        ('Participantes', {
            'fields': ('max_participants',)
        }),
        ('Costos', {
            'fields': (('cost_per_person', 'total_cost'),),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('status',)
        }),
    )
    
    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = 'Participantes'
    
    def status_badge(self, obj):
        colors = {
            'planned': '#17a2b8',
            'in_progress': '#ffc107',
            'completed': '#28a745',
            'cancelled': '#dc3545',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
