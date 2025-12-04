# ========================================================
# SISTEMA ERP UNIVERSAL - Modelos de Recursos Humanos
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Definición de modelos para gestión de RRHH.
# ========================================================

from django.db import models
from django.conf import settings
from django.core.validators import (
    MinValueValidator, MaxValueValidator, RegexValidator
)
from decimal import Decimal
from apps.core.models import BaseModel, SoftDeleteModel


# ========================================================
# Estructura Organizacional
# ========================================================

class Department(BaseModel, SoftDeleteModel):
    """
    Modelo para departamentos de la organización.
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
        null=True,
        verbose_name='Descripción'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Departamento Padre'
    )
    manager = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name='Gerente'
    )
    cost_center = models.ForeignKey(
        'finance.CostCenter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Centro de Costo'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        db_table = 'hr_department'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def employee_count(self):
        """Cuenta empleados del departamento."""
        return self.employees.filter(is_active=True).count()


class Position(BaseModel, SoftDeleteModel):
    """
    Modelo para puestos/cargos de trabajo.
    """
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre del Puesto'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name='Departamento'
    )
    level = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Nivel Jerárquico'
    )
    reports_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name='Reporta a'
    )
    min_salary = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Salario Mínimo'
    )
    max_salary = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Salario Máximo'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        db_table = 'hr_position'
        verbose_name = 'Puesto'
        verbose_name_plural = 'Puestos'
        ordering = ['department', 'level', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


# ========================================================
# Empleados
# ========================================================

class Employee(BaseModel, SoftDeleteModel):
    """
    Modelo para empleados de la organización.
    """
    
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', 'Soltero/a'),
        ('married', 'Casado/a'),
        ('divorced', 'Divorciado/a'),
        ('widowed', 'Viudo/a'),
        ('other', 'Otro'),
    ]
    
    CONTRACT_TYPE_CHOICES = [
        ('indefinite', 'Indefinido'),
        ('fixed', 'Plazo Fijo'),
        ('temporary', 'Temporal'),
        ('internship', 'Pasantía'),
        ('contractor', 'Contratista'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('on_leave', 'En Licencia'),
        ('terminated', 'Terminado'),
        ('suspended', 'Suspendido'),
    ]
    
    # Información básica
    employee_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código de Empleado'
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_profile',
        verbose_name='Usuario del Sistema'
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name='Nombres'
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Apellidos'
    )
    id_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de Identificación'
    )
    id_type = models.CharField(
        max_length=20,
        default='DNI',
        verbose_name='Tipo de Documento'
    )
    
    # Información personal
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name='Género'
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Nacimiento'
    )
    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        default='single',
        verbose_name='Estado Civil'
    )
    nationality = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Nacionalidad'
    )
    
    # Contacto
    email = models.EmailField(
        verbose_name='Correo Personal'
    )
    work_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Correo Corporativo'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    mobile = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Celular'
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='Dirección'
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Ciudad'
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='País'
    )
    
    # Información laboral
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name='employees',
        verbose_name='Departamento'
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        related_name='employees',
        verbose_name='Puesto'
    )
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name='Jefe Directo'
    )
    hire_date = models.DateField(
        verbose_name='Fecha de Contratación'
    )
    termination_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Terminación'
    )
    contract_type = models.CharField(
        max_length=20,
        choices=CONTRACT_TYPE_CHOICES,
        default='indefinite',
        verbose_name='Tipo de Contrato'
    )
    contract_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fin de Contrato'
    )
    
    # Información salarial
    salary = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Salario Base'
    )
    salary_currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name='Moneda'
    )
    payment_frequency = models.CharField(
        max_length=20,
        choices=[
            ('weekly', 'Semanal'),
            ('biweekly', 'Quincenal'),
            ('monthly', 'Mensual'),
        ],
        default='monthly',
        verbose_name='Frecuencia de Pago'
    )
    bank_account = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Cuenta Bancaria'
    )
    bank_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Banco'
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Estado'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    # Foto
    photo = models.ImageField(
        upload_to='employees/photos/',
        null=True,
        blank=True,
        verbose_name='Foto'
    )
    
    class Meta:
        db_table = 'hr_employee'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.employee_code} - {self.full_name}"
    
    @property
    def full_name(self):
        """Nombre completo del empleado."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def years_of_service(self):
        """Años de servicio del empleado."""
        from django.utils import timezone
        end_date = self.termination_date or timezone.now().date()
        delta = end_date - self.hire_date
        return delta.days // 365


