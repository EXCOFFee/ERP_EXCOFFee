import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface SnackbarState {
  visible: boolean;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

interface UIState {
  isDrawerOpen: boolean;
  snackbar: SnackbarState;
  isRefreshing: boolean;
  currentModule: string | null;
}

const initialState: UIState = {
  isDrawerOpen: false,
  snackbar: {
    visible: false,
    message: '',
    type: 'info',
    duration: 3000,
  },
  isRefreshing: false,
  currentModule: null,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleDrawer: (state) => {
      state.isDrawerOpen = !state.isDrawerOpen;
    },
    setDrawerOpen: (state, action: PayloadAction<boolean>) => {
      state.isDrawerOpen = action.payload;
    },
    showSnackbar: (
      state,
      action: PayloadAction<{
        message: string;
        type?: 'success' | 'error' | 'warning' | 'info';
        duration?: number;
      }>
    ) => {
      state.snackbar = {
        visible: true,
        message: action.payload.message,
        type: action.payload.type || 'info',
        duration: action.payload.duration || 3000,
      };
    },
    hideSnackbar: (state) => {
      state.snackbar.visible = false;
    },
    setRefreshing: (state, action: PayloadAction<boolean>) => {
      state.isRefreshing = action.payload;
    },
    setCurrentModule: (state, action: PayloadAction<string | null>) => {
      state.currentModule = action.payload;
    },
  },
});

export const {
  toggleDrawer,
  setDrawerOpen,
  showSnackbar,
  hideSnackbar,
  setRefreshing,
  setCurrentModule,
} = uiSlice.actions;

export default uiSlice.reducer;
