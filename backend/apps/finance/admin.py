# ========================================================
# SISTEMA ERP UNIVERSAL - Admin de Finanzas
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
    TaxRate,
)


@admin.register(AccountingPeriod)
class AccountingPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'start_date', 'end_date', 'status', 'is_current']
    list_filter = ['status', 'is_current']
    search_fields = ['name', 'code']
    ordering = ['-start_date']


@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'nature', 'debit_nature']
    list_filter = ['nature', 'debit_nature']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'account_type', 'is_active']
    list_filter = ['account_type', 'is_active']
    search_fields = ['code', 'name']
    ordering = ['code']


class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 1
    fields = ['account', 'description', 'debit', 'credit']


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['entry_number', 'entry_date', 'description', 'status', 'created_at']
    list_filter = ['status', 'entry_type', 'period']
    search_fields = ['entry_number', 'description']
    ordering = ['-entry_date']
    inlines = [JournalEntryLineInline]


@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['period', 'account', 'cost_center', 'amount', 'created_at']
    list_filter = ['period', 'account']
    search_fields = ['account__name', 'account__code']
    ordering = ['-created_at']


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ['name', 'rate', 'tax_type', 'is_active']
    list_filter = ['tax_type', 'is_active']
    search_fields = ['name']
    ordering = ['name']