class EmergencyContact(BaseModel):
    """
    Contacto de emergencia del empleado.
    """
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='emergency_contacts',
        verbose_name='Empleado'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    relationship = models.CharField(
        max_length=50,
        verbose_name='Parentesco'
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Teléfono'
    )
    mobile = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Celular'
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Correo'
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name='Contacto Principal'
    )
    
    class Meta:
        db_table = 'hr_emergency_contact'
        verbose_name = 'Contacto de Emergencia'
        verbose_name_plural = 'Contactos de Emergencia'
    
    def __str__(self):
        return f"{self.name} ({self.relationship})"


class EmployeeDocument(BaseModel):
    """
    Documentos del empleado.
    """
    
    DOCUMENT_TYPES = [
        ('contract', 'Contrato'),
        ('id_copy', 'Copia de Identificación'),
        ('cv', 'Curriculum Vitae'),
        ('certificate', 'Certificado'),
        ('evaluation', 'Evaluación'),
        ('warning', 'Amonestación'),
        ('other', 'Otro'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Empleado'
    )
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        verbose_name='Tipo de Documento'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    file = models.FileField(
        upload_to='employees/documents/',
        verbose_name='Archivo'
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Vencimiento'
    )
    
    class Meta:
        db_table = 'hr_employee_document'
        verbose_name = 'Documento de Empleado'
        verbose_name_plural = 'Documentos de Empleados'
    
    def __str__(self):
        return f"{self.employee} - {self.name}"


# ========================================================
# Gestión de Tiempo
# ========================================================

class LeaveType(BaseModel):
    """
    Tipos de ausencias/permisos.
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
        null=True,
        verbose_name='Descripción'
    )
    is_paid = models.BooleanField(
        default=True,
        verbose_name='Con Goce de Sueldo'
    )
    max_days_per_year = models.PositiveIntegerField(
        default=0,
        verbose_name='Días Máximos por Año'
    )
    requires_approval = models.BooleanField(
        default=True,
        verbose_name='Requiere Aprobación'
    )
    requires_attachment = models.BooleanField(
        default=False,
        verbose_name='Requiere Adjunto'
    )
    color = models.CharField(
        max_length=7,
        default='#3498db',
        verbose_name='Color en Calendario'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        db_table = 'hr_leave_type'
        verbose_name = 'Tipo de Ausencia'
        verbose_name_plural = 'Tipos de Ausencia'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class LeaveRequest(BaseModel):
    """
    Solicitudes de ausencia/permiso.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('cancelled', 'Cancelado'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_requests',
        verbose_name='Empleado'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.PROTECT,
        related_name='requests',
        verbose_name='Tipo de Ausencia'
    )
    start_date = models.DateField(
        verbose_name='Fecha Inicio'
    )
    end_date = models.DateField(
        verbose_name='Fecha Fin'
    )
    start_half_day = models.BooleanField(
        default=False,
        verbose_name='Inicio Medio Día'
    )
    end_half_day = models.BooleanField(
        default=False,
        verbose_name='Fin Medio Día'
    )
    reason = models.TextField(
        blank=True,
        null=True,
        verbose_name='Motivo'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves',
        verbose_name='Aprobado Por'
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Aprobación'
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name='Motivo de Rechazo'
    )
    attachment = models.FileField(
        upload_to='hr/leaves/',
        null=True,
        blank=True,
        verbose_name='Adjunto'
    )
    
    class Meta:
        db_table = 'hr_leave_request'
        verbose_name = 'Solicitud de Ausencia'
        verbose_name_plural = 'Solicitudes de Ausencia'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date})"
    
    @property
    def days(self):
        """Calcula días de ausencia."""
        delta = (self.end_date - self.start_date).days + 1
        if self.start_half_day:
            delta -= 0.5
        if self.end_half_day:
            delta -= 0.5
        return delta


