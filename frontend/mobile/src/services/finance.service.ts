// ========================================================
// SISTEMA ERP MOBILE - Servicio de Finanzas
// ========================================================

import api from './api';

// Tipos
export interface AccountingPeriod {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
  status: 'open' | 'closed' | 'locked';
  isCurrent: boolean;
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
  accountType: AccountType;
  parent?: string;
  level: number;
  isActive: boolean;
  allowsTransactions: boolean;
  balance: number;
  children?: Account[];
}

export interface JournalEntry {
  id: string;
  entryNumber: string;
  entryDate: string;
  period: AccountingPeriod;
  description: string;
  reference?: string;
  status: 'draft' | 'posted' | 'reversed';
  totalDebit: number;
  totalCredit: number;
  lines: JournalEntryLine[];
  createdBy: string;
  createdAt: string;
}

export interface JournalEntryLine {
  id: string;
  account: Account;
  description?: string;
  debitAmount: number;
  creditAmount: number;
  costCenter?: string;
}

export interface CostCenter {
  id: string;
  code: string;
  name: string;
  description?: string;
  parent?: string;
  isActive: boolean;
}

export interface Budget {
  id: string;
  account: Account;
  period: AccountingPeriod;
  budgetedAmount: number;
  actualAmount: number;
  variance: number;
  variancePercentage: number;
}

export interface TaxRate {
  id: string;
  code: string;
  name: string;
  rate: number;
  taxType: 'sales' | 'purchase' | 'both';
  isActive: boolean;
}

export interface BankAccount {
  id: string;
  accountNumber: string;
  bankName: string;
  accountName: string;
  accountType: 'checking' | 'savings';
  currency: string;
  currentBalance: number;
  isActive: boolean;
}

export interface FinanceFilters {
  search?: string;
  status?: string;
  startDate?: string;
  endDate?: string;
  page?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

class FinanceService {
  // Períodos Contables
  async getPeriods(filters: FinanceFilters = {}): Promise<PaginatedResponse<AccountingPeriod>> {
    const { data } = await api.get('/finance/periods/', { params: filters });
    return data;
  }

  async getPeriod(id: string): Promise<AccountingPeriod> {
    const { data } = await api.get(`/finance/periods/${id}/`);
    return data;
  }

  async getCurrentPeriod(): Promise<AccountingPeriod> {
    const { data } = await api.get('/finance/periods/current/');
    return data;
  }

  // Cuentas Contables
  async getAccounts(filters: FinanceFilters = {}): Promise<PaginatedResponse<Account>> {
    const { data } = await api.get('/finance/accounts/', { params: filters });
    return data;
  }

  async getAccount(id: string): Promise<Account> {
    const { data } = await api.get(`/finance/accounts/${id}/`);
    return data;
  }

  async getAccountTree(): Promise<Account[]> {
    const { data } = await api.get('/finance/accounts/tree/');
    return data;
  }

  async createAccount(account: Partial<Account>): Promise<Account> {
    const { data } = await api.post('/finance/accounts/', account);
    return data;
  }

  async updateAccount(id: string, account: Partial<Account>): Promise<Account> {
    const { data } = await api.put(`/finance/accounts/${id}/`, account);
    return data;
  }

  // Asientos Contables
  async getJournalEntries(filters: FinanceFilters = {}): Promise<PaginatedResponse<JournalEntry>> {
    const { data } = await api.get('/finance/journal-entries/', { params: filters });
    return data;
  }

  async getJournalEntry(id: string): Promise<JournalEntry> {
    const { data } = await api.get(`/finance/journal-entries/${id}/`);
    return data;
  }

  async createJournalEntry(entry: Partial<JournalEntry>): Promise<JournalEntry> {
    const { data } = await api.post('/finance/journal-entries/', entry);
    return data;
  }

  async updateJournalEntry(id: string, entry: Partial<JournalEntry>): Promise<JournalEntry> {
    const { data } = await api.put(`/finance/journal-entries/${id}/`, entry);
    return data;
  }

  async postJournalEntry(id: string): Promise<JournalEntry> {
    const { data } = await api.post(`/finance/journal-entries/${id}/post/`);
    return data;
  }

  async reverseJournalEntry(id: string): Promise<JournalEntry> {
    const { data } = await api.post(`/finance/journal-entries/${id}/reverse/`);
    return data;
  }

  // Centros de Costo
  async getCostCenters(filters: FinanceFilters = {}): Promise<PaginatedResponse<CostCenter>> {
    const { data } = await api.get('/finance/cost-centers/', { params: filters });
    return data;
  }

  async getCostCenter(id: string): Promise<CostCenter> {
    const { data } = await api.get(`/finance/cost-centers/${id}/`);
    return data;
  }

  async createCostCenter(costCenter: Partial<CostCenter>): Promise<CostCenter> {
    const { data } = await api.post('/finance/cost-centers/', costCenter);
    return data;
  }

  async updateCostCenter(id: string, costCenter: Partial<CostCenter>): Promise<CostCenter> {
    const { data } = await api.put(`/finance/cost-centers/${id}/`, costCenter);
    return data;
  }

  // Presupuestos
  async getBudgets(filters: FinanceFilters = {}): Promise<PaginatedResponse<Budget>> {
    const { data } = await api.get('/finance/budgets/', { params: filters });
    return data;
  }

  async getBudget(id: string): Promise<Budget> {
    const { data } = await api.get(`/finance/budgets/${id}/`);
    return data;
  }

  async createBudget(budget: Partial<Budget>): Promise<Budget> {
    const { data } = await api.post('/finance/budgets/', budget);
    return data;
  }

  async updateBudget(id: string, budget: Partial<Budget>): Promise<Budget> {
    const { data } = await api.put(`/finance/budgets/${id}/`, budget);
    return data;
  }

  // Tasas de Impuestos
  async getTaxRates(): Promise<TaxRate[]> {
    const { data } = await api.get('/finance/tax-rates/');
    return data;
  }

  // Cuentas Bancarias
  async getBankAccounts(): Promise<BankAccount[]> {
    const { data } = await api.get('/finance/bank-accounts/');
    return data;
  }

  async getBankAccount(id: string): Promise<BankAccount> {
    const { data } = await api.get(`/finance/bank-accounts/${id}/`);
    return data;
  }

  // Reportes
  async getBalanceSheet(periodId?: string): Promise<any> {
    const params = periodId ? { period_id: periodId } : {};
    const { data } = await api.get('/finance/reports/balance-sheet/', { params });
    return data;
  }

  async getIncomeStatement(periodId?: string): Promise<any> {
    const params = periodId ? { period_id: periodId } : {};
    const { data } = await api.get('/finance/reports/income-statement/', { params });
    return data;
  }

  async getTrialBalance(periodId?: string): Promise<any> {
    const params = periodId ? { period_id: periodId } : {};
    const { data } = await api.get('/finance/reports/trial-balance/', { params });
    return data;
  }

  async getLedger(accountId: string, startDate?: string, endDate?: string): Promise<any> {
    const params: any = { account_id: accountId };
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const { data } = await api.get('/finance/reports/ledger/', { params });
    return data;
  }
}

export const financeService = new FinanceService();
export default financeService;
