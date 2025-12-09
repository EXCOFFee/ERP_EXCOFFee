// ========================================================
// SISTEMA ERP MOBILE - HR Redux Slice
// ========================================================

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import hrService, { 
  Department, 
  Position,
  Employee, 
  LeaveRequest, 
  LeaveType,
  Attendance,
  PayrollPeriod,
  Payslip,
  HRFilters 
} from '../../services/hr.service';

interface HRState {
  // Departments
  departments: Department[];
  departmentsLoading: boolean;
  departmentsError: string | null;
  selectedDepartment: Department | null;
  
  // Positions
  positions: Position[];
  positionsLoading: boolean;
  
  // Employees
  employees: Employee[];
  employeesLoading: boolean;
  employeesError: string | null;
  selectedEmployee: Employee | null;
  
  // Leave
  leaveTypes: LeaveType[];
  leaveRequests: LeaveRequest[];
  leaveRequestsLoading: boolean;
  
  // Attendance
  attendanceRecords: Attendance[];
  attendanceLoading: boolean;
  todayAttendance: Attendance | null;
  
  // Payroll
  payrollPeriods: PayrollPeriod[];
  payrollPeriodsLoading: boolean;
  payslips: Payslip[];
  myPayslips: Payslip[];
  
  // Pagination
  total: number;
  page: number;
  totalPages: number;
}

const initialState: HRState = {
  departments: [],
  departmentsLoading: false,
  departmentsError: null,
  selectedDepartment: null,
  
  positions: [],
  positionsLoading: false,
  
  employees: [],
  employeesLoading: false,
  employeesError: null,
  selectedEmployee: null,
  
  leaveTypes: [],
  leaveRequests: [],
  leaveRequestsLoading: false,
  
  attendanceRecords: [],
  attendanceLoading: false,
  todayAttendance: null,
  
  payrollPeriods: [],
  payrollPeriodsLoading: false,
  payslips: [],
  myPayslips: [],
  
  total: 0,
  page: 1,
  totalPages: 1,
};

// ========== ASYNC THUNKS ==========

// Departments
export const fetchDepartments = createAsyncThunk(
  'hr/fetchDepartments',
  async (filters: HRFilters = {}) => {
    const response = await hrService.getDepartments(filters);
    return response;
  }
);

export const fetchDepartment = createAsyncThunk(
  'hr/fetchDepartment',
  async (id: string) => {
    return await hrService.getDepartment(id);
  }
);

export const createDepartment = createAsyncThunk(
  'hr/createDepartment',
  async (department: Partial<Department>) => {
    return await hrService.createDepartment(department);
  }
);

export const updateDepartment = createAsyncThunk(
  'hr/updateDepartment',
  async ({ id, department }: { id: string; department: Partial<Department> }) => {
    return await hrService.updateDepartment(id, department);
  }
);

export const deleteDepartment = createAsyncThunk(
  'hr/deleteDepartment',
  async (id: string) => {
    await hrService.deleteDepartment(id);
    return id;
  }
);

// Positions
export const fetchPositions = createAsyncThunk(
  'hr/fetchPositions',
  async (filters: HRFilters = {}) => {
    const response = await hrService.getPositions(filters);
    return response;
  }
);

export const createPosition = createAsyncThunk(
  'hr/createPosition',
  async (position: Partial<Position>) => {
    return await hrService.createPosition(position);
  }
);

// Employees
export const fetchEmployees = createAsyncThunk(
  'hr/fetchEmployees',
  async (filters: HRFilters = {}) => {
    const response = await hrService.getEmployees(filters);
    return response;
  }
);

export const fetchEmployee = createAsyncThunk(
  'hr/fetchEmployee',
  async (id: string) => {
    return await hrService.getEmployee(id);
  }
);

export const createEmployee = createAsyncThunk(
  'hr/createEmployee',
  async (employee: Partial<Employee>) => {
    return await hrService.createEmployee(employee);
  }
);

export const updateEmployee = createAsyncThunk(
  'hr/updateEmployee',
  async ({ id, employee }: { id: string; employee: Partial<Employee> }) => {
    return await hrService.updateEmployee(id, employee);
  }
);

// Leave Types
export const fetchLeaveTypes = createAsyncThunk(
  'hr/fetchLeaveTypes',
  async () => {
    return await hrService.getLeaveTypes();
  }
);

// Leave Requests
export const fetchLeaveRequests = createAsyncThunk(
  'hr/fetchLeaveRequests',
  async (filters: HRFilters = {}) => {
    const response = await hrService.getLeaveRequests(filters);
    return response;
  }
);

