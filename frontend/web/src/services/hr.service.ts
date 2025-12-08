// ========================================================
// SISTEMA ERP UNIVERSAL - Servicio de Recursos Humanos
// ========================================================

import { api, apiGet, apiPost, apiPut } from './api';
import type { PaginatedResponse, ListParams } from './inventory.service';

// Tipos
export interface Department {
  id: string;
  code: string;
  name: string;
  description?: string;
  parent?: string;
  manager?: string;
  is_active: boolean;
  children?: Department[];
}

export interface Position {
  id: string;
  code: string;
  name: string;
  department: Department;
  description?: string;
  min_salary: number;
  max_salary: number;
  is_active: boolean;
}

export interface Employee {
  id: string;
  employee_number: string;
  user?: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone?: string;
  mobile?: string;
  date_of_birth?: string;
  gender: 'male' | 'female' | 'other';
  marital_status: 'single' | 'married' | 'divorced' | 'widowed';
  nationality?: string;
  id_number?: string;
  department: Department;
  position: Position;
  manager?: Employee;
  hire_date: string;
  termination_date?: string;
  employment_type: 'full_time' | 'part_time' | 'contract' | 'intern';
  employment_status: 'active' | 'on_leave' | 'terminated' | 'suspended';
  base_salary: number;
  bank_account?: string;
  photo?: string;
  created_at: string;
}

export interface LeaveType {
  id: string;
  code: string;
  name: string;
  description?: string;
  days_allowed: number;
  is_paid: boolean;
  requires_approval: boolean;
  is_active: boolean;
}

export interface LeaveRequest {
  id: string;
  employee: Employee;
  leave_type: LeaveType;
  start_date: string;
  end_date: string;
  days_requested: number;
  reason?: string;
  status: 'pending' | 'approved' | 'rejected' | 'cancelled';
  approved_by?: string;
  approved_at?: string;
  rejection_reason?: string;
  created_at: string;
}

export interface Attendance {
  id: string;
  employee: Employee;
  date: string;
  check_in?: string;
  check_out?: string;
  hours_worked: number;
  overtime_hours: number;
  status: 'present' | 'absent' | 'late' | 'half_day' | 'holiday' | 'leave';
  notes?: string;
}

export interface WorkSchedule {
  id: string;
  name: string;
  monday_start?: string;
  monday_end?: string;
  tuesday_start?: string;
  tuesday_end?: string;
  wednesday_start?: string;
  wednesday_end?: string;
  thursday_start?: string;
  thursday_end?: string;
  friday_start?: string;
  friday_end?: string;
  saturday_start?: string;
  saturday_end?: string;
  sunday_start?: string;
  sunday_end?: string;
  is_active: boolean;
}

export interface Holiday {
  id: string;
  name: string;
  date: string;
  is_recurring: boolean;
  applies_to_all: boolean;
}

export interface PayrollPeriod {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  payment_date: string;
  status: 'draft' | 'processing' | 'approved' | 'paid' | 'cancelled';
  total_gross: number;
  total_deductions: number;
  total_net: number;
}

export interface Payslip {
  id: string;
  payroll_period: PayrollPeriod;
  employee: Employee;
  basic_salary: number;
  gross_salary: number;
  total_deductions: number;
  net_salary: number;
  payment_status: 'pending' | 'paid';
  payment_date?: string;
}

export interface SalaryComponent {
  id: string;
  code: string;
  name: string;
  component_type: 'earning' | 'deduction';
  calculation_type: 'fixed' | 'percentage';
  amount: number;
  is_taxable: boolean;
  is_active: boolean;
}

export interface Loan {
  id: string;
  employee: Employee;
  loan_type: string;
  amount: number;
  interest_rate: number;
  term_months: number;
  monthly_payment: number;
  start_date: string;
  status: 'pending' | 'approved' | 'active' | 'paid' | 'rejected';
  balance: number;
}

export interface PerformanceReview {
  id: string;
  employee: Employee;
  reviewer: string;
  review_period_start: string;
  review_period_end: string;
  review_date: string;
  overall_rating: number;
  status: 'draft' | 'submitted' | 'acknowledged';
  strengths?: string;
  areas_for_improvement?: string;
  goals?: string;
  comments?: string;
}

export interface Training {
  id: string;
  name: string;
  description?: string;
  trainer?: string;
  start_date: string;
  end_date: string;
  location?: string;
  max_participants: number;
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled';
  participants: Employee[];
}

// ========== DEPARTAMENTOS ==========
export const departmentService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<Department>>('/hr/departments/', params),
  
  getTree: () => 
    apiGet<Department[]>('/hr/departments/tree/'),
  
  get: (id: string) => 
    apiGet<Department>(`/hr/departments/${id}/`),
  
  create: (data: Partial<Department>) => 
    apiPost<Department>('/hr/departments/', data),
  
  update: (id: string, data: Partial<Department>) => 
    apiPut<Department>(`/hr/departments/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/hr/departments/${id}/`),
  
  getEmployees: (id: string) => 
    apiGet<Employee[]>(`/hr/departments/${id}/employees/`),
};

