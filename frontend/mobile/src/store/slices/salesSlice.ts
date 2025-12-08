import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { salesService, Customer, Order, CustomerFilters, OrderFilters, PaginatedResponse } from '../../services/sales.service';

interface SalesState {
  customers: Customer[];
  orders: Order[];
  selectedCustomer: Customer | null;
  selectedOrder: Order | null;
  loading: boolean;
  error: string | null;
  customerPagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
  orderPagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

const initialState: SalesState = {
  customers: [],
  orders: [],
  selectedCustomer: null,
  selectedOrder: null,
  loading: false,
  error: null,
  customerPagination: { page: 1, limit: 20, total: 0, totalPages: 0 },
  orderPagination: { page: 1, limit: 20, total: 0, totalPages: 0 },
};

// Customer thunks
export const fetchCustomers = createAsyncThunk(
  'sales/fetchCustomers',
  async (filters: CustomerFilters = {}, { rejectWithValue }) => {
    try {
      return await salesService.getCustomers(filters);
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } }; message?: string };
      return rejectWithValue(err.response?.data?.message || 'Error fetching customers');
    }
  }
);

export const fetchCustomer = createAsyncThunk(
  'sales/fetchCustomer',
  async (id: string, { rejectWithValue }) => {
    try {
      return await salesService.getCustomer(id);
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } }; message?: string };
      return rejectWithValue(err.response?.data?.message || 'Error fetching customer');
    }
  }
);

export const createCustomer = createAsyncThunk(
  'sales/createCustomer',
  async (customer: Partial<Customer>, { rejectWithValue }) => {
    try {
      return await salesService.createCustomer(customer);
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } }; message?: string };
      return rejectWithValue(err.response?.data?.message || 'Error creating customer');
    }
  }
);

export const updateCustomer = createAsyncThunk(
  'sales/updateCustomer',
  async ({ id, data }: { id: string; data: Partial<Customer> }, { rejectWithValue }) => {
    try {
      return await salesService.updateCustomer(id, data);
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } }; message?: string };
      return rejectWithValue(err.response?.data?.message || 'Error updating customer');
    }
  }
);

// Order thunks
export const fetchOrders = createAsyncThunk(
  'sales/fetchOrders',
  async (filters: OrderFilters = {}, { rejectWithValue }) => {
    try {
      return await salesService.getOrders(filters);
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } }; message?: string };
      return rejectWithValue(err.response?.data?.message || 'Error fetching orders');
    }
  }
);

export const fetchOrder = createAsyncThunk(
  'sales/fetchOrder',
  async (id: string, { rejectWithValue }) => {
    try {
      return await salesService.getOrder(id);
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } }; message?: string };
      return rejectWithValue(err.response?.data?.message || 'Error fetching order');
    }
  }
);

export const createOrder = createAsyncThunk(
  'sales/createOrder',
  async (order: Partial<Order>, { rejectWithValue }) => {
    try {
      return await salesService.createOrder(order);
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } }; message?: string };
      return rejectWithValue(err.response?.data?.message || 'Error creating order');
    }
  }
);

export const updateOrderStatus = createAsyncThunk(
  'sales/updateOrderStatus',
  async ({ id, status }: { id: string; status: string }, { rejectWithValue }) => {
    try {
      return await salesService.updateOrderStatus(id, status);
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } }; message?: string };
      return rejectWithValue(err.response?.data?.message || 'Error updating order status');
    }
  }
);

const salesSlice = createSlice({
  name: 'sales',
  initialState,
  reducers: {
    clearSelectedCustomer: (state) => {
      state.selectedCustomer = null;
    },
    clearSelectedOrder: (state) => {
      state.selectedOrder = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Customers
      .addCase(fetchCustomers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCustomers.fulfilled, (state, action: PayloadAction<PaginatedResponse<Customer>>) => {
        state.loading = false;
        state.customers = action.payload.data;
        state.customerPagination = {
          page: action.payload.page,
          limit: action.payload.limit,
          total: action.payload.total,
          totalPages: action.payload.totalPages,
        };
      })
      .addCase(fetchCustomers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchCustomer.fulfilled, (state, action: PayloadAction<Customer>) => {
        state.selectedCustomer = action.payload;
      })
      .addCase(createCustomer.fulfilled, (state, action: PayloadAction<Customer>) => {
        state.customers.unshift(action.payload);
      })
      .addCase(updateCustomer.fulfilled, (state, action: PayloadAction<Customer>) => {
        const index = state.customers.findIndex((c) => c.id === action.payload.id);
        if (index !== -1) {
          state.customers[index] = action.payload;
        }
        state.selectedCustomer = action.payload;
      })
      // Orders
      .addCase(fetchOrders.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOrders.fulfilled, (state, action: PayloadAction<PaginatedResponse<Order>>) => {
        state.loading = false;
        state.orders = action.payload.data;
        state.orderPagination = {
          page: action.payload.page,
          limit: action.payload.limit,
          total: action.payload.total,
          totalPages: action.payload.totalPages,
        };
      })
      .addCase(fetchOrders.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchOrder.fulfilled, (state, action: PayloadAction<Order>) => {
        state.selectedOrder = action.payload;
      })
      .addCase(createOrder.fulfilled, (state, action: PayloadAction<Order>) => {
        state.orders.unshift(action.payload);
      })
      .addCase(updateOrderStatus.fulfilled, (state, action: PayloadAction<Order>) => {
        const index = state.orders.findIndex((o) => o.id === action.payload.id);
        if (index !== -1) {
          state.orders[index] = action.payload;
        }
        state.selectedOrder = action.payload;
      });
  },
});

export const { clearSelectedCustomer, clearSelectedOrder, clearError } = salesSlice.actions;
export default salesSlice.reducer;