class LeaveBalance(BaseModel):
    """
    Saldo de días de ausencia por empleado.
    """
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_balances',
        verbose_name='Empleado'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='balances',
        verbose_name='Tipo de Ausencia'
    )
    year = models.PositiveIntegerField(
        verbose_name='Año'
    )
    allocated_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Días Asignados'
    )
    used_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Días Usados'
    )
    carried_over = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Días Arrastrados'
    )
    
    class Meta:
        db_table = 'hr_leave_balance'
        verbose_name = 'Saldo de Ausencias'
        verbose_name_plural = 'Saldos de Ausencias'
        unique_together = ['employee', 'leave_type', 'year']
    
    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.year})"
    
    @property
    def available_days(self):
        """Días disponibles."""
        return self.allocated_days + self.carried_over - self.used_days


class Attendance(BaseModel):
    """
    Registro de asistencia diaria.
    """
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name='Empleado'
    )
    date = models.DateField(
        verbose_name='Fecha'
    )
    check_in = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Hora Entrada'
    )
    check_out = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Hora Salida'
    )
    worked_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Horas Trabajadas'
    )
    overtime_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Horas Extra'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('present', 'Presente'),
            ('absent', 'Ausente'),
            ('late', 'Tardanza'),
            ('half_day', 'Medio Día'),
            ('on_leave', 'En Licencia'),
            ('holiday', 'Feriado'),
        ],
        default='present',
        verbose_name='Estado'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    class Meta:
        db_table = 'hr_attendance'
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        unique_together = ['employee', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.employee} - {self.date}"