export const createLeaveRequest = createAsyncThunk(
  'hr/createLeaveRequest',
  async (request: Partial<LeaveRequest>) => {
    return await hrService.createLeaveRequest(request);
  }
);

export const approveLeaveRequest = createAsyncThunk(
  'hr/approveLeaveRequest',
  async (id: string) => {
    return await hrService.approveLeaveRequest(id);
  }
);

export const rejectLeaveRequest = createAsyncThunk(
  'hr/rejectLeaveRequest',
  async ({ id, reason }: { id: string; reason: string }) => {
    return await hrService.rejectLeaveRequest(id, reason);
  }
);

// Attendance
export const fetchAttendance = createAsyncThunk(
  'hr/fetchAttendance',
  async (filters: HRFilters = {}) => {
    const response = await hrService.getAttendance(filters);
    return response;
  }
);

export const fetchTodayAttendance = createAsyncThunk(
  'hr/fetchTodayAttendance',
  async (employeeId?: string) => {
    return await hrService.getTodayAttendance(employeeId);
  }
);

export const checkIn = createAsyncThunk(
  'hr/checkIn',
  async (employeeId?: string) => {
    return await hrService.checkIn(employeeId);
  }
);

export const checkOut = createAsyncThunk(
  'hr/checkOut',
  async (employeeId?: string) => {
    return await hrService.checkOut(employeeId);
  }
);

// Payroll
export const fetchPayrollPeriods = createAsyncThunk(
  'hr/fetchPayrollPeriods',
  async (filters: HRFilters = {}) => {
    const response = await hrService.getPayrollPeriods(filters);
    return response;
  }
);

export const fetchPayslips = createAsyncThunk(
  'hr/fetchPayslips',
  async (periodId: string) => {
    return await hrService.getPayslips(periodId);
  }
);

export const fetchMyPayslips = createAsyncThunk(
  'hr/fetchMyPayslips',
  async () => {
    return await hrService.getMyPayslips();
  }
);

// ========== SLICE ==========

