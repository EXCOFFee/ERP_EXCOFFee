# ========================================================
# SISTEMA ERP UNIVERSAL - Servicios de Finanzas
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Lógica de negocio para operaciones financieras.
# ========================================================

from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from django.db import transaction
from django.db.models import Sum, F, Q
from django.utils import timezone

from .models import (
    AccountingPeriod,
    Account,
    AccountType,
    JournalEntry,
    JournalEntryLine,
    CostCenter,
    Budget,
)
from apps.core.exceptions import ValidationException


class AccountingService:
    """
    Servicio para operaciones contables.
    
    Propósito:
        Centralizar la lógica de negocio de contabilidad.
    """
    
    @staticmethod
    def get_current_period() -> Optional[AccountingPeriod]:
        """
        Obtiene el período contable actual.
        
        Returns:
            AccountingPeriod o None
        """
        return AccountingPeriod.objects.filter(
            is_current=True,
            status=AccountingPeriod.PeriodStatus.OPEN
        ).first()
    
    @staticmethod
    @transaction.atomic
    def create_journal_entry(
        entry_date,
        description: str,
        lines: List[Dict],
        entry_type: str = JournalEntry.EntryType.STANDARD,
        reference_type: str = None,
        reference_id: str = None,
        reference_number: str = None,
        notes: str = '',
        auto_post: bool = False,
        user=None
    ) -> JournalEntry:
        """
        Crea un asiento contable con sus líneas.
        
        Propósito:
            Crear asientos contables validando partida doble.
        
        Args:
            entry_date: Fecha del asiento
            description: Descripción del asiento
            lines: Lista de líneas [{'account_id': x, 'debit': 0, 'credit': 100}]
            entry_type: Tipo de asiento
            reference_type: Tipo de documento origen
            reference_id: ID del documento origen
            reference_number: Número del documento
            notes: Notas adicionales
            auto_post: Si True, contabiliza automáticamente
            user: Usuario que crea
        
        Returns:
            JournalEntry: Asiento creado
        
        Raises:
            ValidationException: Si las líneas no están balanceadas
        """
        # Obtener período
        period = AccountingService.get_current_period()
        if not period:
            raise ValidationException(
                message='No hay un período contable abierto',
                source='AccountingService.create_journal_entry'
            )
        
        # Validar fecha dentro del período
        if not (period.start_date <= entry_date <= period.end_date):
            raise ValidationException(
                message='La fecha debe estar dentro del período contable actual',
                source='AccountingService.create_journal_entry'
            )
        
        # Validar balance
        total_debit = sum(Decimal(str(line.get('debit', 0))) for line in lines)
        total_credit = sum(Decimal(str(line.get('credit', 0))) for line in lines)
        
        if total_debit != total_credit:
            raise ValidationException(
                message=f'El asiento no está balanceado. Débito: {total_debit}, Crédito: {total_credit}',
                source='AccountingService.create_journal_entry'
            )
        
        # Generar número de asiento
        import uuid
        entry_number = f"AST-{uuid.uuid4().hex[:8].upper()}"
        
        # Crear asiento
        entry = JournalEntry.objects.create(
            entry_number=entry_number,
            period=period,
            entry_date=entry_date,
            description=description,
            entry_type=entry_type,
            reference_type=reference_type or '',
            reference_id=reference_id,
            reference_number=reference_number or '',
            notes=notes,
            total_debit=total_debit,
            total_credit=total_credit,
            created_by=user
        )
        
        # Crear líneas
        for line in lines:
            account = Account.objects.get(pk=line['account_id'])
            
            if not account.is_detail:
                raise ValidationException(
                    message=f'La cuenta {account.code} no es de detalle',
                    source='AccountingService.create_journal_entry'
                )
            
            JournalEntryLine.objects.create(
                journal_entry=entry,
                account=account,
                debit=Decimal(str(line.get('debit', 0))),
                credit=Decimal(str(line.get('credit', 0))),
                description=line.get('description', ''),
                cost_center_id=line.get('cost_center_id')
            )
        
        # Contabilizar si se solicita
        if auto_post:
            entry.post(user)
        
        return entry
    
    @staticmethod
    def get_account_balance(
        account_id: str,
        period: AccountingPeriod = None,
        start_date=None,
        end_date=None
    ) -> Decimal:
        """
        Obtiene el saldo de una cuenta.
        
        Args:
            account_id: ID de la cuenta
            period: Período contable (opcional)
            start_date: Fecha inicio (opcional)
            end_date: Fecha fin (opcional)
        
        Returns:
            Decimal: Saldo de la cuenta
        """
        account = Account.objects.get(pk=account_id)
        
        entries = JournalEntryLine.objects.filter(
            account=account,
            journal_entry__status=JournalEntry.EntryStatus.POSTED
        )
        
        if period:
            entries = entries.filter(journal_entry__period=period)
        
        if start_date:
            entries = entries.filter(journal_entry__entry_date__gte=start_date)
        
        if end_date:
            entries = entries.filter(journal_entry__entry_date__lte=end_date)
        
        totals = entries.aggregate(
            total_debit=Sum('debit'),
            total_credit=Sum('credit')
        )
        
        debit = totals['total_debit'] or Decimal('0.00')
        credit = totals['total_credit'] or Decimal('0.00')
        
        # El saldo depende de la naturaleza de la cuenta
        if account.account_type.debit_nature:
            return debit - credit
        else:
            return credit - debit
    
    @staticmethod
    def get_trial_balance(period: AccountingPeriod = None) -> List[Dict]:
        """
        Genera el balance de comprobación.
        
        Propósito:
            Reporte de saldos de todas las cuentas para verificar
            que el libro mayor esté balanceado.
        
        Args:
            period: Período contable (opcional)
        
        Returns:
            Lista de cuentas con sus saldos
        """
        accounts = Account.objects.filter(
            is_detail=True,
            is_active=True
        ).select_related('account_type')
        
        result = []
        
        for account in accounts:
            balance = AccountingService.get_account_balance(
                str(account.id),
                period
            )
            
            if balance != 0:  # Solo cuentas con movimiento
                if account.account_type.debit_nature:
                    debit_balance = balance if balance > 0 else Decimal('0.00')
                    credit_balance = abs(balance) if balance < 0 else Decimal('0.00')
                else:
                    credit_balance = balance if balance > 0 else Decimal('0.00')
                    debit_balance = abs(balance) if balance < 0 else Decimal('0.00')
                
                result.append({
                    'account_code': account.code,
                    'account_name': account.name,
                    'account_type': account.account_type.name,
                    'debit_balance': debit_balance,
                    'credit_balance': credit_balance,
                })
        
        return result
    
    @staticmethod
    def get_income_statement(
        period: AccountingPeriod = None,
        start_date=None,
        end_date=None
    ) -> Dict:
        """
        Genera el estado de resultados.
        
        Propósito:
            Reporte de ingresos y gastos del período.
        
        Returns:
            {
                'incomes': [...],
                'expenses': [...],
                'total_income': Decimal,
                'total_expense': Decimal,
                'net_profit': Decimal
            }
        """
        # Obtener cuentas de ingresos
        income_type = AccountType.objects.filter(nature='income').first()
        expense_type = AccountType.objects.filter(nature='expense').first()
        
        incomes = []
        total_income = Decimal('0.00')
        
        if income_type:
            income_accounts = Account.objects.filter(
                account_type=income_type,
                is_detail=True,
                is_active=True
            )
            
            for account in income_accounts:
                balance = AccountingService.get_account_balance(
                    str(account.id), period, start_date, end_date
                )
                if balance != 0:
                    incomes.append({
                        'account_code': account.code,
                        'account_name': account.name,
                        'amount': abs(balance)
                    })
                    total_income += abs(balance)
        
        expenses = []
        total_expense = Decimal('0.00')
        
        if expense_type:
            expense_accounts = Account.objects.filter(
                account_type=expense_type,
                is_detail=True,
                is_active=True
            )
            
            for account in expense_accounts:
                balance = AccountingService.get_account_balance(
                    str(account.id), period, start_date, end_date
                )
                if balance != 0:
                    expenses.append({
                        'account_code': account.code,
                        'account_name': account.name,
                        'amount': abs(balance)
                    })
                    total_expense += abs(balance)
        
        return {
            'incomes': incomes,
            'expenses': expenses,
            'total_income': total_income,
            'total_expense': total_expense,
            'net_profit': total_income - total_expense
        }
    
    @staticmethod
    def get_balance_sheet(as_of_date=None) -> Dict:
        """
        Genera el balance general.
        
        Propósito:
            Reporte de activos, pasivos y patrimonio.
        
        Returns:
            {
                'assets': [...],
                'liabilities': [...],
                'equity': [...],
                'total_assets': Decimal,
                'total_liabilities': Decimal,
                'total_equity': Decimal
            }
        """
        asset_type = AccountType.objects.filter(nature='asset').first()
        liability_type = AccountType.objects.filter(nature='liability').first()
        equity_type = AccountType.objects.filter(nature='equity').first()
        
        def get_section(account_type):
            if not account_type:
                return [], Decimal('0.00')
            
            accounts = Account.objects.filter(
                account_type=account_type,
                is_detail=True,
                is_active=True
            )
            
            section = []
            total = Decimal('0.00')
            
            for account in accounts:
                balance = AccountingService.get_account_balance(
                    str(account.id),
                    end_date=as_of_date
                )
                if balance != 0:
                    section.append({
                        'account_code': account.code,
                        'account_name': account.name,
                        'amount': abs(balance)
                    })
                    total += abs(balance)
            
            return section, total
        
        assets, total_assets = get_section(asset_type)
        liabilities, total_liabilities = get_section(liability_type)
        equity, total_equity = get_section(equity_type)
        
        # Agregar utilidad del ejercicio al patrimonio
        income_statement = AccountingService.get_income_statement(end_date=as_of_date)
        net_profit = income_statement['net_profit']
        
        if net_profit != 0:
            equity.append({
                'account_code': 'RESULT',
                'account_name': 'Resultado del Ejercicio',
                'amount': net_profit
            })
            total_equity += net_profit
        
        return {
            'assets': assets,
            'liabilities': liabilities,
            'equity': equity,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity
        }
    
    @staticmethod
    def get_account_ledger(
        account_id: str,
        period: AccountingPeriod = None,
        start_date=None,
        end_date=None
    ) -> List[Dict]:
        """
        Obtiene el libro mayor de una cuenta.
        
        Propósito:
            Detalle de todos los movimientos de una cuenta.
        
        Returns:
            Lista de movimientos con saldo acumulado
        """
        account = Account.objects.get(pk=account_id)
        
        entries = JournalEntryLine.objects.filter(
            account=account,
            journal_entry__status=JournalEntry.EntryStatus.POSTED
        ).select_related('journal_entry').order_by('journal_entry__entry_date', 'id')
        
        if period:
            entries = entries.filter(journal_entry__period=period)
        
        if start_date:
            entries = entries.filter(journal_entry__entry_date__gte=start_date)
        
        if end_date:
            entries = entries.filter(journal_entry__entry_date__lte=end_date)
        
        result = []
        running_balance = Decimal('0.00')
        
        for entry in entries:
            if account.account_type.debit_nature:
                running_balance += (entry.debit - entry.credit)
            else:
                running_balance += (entry.credit - entry.debit)
            
            result.append({
                'date': entry.journal_entry.entry_date,
                'entry_number': entry.journal_entry.entry_number,
                'description': entry.description or entry.journal_entry.description,
                'debit': entry.debit,
                'credit': entry.credit,
                'balance': running_balance
            })
        
        return result
    
    @staticmethod
    @transaction.atomic
    def close_period(period: AccountingPeriod, user=None) -> JournalEntry:
        """
        Cierra un período contable.
        
        Propósito:
            Crear asiento de cierre y marcar período como cerrado.
        
        Args:
            period: Período a cerrar
            user: Usuario que realiza el cierre
        
        Returns:
            JournalEntry: Asiento de cierre
        """
        if period.status == AccountingPeriod.PeriodStatus.CLOSED:
            raise ValidationException(
                message='El período ya está cerrado',
                source='AccountingService.close_period'
            )
        
        # Calcular resultado del ejercicio
        income_statement = AccountingService.get_income_statement(period=period)
        net_profit = income_statement['net_profit']
        
        # Crear asiento de cierre
        # TODO: Implementar asiento de cierre completo
        # - Cerrar cuentas de ingresos y gastos a resultados
        # - Transferir resultado a patrimonio
        
        period.status = AccountingPeriod.PeriodStatus.CLOSED
        period.save()
        
        return None  # TODO: Retornar asiento de cierre


