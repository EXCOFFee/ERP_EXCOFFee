# ========================================================
# SISTEMA ERP UNIVERSAL - Tareas Asíncronas de Finanzas
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Tareas asíncronas con Celery para el módulo
#            de finanzas. Incluye generación de reportes,
#            cálculos contables y alertas de presupuesto.
# ========================================================

from celery import shared_task
from django.db import transaction
from django.db.models import Sum, F, Q
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


# ========================================================
# Tareas de Reportes Financieros
# ========================================================

@shared_task(bind=True, max_retries=3)
def generate_financial_report(self, report_type: str, period_id: int, params: dict = None):
    """
    Genera un reporte financiero de forma asíncrona.
    
    Args:
        report_type: Tipo de reporte (trial_balance, income_statement, balance_sheet)
        period_id: ID del período contable
        params: Parámetros adicionales del reporte
    """
    from .models import AccountingPeriod, Account, JournalEntry
    from .services import AccountingService
    
    try:
        logger.info(f"Generando reporte {report_type} para período {period_id}")
        
        period = AccountingPeriod.objects.get(pk=period_id)
        service = AccountingService()
        
        if report_type == 'trial_balance':
            report_data = service.get_trial_balance(period_id)
        elif report_type == 'income_statement':
            report_data = _generate_income_statement(period)
        elif report_type == 'balance_sheet':
            report_data = _generate_balance_sheet(period)
        else:
            raise ValueError(f"Tipo de reporte no soportado: {report_type}")
        
        # Guardar reporte generado
        from .models import GeneratedReport
        report = GeneratedReport.objects.create(
            report_type=report_type,
            period=period,
            data=report_data,
            generated_at=timezone.now(),
            status='completed'
        )
        
        logger.info(f"Reporte {report_type} generado exitosamente: {report.id}")
        return {'status': 'success', 'report_id': report.id}
        
    except AccountingPeriod.DoesNotExist:
        logger.error(f"Período contable no encontrado: {period_id}")
        return {'status': 'error', 'message': 'Período no encontrado'}
    except Exception as e:
        logger.error(f"Error generando reporte: {str(e)}")
        self.retry(exc=e, countdown=60)


@shared_task
def generate_trial_balance_pdf(period_id: int, email_to: str = None):
    """
    Genera balance de comprobación en PDF.
    """
    from .models import AccountingPeriod, Account
    from .services import AccountingService
    
    try:
        logger.info(f"Generando PDF de balance de comprobación para período {period_id}")
        
        period = AccountingPeriod.objects.get(pk=period_id)
        service = AccountingService()
        
        # Obtener datos del balance
        trial_balance = service.get_trial_balance(period_id)
        
        # Generar PDF (usando reportlab o weasyprint)
        pdf_content = _generate_trial_balance_pdf(period, trial_balance)
        
        # Guardar PDF
        file_path = f"reports/trial_balance_{period.code}_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf"
        
        # Si hay email, enviar
        if email_to:
            send_mail(
                subject=f'Balance de Comprobación - {period.code}',
                message='Adjunto el balance de comprobación solicitado.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_to],
                fail_silently=True,
            )
        
        logger.info(f"PDF generado: {file_path}")
        return {'status': 'success', 'file_path': file_path}
        
    except Exception as e:
        logger.error(f"Error generando PDF: {str(e)}")
        return {'status': 'error', 'message': str(e)}


# ========================================================
# Tareas de Alertas de Presupuesto
# ========================================================