class WorkSchedule(BaseModel):
    """
    Horarios de trabajo.
    """
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    monday_start = models.TimeField(null=True, blank=True)
    monday_end = models.TimeField(null=True, blank=True)
    tuesday_start = models.TimeField(null=True, blank=True)
    tuesday_end = models.TimeField(null=True, blank=True)
    wednesday_start = models.TimeField(null=True, blank=True)
    wednesday_end = models.TimeField(null=True, blank=True)
    thursday_start = models.TimeField(null=True, blank=True)
    thursday_end = models.TimeField(null=True, blank=True)
    friday_start = models.TimeField(null=True, blank=True)
    friday_end = models.TimeField(null=True, blank=True)
    saturday_start = models.TimeField(null=True, blank=True)
    saturday_end = models.TimeField(null=True, blank=True)
    sunday_start = models.TimeField(null=True, blank=True)
    sunday_end = models.TimeField(null=True, blank=True)
    is_default = models.BooleanField(
        default=False,
        verbose_name='Horario por Defecto'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        db_table = 'hr_work_schedule'
        verbose_name = 'Horario de Trabajo'
        verbose_name_plural = 'Horarios de Trabajo'
    
    def __str__(self):
        return self.name


class Holiday(BaseModel):
    """
    Días feriados.
    """
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    date = models.DateField(
        verbose_name='Fecha'
    )
    is_recurring = models.BooleanField(
        default=True,
        verbose_name='Se Repite Cada Año'
    )
    is_half_day = models.BooleanField(
        default=False,
        verbose_name='Medio Día'
    )
    applies_to_all = models.BooleanField(
        default=True,
        verbose_name='Aplica a Todos'
    )
    departments = models.ManyToManyField(
        Department,
        blank=True,
        related_name='holidays',
        verbose_name='Departamentos'
    )
    
    class Meta:
        db_table = 'hr_holiday'
        verbose_name = 'Feriado'
        verbose_name_plural = 'Feriados'
        ordering = ['date']
    
    def __str__(self):
        return f"{self.name} ({self.date})"


# ========================================================
# Nómina
# ========================================================

class PayrollPeriod(BaseModel):
    """
    Períodos de nómina.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('processing', 'Procesando'),
        ('approved', 'Aprobado'),
        ('paid', 'Pagado'),
        ('closed', 'Cerrado'),
    ]
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    start_date = models.DateField(
        verbose_name='Fecha Inicio'
    )
    end_date = models.DateField(
        verbose_name='Fecha Fin'
    )
    payment_date = models.DateField(
        verbose_name='Fecha de Pago'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )
    total_gross = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Bruto'
    )
    total_deductions = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Deducciones'
    )
    total_net = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Neto'
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payrolls',
        verbose_name='Procesado Por'
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Proceso'
    )
    
    class Meta:
        db_table = 'hr_payroll_period'
        verbose_name = 'Período de Nómina'
        verbose_name_plural = 'Períodos de Nómina'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class SalaryComponent(BaseModel):
    """
    Componentes de salario (ingresos y deducciones).
    """
    
    COMPONENT_TYPES = [
        ('earning', 'Ingreso'),
        ('deduction', 'Deducción'),
    ]
    
    CALCULATION_TYPES = [
        ('fixed', 'Monto Fijo'),
        ('percentage', 'Porcentaje'),
        ('formula', 'Fórmula'),
    ]
    
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
        null=True,
        verbose_name='Descripción'
    )
    component_type = models.CharField(
        max_length=20,
        choices=COMPONENT_TYPES,
        verbose_name='Tipo'
    )
    calculation_type = models.CharField(
        max_length=20,
        choices=CALCULATION_TYPES,
        default='fixed',
        verbose_name='Tipo de Cálculo'
    )
    default_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto por Defecto'
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Porcentaje'
    )
    base_component = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dependent_components',
        verbose_name='Componente Base'
    )
    is_taxable = models.BooleanField(
        default=True,
        verbose_name='Es Gravable'
    )
    is_statutory = models.BooleanField(
        default=False,
        verbose_name='Es Legal/Obligatorio'
    )
    affects_social_security = models.BooleanField(
        default=True,
        verbose_name='Afecta Seguridad Social'
    )
    account = models.ForeignKey(
        'finance.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Cuenta Contable'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        db_table = 'hr_salary_component'
        verbose_name = 'Componente Salarial'
        verbose_name_plural = 'Componentes Salariales'
        ordering = ['component_type', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Payslip(BaseModel):
    """
    Recibo/Comprobante de pago individual.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('calculated', 'Calculado'),
        ('approved', 'Aprobado'),
        ('paid', 'Pagado'),
        ('cancelled', 'Cancelado'),
    ]
    
    period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE,
        related_name='payslips',
        verbose_name='Período'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payslips',
        verbose_name='Empleado'
    )
    base_salary = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Salario Base'
    )
    gross_salary = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Salario Bruto'
    )
    total_deductions = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Total Deducciones'
    )
    net_salary = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Salario Neto'
    )
    worked_days = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Días Trabajados'
    )
    worked_hours = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Horas Trabajadas'
    )
    overtime_hours = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Horas Extra'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('transfer', 'Transferencia'),
            ('check', 'Cheque'),
            ('cash', 'Efectivo'),
        ],
        default='transfer',
        verbose_name='Método de Pago'
    )
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Referencia de Pago'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    class Meta:
        db_table = 'hr_payslip'
        verbose_name = 'Recibo de Nómina'
        verbose_name_plural = 'Recibos de Nómina'
        unique_together = ['period', 'employee']
        ordering = ['-period__start_date', 'employee__last_name']
    
    def __str__(self):
        return f"{self.employee} - {self.period}"


class PayslipLine(BaseModel):
    """
    Líneas de detalle del recibo de nómina.
    """
    
    payslip = models.ForeignKey(
        Payslip,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name='Recibo'
    )
    component = models.ForeignKey(
        SalaryComponent,
        on_delete=models.PROTECT,
        related_name='payslip_lines',
        verbose_name='Componente'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('1.00'),
        verbose_name='Cantidad'
    )
    rate = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Tasa'
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto'
    )
    notes = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    class Meta:
        db_table = 'hr_payslip_line'
        verbose_name = 'Línea de Nómina'
        verbose_name_plural = 'Líneas de Nómina'
    
    def __str__(self):
        return f"{self.payslip} - {self.component}"