// ========== PUESTOS ==========
export const positionService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<Position>>('/hr/positions/', params),
  
  get: (id: string) => 
    apiGet<Position>(`/hr/positions/${id}/`),
  
  create: (data: Partial<Position>) => 
    apiPost<Position>('/hr/positions/', data),
  
  update: (id: string, data: Partial<Position>) => 
    apiPut<Position>(`/hr/positions/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/hr/positions/${id}/`),
};

// ========== EMPLEADOS ==========
export const employeeService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<Employee>>('/hr/employees/', params),
  
  get: (id: string) => 
    apiGet<Employee>(`/hr/employees/${id}/`),
  
  create: (data: Partial<Employee>) => 
    apiPost<Employee>('/hr/employees/', data),
  
  update: (id: string, data: Partial<Employee>) => 
    apiPut<Employee>(`/hr/employees/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/hr/employees/${id}/`),
  
  getOrgChart: () => 
    apiGet('/hr/employees/org-chart/'),
  
  terminate: (id: string, data: { termination_date: string; reason: string }) => 
    apiPost(`/hr/employees/${id}/terminate/`, data),
  
  getAttendance: (id: string, params?: { start_date?: string; end_date?: string }) => 
    apiGet<Attendance[]>(`/hr/employees/${id}/attendance/`, params),
  
  getLeaves: (id: string, params?: ListParams) => 
    apiGet<PaginatedResponse<LeaveRequest>>(`/hr/employees/${id}/leaves/`, params),
  
  getPayslips: (id: string, params?: ListParams) => 
    apiGet<PaginatedResponse<Payslip>>(`/hr/employees/${id}/payslips/`, params),
};

// ========== TIPOS DE AUSENCIA ==========
export const leaveTypeService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<LeaveType>>('/hr/leave-types/', params),
  
  get: (id: string) => 
    apiGet<LeaveType>(`/hr/leave-types/${id}/`),
  
  create: (data: Partial<LeaveType>) => 
    apiPost<LeaveType>('/hr/leave-types/', data),
  
  update: (id: string, data: Partial<LeaveType>) => 
    apiPut<LeaveType>(`/hr/leave-types/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/hr/leave-types/${id}/`),
};

// ========== SOLICITUDES DE AUSENCIA ==========
export const leaveRequestService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<LeaveRequest>>('/hr/leave-requests/', params),
  
  get: (id: string) => 
    apiGet<LeaveRequest>(`/hr/leave-requests/${id}/`),
  
  create: (data: Partial<LeaveRequest>) => 
    apiPost<LeaveRequest>('/hr/leave-requests/', data),
  
  update: (id: string, data: Partial<LeaveRequest>) => 
    apiPut<LeaveRequest>(`/hr/leave-requests/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/hr/leave-requests/${id}/`),
  
  approve: (id: string) => 
    apiPost(`/hr/leave-requests/${id}/approve/`),
  
  reject: (id: string, reason: string) => 
    apiPost(`/hr/leave-requests/${id}/reject/`, { reason }),
  
  cancel: (id: string) => 
    apiPost(`/hr/leave-requests/${id}/cancel/`),
  
  getCalendar: (params?: { start_date?: string; end_date?: string }) => 
    apiGet('/hr/leave-requests/calendar/', params),
};

// ========== ASISTENCIA ==========
export const attendanceService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<Attendance>>('/hr/attendance/', params),
  
  get: (id: string) => 
    apiGet<Attendance>(`/hr/attendance/${id}/`),
  
  checkIn: (employee_id: string) => 
    apiPost('/hr/attendance/check-in/', { employee: employee_id }),
  
  checkOut: (employee_id: string) => 
    apiPost('/hr/attendance/check-out/', { employee: employee_id }),
  
  getReport: (params?: { start_date?: string; end_date?: string; department?: string }) => 
    apiGet('/hr/attendance/report/', params),
};

// ========== HORARIOS ==========
export const workScheduleService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<WorkSchedule>>('/hr/work-schedules/', params),
  
  get: (id: string) => 
    apiGet<WorkSchedule>(`/hr/work-schedules/${id}/`),
  
  create: (data: Partial<WorkSchedule>) => 
    apiPost<WorkSchedule>('/hr/work-schedules/', data),
  
  update: (id: string, data: Partial<WorkSchedule>) => 
    apiPut<WorkSchedule>(`/hr/work-schedules/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/hr/work-schedules/${id}/`),
};

// ========== FERIADOS ==========
export const holidayService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<Holiday>>('/hr/holidays/', params),
  
  get: (id: string) => 
    apiGet<Holiday>(`/hr/holidays/${id}/`),
  
  create: (data: Partial<Holiday>) => 
    apiPost<Holiday>('/hr/holidays/', data),
  
  update: (id: string, data: Partial<Holiday>) => 
    apiPut<Holiday>(`/hr/holidays/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/hr/holidays/${id}/`),
};