@shared_task
def check_budget_alerts():
    """
    Verifica alertas de presupuesto y notifica cuando
    se exceden los umbrales configurados.
    """
    from .models import Budget, BudgetLine, Account
    
    logger.info("Verificando alertas de presupuesto")
    
    # Obtener presupuestos activos
    active_budgets = Budget.objects.filter(
        status='approved',
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    )
    
    alerts = []
    
    for budget in active_budgets:
        budget_lines = BudgetLine.objects.filter(budget=budget).select_related('account')
        
        for line in budget_lines:
            # Calcular ejecución actual
            executed_amount = _calculate_budget_execution(line)
            
            if line.budgeted_amount > 0:
                execution_percentage = (executed_amount / line.budgeted_amount) * 100
            else:
                execution_percentage = 0
            
            # Verificar umbrales
            if execution_percentage >= 100:
                alert_level = 'critical'
            elif execution_percentage >= 90:
                alert_level = 'warning'
            elif execution_percentage >= 75:
                alert_level = 'info'
            else:
                continue
            
            alerts.append({
                'budget': budget.name,
                'account': line.account.name,
                'budgeted': float(line.budgeted_amount),
                'executed': float(executed_amount),
                'percentage': round(execution_percentage, 2),
                'alert_level': alert_level
            })
    
    # Enviar notificaciones
    if alerts:
        _send_budget_alerts(alerts)
    
    logger.info(f"Verificación completada: {len(alerts)} alertas encontradas")
    return {'alerts_count': len(alerts), 'alerts': alerts}


@shared_task
def check_budget_overruns():
    """
    Detecta sobregiros presupuestarios.
    """
    from .models import Budget, BudgetLine
    
    logger.info("Verificando sobregiros presupuestarios")
    
    overruns = []
    active_budgets = Budget.objects.filter(
        status='approved',
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    )
    
    for budget in active_budgets:
        lines = BudgetLine.objects.filter(budget=budget)
        
        for line in lines:
            executed = _calculate_budget_execution(line)
            
            if executed > line.budgeted_amount:
                overrun_amount = executed - line.budgeted_amount
                overruns.append({
                    'budget_id': budget.id,
                    'budget_name': budget.name,
                    'account_id': line.account_id,
                    'account_name': line.account.name,
                    'budgeted': float(line.budgeted_amount),
                    'executed': float(executed),
                    'overrun': float(overrun_amount)
                })
    
    logger.info(f"Sobregiros detectados: {len(overruns)}")
    return {'overruns': overruns}


# ========================================================
# Tareas de Cierre Contable
# ========================================================

@shared_task(bind=True, max_retries=3)
def close_accounting_period(self, period_id: int, user_id: int):
    """
    Cierra un período contable de forma asíncrona.
    """
    from .models import AccountingPeriod, JournalEntry
    from .services import AccountingService
    
    try:
        logger.info(f"Iniciando cierre de período {period_id}")
        
        period = AccountingPeriod.objects.get(pk=period_id)
        
        if period.is_closed:
            return {'status': 'error', 'message': 'El período ya está cerrado'}
        
        with transaction.atomic():
            # Verificar asientos sin contabilizar
            pending_entries = JournalEntry.objects.filter(
                period=period,
                status='draft'
            ).count()
            
            if pending_entries > 0:
                return {
                    'status': 'error',
                    'message': f'Existen {pending_entries} asientos pendientes de contabilizar'
                }
            
            # Generar asientos de cierre
            service = AccountingService()
            service.close_period(period_id, user_id)
            
            # Marcar período como cerrado
            period.is_closed = True
            period.closed_at = timezone.now()
            period.closed_by_id = user_id
            period.save()
            
        logger.info(f"Período {period_id} cerrado exitosamente")
        return {'status': 'success', 'message': 'Período cerrado exitosamente'}
        
    except AccountingPeriod.DoesNotExist:
        logger.error(f"Período no encontrado: {period_id}")
        return {'status': 'error', 'message': 'Período no encontrado'}
    except Exception as e:
        logger.error(f"Error cerrando período: {str(e)}")
        self.retry(exc=e, countdown=120)