const hrSlice = createSlice({
  name: 'hr',
  initialState,
  reducers: {
    setSelectedDepartment: (state, action: PayloadAction<Department | null>) => {
      state.selectedDepartment = action.payload;
    },
    setSelectedEmployee: (state, action: PayloadAction<Employee | null>) => {
      state.selectedEmployee = action.payload;
    },
    clearHRErrors: (state) => {
      state.departmentsError = null;
      state.employeesError = null;
    },
  },
  extraReducers: (builder) => {
    // Departments
    builder
      .addCase(fetchDepartments.pending, (state) => {
        state.departmentsLoading = true;
        state.departmentsError = null;
      })
      .addCase(fetchDepartments.fulfilled, (state, action) => {
        state.departmentsLoading = false;
        state.departments = action.payload.data;
        state.total = action.payload.total;
        state.page = action.payload.page;
        state.totalPages = action.payload.totalPages;
      })
      .addCase(fetchDepartments.rejected, (state, action) => {
        state.departmentsLoading = false;
        state.departmentsError = action.error.message || 'Error loading departments';
      })
      .addCase(fetchDepartment.fulfilled, (state, action) => {
        state.selectedDepartment = action.payload;
      })
      .addCase(createDepartment.fulfilled, (state, action) => {
        state.departments.push(action.payload);
      })
      .addCase(updateDepartment.fulfilled, (state, action) => {
        const index = state.departments.findIndex(d => d.id === action.payload.id);
        if (index !== -1) {
          state.departments[index] = action.payload;
        }
      })
      .addCase(deleteDepartment.fulfilled, (state, action) => {
        state.departments = state.departments.filter(d => d.id !== action.payload);
      });

    // Positions
    builder
      .addCase(fetchPositions.pending, (state) => {
        state.positionsLoading = true;
      })
      .addCase(fetchPositions.fulfilled, (state, action) => {
        state.positionsLoading = false;
        state.positions = action.payload.data;
      })
      .addCase(createPosition.fulfilled, (state, action) => {
        state.positions.push(action.payload);
      });

    // Employees
    builder
      .addCase(fetchEmployees.pending, (state) => {
        state.employeesLoading = true;
        state.employeesError = null;
      })
      .addCase(fetchEmployees.fulfilled, (state, action) => {
        state.employeesLoading = false;
        state.employees = action.payload.data;
        state.total = action.payload.total;
        state.page = action.payload.page;
        state.totalPages = action.payload.totalPages;
      })
      .addCase(fetchEmployees.rejected, (state, action) => {
        state.employeesLoading = false;
        state.employeesError = action.error.message || 'Error loading employees';
      })
      .addCase(fetchEmployee.fulfilled, (state, action) => {
        state.selectedEmployee = action.payload;
      })
      .addCase(createEmployee.fulfilled, (state, action) => {
        state.employees.push(action.payload);
      })
      .addCase(updateEmployee.fulfilled, (state, action) => {
        const index = state.employees.findIndex(e => e.id === action.payload.id);
        if (index !== -1) {
          state.employees[index] = action.payload;
        }
      });

    // Leave Types
    builder
      .addCase(fetchLeaveTypes.fulfilled, (state, action) => {
        state.leaveTypes = action.payload;
      });

    // Leave Requests
    builder
      .addCase(fetchLeaveRequests.pending, (state) => {
        state.leaveRequestsLoading = true;
      })
      .addCase(fetchLeaveRequests.fulfilled, (state, action) => {
        state.leaveRequestsLoading = false;
        state.leaveRequests = action.payload.data;
      })
      .addCase(createLeaveRequest.fulfilled, (state, action) => {
        state.leaveRequests.unshift(action.payload);
      })
      .addCase(approveLeaveRequest.fulfilled, (state, action) => {
        const index = state.leaveRequests.findIndex(l => l.id === action.payload.id);
        if (index !== -1) {
          state.leaveRequests[index] = action.payload;
        }
      })
      .addCase(rejectLeaveRequest.fulfilled, (state, action) => {
        const index = state.leaveRequests.findIndex(l => l.id === action.payload.id);
        if (index !== -1) {
          state.leaveRequests[index] = action.payload;
        }
      });

    // Attendance
    builder
      .addCase(fetchAttendance.pending, (state) => {
        state.attendanceLoading = true;
      })
      .addCase(fetchAttendance.fulfilled, (state, action) => {
        state.attendanceLoading = false;
        state.attendanceRecords = action.payload.data;
      })
      .addCase(fetchTodayAttendance.fulfilled, (state, action) => {
        state.todayAttendance = action.payload;
      })
      .addCase(checkIn.fulfilled, (state, action) => {
        state.todayAttendance = action.payload;
      })
      .addCase(checkOut.fulfilled, (state, action) => {
        state.todayAttendance = action.payload;
      });

    // Payroll
    builder
      .addCase(fetchPayrollPeriods.pending, (state) => {
        state.payrollPeriodsLoading = true;
      })
      .addCase(fetchPayrollPeriods.fulfilled, (state, action) => {
        state.payrollPeriodsLoading = false;
        state.payrollPeriods = action.payload.data;
      })
      .addCase(fetchPayslips.fulfilled, (state, action) => {
        state.payslips = action.payload;
      })
      .addCase(fetchMyPayslips.fulfilled, (state, action) => {
        state.myPayslips = action.payload;
      });
  },
});

export const { setSelectedDepartment, setSelectedEmployee, clearHRErrors } = hrSlice.actions;
export default hrSlice.reducer;

// Selectors
export const selectDepartments = (state: { hr: HRState }) => state.hr.departments;
export const selectDepartmentsLoading = (state: { hr: HRState }) => state.hr.departmentsLoading;
export const selectSelectedDepartment = (state: { hr: HRState }) => state.hr.selectedDepartment;
export const selectPositions = (state: { hr: HRState }) => state.hr.positions;
export const selectEmployees = (state: { hr: HRState }) => state.hr.employees;
export const selectEmployeesLoading = (state: { hr: HRState }) => state.hr.employeesLoading;
export const selectSelectedEmployee = (state: { hr: HRState }) => state.hr.selectedEmployee;
export const selectLeaveTypes = (state: { hr: HRState }) => state.hr.leaveTypes;
export const selectLeaveRequests = (state: { hr: HRState }) => state.hr.leaveRequests;
export const selectAttendanceRecords = (state: { hr: HRState }) => state.hr.attendanceRecords;
export const selectTodayAttendance = (state: { hr: HRState }) => state.hr.todayAttendance;
export const selectPayrollPeriods = (state: { hr: HRState }) => state.hr.payrollPeriods;
export const selectPayslips = (state: { hr: HRState }) => state.hr.payslips;
export const selectMyPayslips = (state: { hr: HRState }) => state.hr.myPayslips;