class Loan(BaseModel):
    """
    Préstamos a empleados.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('active', 'Activo'),
        ('paid', 'Pagado'),
        ('cancelled', 'Cancelado'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='loans',
        verbose_name='Empleado'
    )
    loan_type = models.CharField(
        max_length=50,
        verbose_name='Tipo de Préstamo'
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Monto Total'
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Tasa de Interés'
    )
    installments = models.PositiveIntegerField(
        verbose_name='Número de Cuotas'
    )
    installment_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Monto de Cuota'
    )
    start_date = models.DateField(
        verbose_name='Fecha de Inicio'
    )
    end_date = models.DateField(
        verbose_name='Fecha de Fin'
    )
    remaining_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Monto Pendiente'
    )
    paid_installments = models.PositiveIntegerField(
        default=0,
        verbose_name='Cuotas Pagadas'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_loans',
        verbose_name='Aprobado Por'
    )
    reason = models.TextField(
        blank=True,
        null=True,
        verbose_name='Motivo'
    )
    
    class Meta:
        db_table = 'hr_loan'
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.employee} - {self.loan_type} (${self.amount})"


class LoanPayment(BaseModel):
    """
    Pagos de préstamos.
    """
    
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Préstamo'
    )
    payslip = models.ForeignKey(
        Payslip,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='loan_payments',
        verbose_name='Recibo de Nómina'
    )
    payment_date = models.DateField(
        verbose_name='Fecha de Pago'
    )
    principal_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Capital'
    )
    interest_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Interés'
    )
    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Total'
    )
    installment_number = models.PositiveIntegerField(
        verbose_name='Número de Cuota'
    )
    
    class Meta:
        db_table = 'hr_loan_payment'
        verbose_name = 'Pago de Préstamo'
        verbose_name_plural = 'Pagos de Préstamos'
        ordering = ['loan', 'installment_number']
    
    def __str__(self):
        return f"{self.loan} - Cuota {self.installment_number}"


# ========================================================
# Evaluaciones de Desempeño
# ========================================================

class PerformanceReviewTemplate(BaseModel):
    """
    Plantilla de evaluación de desempeño.
    """
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    
    class Meta:
        db_table = 'hr_performance_template'
        verbose_name = 'Plantilla de Evaluación'
        verbose_name_plural = 'Plantillas de Evaluación'
    
    def __str__(self):
        return self.name


class PerformanceCriteria(BaseModel):
    """
    Criterios de evaluación.
    """
    
    template = models.ForeignKey(
        PerformanceReviewTemplate,
        on_delete=models.CASCADE,
        related_name='criteria',
        verbose_name='Plantilla'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00'),
        verbose_name='Peso'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden'
    )
    
    class Meta:
        db_table = 'hr_performance_criteria'
        verbose_name = 'Criterio de Evaluación'
        verbose_name_plural = 'Criterios de Evaluación'
        ordering = ['template', 'order']
    
    def __str__(self):
        return f"{self.template} - {self.name}"


class PerformanceReview(BaseModel):
    """
    Evaluaciones de desempeño de empleados.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('in_progress', 'En Progreso'),
        ('pending_approval', 'Pendiente Aprobación'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='performance_reviews',
        verbose_name='Empleado'
    )
    reviewer = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reviews_given',
        verbose_name='Evaluador'
    )
    template = models.ForeignKey(
        PerformanceReviewTemplate,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Plantilla'
    )
    period_start = models.DateField(
        verbose_name='Inicio del Período'
    )
    period_end = models.DateField(
        verbose_name='Fin del Período'
    )
    review_date = models.DateField(
        verbose_name='Fecha de Evaluación'
    )
    overall_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Puntuación General'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )
    employee_comments = models.TextField(
        blank=True,
        null=True,
        verbose_name='Comentarios del Empleado'
    )
    reviewer_comments = models.TextField(
        blank=True,
        null=True,
        verbose_name='Comentarios del Evaluador'
    )
    goals_next_period = models.TextField(
        blank=True,
        null=True,
        verbose_name='Objetivos Próximo Período'
    )
    training_recommendations = models.TextField(
        blank=True,
        null=True,
        verbose_name='Recomendaciones de Capacitación'
    )
    
    class Meta:
        db_table = 'hr_performance_review'
        verbose_name = 'Evaluación de Desempeño'
        verbose_name_plural = 'Evaluaciones de Desempeño'
        ordering = ['-review_date']
    
    def __str__(self):
        return f"{self.employee} - {self.review_date}"