@shared_task
def generate_closing_entries(period_id: int, user_id: int):
    """
    Genera asientos de cierre automáticos.
    """
    from .models import AccountingPeriod, Account, JournalEntry, JournalEntryLine
    
    try:
        logger.info(f"Generando asientos de cierre para período {period_id}")
        
        period = AccountingPeriod.objects.get(pk=period_id)
        
        # Cuentas de resultados (ingresos y gastos)
        income_accounts = Account.objects.filter(
            account_type__nature='credit',
            account_type__classification='income'
        )
        expense_accounts = Account.objects.filter(
            account_type__nature='debit',
            account_type__classification='expense'
        )
        
        # Calcular saldos
        total_income = Decimal('0')
        total_expenses = Decimal('0')
        
        closing_lines = []
        
        # Cerrar ingresos
        for account in income_accounts:
            balance = _get_account_balance(account, period)
            if balance != 0:
                total_income += balance
                closing_lines.append({
                    'account': account,
                    'debit': balance if balance > 0 else 0,
                    'credit': abs(balance) if balance < 0 else 0
                })
        
        # Cerrar gastos
        for account in expense_accounts:
            balance = _get_account_balance(account, period)
            if balance != 0:
                total_expenses += abs(balance)
                closing_lines.append({
                    'account': account,
                    'debit': 0 if balance > 0 else abs(balance),
                    'credit': balance if balance > 0 else 0
                })
        
        # Crear asiento de cierre
        net_result = total_income - total_expenses
        
        with transaction.atomic():
            entry = JournalEntry.objects.create(
                period=period,
                date=period.end_date,
                reference=f'CIERRE-{period.code}',
                description='Asiento de cierre de período',
                entry_type='closing',
                created_by_id=user_id
            )
            
            # Agregar líneas
            for line_data in closing_lines:
                JournalEntryLine.objects.create(
                    entry=entry,
                    account=line_data['account'],
                    debit=line_data['debit'],
                    credit=line_data['credit']
                )
            
            # Línea de resultado
            retained_earnings = Account.objects.filter(
                code__startswith='3.2'  # Utilidades retenidas
            ).first()
            
            if retained_earnings:
                JournalEntryLine.objects.create(
                    entry=entry,
                    account=retained_earnings,
                    debit=abs(net_result) if net_result < 0 else 0,
                    credit=net_result if net_result > 0 else 0
                )
        
        logger.info(f"Asientos de cierre generados: {entry.id}")
        return {'status': 'success', 'entry_id': entry.id, 'net_result': float(net_result)}
        
    except Exception as e:
        logger.error(f"Error generando asientos de cierre: {str(e)}")
        return {'status': 'error', 'message': str(e)}


# ========================================================
# Tareas de Conciliación Bancaria
# ========================================================