class BudgetService:
    """
    Servicio para operaciones de presupuesto.
    """
    
    @staticmethod
    def check_budget_availability(
        account_id: str,
        amount: Decimal,
        cost_center_id: str = None
    ) -> Tuple[bool, Decimal]:
        """
        Verifica disponibilidad presupuestal.
        
        Args:
            account_id: ID de la cuenta
            amount: Monto a verificar
            cost_center_id: ID del centro de costo (opcional)
        
        Returns:
            Tuple[bool, Decimal]: (hay_disponibilidad, monto_disponible)
        """
        period = AccountingService.get_current_period()
        if not period:
            return True, Decimal('0.00')  # Sin período, sin control
        
        try:
            budget = Budget.objects.get(
                period=period,
                account_id=account_id,
                cost_center_id=cost_center_id
            )
            
            remaining = budget.remaining_amount
            return remaining >= amount, remaining
            
        except Budget.DoesNotExist:
            return True, Decimal('0.00')  # Sin presupuesto, permitir
    
    @staticmethod
    def get_budget_execution_report(
        period: AccountingPeriod = None,
        cost_center_id: str = None
    ) -> List[Dict]:
        """
        Genera reporte de ejecución presupuestal.
        
        Returns:
            Lista de presupuestos con su ejecución
        """
        if not period:
            period = AccountingService.get_current_period()
        
        if not period:
            return []
        
        budgets = Budget.objects.filter(period=period)
        
        if cost_center_id:
            budgets = budgets.filter(cost_center_id=cost_center_id)
        
        result = []
        for budget in budgets.select_related('account', 'cost_center'):
            result.append({
                'account_code': budget.account.code,
                'account_name': budget.account.name,
                'cost_center': budget.cost_center.name if budget.cost_center else None,
                'budgeted': budget.amount,
                'executed': budget.executed_amount,
                'remaining': budget.remaining_amount,
                'execution_percentage': budget.execution_percentage,
                'status': 'OK' if budget.execution_percentage <= 100 else 'OVER'
            })
        
        return result