// ========== PERÍODOS DE NÓMINA ==========
export const payrollPeriodService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<PayrollPeriod>>('/hr/payroll-periods/', params),
  
  get: (id: string) => 
    apiGet<PayrollPeriod>(`/hr/payroll-periods/${id}/`),
  
  create: (data: Partial<PayrollPeriod>) => 
    apiPost<PayrollPeriod>('/hr/payroll-periods/', data),
  
  generate: (id: string) => 
    apiPost(`/hr/payroll-periods/${id}/generate/`),
  
  approve: (id: string) => 
    apiPost(`/hr/payroll-periods/${id}/approve/`),
  
  processPayment: (id: string) => 
    apiPost(`/hr/payroll-periods/${id}/process-payment/`),
  
  getPayslips: (id: string) => 
    apiGet<Payslip[]>(`/hr/payroll-periods/${id}/payslips/`),
};

// ========== COMPONENTES SALARIALES ==========
export const salaryComponentService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<SalaryComponent>>('/hr/salary-components/', params),
  
  get: (id: string) => 
    apiGet<SalaryComponent>(`/hr/salary-components/${id}/`),
  
  create: (data: Partial<SalaryComponent>) => 
    apiPost<SalaryComponent>('/hr/salary-components/', data),
  
  update: (id: string, data: Partial<SalaryComponent>) => 
    apiPut<SalaryComponent>(`/hr/salary-components/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/hr/salary-components/${id}/`),
};

// ========== PRÉSTAMOS ==========
export const loanService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<Loan>>('/hr/loans/', params),
  
  get: (id: string) => 
    apiGet<Loan>(`/hr/loans/${id}/`),
  
  create: (data: Partial<Loan>) => 
    apiPost<Loan>('/hr/loans/', data),
  
  approve: (id: string) => 
    apiPost(`/hr/loans/${id}/approve/`),
  
  reject: (id: string, reason: string) => 
    apiPost(`/hr/loans/${id}/reject/`, { reason }),
};

// ========== EVALUACIONES DE DESEMPEÑO ==========
export const performanceReviewService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<PerformanceReview>>('/hr/performance-reviews/', params),
  
  get: (id: string) => 
    apiGet<PerformanceReview>(`/hr/performance-reviews/${id}/`),
  
  create: (data: Partial<PerformanceReview>) => 
    apiPost<PerformanceReview>('/hr/performance-reviews/', data),
  
  update: (id: string, data: Partial<PerformanceReview>) => 
    apiPut<PerformanceReview>(`/hr/performance-reviews/${id}/`, data),
  
  submit: (id: string) => 
    apiPost(`/hr/performance-reviews/${id}/submit/`),
  
  acknowledge: (id: string) => 
    apiPost(`/hr/performance-reviews/${id}/acknowledge/`),
};

// ========== CAPACITACIONES ==========
export const trainingService = {
  list: (params?: ListParams) => 
    apiGet<PaginatedResponse<Training>>('/hr/trainings/', params),
  
  get: (id: string) => 
    apiGet<Training>(`/hr/trainings/${id}/`),
  
  create: (data: Partial<Training>) => 
    apiPost<Training>('/hr/trainings/', data),
  
  update: (id: string, data: Partial<Training>) => 
    apiPut<Training>(`/hr/trainings/${id}/`, data),
  
  delete: (id: string) => 
    api.delete(`/hr/trainings/${id}/`),
  
  enroll: (id: string, employee_ids: string[]) => 
    apiPost(`/hr/trainings/${id}/enroll/`, { employees: employee_ids }),
  
  complete: (id: string) => 
    apiPost(`/hr/trainings/${id}/complete/`),
};

// ========== SERVICIO UNIFICADO DE HR ==========
// Exporta un servicio unificado para facilitar el uso en componentes
export const hrService = {
  // Empleados
  getEmployees: employeeService.list,
  getEmployee: employeeService.get,
  createEmployee: employeeService.create,
  updateEmployee: employeeService.update,
  deleteEmployee: employeeService.delete,

  // Departamentos
  getDepartments: departmentService.list,
  getDepartment: departmentService.get,
  createDepartment: departmentService.create,
  updateDepartment: departmentService.update,
  deleteDepartment: departmentService.delete,

  // Cargos
  getPositions: positionService.list,
  getPosition: positionService.get,
  createPosition: positionService.create,
  updatePosition: positionService.update,
  deletePosition: positionService.delete,

  // Asistencia
  getAttendance: attendanceService.list,
  checkIn: attendanceService.checkIn,
  checkOut: attendanceService.checkOut,

  // Nómina
  getPayrolls: (params?: ListParams & { year?: number; month?: number; status?: string }) => 
    apiGet<PaginatedResponse<Payslip>>('/hr/payslips/', params),
  getPayroll: (id: string) => apiGet<Payslip>(`/hr/payslips/${id}/`),
  approvePayroll: (id: string) => apiPost(`/hr/payslips/${id}/approve/`),
  processPayment: (id: string) => apiPost(`/hr/payslips/${id}/pay/`),

  // Períodos de nómina
  getPayrollPeriods: payrollPeriodService.list,
  createPayrollPeriod: payrollPeriodService.create,
  generatePayroll: payrollPeriodService.generate,
  approvePayrollPeriod: payrollPeriodService.approve,
  processPayrollPayment: payrollPeriodService.processPayment,
};

// Type alias para compatibilidad
export type Payroll = Payslip;