@shared_task
def process_bank_statement(bank_account_id: int, statement_data: list):
    """
    Procesa un estado de cuenta bancario.
    """
    from .models import BankAccount, BankTransaction
    
    try:
        logger.info(f"Procesando estado de cuenta para banco {bank_account_id}")
        
        bank_account = BankAccount.objects.get(pk=bank_account_id)
        created_count = 0
        matched_count = 0
        
        with transaction.atomic():
            for row in statement_data:
                # Verificar si ya existe
                existing = BankTransaction.objects.filter(
                    bank_account=bank_account,
                    reference=row.get('reference'),
                    amount=row.get('amount')
                ).first()
                
                if existing:
                    matched_count += 1
                    continue
                
                # Crear nueva transacción
                BankTransaction.objects.create(
                    bank_account=bank_account,
                    date=row.get('date'),
                    reference=row.get('reference'),
                    description=row.get('description'),
                    amount=row.get('amount'),
                    transaction_type=row.get('type', 'other'),
                    status='pending'
                )
                created_count += 1
        
        logger.info(f"Estado procesado: {created_count} nuevas, {matched_count} existentes")
        return {
            'status': 'success',
            'created': created_count,
            'matched': matched_count
        }
        
    except Exception as e:
        logger.error(f"Error procesando estado de cuenta: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def auto_reconcile_bank_transactions(bank_account_id: int):
    """
    Conciliación automática de transacciones bancarias.
    """
    from .models import BankAccount, BankTransaction, JournalEntry
    
    try:
        logger.info(f"Iniciando conciliación automática para banco {bank_account_id}")
        
        bank_account = BankAccount.objects.get(pk=bank_account_id)
        pending_transactions = BankTransaction.objects.filter(
            bank_account=bank_account,
            status='pending'
        )
        
        reconciled_count = 0
        
        for transaction in pending_transactions:
            # Buscar asiento contable que coincida
            matching_entry = JournalEntry.objects.filter(
                status='posted',
                lines__account=bank_account.account,
                total_amount=abs(transaction.amount)
            ).first()
            
            if matching_entry:
                transaction.journal_entry = matching_entry
                transaction.status = 'reconciled'
                transaction.reconciled_at = timezone.now()
                transaction.save()
                reconciled_count += 1
        
        logger.info(f"Conciliación completada: {reconciled_count} transacciones")
        return {
            'status': 'success',
            'reconciled_count': reconciled_count,
            'pending_count': pending_transactions.count() - reconciled_count
        }
        
    except Exception as e:
        logger.error(f"Error en conciliación: {str(e)}")
        return {'status': 'error', 'message': str(e)}


# ========================================================
# Tareas de Cálculo de Impuestos
# ========================================================

@shared_task
def calculate_tax_liabilities(period_id: int):
    """
    Calcula las obligaciones tributarias del período.
    """
    from .models import AccountingPeriod, Tax, JournalEntry
    
    try:
        logger.info(f"Calculando obligaciones tributarias para período {period_id}")
        
        period = AccountingPeriod.objects.get(pk=period_id)
        taxes = Tax.objects.filter(is_active=True)
        
        tax_liabilities = []
        
        for tax in taxes:
            # Calcular base gravable según tipo de impuesto
            if tax.tax_type == 'sales':
                taxable_base = _calculate_sales_tax_base(period, tax)
            elif tax.tax_type == 'income':
                taxable_base = _calculate_income_tax_base(period, tax)
            elif tax.tax_type == 'withholding':
                taxable_base = _calculate_withholding_base(period, tax)
            else:
                continue
            
            tax_amount = taxable_base * (tax.rate / 100)
            
            tax_liabilities.append({
                'tax_id': tax.id,
                'tax_name': tax.name,
                'taxable_base': float(taxable_base),
                'rate': float(tax.rate),
                'tax_amount': float(tax_amount)
            })
        
        logger.info(f"Obligaciones calculadas: {len(tax_liabilities)} impuestos")
        return {'status': 'success', 'liabilities': tax_liabilities}
        
    except Exception as e:
        logger.error(f"Error calculando impuestos: {str(e)}")
        return {'status': 'error', 'message': str(e)}


# ========================================================
# Funciones Auxiliares
# ========================================================

def _calculate_budget_execution(budget_line) -> Decimal:
    """Calcula la ejecución de una línea de presupuesto."""
    from .models import JournalEntryLine
    
    result = JournalEntryLine.objects.filter(
        account=budget_line.account,
        entry__period__start_date__gte=budget_line.budget.start_date,
        entry__period__end_date__lte=budget_line.budget.end_date,
        entry__status='posted'
    ).aggregate(
        total_debit=Sum('debit'),
        total_credit=Sum('credit')
    )
    
    total_debit = result['total_debit'] or Decimal('0')
    total_credit = result['total_credit'] or Decimal('0')
    
    # Retornar según naturaleza de la cuenta
    if budget_line.account.account_type.nature == 'debit':
        return total_debit - total_credit
    return total_credit - total_debit


def _get_account_balance(account, period) -> Decimal:
    """Obtiene el saldo de una cuenta en un período."""
    from .models import JournalEntryLine
    
    result = JournalEntryLine.objects.filter(
        account=account,
        entry__period=period,
        entry__status='posted'
    ).aggregate(
        total_debit=Sum('debit'),
        total_credit=Sum('credit')
    )
    
    total_debit = result['total_debit'] or Decimal('0')
    total_credit = result['total_credit'] or Decimal('0')
    
    if account.account_type.nature == 'debit':
        return total_debit - total_credit
    return total_credit - total_debit


def _send_budget_alerts(alerts: list):
    """Envía notificaciones de alertas de presupuesto."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Obtener usuarios con rol de finanzas
    finance_users = User.objects.filter(
        role__permissions__codename='view_budget_alerts'
    ).distinct()
    
    for user in finance_users:
        if user.email:
            critical_alerts = [a for a in alerts if a['alert_level'] == 'critical']
            
            if critical_alerts:
                send_mail(
                    subject='[ERP] Alerta Crítica de Presupuesto',
                    message=f'Se han detectado {len(critical_alerts)} sobregiros críticos.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )


def _generate_income_statement(period) -> dict:
    """Genera estado de resultados."""
    from .models import Account, JournalEntryLine
    
    income_accounts = Account.objects.filter(
        account_type__classification='income'
    )
    expense_accounts = Account.objects.filter(
        account_type__classification='expense'
    )
    
    income_data = []
    expense_data = []
    total_income = Decimal('0')
    total_expenses = Decimal('0')
    
    for account in income_accounts:
        balance = _get_account_balance(account, period)
        if balance != 0:
            total_income += balance
            income_data.append({
                'code': account.code,
                'name': account.name,
                'balance': float(balance)
            })
    
    for account in expense_accounts:
        balance = abs(_get_account_balance(account, period))
        if balance != 0:
            total_expenses += balance
            expense_data.append({
                'code': account.code,
                'name': account.name,
                'balance': float(balance)
            })
    
    return {
        'period': period.code,
        'incomes': income_data,
        'expenses': expense_data,
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'net_result': float(total_income - total_expenses)
    }


def _generate_balance_sheet(period) -> dict:
    """Genera balance general."""
    from .models import Account, JournalEntryLine
    
    assets = []
    liabilities = []
    equity = []
    
    total_assets = Decimal('0')
    total_liabilities = Decimal('0')
    total_equity = Decimal('0')
    
    for account in Account.objects.filter(account_type__classification='asset'):
        balance = _get_account_balance(account, period)
        if balance != 0:
            total_assets += balance
            assets.append({
                'code': account.code,
                'name': account.name,
                'balance': float(balance)
            })
    
    for account in Account.objects.filter(account_type__classification='liability'):
        balance = _get_account_balance(account, period)
        if balance != 0:
            total_liabilities += balance
            liabilities.append({
                'code': account.code,
                'name': account.name,
                'balance': float(balance)
            })
    
    for account in Account.objects.filter(account_type__classification='equity'):
        balance = _get_account_balance(account, period)
        if balance != 0:
            total_equity += balance
            equity.append({
                'code': account.code,
                'name': account.name,
                'balance': float(balance)
            })
    
    return {
        'period': period.code,
        'assets': assets,
        'liabilities': liabilities,
        'equity': equity,
        'total_assets': float(total_assets),
        'total_liabilities': float(total_liabilities),
        'total_equity': float(total_equity),
        'balance_check': float(total_assets - total_liabilities - total_equity)
    }


def _generate_trial_balance_pdf(period, data: dict) -> bytes:
    """Genera PDF del balance de comprobación."""
    # Implementación con reportlab o weasyprint
    # Placeholder - requiere biblioteca de generación de PDF
    return b''


def _calculate_sales_tax_base(period, tax) -> Decimal:
    """Calcula base gravable de IVA ventas."""
    from .models import JournalEntryLine, Account
    
    sales_accounts = Account.objects.filter(
        code__startswith='4.1'  # Cuentas de ventas
    )
    
    result = JournalEntryLine.objects.filter(
        account__in=sales_accounts,
        entry__period=period,
        entry__status='posted'
    ).aggregate(total=Sum('credit'))
    
    return result['total'] or Decimal('0')


def _calculate_income_tax_base(period, tax) -> Decimal:
    """Calcula base gravable de impuesto de renta."""
    # Utilidad antes de impuestos
    income_statement = _generate_income_statement(period)
    return Decimal(str(income_statement['net_result']))


def _calculate_withholding_base(period, tax) -> Decimal:
    """Calcula base de retenciones."""
    from .models import JournalEntryLine, Account
    
    # Cuentas de retención
    withholding_accounts = Account.objects.filter(
        code__startswith='2.4.7'  # Retenciones por pagar
    )
    
    result = JournalEntryLine.objects.filter(
        account__in=withholding_accounts,
        entry__period=period,
        entry__status='posted'
    ).aggregate(total=Sum('credit'))
    
    return result['total'] or Decimal('0')
