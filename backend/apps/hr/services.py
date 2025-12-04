# ========================================================
# SISTEMA ERP UNIVERSAL - Servicios de RRHH
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Lógica de negocio para el módulo de RRHH.
# ========================================================

from django.db import transaction
from django.db.models import Sum, Avg, Count, Q, F
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class HRService:
    """
    Servicio principal de Recursos Humanos.
    """
    
    # ====================================================
    # Gestión de Empleados
    # ====================================================
    
    def get_employee_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de empleados.
        """
        from .models import Employee, Department
        
        employees = Employee.objects.filter(is_deleted=False)
        
        total = employees.count()
        active = employees.filter(status='active').count()
        
        by_department = list(
            employees.filter(status='active')
            .values('department__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        by_contract_type = list(
            employees.filter(status='active')
            .values('contract_type')
            .annotate(count=Count('id'))
        )
        
        by_status = list(
            employees.values('status')
            .annotate(count=Count('id'))
        )
        
        # Calcular promedio de antigüedad
        today = timezone.now().date()
        active_employees = employees.filter(status='active', hire_date__isnull=False)
        
        if active_employees.exists():
            total_days = sum([
                (today - emp.hire_date).days
                for emp in active_employees
            ])
            avg_years = Decimal(str(total_days / active_employees.count() / 365))
        else:
            avg_years = Decimal('0')
        
        return {
            'total_employees': total,
            'active_employees': active,
            'by_department': by_department,
            'by_contract_type': by_contract_type,
            'by_status': by_status,
            'average_years_of_service': round(avg_years, 2)
        }
    
    def get_employee_org_chart(self, department_id: Optional[int] = None) -> List[Dict]:
        """
        Genera el organigrama de la empresa.
        """
        from .models import Employee, Department
        
        def build_tree(manager_id):
            subordinates = Employee.objects.filter(
                manager_id=manager_id,
                status='active'
            ).select_related('position', 'department')
            
            return [
                {
                    'id': emp.id,
                    'name': emp.full_name,
                    'position': emp.position.name if emp.position else None,
                    'department': emp.department.name if emp.department else None,
                    'photo': emp.photo.url if emp.photo else None,
                    'subordinates': build_tree(emp.id)
                }
                for emp in subordinates
            ]
        
        # Obtener empleados sin manager (top level)
        query = Employee.objects.filter(
            manager__isnull=True,
            status='active'
        )
        
        if department_id:
            query = query.filter(department_id=department_id)
        
        top_employees = query.select_related('position', 'department')
        
        return [
            {
                'id': emp.id,
                'name': emp.full_name,
                'position': emp.position.name if emp.position else None,
                'department': emp.department.name if emp.department else None,
                'photo': emp.photo.url if emp.photo else None,
                'subordinates': build_tree(emp.id)
            }
            for emp in top_employees
        ]
    
    def terminate_employee(
        self,
        employee_id: int,
        termination_date: date,
        reason: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Procesa la terminación de un empleado.
        """
        from .models import Employee
        
        with transaction.atomic():
            employee = Employee.objects.select_for_update().get(pk=employee_id)
            
            employee.status = 'terminated'
            employee.termination_date = termination_date
            employee.is_active = False
            employee.save()
            
            # Desactivar usuario del sistema si existe
            if employee.user:
                employee.user.is_active = False
                employee.user.save()
            
            # Registrar en auditoría
            logger.info(
                f"Empleado {employee.employee_code} terminado por usuario {user_id}. "
                f"Motivo: {reason}"
            )
            
            return {
                'success': True,
                'employee_code': employee.employee_code,
                'termination_date': termination_date.isoformat()
            }


