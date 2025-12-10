// ========================================================
// SISTEMA ERP UNIVERSAL - Servicio de Finanzas
// ========================================================

import { api, apiGet, apiPost, apiPut } from './api';
import type { PaginatedResponse, ListParams } from './inventory.service';

// Tipos
export interface AccountingPeriod {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  status: 'open' | 'closed' | 'locked';
  is_current: boolean;
}

export interface AccountType {
  id: string;
  name: string;
  nature: 'debit' | 'credit';
  classification: 'asset' | 'liability' | 'equity' | 'income' | 'expense';
}

export interface Account {
  id: string;
  code: string;
  name: string;
  account_type: AccountType;
  parent?: string;
  level: number;
  is_active: boolean;
  allows_transactions: boolean;
  balance: number;
  children?: Account[];
}

export interface JournalEntry {
  id: string;
  entry_number: string;
  entry_date: string;
  period: AccountingPeriod;
  description: string;
  reference?: string;
  status: 'draft' | 'posted' | 'reversed';
  total_debit: number;
  total_credit: number;
  lines: JournalEntryLine[];
  created_by: string;
  created_at: string;
}

export interface JournalEntryLine {
  id: string;
  account: Account;
  description?: string;
  debit_amount: number;
  credit_amount: number;
  cost_center?: string;
}

export interface CostCenter {
  id: string;
  code: string;
  name: string;
  description?: string;
  parent?: string;
  is_active: boolean;
}

export interface Budget {
  id: string;
  account: Account;
  period: AccountingPeriod;
  budgeted_amount: number;
  actual_amount: number;
  variance: number;
  variance_percentage: number;
}

export interface TaxRate {
  id: string;
  code: string;
  name: string;
  rate: number;
  tax_type: 'sales' | 'purchase' | 'both';
  is_active: boolean;
}

export interface PaymentMethod {
  id: string;
  code: string;
  name: string;
  payment_type: 'cash' | 'bank' | 'card' | 'check' | 'transfer' | 'other';
  is_active: boolean;
}

export interface BankAccount {
  id: string;
  account_number: string;
  bank_name: string;
  account_name: string;
  account_type: 'checking' | 'savings';
  currency: string;
  current_balance: number;
  is_active: boolean;
}

// ========== PERÍODOS CONTABLES ==========
export const accountingPeriodService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<AccountingPeriod>>('/finance/periods/', params),
  
  get: (id: string) => 
    apiGet<AccountingPeriod>(`/finance/periods/${id}/`),
  
  create: (data: Partial<AccountingPeriod>) => 
    apiPost<AccountingPeriod>('/finance/periods/', data),
  
  update: (id: string, data: Partial<AccountingPeriod>) => 
    apiPut<AccountingPeriod>(`/finance/periods/${id}/`, data),
  
  close: (id: string) => 
    apiPost(`/finance/periods/${id}/close/`),
  
  reopen: (id: string) => 
    apiPost(`/finance/periods/${id}/reopen/`),
  
  setCurrent: (id: string) => 
    apiPost(`/finance/periods/${id}/set-current/`),
};

// ========== TIPOS DE CUENTA ==========
export const accountTypeService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<AccountType>>('/finance/account-types/', params),
  
  get: (id: string) => 
    apiGet<AccountType>(`/finance/account-types/${id}/`),
};

// ========== CUENTAS CONTABLES ==========
export const accountService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<Account>>('/finance/accounts/', params),
  
  getTree: () => 
    apiGet<Account[]>('/finance/accounts/tree/'),
  
  get: (id: string) => 
    apiGet<Account>(`/finance/accounts/${id}/`),
  
  create: (data: Partial<Account>) => 
    apiPost<Account>('/finance/accounts/', data),
  
  update: (id: string, data: Partial<Account>) => 
    apiPut<Account>(`/finance/accounts/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/finance/accounts/${id}/`),
  
  getBalance: (id: string, params?: { start_date?: string; end_date?: string }) => 
    apiGet(`/finance/accounts/${id}/balance/`, params),
  
  getLedger: (id: string, params?: { start_date?: string; end_date?: string }) => 
    apiGet(`/finance/accounts/${id}/ledger/`, params),
};

// ========== ASIENTOS CONTABLES ==========
export const journalEntryService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<JournalEntry>>('/finance/entries/', params),
  
  get: (id: string) => 
    apiGet<JournalEntry>(`/finance/entries/${id}/`),
  
  create: (data: any) => 
    apiPost<JournalEntry>('/finance/entries/', data),
  
  update: (id: string, data: any) => 
    apiPut<JournalEntry>(`/finance/entries/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/finance/entries/${id}/`),
  
  post: (id: string) => 
    apiPost(`/finance/entries/${id}/post/`),
  
  reverse: (id: string) => 
    apiPost<JournalEntry>(`/finance/entries/${id}/reverse/`),
};

// ========== CENTROS DE COSTO ==========
export const costCenterService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<CostCenter>>('/finance/cost-centers/', params),
  
  get: (id: string) => 
    apiGet<CostCenter>(`/finance/cost-centers/${id}/`),
  
  create: (data: Partial<CostCenter>) => 
    apiPost<CostCenter>('/finance/cost-centers/', data),
  
  update: (id: string, data: Partial<CostCenter>) => 
    apiPut<CostCenter>(`/finance/cost-centers/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/finance/cost-centers/${id}/`),
};