class PerformanceScore(BaseModel):
    """
    Puntuaciones por criterio en evaluación.
    """
    
    review = models.ForeignKey(
        PerformanceReview,
        on_delete=models.CASCADE,
        related_name='scores',
        verbose_name='Evaluación'
    )
    criteria = models.ForeignKey(
        PerformanceCriteria,
        on_delete=models.CASCADE,
        verbose_name='Criterio'
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name='Puntuación'
    )
    comments = models.TextField(
        blank=True,
        null=True,
        verbose_name='Comentarios'
    )
    
    class Meta:
        db_table = 'hr_performance_score'
        verbose_name = 'Puntuación'
        verbose_name_plural = 'Puntuaciones'
        unique_together = ['review', 'criteria']
    
    def __str__(self):
        return f"{self.review} - {self.criteria}: {self.score}"


# ========================================================
# Capacitación
# ========================================================

class Training(BaseModel):
    """
    Cursos y capacitaciones.
    """
    
    STATUS_CHOICES = [
        ('planned', 'Planificado'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]
    
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    training_type = models.CharField(
        max_length=50,
        choices=[
            ('internal', 'Interna'),
            ('external', 'Externa'),
            ('online', 'En Línea'),
            ('conference', 'Conferencia'),
        ],
        default='internal',
        verbose_name='Tipo'
    )
    provider = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Proveedor'
    )
    instructor = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Instructor'
    )
    start_date = models.DateField(
        verbose_name='Fecha Inicio'
    )
    end_date = models.DateField(
        verbose_name='Fecha Fin'
    )
    duration_hours = models.PositiveIntegerField(
        default=0,
        verbose_name='Duración (horas)'
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Ubicación'
    )
    max_participants = models.PositiveIntegerField(
        default=0,
        verbose_name='Máximo Participantes'
    )
    cost_per_person = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Costo por Persona'
    )
    total_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Costo Total'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        verbose_name='Estado'
    )
    
    class Meta:
        db_table = 'hr_training'
        verbose_name = 'Capacitación'
        verbose_name_plural = 'Capacitaciones'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class TrainingParticipant(BaseModel):
    """
    Participantes de capacitación.
    """
    
    STATUS_CHOICES = [
        ('enrolled', 'Inscrito'),
        ('confirmed', 'Confirmado'),
        ('attended', 'Asistió'),
        ('passed', 'Aprobado'),
        ('failed', 'Reprobado'),
        ('cancelled', 'Cancelado'),
    ]
    
    training = models.ForeignKey(
        Training,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name='Capacitación'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='trainings',
        verbose_name='Empleado'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='enrolled',
        verbose_name='Estado'
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Calificación'
    )
    attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Porcentaje Asistencia'
    )
    certificate_issued = models.BooleanField(
        default=False,
        verbose_name='Certificado Emitido'
    )
    certificate_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Certificado'
    )
    feedback = models.TextField(
        blank=True,
        null=True,
        verbose_name='Retroalimentación'
    )
    
    class Meta:
        db_table = 'hr_training_participant'
        verbose_name = 'Participante'
        verbose_name_plural = 'Participantes'
        unique_together = ['training', 'employee']
    
    def __str__(self):
        return f"{self.training} - {self.employee}"
