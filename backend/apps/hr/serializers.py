# ========================================================
# SISTEMA ERP UNIVERSAL - Serializadores de RRHH
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Serializadores para el módulo de RRHH.
# ========================================================

from rest_framework import serializers
from django.db import transaction
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
# Estructura Organizacional
# ========================================================

class DepartmentSerializer(serializers.ModelSerializer):
    """Serializador de departamentos."""
    
    employee_count = serializers.IntegerField(read_only=True)
    manager_name = serializers.CharField(
        source='manager.full_name',
        read_only=True
    )
    parent_name = serializers.CharField(
        source='parent.name',
        read_only=True
    )
    
    class Meta:
        model = Department
        fields = [
            'id', 'code', 'name', 'description', 'parent', 'parent_name',
            'manager', 'manager_name', 'cost_center', 'is_active',
            'employee_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DepartmentTreeSerializer(serializers.ModelSerializer):
    """Serializador para árbol de departamentos."""
    
    children = serializers.SerializerMethodField()
    employee_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Department
        fields = ['id', 'code', 'name', 'children', 'employee_count']
    
    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return DepartmentTreeSerializer(children, many=True).data


class PositionSerializer(serializers.ModelSerializer):
    """Serializador de puestos."""
    
    department_name = serializers.CharField(
        source='department.name',
        read_only=True
    )
    reports_to_name = serializers.CharField(
        source='reports_to.name',
        read_only=True
    )
    
    class Meta:
        model = Position
        fields = [
            'id', 'code', 'name', 'description', 'department', 'department_name',
            'level', 'reports_to', 'reports_to_name', 'min_salary', 'max_salary',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ========================================================
# Empleados
# ========================================================

class EmergencyContactSerializer(serializers.ModelSerializer):
    """Serializador de contactos de emergencia."""
    
    class Meta:
        model = EmergencyContact
        fields = [
            'id', 'name', 'relationship', 'phone', 'mobile', 'email', 'is_primary'
        ]


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    """Serializador de documentos de empleado."""
    
    class Meta:
        model = EmployeeDocument
        fields = [
            'id', 'document_type', 'name', 'description', 'file',
            'expiry_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EmployeeListSerializer(serializers.ModelSerializer):
    """Serializador de lista de empleados."""
    
    full_name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(
        source='department.name',
        read_only=True
    )
    position_name = serializers.CharField(
        source='position.name',
        read_only=True
    )
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_code', 'full_name', 'first_name', 'last_name',
            'department', 'department_name', 'position', 'position_name',
            'status', 'is_active', 'photo'
        ]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Serializador detallado de empleados."""
    
    full_name = serializers.CharField(read_only=True)
    years_of_service = serializers.IntegerField(read_only=True)
    department_name = serializers.CharField(
        source='department.name',
        read_only=True
    )
    position_name = serializers.CharField(
        source='position.name',
        read_only=True
    )
    manager_name = serializers.CharField(
        source='manager.full_name',
        read_only=True
    )
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_code', 'user', 'first_name', 'last_name', 'full_name',
            'id_number', 'id_type', 'gender', 'birth_date', 'marital_status',
            'nationality', 'email', 'work_email', 'phone', 'mobile', 'address',
            'city', 'country', 'department', 'department_name', 'position',
            'position_name', 'manager', 'manager_name', 'hire_date',
            'termination_date', 'contract_type', 'contract_end_date', 'salary',
            'salary_currency', 'payment_frequency', 'bank_account', 'bank_name',
            'status', 'is_active', 'photo', 'years_of_service',
            'emergency_contacts', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'years_of_service', 'created_at', 'updated_at']


class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializador para crear/actualizar empleados."""
    
    emergency_contacts = EmergencyContactSerializer(many=True, required=False)
    
    class Meta:
        model = Employee
        fields = [
            'employee_code', 'user', 'first_name', 'last_name', 'id_number',
            'id_type', 'gender', 'birth_date', 'marital_status', 'nationality',
            'email', 'work_email', 'phone', 'mobile', 'address', 'city',
            'country', 'department', 'position', 'manager', 'hire_date',
            'termination_date', 'contract_type', 'contract_end_date', 'salary',
            'salary_currency', 'payment_frequency', 'bank_account', 'bank_name',
            'status', 'is_active', 'photo', 'emergency_contacts'
        ]
    
    @transaction.atomic
    def create(self, validated_data):
        contacts_data = validated_data.pop('emergency_contacts', [])
        employee = Employee.objects.create(**validated_data)
        
        for contact_data in contacts_data:
            EmergencyContact.objects.create(employee=employee, **contact_data)
        
        return employee
    
    @transaction.atomic
    def update(self, instance, validated_data):
        contacts_data = validated_data.pop('emergency_contacts', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if contacts_data is not None:
            instance.emergency_contacts.all().delete()
            for contact_data in contacts_data:
                EmergencyContact.objects.create(employee=instance, **contact_data)
        
        return instance


# ========================================================
# Gestión de Tiempo
# ========================================================

class LeaveTypeSerializer(serializers.ModelSerializer):
    """Serializador de tipos de ausencia."""
    
    class Meta:
        model = LeaveType
        fields = [
            'id', 'code', 'name', 'description', 'is_paid', 'max_days_per_year',
            'requires_approval', 'requires_attachment', 'color', 'is_active'
        ]


class LeaveRequestSerializer(serializers.ModelSerializer):
    """Serializador de solicitudes de ausencia."""
    
    employee_name = serializers.CharField(
        source='employee.full_name',
        read_only=True
    )
    leave_type_name = serializers.CharField(
        source='leave_type.name',
        read_only=True
    )
    days = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True
    )
    approved_by_name = serializers.CharField(
        source='approved_by.full_name',
        read_only=True
    )
    
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_name', 'leave_type', 'leave_type_name',
            'start_date', 'end_date', 'start_half_day', 'end_half_day', 'days',
            'reason', 'status', 'approved_by', 'approved_by_name', 'approved_at',
            'rejection_reason', 'attachment', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'days', 'approved_by', 'approved_at', 'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError({
                    'end_date': 'La fecha de fin no puede ser anterior a la fecha de inicio.'
                })
        return data


