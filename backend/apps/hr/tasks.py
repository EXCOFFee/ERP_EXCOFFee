# ========================================================
# SISTEMA ERP UNIVERSAL - Tareas Asíncronas de RRHH
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Tareas asíncronas con Celery para el módulo
#            de recursos humanos.
# ========================================================

from celery import shared_task
from django.db import transaction
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta, date
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


# ========================================================
# Tareas de Notificaciones
# ========================================================

@shared_task
def send_leave_request_notification(request_id: int, action: str):
    """
    Envía notificación sobre solicitud de ausencia.
    
    Args:
        request_id: ID de la solicitud
        action: Acción realizada (submitted, approved, rejected)
    """
    from .models import LeaveRequest
    
    try:
        request = LeaveRequest.objects.select_related(
            'employee', 'leave_type', 'approved_by'
        ).get(pk=request_id)
        
        subject_map = {
            'submitted': f'Nueva solicitud de ausencia - {request.employee.full_name}',
            'approved': f'Solicitud de ausencia aprobada - {request.leave_type.name}',
            'rejected': f'Solicitud de ausencia rechazada - {request.leave_type.name}'
        }
        
        if action == 'submitted':
            # Notificar al manager
            if request.employee.manager and request.employee.manager.work_email:
                send_mail(
                    subject=subject_map[action],
                    message=f'{request.employee.full_name} ha solicitado {request.days} días '
                            f'de {request.leave_type.name} del {request.start_date} al {request.end_date}.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.employee.manager.work_email],
                    fail_silently=True,
                )
        
        elif action in ['approved', 'rejected']:
            # Notificar al empleado
            email = request.employee.work_email or request.employee.email
            if email:
                message = f'Tu solicitud de {request.leave_type.name} ha sido {action}.'
                if action == 'rejected' and request.rejection_reason:
                    message += f'\nMotivo: {request.rejection_reason}'
                
                send_mail(
                    subject=subject_map[action],
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
        
        logger.info(f"Notificación de ausencia enviada: {action} - {request_id}")
        return {'status': 'success'}
        
    except LeaveRequest.DoesNotExist:
        logger.error(f"Solicitud de ausencia no encontrada: {request_id}")
        return {'status': 'error', 'message': 'Solicitud no encontrada'}


@shared_task
def send_birthday_greetings():
    """
    Envía felicitaciones de cumpleaños.
    """
    from .models import Employee
    
    today = timezone.now().date()
    
    birthday_employees = Employee.objects.filter(
        birth_date__month=today.month,
        birth_date__day=today.day,
        status='active'
    )
    
    sent_count = 0
    for employee in birthday_employees:
        email = employee.work_email or employee.email
        if email:
            send_mail(
                subject=f'¡Feliz Cumpleaños {employee.first_name}! 🎂',
                message=f'Querido/a {employee.first_name},\n\n'
                        f'Todo el equipo te desea un muy feliz cumpleaños. '
                        f'Que este nuevo año de vida esté lleno de éxitos y bendiciones.\n\n'
                        f'¡Feliz día!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
            sent_count += 1
    
    logger.info(f"Felicitaciones de cumpleaños enviadas: {sent_count}")
    return {'status': 'success', 'sent': sent_count}


@shared_task
def notify_contract_expiration():
    """
    Notifica contratos próximos a vencer.
    """
    from .models import Employee
    
    # Contratos que vencen en los próximos 30 días
    today = timezone.now().date()
    expiration_date = today + timedelta(days=30)
    
    expiring_contracts = Employee.objects.filter(
        contract_type='fixed',
        contract_end_date__lte=expiration_date,
        contract_end_date__gte=today,
        status='active'
    ).select_related('department', 'manager')
    
    if not expiring_contracts.exists():
        return {'status': 'success', 'message': 'No hay contratos por vencer'}
    
    # Agrupar por departamento y notificar a managers
    notifications = {}
    for employee in expiring_contracts:
        if employee.manager and employee.manager.work_email:
            if employee.manager.id not in notifications:
                notifications[employee.manager.id] = {
                    'email': employee.manager.work_email,
                    'employees': []
                }
            notifications[employee.manager.id]['employees'].append({
                'name': employee.full_name,
                'end_date': employee.contract_end_date.isoformat(),
                'days_remaining': (employee.contract_end_date - today).days
            })
    
    for manager_id, data in notifications.items():
        employee_list = '\n'.join([
            f"- {e['name']}: {e['days_remaining']} días restantes (vence {e['end_date']})"
            for e in data['employees']
        ])
        
        send_mail(
            subject='[ERP] Contratos próximos a vencer',
            message=f'Los siguientes contratos están próximos a vencer:\n\n{employee_list}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[data['email']],
            fail_silently=True,
        )
    
    logger.info(f"Notificaciones de contratos enviadas: {len(notifications)}")
    return {'status': 'success', 'notifications': len(notifications)}


# ========================================================
# Tareas de Alertas
# ========================================================

@shared_task
def check_document_expiration():
    """
    Verifica documentos próximos a vencer.
    """
    from .models import EmployeeDocument
    
    today = timezone.now().date()
    expiration_threshold = today + timedelta(days=30)
    
    expiring_docs = EmployeeDocument.objects.filter(
        expiry_date__lte=expiration_threshold,
        expiry_date__gte=today,
        employee__status='active'
    ).select_related('employee')
    
    alerts = []
    for doc in expiring_docs:
        days_remaining = (doc.expiry_date - today).days
        alerts.append({
            'employee': doc.employee.full_name,
            'document': doc.name,
            'type': doc.document_type,
            'expiry_date': doc.expiry_date.isoformat(),
            'days_remaining': days_remaining
        })
        
        # Notificar al empleado
        email = doc.employee.work_email or doc.employee.email
        if email:
            send_mail(
                subject=f'[ERP] Documento próximo a vencer: {doc.name}',
                message=f'Tu documento "{doc.name}" vence el {doc.expiry_date}. '
                        f'Quedan {days_remaining} días para renovarlo.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
    
    logger.info(f"Alertas de documentos generadas: {len(alerts)}")
    return {'status': 'success', 'alerts': alerts}


@shared_task
def check_probation_period_ending():
    """
    Verifica períodos de prueba próximos a terminar.
    """
    from .models import Employee
    
    today = timezone.now().date()
    
    # Empleados con menos de 90 días y próximos a cumplir el período
    probation_end = today + timedelta(days=7)
    probation_start = probation_end - timedelta(days=90)
    
    employees = Employee.objects.filter(
        hire_date__gte=probation_start,
        hire_date__lte=today - timedelta(days=83),  # 83-90 días
        status='active'
    ).select_related('department', 'manager')
    
    alerts = []
    for employee in employees:
        days_employed = (today - employee.hire_date).days
        days_remaining = 90 - days_employed
        
        if days_remaining <= 7:
            alerts.append({
                'employee_id': employee.id,
                'employee_name': employee.full_name,
                'department': employee.department.name if employee.department else None,
                'hire_date': employee.hire_date.isoformat(),
                'probation_ends': (employee.hire_date + timedelta(days=90)).isoformat(),
                'days_remaining': days_remaining
            })
            
            # Notificar al manager
            if employee.manager and employee.manager.work_email:
                send_mail(
                    subject=f'[ERP] Período de prueba finalizando: {employee.full_name}',
                    message=f'El período de prueba de {employee.full_name} finaliza en '
                            f'{days_remaining} días. Por favor toma una decisión de continuidad.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[employee.manager.work_email],
                    fail_silently=True,
                )
    
    logger.info(f"Alertas de período de prueba: {len(alerts)}")
    return {'status': 'success', 'alerts': alerts}


@shared_task
def check_leave_balance_low():
    """
    Verifica empleados con saldo bajo de ausencias.
    """
    from .models import LeaveBalance, LeaveType
    
    current_year = timezone.now().year
    
    low_balances = LeaveBalance.objects.filter(
        year=current_year,
        employee__status='active'
    ).select_related('employee', 'leave_type')
    
    alerts = []
    for balance in low_balances:
        available = balance.allocated_days + balance.carried_over - balance.used_days
        
        # Alertar si queda menos del 20% del asignado
        if balance.allocated_days > 0:
            percentage = (available / balance.allocated_days) * 100
            if percentage <= 20 and available > 0:
                alerts.append({
                    'employee': balance.employee.full_name,
                    'leave_type': balance.leave_type.name,
                    'available_days': float(available),
                    'percentage': round(percentage, 1)
                })
    
    logger.info(f"Alertas de saldo bajo: {len(alerts)}")
    return {'status': 'success', 'alerts': alerts}


# ========================================================
# Tareas de Nómina
# ========================================================

@shared_task(bind=True, max_retries=3)
def process_payroll_async(self, period_id: int, user_id: int):
    """
    Procesa la nómina de forma asíncrona.
    """
    from .services import PayrollService
    
    try:
        logger.info(f"Iniciando procesamiento de nómina: {period_id}")
        
        service = PayrollService()
        result = service.generate_payslips(period_id=period_id)
        
        if result['success']:
            logger.info(f"Nómina procesada exitosamente: {result['payslips_created']} recibos")
            return result
        else:
            logger.error(f"Error procesando nómina: {result.get('error')}")
            return result
            
    except Exception as e:
        logger.error(f"Error en tarea de nómina: {str(e)}")
        self.retry(exc=e, countdown=60)


@shared_task
def send_payslip_notifications(period_id: int):
    """
    Envía notificaciones de recibos de nómina.
    """
    from .models import Payslip
    
    payslips = Payslip.objects.filter(
        period_id=period_id,
        status='paid'
    ).select_related('employee', 'period')
    
    sent_count = 0
    for payslip in payslips:
        email = payslip.employee.work_email or payslip.employee.email
        if email:
            send_mail(
                subject=f'Tu recibo de nómina - {payslip.period.name}',
                message=f'Hola {payslip.employee.first_name},\n\n'
                        f'Tu recibo de nómina para el período {payslip.period.name} '
                        f'está disponible.\n\n'
                        f'Salario Neto: ${payslip.net_salary:,.2f}\n\n'
                        f'Puedes consultarlo en el sistema.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
            sent_count += 1
    
    logger.info(f"Notificaciones de nómina enviadas: {sent_count}")
    return {'status': 'success', 'sent': sent_count}


@shared_task
def process_loan_deductions(period_id: int):
    """
    Procesa deducciones de préstamos para un período de nómina.
    """
    from .models import PayrollPeriod, Payslip, PayslipLine, Loan, LoanPayment, SalaryComponent
    
    try:
        period = PayrollPeriod.objects.get(pk=period_id)
        
        # Obtener componente de deducción de préstamo
        loan_component = SalaryComponent.objects.filter(
            code='LOAN_DEDUCTION',
            component_type='deduction',
            is_active=True
        ).first()
        
        if not loan_component:
            return {'status': 'error', 'message': 'Componente de deducción de préstamo no encontrado'}
        
        # Obtener préstamos activos
        active_loans = Loan.objects.filter(
            status='active',
            start_date__lte=period.end_date,
            remaining_amount__gt=0
        ).select_related('employee')
        
        processed_count = 0
        
        with transaction.atomic():
            for loan in active_loans:
                # Verificar si existe payslip
                payslip = Payslip.objects.filter(
                    period=period,
                    employee=loan.employee
                ).first()
                
                if not payslip:
                    continue
                
                # Crear línea de deducción
                PayslipLine.objects.create(
                    payslip=payslip,
                    component=loan_component,
                    amount=loan.installment_amount,
                    notes=f'Cuota préstamo #{loan.id}'
                )
                
                # Registrar pago del préstamo
                LoanPayment.objects.create(
                    loan=loan,
                    payslip=payslip,
                    payment_date=period.payment_date,
                    principal_amount=loan.installment_amount,
                    interest_amount=Decimal('0'),
                    total_amount=loan.installment_amount,
                    installment_number=loan.paid_installments + 1
                )
                
                # Actualizar préstamo
                loan.paid_installments += 1
                loan.remaining_amount -= loan.installment_amount
                
                if loan.remaining_amount <= 0:
                    loan.status = 'paid'
                    loan.remaining_amount = Decimal('0')
                
                loan.save()
                processed_count += 1
        
        logger.info(f"Deducciones de préstamos procesadas: {processed_count}")
        return {'status': 'success', 'processed': processed_count}
        
    except Exception as e:
        logger.error(f"Error procesando deducciones: {str(e)}")
        return {'status': 'error', 'message': str(e)}


# ========================================================
# Tareas de Asistencia
# ========================================================

@shared_task
def generate_attendance_report(start_date: str, end_date: str, department_id: int = None):
    """
    Genera reporte de asistencia.
    """
    from .services import AttendanceService
    from datetime import datetime
    
    service = AttendanceService()
    report = service.get_attendance_report(
        start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
        end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
        department_id=department_id
    )
    
    logger.info(f"Reporte de asistencia generado: {start_date} a {end_date}")
    return report


@shared_task
def mark_absent_employees():
    """
    Marca como ausentes a empleados sin registro de asistencia.
    """
    from .models import Employee, Attendance, Holiday
    
    today = timezone.now().date()
    
    # Verificar si es feriado
    is_holiday = Holiday.objects.filter(
        date=today,
        applies_to_all=True
    ).exists()
    
    if is_holiday or today.weekday() >= 5:  # Fin de semana
        return {'status': 'skipped', 'reason': 'Holiday or weekend'}
    
    # Empleados activos sin registro de asistencia
    employees_with_attendance = Attendance.objects.filter(
        date=today
    ).values_list('employee_id', flat=True)
    
    employees_without = Employee.objects.filter(
        status='active'
    ).exclude(id__in=employees_with_attendance)
    
    created_count = 0
    for employee in employees_without:
        Attendance.objects.create(
            employee=employee,
            date=today,
            status='absent'
        )
        created_count += 1
    
    logger.info(f"Empleados marcados ausentes: {created_count}")
    return {'status': 'success', 'marked_absent': created_count}


@shared_task
def calculate_overtime_hours(period_start: str, period_end: str):
    """
    Calcula horas extra para un período.
    """
    from .models import Attendance, Employee
    from datetime import datetime
    
    start = datetime.strptime(period_start, '%Y-%m-%d').date()
    end = datetime.strptime(period_end, '%Y-%m-%d').date()
    
    # Agrupar por empleado
    overtime_summary = Attendance.objects.filter(
        date__gte=start,
        date__lte=end,
        overtime_hours__gt=0
    ).values('employee_id', 'employee__first_name', 'employee__last_name').annotate(
        total_overtime=Sum('overtime_hours'),
        days_with_overtime=Count('id')
    ).order_by('-total_overtime')
    
    return {
        'status': 'success',
        'period': {'start': period_start, 'end': period_end},
        'summary': list(overtime_summary)
    }


# ========================================================
# Tareas de Evaluación de Desempeño
# ========================================================

@shared_task
def send_performance_review_reminders():
    """
    Envía recordatorios de evaluaciones pendientes.
    """
    from .models import PerformanceReview
    
    pending_reviews = PerformanceReview.objects.filter(
        status__in=['draft', 'in_progress']
    ).select_related('employee', 'reviewer')
    
    sent_count = 0
    for review in pending_reviews:
        if review.reviewer and review.reviewer.work_email:
            send_mail(
                subject=f'[ERP] Evaluación pendiente: {review.employee.full_name}',
                message=f'Tienes una evaluación de desempeño pendiente para '
                        f'{review.employee.full_name}. Por favor complétala.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[review.reviewer.work_email],
                fail_silently=True,
            )
            sent_count += 1
    
    logger.info(f"Recordatorios de evaluación enviados: {sent_count}")
    return {'status': 'success', 'sent': sent_count}


@shared_task
def generate_performance_analytics(year: int = None):
    """
    Genera analíticas de desempeño anuales.
    """
    from .services import PerformanceService
    
    if not year:
        year = timezone.now().year
    
    service = PerformanceService()
    analytics = service.get_performance_analytics(year=year)
    
    logger.info(f"Analíticas de desempeño generadas para {year}")
    return analytics


# ========================================================
# Tareas de Capacitación
# ========================================================

@shared_task
def send_training_reminders():
    """
    Envía recordatorios de capacitaciones próximas.
    """
    from .models import Training, TrainingParticipant
    
    today = timezone.now().date()
    reminder_date = today + timedelta(days=7)
    
    upcoming_trainings = Training.objects.filter(
        start_date__lte=reminder_date,
        start_date__gt=today,
        status='planned'
    )
    
    sent_count = 0
    for training in upcoming_trainings:
        participants = TrainingParticipant.objects.filter(
            training=training,
            status__in=['enrolled', 'confirmed']
        ).select_related('employee')
        
        for participant in participants:
            email = participant.employee.work_email or participant.employee.email
            if email:
                days_until = (training.start_date - today).days
                send_mail(
                    subject=f'[ERP] Recordatorio: Capacitación "{training.name}"',
                    message=f'Te recordamos que la capacitación "{training.name}" '
                            f'inicia en {days_until} días ({training.start_date}).\n\n'
                            f'Ubicación: {training.location or "Por confirmar"}\n'
                            f'Duración: {training.duration_hours} horas',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
                sent_count += 1
    
    logger.info(f"Recordatorios de capacitación enviados: {sent_count}")
    return {'status': 'success', 'sent': sent_count}


@shared_task
def update_training_status():
    """
    Actualiza estado de capacitaciones según fechas.
    """
    from .models import Training
    
    today = timezone.now().date()
    
    # Marcar como en progreso
    Training.objects.filter(
        status='planned',
        start_date__lte=today,
        end_date__gte=today
    ).update(status='in_progress')
    
    # Marcar como completadas
    Training.objects.filter(
        status='in_progress',
        end_date__lt=today
    ).update(status='completed')
    
    logger.info("Estados de capacitación actualizados")
    return {'status': 'success'}
