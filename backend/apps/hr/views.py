# ========================================================
# SISTEMA ERP UNIVERSAL - Vistas de RRHH
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: ViewSets y vistas para el módulo de RRHH.
# ========================================================

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils import timezone

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
    Loan,
    PerformanceReviewTemplate,
    PerformanceReview,
    Training,
    TrainingParticipant,
)
from .serializers import (
    DepartmentSerializer,
    DepartmentTreeSerializer,
    PositionSerializer,
    EmployeeListSerializer,
    EmployeeDetailSerializer,
    EmployeeCreateUpdateSerializer,
    EmployeeDocumentSerializer,
    LeaveTypeSerializer,
    LeaveRequestSerializer,
    LeaveBalanceSerializer,
    AttendanceSerializer,
    WorkScheduleSerializer,
    HolidaySerializer,
    PayrollPeriodSerializer,
    SalaryComponentSerializer,
    PayslipSerializer,
    PayslipDetailSerializer,
    LoanSerializer,
    PerformanceReviewTemplateSerializer,
    PerformanceReviewSerializer,
    TrainingSerializer,
    TrainingDetailSerializer,
    TrainingParticipantSerializer,
    EmployeeReportSerializer,
    AttendanceReportSerializer,
    PayrollSummarySerializer,
)
from .services import (
    HRService,
    LeaveService,
    AttendanceService,
    PayrollService,
    PerformanceService,
)


