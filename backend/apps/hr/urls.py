# ========================================================
# SISTEMA ERP UNIVERSAL - URLs de RRHH
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Definición de rutas para el módulo de RRHH.
# ========================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DepartmentViewSet,
    PositionViewSet,
    EmployeeViewSet,
    LeaveTypeViewSet,
    LeaveRequestViewSet,
    AttendanceViewSet,
    WorkScheduleViewSet,
    HolidayViewSet,
    PayrollPeriodViewSet,
    SalaryComponentViewSet,
    PayslipViewSet,
    LoanViewSet,
    PerformanceReviewTemplateViewSet,
    PerformanceReviewViewSet,
    TrainingViewSet,
)

# Crear router
router = DefaultRouter()

# Estructura Organizacional
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'positions', PositionViewSet, basename='position')

# Empleados
router.register(r'employees', EmployeeViewSet, basename='employee')

# Gestión de Tiempo
router.register(r'leave-types', LeaveTypeViewSet, basename='leave-type')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave-request')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'work-schedules', WorkScheduleViewSet, basename='work-schedule')
router.register(r'holidays', HolidayViewSet, basename='holiday')

# Nómina
router.register(r'payroll-periods', PayrollPeriodViewSet, basename='payroll-period')
router.register(r'salary-components', SalaryComponentViewSet, basename='salary-component')
router.register(r'payslips', PayslipViewSet, basename='payslip')
router.register(r'loans', LoanViewSet, basename='loan')

# Evaluaciones de Desempeño
router.register(r'review-templates', PerformanceReviewTemplateViewSet, basename='review-template')
router.register(r'performance-reviews', PerformanceReviewViewSet, basename='performance-review')

# Capacitación
router.register(r'trainings', TrainingViewSet, basename='training')

# Nombre de la aplicación
app_name = 'hr'

# Patrones de URL
# ========================================================
# URLs generadas:
#
# Estructura Organizacional:
#   GET    /api/v1/hr/departments/              - Lista departamentos
#   GET    /api/v1/hr/departments/tree/         - Árbol de departamentos
#   GET    /api/v1/hr/departments/{id}/employees/ - Empleados del departamento
#   GET    /api/v1/hr/positions/                - Lista puestos
#
# Empleados:
#   GET    /api/v1/hr/employees/                - Lista empleados
#   GET    /api/v1/hr/employees/statistics/     - Estadísticas
#   GET    /api/v1/hr/employees/org-chart/      - Organigrama
#   POST   /api/v1/hr/employees/{id}/terminate/ - Terminar contrato
#   GET    /api/v1/hr/employees/{id}/documents/ - Documentos
#   GET    /api/v1/hr/employees/{id}/leave-balance/ - Saldo ausencias
#   GET    /api/v1/hr/employees/{id}/payslips/  - Recibos de nómina
#
# Gestión de Tiempo:
#   GET    /api/v1/hr/leave-types/              - Tipos de ausencia
#   GET    /api/v1/hr/leave-requests/           - Solicitudes de ausencia
#   POST   /api/v1/hr/leave-requests/{id}/approve/ - Aprobar solicitud
#   POST   /api/v1/hr/leave-requests/{id}/reject/  - Rechazar solicitud
#   GET    /api/v1/hr/leave-requests/calendar/  - Calendario de ausencias
#   POST   /api/v1/hr/leave-requests/allocate-balances/ - Asignar saldos
#   POST   /api/v1/hr/attendance/check-in/      - Registrar entrada
#   POST   /api/v1/hr/attendance/check-out/     - Registrar salida
#   GET    /api/v1/hr/attendance/report/        - Reporte de asistencia
#   GET    /api/v1/hr/work-schedules/           - Horarios de trabajo
#   GET    /api/v1/hr/holidays/                 - Feriados
#
# Nómina:
#   GET    /api/v1/hr/payroll-periods/          - Períodos de nómina
#   POST   /api/v1/hr/payroll-periods/{id}/generate-payslips/ - Generar nómina
#   POST   /api/v1/hr/payroll-periods/{id}/approve/ - Aprobar nómina
#   POST   /api/v1/hr/payroll-periods/{id}/process-payment/ - Procesar pago
#   GET    /api/v1/hr/payroll-periods/{id}/summary/ - Resumen de nómina
#   GET    /api/v1/hr/salary-components/        - Componentes salariales
#   GET    /api/v1/hr/payslips/                 - Recibos de nómina
#   GET    /api/v1/hr/loans/                    - Préstamos
#   POST   /api/v1/hr/loans/{id}/approve/       - Aprobar préstamo
#
# Evaluaciones:
#   GET    /api/v1/hr/review-templates/         - Plantillas de evaluación
#   GET    /api/v1/hr/performance-reviews/      - Evaluaciones
#   POST   /api/v1/hr/performance-reviews/create-review/ - Crear evaluación
#   POST   /api/v1/hr/performance-reviews/{id}/submit-scores/ - Enviar puntuaciones
#   POST   /api/v1/hr/performance-reviews/{id}/complete/ - Completar evaluación
#   GET    /api/v1/hr/performance-reviews/analytics/ - Analíticas
#
# Capacitación:
#   GET    /api/v1/hr/trainings/                - Lista capacitaciones
#   POST   /api/v1/hr/trainings/{id}/enroll/    - Inscribir empleados
#   POST   /api/v1/hr/trainings/{id}/update-participant/ - Actualizar participante
#   GET    /api/v1/hr/trainings/{id}/participants/ - Lista participantes
# ========================================================

urlpatterns = [
    path('', include(router.urls)),
]
