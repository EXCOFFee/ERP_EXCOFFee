// ========================================================
// SISTEMA ERP MOBILE - Finance Redux Slice
// ========================================================

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import financeService, { 
  Account, 
  JournalEntry, 
  AccountingPeriod, 
  CostCenter,
  Budget,
  BankAccount,
  FinanceFilters 
} from '../../services/finance.service';

interface FinanceState {
  // Accounts
  accounts: Account[];
  accountsLoading: boolean;
  accountsError: string | null;
  selectedAccount: Account | null;
  
  // Journal Entries
  journalEntries: JournalEntry[];
  journalEntriesLoading: boolean;
  journalEntriesError: string | null;
  selectedJournalEntry: JournalEntry | null;
  
  // Periods
  periods: AccountingPeriod[];
  currentPeriod: AccountingPeriod | null;
  periodsLoading: boolean;
  
  // Cost Centers
  costCenters: CostCenter[];
  costCentersLoading: boolean;
  
  // Budgets
  budgets: Budget[];
  budgetsLoading: boolean;
  
  // Bank Accounts
  bankAccounts: BankAccount[];
  bankAccountsLoading: boolean;
  
  // Pagination
  total: number;
  page: number;
  totalPages: number;
}

const initialState: FinanceState = {
  accounts: [],
  accountsLoading: false,
  accountsError: null,
  selectedAccount: null,
  
  journalEntries: [],
  journalEntriesLoading: false,
  journalEntriesError: null,
  selectedJournalEntry: null,
  
  periods: [],
  currentPeriod: null,
  periodsLoading: false,
  
  costCenters: [],
  costCentersLoading: false,
  
  budgets: [],
  budgetsLoading: false,
  
  bankAccounts: [],
  bankAccountsLoading: false,
  
  total: 0,
  page: 1,
  totalPages: 1,
};

// ========== ASYNC THUNKS ==========

// Accounts
export const fetchAccounts = createAsyncThunk(
  'finance/fetchAccounts',
  async (filters: FinanceFilters = {}) => {
    const response = await financeService.getAccounts(filters);
    return response;
  }
);

export const fetchAccount = createAsyncThunk(
  'finance/fetchAccount',
  async (id: string) => {
    return await financeService.getAccount(id);
  }
);

export const createAccount = createAsyncThunk(
  'finance/createAccount',
  async (account: Partial<Account>) => {
    return await financeService.createAccount(account);
  }
);

export const updateAccount = createAsyncThunk(
  'finance/updateAccount',
  async ({ id, account }: { id: string; account: Partial<Account> }) => {
    return await financeService.updateAccount(id, account);
  }
);

// Journal Entries
export const fetchJournalEntries = createAsyncThunk(
  'finance/fetchJournalEntries',
  async (filters: FinanceFilters = {}) => {
    const response = await financeService.getJournalEntries(filters);
    return response;
  }
);

export const fetchJournalEntry = createAsyncThunk(
  'finance/fetchJournalEntry',
  async (id: string) => {
    return await financeService.getJournalEntry(id);
  }
);

export const createJournalEntry = createAsyncThunk(
  'finance/createJournalEntry',
  async (entry: Partial<JournalEntry>) => {
    return await financeService.createJournalEntry(entry);
  }
);

export const updateJournalEntry = createAsyncThunk(
  'finance/updateJournalEntry',
  async ({ id, entry }: { id: string; entry: Partial<JournalEntry> }) => {
    return await financeService.updateJournalEntry(id, entry);
  }
);

export const postJournalEntry = createAsyncThunk(
  'finance/postJournalEntry',
  async (id: string) => {
    return await financeService.postJournalEntry(id);
  }
);

// Periods
export const fetchPeriods = createAsyncThunk(
  'finance/fetchPeriods',
  async (filters: FinanceFilters = {}) => {
    const response = await financeService.getPeriods(filters);
    return response;
  }
);

export const fetchCurrentPeriod = createAsyncThunk(
  'finance/fetchCurrentPeriod',
  async () => {
    return await financeService.getCurrentPeriod();
  }
);

// Cost Centers
export const fetchCostCenters = createAsyncThunk(
  'finance/fetchCostCenters',
  async (filters: FinanceFilters = {}) => {
    const response = await financeService.getCostCenters(filters);
    return response;
  }
);

export const createCostCenter = createAsyncThunk(
  'finance/createCostCenter',
  async (costCenter: Partial<CostCenter>) => {
    return await financeService.createCostCenter(costCenter);
  }
);

// Budgets
export const fetchBudgets = createAsyncThunk(
  'finance/fetchBudgets',
  async (filters: FinanceFilters = {}) => {
    const response = await financeService.getBudgets(filters);
    return response;
  }
);

// Bank Accounts
export const fetchBankAccounts = createAsyncThunk(
  'finance/fetchBankAccounts',
  async () => {
    return await financeService.getBankAccounts();
  }
);

// ========== SLICE ==========