# ========================================================
# Estructura Organizacional
# ========================================================

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de departamentos.
    """
    
    queryset = Department.objects.filter(is_deleted=False)
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'parent']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['code']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(employee_count=Count('employees'))
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Retorna estructura de árbol de departamentos."""
        root_departments = self.get_queryset().filter(parent__isnull=True)
        serializer = DepartmentTreeSerializer(root_departments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """Lista empleados del departamento."""
        department = self.get_object()
        employees = Employee.objects.filter(
            department=department,
            is_active=True
        )
        serializer = EmployeeListSerializer(employees, many=True)
        return Response(serializer.data)


class PositionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de puestos.
    """
    
    queryset = Position.objects.filter(is_deleted=False)
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'department', 'level']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name', 'level']
    ordering = ['department', 'level', 'code']


# ========================================================
# Empleados
# ========================================================

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de empleados.
    """
    
    queryset = Employee.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'status', 'department', 'position', 'contract_type']
    search_fields = ['employee_code', 'first_name', 'last_name', 'id_number', 'email']
    ordering_fields = ['employee_code', 'last_name', 'hire_date']
    ordering = ['last_name', 'first_name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmployeeCreateUpdateSerializer
        return EmployeeDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('department', 'position', 'manager')
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas de empleados."""
        service = HRService()
        stats = service.get_employee_statistics()
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def org_chart(self, request):
        """Organigrama de la empresa."""
        department_id = request.query_params.get('department')
        service = HRService()
        chart = service.get_employee_org_chart(
            department_id=int(department_id) if department_id else None
        )
        return Response(chart)
    
    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Termina el contrato de un empleado."""
        employee = self.get_object()
        termination_date = request.data.get('termination_date')
        reason = request.data.get('reason')
        
        if not termination_date or not reason:
            return Response(
                {'error': 'Se requiere fecha de terminación y motivo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = HRService()
        result = service.terminate_employee(
            employee_id=employee.id,
            termination_date=termination_date,
            reason=reason,
            user_id=request.user.id
        )
        
        return Response(result)
    
    @action(detail=True, methods=['get', 'post'])
    def documents(self, request, pk=None):
        """Gestión de documentos del empleado."""
        employee = self.get_object()
        
        if request.method == 'GET':
            documents = EmployeeDocument.objects.filter(employee=employee)
            serializer = EmployeeDocumentSerializer(documents, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = EmployeeDocumentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(employee=employee)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def leave_balance(self, request, pk=None):
        """Saldo de ausencias del empleado."""
        employee = self.get_object()
        year = request.query_params.get('year', timezone.now().year)
        balances = LeaveBalance.objects.filter(
            employee=employee,
            year=year
        ).select_related('leave_type')
        serializer = LeaveBalanceSerializer(balances, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payslips(self, request, pk=None):
        """Recibos de nómina del empleado."""
        employee = self.get_object()
        payslips = Payslip.objects.filter(
            employee=employee
        ).select_related('period').order_by('-period__start_date')[:12]
        serializer = PayslipSerializer(payslips, many=True)
        return Response(serializer.data)


# ========================================================
# Gestión de Tiempo
# ========================================================

class LeaveTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para tipos de ausencia.
    """
    
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active', 'is_paid', 'requires_approval']
    search_fields = ['code', 'name']


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet para solicitudes de ausencia.
    """
    
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'leave_type', 'status']
    search_fields = ['employee__first_name', 'employee__last_name']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-start_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('employee', 'leave_type', 'approved_by')
    
    def create(self, request, *args, **kwargs):
        """Crear solicitud usando el servicio."""
        service = LeaveService()
        result = service.request_leave(
            employee_id=request.data.get('employee'),
            leave_type_id=request.data.get('leave_type'),
            start_date=request.data.get('start_date'),
            end_date=request.data.get('end_date'),
            reason=request.data.get('reason'),
            start_half_day=request.data.get('start_half_day', False),
            end_half_day=request.data.get('end_half_day', False)
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprueba una solicitud de ausencia."""
        approver_id = request.data.get('approver_id')
        if not approver_id:
            # Usar el empleado del usuario actual
            try:
                approver_id = request.user.employee_profile.id
            except:
                return Response(
                    {'error': 'No se pudo identificar el aprobador'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        service = LeaveService()
        result = service.approve_leave(
            request_id=pk,
            approver_id=approver_id
        )
        
        if result['success']:
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rechaza una solicitud de ausencia."""
        approver_id = request.data.get('approver_id')
        rejection_reason = request.data.get('rejection_reason')
        
        if not rejection_reason:
            return Response(
                {'error': 'Se requiere motivo de rechazo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not approver_id:
            try:
                approver_id = request.user.employee_profile.id
            except:
                return Response(
                    {'error': 'No se pudo identificar el aprobador'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        service = LeaveService()
        result = service.reject_leave(
            request_id=pk,
            approver_id=approver_id,
            rejection_reason=rejection_reason
        )
        
        if result['success']:
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """Calendario de ausencias."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        department_id = request.query_params.get('department')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Se requieren fechas de inicio y fin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = LeaveService()
        calendar = service.get_leave_calendar(
            start_date=start_date,
            end_date=end_date,
            department_id=int(department_id) if department_id else None
        )
        
        return Response(calendar)
    
    @action(detail=False, methods=['post'])
    def allocate_balances(self, request):
        """Asigna saldos de ausencias para un año."""
        year = request.data.get('year', timezone.now().year)
        leave_type_id = request.data.get('leave_type_id')
        
        service = LeaveService()
        result = service.allocate_leave_balances(
            year=year,
            leave_type_id=leave_type_id
        )
        
        return Response(result)


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de asistencia.
    """
    
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'date', 'status']
    ordering_fields = ['date', 'check_in']
    ordering = ['-date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por rango de fechas
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.select_related('employee')
    
    @action(detail=False, methods=['post'])
    def check_in(self, request):
        """Registra entrada."""
        employee_id = request.data.get('employee_id')
        check_time = request.data.get('check_time')
        
        if not employee_id:
            try:
                employee_id = request.user.employee_profile.id
            except:
                return Response(
                    {'error': 'No se pudo identificar el empleado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        service = AttendanceService()
        result = service.record_check_in(
            employee_id=employee_id,
            check_time=check_time
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def check_out(self, request):
        """Registra salida."""
        employee_id = request.data.get('employee_id')
        check_time = request.data.get('check_time')
        
        if not employee_id:
            try:
                employee_id = request.user.employee_profile.id
            except:
                return Response(
                    {'error': 'No se pudo identificar el empleado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        service = AttendanceService()
        result = service.record_check_out(
            employee_id=employee_id,
            check_time=check_time
        )
        
        if result['success']:
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """Genera reporte de asistencia."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        department_id = request.query_params.get('department')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Se requieren fechas de inicio y fin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = AttendanceService()
        report = service.get_attendance_report(
            start_date=start_date,
            end_date=end_date,
            department_id=int(department_id) if department_id else None
        )
        
        return Response(report)


class WorkScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para horarios de trabajo.
    """
    
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class HolidayViewSet(viewsets.ModelViewSet):
    """
    ViewSet para feriados.
    """
    
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_recurring', 'applies_to_all']
    ordering_fields = ['date']
    ordering = ['date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(date__year=year)
        return queryset


# ========================================================
# Nómina
# ========================================================

class PayrollPeriodViewSet(viewsets.ModelViewSet):
    """
    ViewSet para períodos de nómina.
    """
    
    queryset = PayrollPeriod.objects.all()
    serializer_class = PayrollPeriodSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['start_date', 'payment_date']
    ordering = ['-start_date']
    
    @action(detail=True, methods=['post'])
    def generate_payslips(self, request, pk=None):
        """Genera recibos de nómina."""
        employee_ids = request.data.get('employee_ids')
        
        service = PayrollService()
        result = service.generate_payslips(
            period_id=pk,
            employee_ids=employee_ids
        )
        
        if result['success']:
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprueba la nómina."""
        service = PayrollService()
        result = service.approve_payroll(
            period_id=pk,
            user_id=request.user.id
        )
        
        if result['success']:
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Procesa el pago de la nómina."""
        service = PayrollService()
        result = service.process_payment(
            period_id=pk,
            user_id=request.user.id
        )
        
        if result['success']:
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Resumen de nómina."""
        service = PayrollService()
        summary = service.get_payroll_summary(period_id=pk)
        return Response(summary)
    
    @action(detail=True, methods=['get'])
    def payslips(self, request, pk=None):
        """Lista recibos del período."""
        period = self.get_object()
        payslips = Payslip.objects.filter(period=period).select_related('employee')
        serializer = PayslipSerializer(payslips, many=True)
        return Response(serializer.data)


class SalaryComponentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para componentes salariales.
    """
    
    queryset = SalaryComponent.objects.all()
    serializer_class = SalaryComponentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['component_type', 'calculation_type', 'is_active']
    search_fields = ['code', 'name']


class PayslipViewSet(viewsets.ModelViewSet):
    """
    ViewSet para recibos de nómina.
    """
    
    queryset = Payslip.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['period', 'employee', 'status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PayslipDetailSerializer
        return PayslipSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('period', 'employee').prefetch_related('lines')


class LoanViewSet(viewsets.ModelViewSet):
    """
    ViewSet para préstamos a empleados.
    """
    
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'status', 'loan_type']
    ordering_fields = ['start_date', 'amount']
    ordering = ['-start_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('employee')
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Aprueba un préstamo."""
        loan = self.get_object()
        
        if loan.status != 'pending':
            return Response(
                {'error': 'El préstamo no está pendiente de aprobación'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        loan.status = 'approved'
        loan.approved_by = request.user
        loan.save()
        
        return Response({'success': True, 'message': 'Préstamo aprobado'})
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activa un préstamo aprobado."""
        loan = self.get_object()
        
        if loan.status != 'approved':
            return Response(
                {'error': 'El préstamo no está aprobado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        loan.status = 'active'
        loan.remaining_amount = loan.amount
        loan.save()
        
        return Response({'success': True, 'message': 'Préstamo activado'})


# ========================================================
# Evaluaciones de Desempeño
# ========================================================

class PerformanceReviewTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet para plantillas de evaluación.
    """
    
    queryset = PerformanceReviewTemplate.objects.all()
    serializer_class = PerformanceReviewTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class PerformanceReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet para evaluaciones de desempeño.
    """
    
    queryset = PerformanceReview.objects.all()
    serializer_class = PerformanceReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'reviewer', 'status']
    ordering_fields = ['review_date', 'overall_score']
    ordering = ['-review_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('employee', 'reviewer', 'template')
    
    @action(detail=False, methods=['post'])
    def create_review(self, request):
        """Crea una nueva evaluación."""
        service = PerformanceService()
        result = service.create_review(
            employee_id=request.data.get('employee_id'),
            reviewer_id=request.data.get('reviewer_id'),
            template_id=request.data.get('template_id'),
            period_start=request.data.get('period_start'),
            period_end=request.data.get('period_end'),
            review_date=request.data.get('review_date')
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def submit_scores(self, request, pk=None):
        """Envía puntuaciones de evaluación."""
        service = PerformanceService()
        result = service.submit_scores(
            review_id=pk,
            scores=request.data.get('scores', []),
            reviewer_comments=request.data.get('reviewer_comments'),
            goals_next_period=request.data.get('goals_next_period'),
            training_recommendations=request.data.get('training_recommendations')
        )
        
        if result['success']:
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Completa una evaluación."""
        service = PerformanceService()
        result = service.complete_review(
            review_id=pk,
            employee_comments=request.data.get('employee_comments')
        )
        
        if result['success']:
            return Response(result)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Analíticas de desempeño."""
        department_id = request.query_params.get('department')
        year = request.query_params.get('year')
        
        service = PerformanceService()
        analytics = service.get_performance_analytics(
            department_id=int(department_id) if department_id else None,
            year=int(year) if year else None
        )
        
        return Response(analytics)


# ========================================================
# Capacitación
# ========================================================

class TrainingViewSet(viewsets.ModelViewSet):
    """
    ViewSet para capacitaciones.
    """
    
    queryset = Training.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'training_type']
    search_fields = ['code', 'name', 'provider', 'instructor']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-start_date']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TrainingDetailSerializer
        return TrainingSerializer
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        """Inscribe empleados en capacitación."""
        training = self.get_object()
        employee_ids = request.data.get('employee_ids', [])
        
        if training.max_participants > 0:
            current_count = training.participants.count()
            if current_count + len(employee_ids) > training.max_participants:
                return Response(
                    {'error': 'Se excede el máximo de participantes'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        created = 0
        for emp_id in employee_ids:
            participant, is_new = TrainingParticipant.objects.get_or_create(
                training=training,
                employee_id=emp_id,
                defaults={'status': 'enrolled'}
            )
            if is_new:
                created += 1
        
        return Response({
            'success': True,
            'enrolled': created
        })
    
    @action(detail=True, methods=['post'])
    def update_participant(self, request, pk=None):
        """Actualiza estado de participante."""
        training = self.get_object()
        employee_id = request.data.get('employee_id')
        
        try:
            participant = TrainingParticipant.objects.get(
                training=training,
                employee_id=employee_id
            )
        except TrainingParticipant.DoesNotExist:
            return Response(
                {'error': 'Participante no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TrainingParticipantSerializer(
            participant,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """Lista participantes de capacitación."""
        training = self.get_object()
        participants = training.participants.select_related('employee')
        serializer = TrainingParticipantSerializer(participants, many=True)
        return Response(serializer.data)