class LeaveBalanceSerializer(serializers.ModelSerializer):
    """Serializador de saldos de ausencias."""
    
    available_days = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True
    )
    leave_type_name = serializers.CharField(
        source='leave_type.name',
        read_only=True
    )
    
    class Meta:
        model = LeaveBalance
        fields = [
            'id', 'employee', 'leave_type', 'leave_type_name', 'year',
            'allocated_days', 'used_days', 'carried_over', 'available_days'
        ]


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializador de asistencia."""
    
    employee_name = serializers.CharField(
        source='employee.full_name',
        read_only=True
    )
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'employee', 'employee_name', 'date', 'check_in', 'check_out',
            'worked_hours', 'overtime_hours', 'status', 'notes'
        ]
        read_only_fields = ['id']


class WorkScheduleSerializer(serializers.ModelSerializer):
    """Serializador de horarios."""
    
    class Meta:
        model = WorkSchedule
        fields = [
            'id', 'name', 'description',
            'monday_start', 'monday_end',
            'tuesday_start', 'tuesday_end',
            'wednesday_start', 'wednesday_end',
            'thursday_start', 'thursday_end',
            'friday_start', 'friday_end',
            'saturday_start', 'saturday_end',
            'sunday_start', 'sunday_end',
            'is_default', 'is_active'
        ]


class HolidaySerializer(serializers.ModelSerializer):
    """Serializador de feriados."""
    
    class Meta:
        model = Holiday
        fields = [
            'id', 'name', 'date', 'is_recurring', 'is_half_day',
            'applies_to_all', 'departments'
        ]


# ========================================================
# Nómina
# ========================================================

class PayrollPeriodSerializer(serializers.ModelSerializer):
    """Serializador de períodos de nómina."""
    
    payslips_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PayrollPeriod
        fields = [
            'id', 'code', 'name', 'start_date', 'end_date', 'payment_date',
            'status', 'total_gross', 'total_deductions', 'total_net',
            'processed_by', 'processed_at', 'payslips_count', 'created_at'
        ]
        read_only_fields = [
            'id', 'total_gross', 'total_deductions', 'total_net',
            'processed_by', 'processed_at', 'created_at'
        ]
    
    def get_payslips_count(self, obj):
        return obj.payslips.count()


class SalaryComponentSerializer(serializers.ModelSerializer):
    """Serializador de componentes salariales."""
    
    class Meta:
        model = SalaryComponent
        fields = [
            'id', 'code', 'name', 'description', 'component_type',
            'calculation_type', 'default_amount', 'percentage', 'base_component',
            'is_taxable', 'is_statutory', 'affects_social_security', 'account',
            'is_active'
        ]


class PayslipLineSerializer(serializers.ModelSerializer):
    """Serializador de líneas de nómina."""
    
    component_name = serializers.CharField(
        source='component.name',
        read_only=True
    )
    component_type = serializers.CharField(
        source='component.component_type',
        read_only=True
    )
    
    class Meta:
        model = PayslipLine
        fields = [
            'id', 'component', 'component_name', 'component_type',
            'quantity', 'rate', 'amount', 'notes'
        ]


class PayslipSerializer(serializers.ModelSerializer):
    """Serializador de recibos de nómina."""
    
    employee_name = serializers.CharField(
        source='employee.full_name',
        read_only=True
    )
    period_name = serializers.CharField(
        source='period.name',
        read_only=True
    )
    lines = PayslipLineSerializer(many=True, read_only=True)
    
    class Meta:
        model = Payslip
        fields = [
            'id', 'period', 'period_name', 'employee', 'employee_name',
            'base_salary', 'gross_salary', 'total_deductions', 'net_salary',
            'worked_days', 'worked_hours', 'overtime_hours', 'status',
            'payment_method', 'payment_reference', 'notes', 'lines',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'gross_salary', 'total_deductions', 'net_salary',
            'created_at', 'updated_at'
        ]


class PayslipDetailSerializer(PayslipSerializer):
    """Serializador detallado de recibos."""
    
    earnings = serializers.SerializerMethodField()
    deductions = serializers.SerializerMethodField()
    
    class Meta(PayslipSerializer.Meta):
        fields = PayslipSerializer.Meta.fields + ['earnings', 'deductions']
    
    def get_earnings(self, obj):
        earning_lines = obj.lines.filter(component__component_type='earning')
        return PayslipLineSerializer(earning_lines, many=True).data
    
    def get_deductions(self, obj):
        deduction_lines = obj.lines.filter(component__component_type='deduction')
        return PayslipLineSerializer(deduction_lines, many=True).data


class LoanSerializer(serializers.ModelSerializer):
    """Serializador de préstamos."""
    
    employee_name = serializers.CharField(
        source='employee.full_name',
        read_only=True
    )
    remaining_installments = serializers.SerializerMethodField()
    
    class Meta:
        model = Loan
        fields = [
            'id', 'employee', 'employee_name', 'loan_type', 'amount',
            'interest_rate', 'installments', 'installment_amount', 'start_date',
            'end_date', 'remaining_amount', 'paid_installments',
            'remaining_installments', 'status', 'approved_by', 'reason',
            'created_at'
        ]
        read_only_fields = [
            'id', 'remaining_amount', 'paid_installments', 'approved_by',
            'created_at'
        ]
    
    def get_remaining_installments(self, obj):
        return obj.installments - obj.paid_installments


class LoanPaymentSerializer(serializers.ModelSerializer):
    """Serializador de pagos de préstamo."""
    
    class Meta:
        model = LoanPayment
        fields = [
            'id', 'loan', 'payslip', 'payment_date', 'principal_amount',
            'interest_amount', 'total_amount', 'installment_number'
        ]


# ========================================================
# Evaluaciones de Desempeño
# ========================================================

class PerformanceCriteriaSerializer(serializers.ModelSerializer):
    """Serializador de criterios de evaluación."""
    
    class Meta:
        model = PerformanceCriteria
        fields = ['id', 'name', 'description', 'weight', 'order']


class PerformanceReviewTemplateSerializer(serializers.ModelSerializer):
    """Serializador de plantillas de evaluación."""
    
    criteria = PerformanceCriteriaSerializer(many=True, read_only=True)
    
    class Meta:
        model = PerformanceReviewTemplate
        fields = ['id', 'name', 'description', 'is_active', 'criteria']


class PerformanceScoreSerializer(serializers.ModelSerializer):
    """Serializador de puntuaciones."""
    
    criteria_name = serializers.CharField(
        source='criteria.name',
        read_only=True
    )
    
    class Meta:
        model = PerformanceScore
        fields = ['id', 'criteria', 'criteria_name', 'score', 'comments']


class PerformanceReviewSerializer(serializers.ModelSerializer):
    """Serializador de evaluaciones de desempeño."""
    
    employee_name = serializers.CharField(
        source='employee.full_name',
        read_only=True
    )
    reviewer_name = serializers.CharField(
        source='reviewer.full_name',
        read_only=True
    )
    template_name = serializers.CharField(
        source='template.name',
        read_only=True
    )
    scores = PerformanceScoreSerializer(many=True, read_only=True)
    
    class Meta:
        model = PerformanceReview
        fields = [
            'id', 'employee', 'employee_name', 'reviewer', 'reviewer_name',
            'template', 'template_name', 'period_start', 'period_end',
            'review_date', 'overall_score', 'status', 'employee_comments',
            'reviewer_comments', 'goals_next_period', 'training_recommendations',
            'scores', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'overall_score', 'created_at', 'updated_at']


# ========================================================
# Capacitación
# ========================================================

class TrainingParticipantSerializer(serializers.ModelSerializer):
    """Serializador de participantes de capacitación."""
    
    employee_name = serializers.CharField(
        source='employee.full_name',
        read_only=True
    )
    employee_department = serializers.CharField(
        source='employee.department.name',
        read_only=True
    )
    
    class Meta:
        model = TrainingParticipant
        fields = [
            'id', 'employee', 'employee_name', 'employee_department', 'status',
            'score', 'attendance_percentage', 'certificate_issued',
            'certificate_date', 'feedback'
        ]


class TrainingSerializer(serializers.ModelSerializer):
    """Serializador de capacitaciones."""
    
    participants_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Training
        fields = [
            'id', 'code', 'name', 'description', 'training_type', 'provider',
            'instructor', 'start_date', 'end_date', 'duration_hours', 'location',
            'max_participants', 'cost_per_person', 'total_cost', 'status',
            'participants_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_participants_count(self, obj):
        return obj.participants.count()


class TrainingDetailSerializer(TrainingSerializer):
    """Serializador detallado de capacitaciones."""
    
    participants = TrainingParticipantSerializer(many=True, read_only=True)
    
    class Meta(TrainingSerializer.Meta):
        fields = TrainingSerializer.Meta.fields + ['participants']


# ========================================================
# Reportes
# ========================================================

class EmployeeReportSerializer(serializers.Serializer):
    """Serializador para reportes de empleados."""
    
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    by_department = serializers.ListField()
    by_contract_type = serializers.ListField()
    by_status = serializers.ListField()
    average_years_of_service = serializers.DecimalField(max_digits=5, decimal_places=2)


class AttendanceReportSerializer(serializers.Serializer):
    """Serializador para reportes de asistencia."""
    
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    total_working_days = serializers.IntegerField()
    attendance_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    by_status = serializers.ListField()
    top_absences = serializers.ListField()


class PayrollSummarySerializer(serializers.Serializer):
    """Serializador para resumen de nómina."""
    
    period = serializers.CharField()
    total_employees = serializers.IntegerField()
    total_gross = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_deductions = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_net = serializers.DecimalField(max_digits=18, decimal_places=2)
    by_department = serializers.ListField()
    by_component = serializers.ListField()
