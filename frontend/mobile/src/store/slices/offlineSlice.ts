import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import api from '../../services/api';

export interface PendingAction {
  id: string;
  type: 'CREATE' | 'UPDATE' | 'DELETE';
  entity: string;
  endpoint: string;
  data: Record<string, unknown>;
  timestamp: number;
  retryCount: number;
}

interface OfflineState {
  isOnline: boolean;
  pendingActions: PendingAction[];
  syncInProgress: boolean;
  lastSyncTime: number | null;
  error: string | null;
}

const initialState: OfflineState = {
  isOnline: true,
  pendingActions: [],
  syncInProgress: false,
  lastSyncTime: null,
  error: null,
};

const PENDING_ACTIONS_KEY = '@erp_pending_actions';

// Load pending actions from storage
export const loadPendingActions = createAsyncThunk(
  'offline/loadPendingActions',
  async () => {
    const stored = await AsyncStorage.getItem(PENDING_ACTIONS_KEY);
    return stored ? JSON.parse(stored) : [];
  }
);

// Save pending action
export const savePendingAction = createAsyncThunk(
  'offline/savePendingAction',
  async (action: Omit<PendingAction, 'id' | 'timestamp' | 'retryCount'>, { getState }) => {
    const state = getState() as { offline: OfflineState };
    const newAction: PendingAction = {
      ...action,
      id: `${Date.now()}-${Math.random().toString(36).substring(7)}`,
      timestamp: Date.now(),
      retryCount: 0,
    };
    
    const updatedActions = [...state.offline.pendingActions, newAction];
    await AsyncStorage.setItem(PENDING_ACTIONS_KEY, JSON.stringify(updatedActions));
    
    return newAction;
  }
);

// Sync pending actions
export const syncPendingActions = createAsyncThunk(
  'offline/syncPendingActions',
  async (_, { getState, dispatch }) => {
    const state = getState() as { offline: OfflineState };
    const { pendingActions } = state.offline;
    
    const netInfo = await NetInfo.fetch();
    if (!netInfo.isConnected) {
      throw new Error('No internet connection');
    }
    
    const results: { success: string[]; failed: string[] } = {
      success: [],
      failed: [],
    };
    
    for (const action of pendingActions) {
      try {
        switch (action.type) {
          case 'CREATE':
            await api.post(action.endpoint, action.data);
            break;
          case 'UPDATE':
            await api.patch(action.endpoint, action.data);
            break;
          case 'DELETE':
            await api.delete(action.endpoint);
            break;
        }
        results.success.push(action.id);
      } catch (error) {
        results.failed.push(action.id);
        // Update retry count
        dispatch(incrementRetryCount(action.id));
      }
    }
    
    // Remove successful actions
    const remainingActions = pendingActions.filter(
      (a) => !results.success.includes(a.id)
    );
    await AsyncStorage.setItem(PENDING_ACTIONS_KEY, JSON.stringify(remainingActions));
    
    return results;
  }
);

// Check network status
export const checkNetworkStatus = createAsyncThunk(
  'offline/checkNetworkStatus',
  async () => {
    const netInfo = await NetInfo.fetch();
    return netInfo.isConnected ?? false;
  }
);

const offlineSlice = createSlice({
  name: 'offline',
  initialState,
  reducers: {
    setOnlineStatus: (state, action: PayloadAction<boolean>) => {
      state.isOnline = action.payload;
    },
    incrementRetryCount: (state, action: PayloadAction<string>) => {
      const actionToUpdate = state.pendingActions.find((a) => a.id === action.payload);
      if (actionToUpdate) {
        actionToUpdate.retryCount += 1;
      }
    },
    removePendingAction: (state, action: PayloadAction<string>) => {
      state.pendingActions = state.pendingActions.filter((a) => a.id !== action.payload);
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Load pending actions
      .addCase(loadPendingActions.fulfilled, (state, action: PayloadAction<PendingAction[]>) => {
        state.pendingActions = action.payload;
      })
      // Save pending action
      .addCase(savePendingAction.fulfilled, (state, action: PayloadAction<PendingAction>) => {
        state.pendingActions.push(action.payload);
      })
      // Sync pending actions
      .addCase(syncPendingActions.pending, (state) => {
        state.syncInProgress = true;
        state.error = null;
      })
      .addCase(syncPendingActions.fulfilled, (state, action) => {
        state.syncInProgress = false;
        state.lastSyncTime = Date.now();
        state.pendingActions = state.pendingActions.filter(
          (a) => !action.payload.success.includes(a.id)
        );
      })
      .addCase(syncPendingActions.rejected, (state, action) => {
        state.syncInProgress = false;
        state.error = action.error.message || 'Sync failed';
      })
      // Check network
      .addCase(checkNetworkStatus.fulfilled, (state, action: PayloadAction<boolean>) => {
        state.isOnline = action.payload;
      });
  },
});

export const { setOnlineStatus, incrementRetryCount, removePendingAction, clearError } = offlineSlice.actions;
export default offlineSlice.reducer;