class LeaveService:
    """
    Servicio de gestión de ausencias.
    """
    
    def request_leave(
        self,
        employee_id: int,
        leave_type_id: int,
        start_date: date,
        end_date: date,
        reason: str = None,
        start_half_day: bool = False,
        end_half_day: bool = False
    ) -> Dict[str, Any]:
        """
        Crea una solicitud de ausencia.
        """
        from .models import Employee, LeaveType, LeaveRequest, LeaveBalance
        
        employee = Employee.objects.get(pk=employee_id)
        leave_type = LeaveType.objects.get(pk=leave_type_id)
        
        # Calcular días
        total_days = (end_date - start_date).days + 1
        if start_half_day:
            total_days -= 0.5
        if end_half_day:
            total_days -= 0.5
        
        # Verificar saldo disponible
        current_year = start_date.year
        balance = LeaveBalance.objects.filter(
            employee=employee,
            leave_type=leave_type,
            year=current_year
        ).first()
        
        if balance:
            available = balance.allocated_days + balance.carried_over - balance.used_days
            if total_days > available:
                return {
                    'success': False,
                    'error': f'Saldo insuficiente. Disponible: {available} días, Solicitado: {total_days} días'
                }
        
        # Verificar conflictos
        conflicts = LeaveRequest.objects.filter(
            employee=employee,
            status__in=['pending', 'approved'],
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        
        if conflicts.exists():
            return {
                'success': False,
                'error': 'Existe una solicitud que se cruza con las fechas indicadas'
            }
        
        # Crear solicitud
        status = 'pending' if leave_type.requires_approval else 'approved'
        
        leave_request = LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            start_half_day=start_half_day,
            end_half_day=end_half_day,
            reason=reason,
            status=status
        )
        
        # Si no requiere aprobación, actualizar saldo
        if not leave_type.requires_approval and balance:
            balance.used_days += Decimal(str(total_days))
            balance.save()
        
        return {
            'success': True,
            'request_id': leave_request.id,
            'status': status,
            'days': total_days
        }
    
    def approve_leave(
        self,
        request_id: int,
        approver_id: int
    ) -> Dict[str, Any]:
        """
        Aprueba una solicitud de ausencia.
        """
        from .models import LeaveRequest, LeaveBalance, Employee
        
        with transaction.atomic():
            leave_request = LeaveRequest.objects.select_for_update().get(pk=request_id)
            
            if leave_request.status != 'pending':
                return {
                    'success': False,
                    'error': 'La solicitud no está pendiente de aprobación'
                }
            
            approver = Employee.objects.get(pk=approver_id)
            
            leave_request.status = 'approved'
            leave_request.approved_by = approver
            leave_request.approved_at = timezone.now()
            leave_request.save()
            
            # Actualizar saldo
            balance = LeaveBalance.objects.filter(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                year=leave_request.start_date.year
            ).first()
            
            if balance:
                balance.used_days += Decimal(str(leave_request.days))
                balance.save()
            
            return {
                'success': True,
                'message': 'Solicitud aprobada exitosamente'
            }
    
    def reject_leave(
        self,
        request_id: int,
        approver_id: int,
        rejection_reason: str
    ) -> Dict[str, Any]:
        """
        Rechaza una solicitud de ausencia.
        """
        from .models import LeaveRequest, Employee
        
        leave_request = LeaveRequest.objects.get(pk=request_id)
        
        if leave_request.status != 'pending':
            return {
                'success': False,
                'error': 'La solicitud no está pendiente de aprobación'
            }
        
        approver = Employee.objects.get(pk=approver_id)
        
        leave_request.status = 'rejected'
        leave_request.approved_by = approver
        leave_request.approved_at = timezone.now()
        leave_request.rejection_reason = rejection_reason
        leave_request.save()
        
        return {
            'success': True,
            'message': 'Solicitud rechazada'
        }
    
    def get_leave_calendar(
        self,
        start_date: date,
        end_date: date,
        department_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Obtiene calendario de ausencias.
        """
        from .models import LeaveRequest
        
        query = LeaveRequest.objects.filter(
            status='approved',
            start_date__lte=end_date,
            end_date__gte=start_date
        ).select_related('employee', 'leave_type')
        
        if department_id:
            query = query.filter(employee__department_id=department_id)
        
        return [
            {
                'id': req.id,
                'employee_id': req.employee_id,
                'employee_name': req.employee.full_name,
                'leave_type': req.leave_type.name,
                'color': req.leave_type.color,
                'start_date': req.start_date.isoformat(),
                'end_date': req.end_date.isoformat(),
                'days': float(req.days)
            }
            for req in query
        ]
    
    def allocate_leave_balances(
        self,
        year: int,
        leave_type_id: int = None
    ) -> Dict[str, Any]:
        """
        Asigna saldos de ausencias para un año.
        """
        from .models import Employee, LeaveType, LeaveBalance
        
        active_employees = Employee.objects.filter(status='active')
        
        if leave_type_id:
            leave_types = LeaveType.objects.filter(pk=leave_type_id, is_active=True)
        else:
            leave_types = LeaveType.objects.filter(is_active=True)
        
        created_count = 0
        
        with transaction.atomic():
            for employee in active_employees:
                for leave_type in leave_types:
                    balance, created = LeaveBalance.objects.get_or_create(
                        employee=employee,
                        leave_type=leave_type,
                        year=year,
                        defaults={
                            'allocated_days': leave_type.max_days_per_year
                        }
                    )
                    if created:
                        created_count += 1
                        
                        # Arrastrar días del año anterior si aplica
                        prev_balance = LeaveBalance.objects.filter(
                            employee=employee,
                            leave_type=leave_type,
                            year=year - 1
                        ).first()
                        
                        if prev_balance and prev_balance.available_days > 0:
                            # Máximo 5 días arrastrados
                            balance.carried_over = min(
                                prev_balance.available_days,
                                Decimal('5')
                            )
                            balance.save()
        
        return {
            'success': True,
            'created_count': created_count,
            'year': year
        }


class AttendanceService:
    """
    Servicio de gestión de asistencia.
    """
    
    def record_check_in(
        self,
        employee_id: int,
        check_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registra entrada de empleado.
        """
        from .models import Employee, Attendance, WorkSchedule
        from datetime import datetime
        
        employee = Employee.objects.get(pk=employee_id)
        today = timezone.now().date()
        current_time = timezone.now().time() if not check_time else datetime.strptime(check_time, '%H:%M').time()
        
        # Verificar si ya existe registro
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                'check_in': current_time,
                'status': 'present'
            }
        )
        
        if not created:
            if attendance.check_in:
                return {
                    'success': False,
                    'error': 'Ya existe un registro de entrada para hoy'
                }
            attendance.check_in = current_time
            attendance.save()
        
        # Verificar tardanza
        schedule = WorkSchedule.objects.filter(is_default=True).first()
        if schedule:
            weekday = today.weekday()
            day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            expected_start = getattr(schedule, f'{day_names[weekday]}_start')
            
            if expected_start and current_time > expected_start:
                attendance.status = 'late'
                attendance.save()
        
        return {
            'success': True,
            'attendance_id': attendance.id,
            'check_in': str(current_time),
            'status': attendance.status
        }
    
    def record_check_out(
        self,
        employee_id: int,
        check_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registra salida de empleado.
        """
        from .models import Employee, Attendance
        from datetime import datetime, timedelta
        
        employee = Employee.objects.get(pk=employee_id)
        today = timezone.now().date()
        current_time = timezone.now().time() if not check_time else datetime.strptime(check_time, '%H:%M').time()
        
        try:
            attendance = Attendance.objects.get(
                employee=employee,
                date=today
            )
        except Attendance.DoesNotExist:
            return {
                'success': False,
                'error': 'No existe registro de entrada para hoy'
            }
        
        if attendance.check_out:
            return {
                'success': False,
                'error': 'Ya existe un registro de salida para hoy'
            }
        
        attendance.check_out = current_time
        
        # Calcular horas trabajadas
        if attendance.check_in:
            check_in_dt = datetime.combine(today, attendance.check_in)
            check_out_dt = datetime.combine(today, current_time)
            worked_delta = check_out_dt - check_in_dt
            worked_hours = Decimal(str(worked_delta.total_seconds() / 3600))
            
            attendance.worked_hours = worked_hours
            
            # Calcular horas extra (más de 8 horas)
            if worked_hours > 8:
                attendance.overtime_hours = worked_hours - 8
        
        attendance.save()
        
        return {
            'success': True,
            'attendance_id': attendance.id,
            'check_out': str(current_time),
            'worked_hours': float(attendance.worked_hours),
            'overtime_hours': float(attendance.overtime_hours)
        }
    
    def get_attendance_report(
        self,
        start_date: date,
        end_date: date,
        department_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Genera reporte de asistencia.
        """
        from .models import Attendance, Employee, Holiday
        
        # Calcular días laborables
        holidays = Holiday.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).values_list('date', flat=True)
        
        working_days = 0
        current = start_date
        while current <= end_date:
            if current.weekday() < 5 and current not in holidays:  # Lun-Vie
                working_days += 1
            current += timedelta(days=1)
        
        # Query de asistencia
        query = Attendance.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        
        if department_id:
            query = query.filter(employee__department_id=department_id)
        
        # Estadísticas por estado
        by_status = list(
            query.values('status')
            .annotate(count=Count('id'))
        )
        
        # Total de registros
        total_records = query.count()
        present_count = query.filter(status='present').count()
        
        # Empleados con más ausencias
        top_absences = list(
            query.filter(status='absent')
            .values('employee__first_name', 'employee__last_name')
            .annotate(absences=Count('id'))
            .order_by('-absences')[:10]
        )
        
        attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0
        
        return {
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'total_working_days': working_days,
            'attendance_rate': round(attendance_rate, 2),
            'by_status': by_status,
            'top_absences': top_absences
        }