const financeSlice = createSlice({
  name: 'finance',
  initialState,
  reducers: {
    setSelectedAccount: (state, action: PayloadAction<Account | null>) => {
      state.selectedAccount = action.payload;
    },
    setSelectedJournalEntry: (state, action: PayloadAction<JournalEntry | null>) => {
      state.selectedJournalEntry = action.payload;
    },
    clearFinanceErrors: (state) => {
      state.accountsError = null;
      state.journalEntriesError = null;
    },
  },
  extraReducers: (builder) => {
    // Accounts
    builder
      .addCase(fetchAccounts.pending, (state) => {
        state.accountsLoading = true;
        state.accountsError = null;
      })
      .addCase(fetchAccounts.fulfilled, (state, action) => {
        state.accountsLoading = false;
        state.accounts = action.payload.data;
        state.total = action.payload.total;
        state.page = action.payload.page;
        state.totalPages = action.payload.totalPages;
      })
      .addCase(fetchAccounts.rejected, (state, action) => {
        state.accountsLoading = false;
        state.accountsError = action.error.message || 'Error loading accounts';
      })
      .addCase(fetchAccount.fulfilled, (state, action) => {
        state.selectedAccount = action.payload;
      })
      .addCase(createAccount.fulfilled, (state, action) => {
        state.accounts.push(action.payload);
      })
      .addCase(updateAccount.fulfilled, (state, action) => {
        const index = state.accounts.findIndex(a => a.id === action.payload.id);
        if (index !== -1) {
          state.accounts[index] = action.payload;
        }
        if (state.selectedAccount?.id === action.payload.id) {
          state.selectedAccount = action.payload;
        }
      });

    // Journal Entries
    builder
      .addCase(fetchJournalEntries.pending, (state) => {
        state.journalEntriesLoading = true;
        state.journalEntriesError = null;
      })
      .addCase(fetchJournalEntries.fulfilled, (state, action) => {
        state.journalEntriesLoading = false;
        state.journalEntries = action.payload.data;
        state.total = action.payload.total;
        state.page = action.payload.page;
        state.totalPages = action.payload.totalPages;
      })
      .addCase(fetchJournalEntries.rejected, (state, action) => {
        state.journalEntriesLoading = false;
        state.journalEntriesError = action.error.message || 'Error loading journal entries';
      })
      .addCase(fetchJournalEntry.fulfilled, (state, action) => {
        state.selectedJournalEntry = action.payload;
      })
      .addCase(createJournalEntry.fulfilled, (state, action) => {
        state.journalEntries.unshift(action.payload);
      })
      .addCase(updateJournalEntry.fulfilled, (state, action) => {
        const index = state.journalEntries.findIndex(j => j.id === action.payload.id);
        if (index !== -1) {
          state.journalEntries[index] = action.payload;
        }
      })
      .addCase(postJournalEntry.fulfilled, (state, action) => {
        const index = state.journalEntries.findIndex(j => j.id === action.payload.id);
        if (index !== -1) {
          state.journalEntries[index] = action.payload;
        }
      });

    // Periods
    builder
      .addCase(fetchPeriods.pending, (state) => {
        state.periodsLoading = true;
      })
      .addCase(fetchPeriods.fulfilled, (state, action) => {
        state.periodsLoading = false;
        state.periods = action.payload.data;
      })
      .addCase(fetchCurrentPeriod.fulfilled, (state, action) => {
        state.currentPeriod = action.payload;
      });

    // Cost Centers
    builder
      .addCase(fetchCostCenters.pending, (state) => {
        state.costCentersLoading = true;
      })
      .addCase(fetchCostCenters.fulfilled, (state, action) => {
        state.costCentersLoading = false;
        state.costCenters = action.payload.data;
      })
      .addCase(createCostCenter.fulfilled, (state, action) => {
        state.costCenters.push(action.payload);
      });

    // Budgets
    builder
      .addCase(fetchBudgets.pending, (state) => {
        state.budgetsLoading = true;
      })
      .addCase(fetchBudgets.fulfilled, (state, action) => {
        state.budgetsLoading = false;
        state.budgets = action.payload.data;
      });

    // Bank Accounts
    builder
      .addCase(fetchBankAccounts.pending, (state) => {
        state.bankAccountsLoading = true;
      })
      .addCase(fetchBankAccounts.fulfilled, (state, action) => {
        state.bankAccountsLoading = false;
        state.bankAccounts = action.payload;
      });
  },
});

export const { setSelectedAccount, setSelectedJournalEntry, clearFinanceErrors } = financeSlice.actions;
export default financeSlice.reducer;

// Selectors
export const selectAccounts = (state: { finance: FinanceState }) => state.finance.accounts;
export const selectAccountsLoading = (state: { finance: FinanceState }) => state.finance.accountsLoading;
export const selectSelectedAccount = (state: { finance: FinanceState }) => state.finance.selectedAccount;
export const selectJournalEntries = (state: { finance: FinanceState }) => state.finance.journalEntries;
export const selectJournalEntriesLoading = (state: { finance: FinanceState }) => state.finance.journalEntriesLoading;
export const selectPeriods = (state: { finance: FinanceState }) => state.finance.periods;
export const selectCurrentPeriod = (state: { finance: FinanceState }) => state.finance.currentPeriod;
export const selectCostCenters = (state: { finance: FinanceState }) => state.finance.costCenters;
export const selectBudgets = (state: { finance: FinanceState }) => state.finance.budgets;
export const selectBankAccounts = (state: { finance: FinanceState }) => state.finance.bankAccounts;