// ========== PRESUPUESTOS ==========
export const budgetService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<Budget>>('/finance/budgets/', params),
  
  get: (id: string) => 
    apiGet<Budget>(`/finance/budgets/${id}/`),
  
  create: (data: Partial<Budget>) => 
    apiPost<Budget>('/finance/budgets/', data),
  
  update: (id: string, data: Partial<Budget>) => 
    apiPut<Budget>(`/finance/budgets/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/finance/budgets/${id}/`),
  
  getExecutionReport: (params?: { period?: string }) => 
    apiGet('/finance/budgets/execution-report/', params),
};

// ========== TASAS DE IMPUESTO ==========
export const taxRateService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<TaxRate>>('/finance/tax-rates/', params),
  
  get: (id: string) => 
    apiGet<TaxRate>(`/finance/tax-rates/${id}/`),
  
  create: (data: Partial<TaxRate>) => 
    apiPost<TaxRate>('/finance/tax-rates/', data),
  
  update: (id: string, data: Partial<TaxRate>) => 
    apiPut<TaxRate>(`/finance/tax-rates/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/finance/tax-rates/${id}/`),
};

// ========== MÉTODOS DE PAGO ==========
export const paymentMethodService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<PaymentMethod>>('/finance/payment-methods/', params),
  
  get: (id: string) => 
    apiGet<PaymentMethod>(`/finance/payment-methods/${id}/`),
  
  create: (data: Partial<PaymentMethod>) => 
    apiPost<PaymentMethod>('/finance/payment-methods/', data),
  
  update: (id: string, data: Partial<PaymentMethod>) => 
    apiPut<PaymentMethod>(`/finance/payment-methods/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/finance/payment-methods/${id}/`),
};

// ========== CUENTAS BANCARIAS ==========
export const bankAccountService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<BankAccount>>('/finance/bank-accounts/', params),
  
  get: (id: string) => 
    apiGet<BankAccount>(`/finance/bank-accounts/${id}/`),
  
  create: (data: Partial<BankAccount>) => 
    apiPost<BankAccount>('/finance/bank-accounts/', data),
  
  update: (id: string, data: Partial<BankAccount>) => 
    apiPut<BankAccount>(`/finance/bank-accounts/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/finance/bank-accounts/${id}/`),
};

// ========== REPORTES FINANCIEROS ==========
export const financeReportService = {
  getTrialBalance: (params?: { period?: string; date?: string }) => 
    apiGet('/finance/reports/trial-balance/', params),
  
  getIncomeStatement: (params?: { period?: string; start_date?: string; end_date?: string }) => 
    apiGet('/finance/reports/income-statement/', params),
  
  getBalanceSheet: (params?: { date?: string }) => 
    apiGet('/finance/reports/balance-sheet/', params),
  
  getCashFlow: (params?: { start_date?: string; end_date?: string }) => 
    apiGet('/finance/reports/cash-flow/', params),
};

// ========== SERVICIO UNIFICADO DE FINANZAS ==========
export const financeService = {
  // Cuentas contables
  getAccounts: accountService.list,
  getAccount: accountService.get,
  createAccount: accountService.create,
  updateAccount: accountService.update,
  deleteAccount: accountService.delete,
  getAccountTree: accountService.getTree,
  getAccountBalance: accountService.getBalance,
  getAccountLedger: accountService.getLedger,
  
  // Tipos de cuenta
  getAccountTypes: () => accountTypeService.list(),
  
  // Asientos contables
  getJournalEntries: journalEntryService.list,
  getJournalEntry: journalEntryService.get,
  createJournalEntry: journalEntryService.create,
  updateJournalEntry: journalEntryService.update,
  deleteJournalEntry: journalEntryService.delete,
  postJournalEntry: journalEntryService.post,
  reverseJournalEntry: journalEntryService.reverse,
  
  // Períodos contables
  getFiscalPeriods: () => accountingPeriodService.list(),
  getPeriods: accountingPeriodService.list,
  getPeriod: accountingPeriodService.get,
  createPeriod: accountingPeriodService.create,
  closePeriod: accountingPeriodService.close,
  
  // Centros de costo
  getCostCenters: costCenterService.list,
  getCostCenter: costCenterService.get,
  createCostCenter: costCenterService.create,
  
  // Presupuestos
  getBudgets: budgetService.list,
  getBudget: budgetService.get,
  createBudget: budgetService.create,
  
  // Cuentas bancarias
  getBankAccounts: bankAccountService.list,
  getBankAccount: bankAccountService.get,
  createBankAccount: bankAccountService.create,
  
  // Reportes
  getTrialBalance: financeReportService.getTrialBalance,
  getIncomeStatement: financeReportService.getIncomeStatement,
  getBalanceSheet: financeReportService.getBalanceSheet,
  getCashFlowStatement: financeReportService.getCashFlow,
  getGeneralLedger: (params?: any) => apiGet('/finance/reports/general-ledger/', params),
};