class PayrollService:
    """
    Servicio de gestión de nómina.
    """
    
    def create_payroll_period(
        self,
        code: str,
        name: str,
        start_date: date,
        end_date: date,
        payment_date: date
    ) -> Dict[str, Any]:
        """
        Crea un período de nómina.
        """
        from .models import PayrollPeriod
        
        period = PayrollPeriod.objects.create(
            code=code,
            name=name,
            start_date=start_date,
            end_date=end_date,
            payment_date=payment_date,
            status='draft'
        )
        
        return {
            'success': True,
            'period_id': period.id,
            'code': period.code
        }
    
    def generate_payslips(
        self,
        period_id: int,
        employee_ids: List[int] = None
    ) -> Dict[str, Any]:
        """
        Genera recibos de nómina para un período.
        """
        from .models import (
            PayrollPeriod, Employee, Payslip, PayslipLine,
            SalaryComponent, Attendance, LeaveRequest
        )
        
        period = PayrollPeriod.objects.get(pk=period_id)
        
        if period.status not in ['draft', 'processing']:
            return {
                'success': False,
                'error': 'El período no está en estado válido para generar nómina'
            }
        
        period.status = 'processing'
        period.save()
        
        # Obtener empleados activos
        if employee_ids:
            employees = Employee.objects.filter(id__in=employee_ids, status='active')
        else:
            employees = Employee.objects.filter(status='active')
        
        # Obtener componentes salariales activos
        earnings = SalaryComponent.objects.filter(
            component_type='earning',
            is_active=True
        )
        deductions = SalaryComponent.objects.filter(
            component_type='deduction',
            is_active=True
        )
        
        created_count = 0
        
        with transaction.atomic():
            for employee in employees:
                # Verificar si ya existe payslip
                existing = Payslip.objects.filter(
                    period=period,
                    employee=employee
                ).first()
                
                if existing:
                    continue
                
                # Calcular días y horas trabajadas
                attendances = Attendance.objects.filter(
                    employee=employee,
                    date__gte=period.start_date,
                    date__lte=period.end_date
                )
                
                worked_days = attendances.filter(
                    status__in=['present', 'late']
                ).count()
                worked_hours = attendances.aggregate(
                    total=Sum('worked_hours')
                )['total'] or Decimal('0')
                overtime_hours = attendances.aggregate(
                    total=Sum('overtime_hours')
                )['total'] or Decimal('0')
                
                # Crear payslip
                payslip = Payslip.objects.create(
                    period=period,
                    employee=employee,
                    base_salary=employee.salary,
                    worked_days=worked_days,
                    worked_hours=worked_hours,
                    overtime_hours=overtime_hours,
                    status='draft'
                )
                
                total_earnings = Decimal('0')
                total_deductions = Decimal('0')
                
                # Agregar ingresos
                for component in earnings:
                    amount = self._calculate_component_amount(
                        component, employee, payslip
                    )
                    if amount > 0:
                        PayslipLine.objects.create(
                            payslip=payslip,
                            component=component,
                            amount=amount
                        )
                        total_earnings += amount
                
                # Agregar deducciones
                for component in deductions:
                    amount = self._calculate_component_amount(
                        component, employee, payslip, total_earnings
                    )
                    if amount > 0:
                        PayslipLine.objects.create(
                            payslip=payslip,
                            component=component,
                            amount=amount
                        )
                        total_deductions += amount
                
                # Actualizar totales
                payslip.gross_salary = total_earnings
                payslip.total_deductions = total_deductions
                payslip.net_salary = total_earnings - total_deductions
                payslip.status = 'calculated'
                payslip.save()
                
                created_count += 1
            
            # Actualizar totales del período
            period_totals = Payslip.objects.filter(period=period).aggregate(
                total_gross=Sum('gross_salary'),
                total_deductions=Sum('total_deductions'),
                total_net=Sum('net_salary')
            )
            
            period.total_gross = period_totals['total_gross'] or Decimal('0')
            period.total_deductions = period_totals['total_deductions'] or Decimal('0')
            period.total_net = period_totals['total_net'] or Decimal('0')
            period.save()
        
        return {
            'success': True,
            'period_id': period.id,
            'payslips_created': created_count,
            'total_gross': float(period.total_gross),
            'total_net': float(period.total_net)
        }
    
    def _calculate_component_amount(
        self,
        component,
        employee,
        payslip,
        base_amount: Decimal = None
    ) -> Decimal:
        """
        Calcula el monto de un componente salarial.
        """
        if component.calculation_type == 'fixed':
            return component.default_amount
        
        elif component.calculation_type == 'percentage':
            if base_amount is not None:
                return base_amount * (component.percentage / 100)
            elif component.base_component:
                base = component.base_component.default_amount
                return base * (component.percentage / 100)
            else:
                return payslip.base_salary * (component.percentage / 100)
        
        return Decimal('0')
    
    def approve_payroll(
        self,
        period_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Aprueba la nómina de un período.
        """
        from .models import PayrollPeriod, Payslip
        
        with transaction.atomic():
            period = PayrollPeriod.objects.select_for_update().get(pk=period_id)
            
            if period.status != 'processing':
                return {
                    'success': False,
                    'error': 'El período no está en estado de procesamiento'
                }
            
            # Aprobar todos los payslips calculados
            Payslip.objects.filter(
                period=period,
                status='calculated'
            ).update(status='approved')
            
            period.status = 'approved'
            period.processed_by_id = user_id
            period.processed_at = timezone.now()
            period.save()
        
        return {
            'success': True,
            'message': 'Nómina aprobada exitosamente'
        }
    
    def process_payment(
        self,
        period_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Procesa el pago de la nómina.
        """
        from .models import PayrollPeriod, Payslip
        
        with transaction.atomic():
            period = PayrollPeriod.objects.select_for_update().get(pk=period_id)
            
            if period.status != 'approved':
                return {
                    'success': False,
                    'error': 'El período no está aprobado'
                }
            
            # Marcar payslips como pagados
            Payslip.objects.filter(
                period=period,
                status='approved'
            ).update(status='paid')
            
            period.status = 'paid'
            period.save()
            
            # Aquí se integraría con el módulo de finanzas
            # para generar los asientos contables
        
        return {
            'success': True,
            'message': 'Pago procesado exitosamente',
            'total_paid': float(period.total_net)
        }
    
    def get_payroll_summary(
        self,
        period_id: int
    ) -> Dict[str, Any]:
        """
        Obtiene resumen de nómina por período.
        """
        from .models import PayrollPeriod, Payslip, PayslipLine
        
        period = PayrollPeriod.objects.get(pk=period_id)
        payslips = Payslip.objects.filter(period=period)
        
        by_department = list(
            payslips.values('employee__department__name')
            .annotate(
                employees=Count('id'),
                total_gross=Sum('gross_salary'),
                total_net=Sum('net_salary')
            )
        )
        
        by_component = list(
            PayslipLine.objects.filter(payslip__period=period)
            .values('component__name', 'component__component_type')
            .annotate(total=Sum('amount'))
            .order_by('component__component_type', '-total')
        )
        
        return {
            'period': period.name,
            'total_employees': payslips.count(),
            'total_gross': float(period.total_gross),
            'total_deductions': float(period.total_deductions),
            'total_net': float(period.total_net),
            'by_department': by_department,
            'by_component': by_component
        }


class PerformanceService:
    """
    Servicio de evaluación de desempeño.
    """
    
    def create_review(
        self,
        employee_id: int,
        reviewer_id: int,
        template_id: int,
        period_start: date,
        period_end: date,
        review_date: date
    ) -> Dict[str, Any]:
        """
        Crea una nueva evaluación de desempeño.
        """
        from .models import (
            Employee, PerformanceReviewTemplate, PerformanceReview,
            PerformanceCriteria, PerformanceScore
        )
        
        employee = Employee.objects.get(pk=employee_id)
        reviewer = Employee.objects.get(pk=reviewer_id)
        template = PerformanceReviewTemplate.objects.get(pk=template_id)
        
        with transaction.atomic():
            review = PerformanceReview.objects.create(
                employee=employee,
                reviewer=reviewer,
                template=template,
                period_start=period_start,
                period_end=period_end,
                review_date=review_date,
                status='draft'
            )
            
            # Crear puntuaciones vacías para cada criterio
            for criteria in template.criteria.all():
                PerformanceScore.objects.create(
                    review=review,
                    criteria=criteria,
                    score=Decimal('0')
                )
        
        return {
            'success': True,
            'review_id': review.id
        }
    
    def submit_scores(
        self,
        review_id: int,
        scores: List[Dict[str, Any]],
        reviewer_comments: str = None,
        goals_next_period: str = None,
        training_recommendations: str = None
    ) -> Dict[str, Any]:
        """
        Envía las puntuaciones de una evaluación.
        """
        from .models import PerformanceReview, PerformanceScore
        
        review = PerformanceReview.objects.get(pk=review_id)
        
        with transaction.atomic():
            total_weighted_score = Decimal('0')
            total_weight = Decimal('0')
            
            for score_data in scores:
                score = PerformanceScore.objects.get(
                    review=review,
                    criteria_id=score_data['criteria_id']
                )
                score.score = Decimal(str(score_data['score']))
                score.comments = score_data.get('comments')
                score.save()
                
                total_weighted_score += score.score * score.criteria.weight
                total_weight += score.criteria.weight
            
            # Calcular puntuación general
            if total_weight > 0:
                review.overall_score = total_weighted_score / total_weight
            
            review.reviewer_comments = reviewer_comments
            review.goals_next_period = goals_next_period
            review.training_recommendations = training_recommendations
            review.status = 'pending_approval'
            review.save()
        
        return {
            'success': True,
            'overall_score': float(review.overall_score)
        }
    
    def complete_review(
        self,
        review_id: int,
        employee_comments: str = None
    ) -> Dict[str, Any]:
        """
        Completa una evaluación (empleado la acepta).
        """
        from .models import PerformanceReview
        
        review = PerformanceReview.objects.get(pk=review_id)
        
        if review.status != 'pending_approval':
            return {
                'success': False,
                'error': 'La evaluación no está pendiente de aprobación'
            }
        
        review.employee_comments = employee_comments
        review.status = 'completed'
        review.save()
        
        return {
            'success': True,
            'message': 'Evaluación completada'
        }
    
    def get_performance_analytics(
        self,
        department_id: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene analíticas de desempeño.
        """
        from .models import PerformanceReview
        
        query = PerformanceReview.objects.filter(status='completed')
        
        if department_id:
            query = query.filter(employee__department_id=department_id)
        
        if year:
            query = query.filter(review_date__year=year)
        
        stats = query.aggregate(
            avg_score=Avg('overall_score'),
            total_reviews=Count('id')
        )
        
        by_department = list(
            query.values('employee__department__name')
            .annotate(
                avg_score=Avg('overall_score'),
                count=Count('id')
            )
            .order_by('-avg_score')
        )
        
        score_distribution = {
            'excellent': query.filter(overall_score__gte=9).count(),
            'good': query.filter(overall_score__gte=7, overall_score__lt=9).count(),
            'average': query.filter(overall_score__gte=5, overall_score__lt=7).count(),
            'below_average': query.filter(overall_score__lt=5).count()
        }
        
        return {
            'average_score': float(stats['avg_score'] or 0),
            'total_reviews': stats['total_reviews'],
            'by_department': by_department,
            'score_distribution': score_distribution
        }
