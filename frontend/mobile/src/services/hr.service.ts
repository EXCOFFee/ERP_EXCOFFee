// ========================================================
// SISTEMA ERP MOBILE - Servicio de Recursos Humanos
// ========================================================

import api from './api';

// Tipos
export interface Department {
  id: string;
  code: string;
  name: string;
  description?: string;
  parent?: string;
  manager?: string;
  isActive: boolean;
  children?: Department[];
}

export interface Position {
  id: string;
  code: string;
  name: string;
  department: Department;
  description?: string;
  minSalary: number;
  maxSalary: number;
  isActive: boolean;
}

export interface Employee {
  id: string;
  employeeNumber: string;
  user?: string;
  firstName: string;
  lastName: string;
  fullName: string;
  email: string;
  phone?: string;
  mobile?: string;
  dateOfBirth?: string;
  gender: 'male' | 'female' | 'other';
  maritalStatus: 'single' | 'married' | 'divorced' | 'widowed';
  nationality?: string;
  idNumber?: string;
  department: Department;
  position: Position;
  manager?: Employee;
  hireDate: string;
  terminationDate?: string;
  employmentType: 'full_time' | 'part_time' | 'contract' | 'intern';
  employmentStatus: 'active' | 'on_leave' | 'terminated' | 'suspended';
  baseSalary: number;
  bankAccount?: string;
  photo?: string;
  createdAt: string;
}

export interface LeaveType {
  id: string;
  code: string;
  name: string;
  description?: string;
  daysAllowed: number;
  isPaid: boolean;
  requiresApproval: boolean;
  isActive: boolean;
}

export interface LeaveRequest {
  id: string;
  employee: Employee;
  leaveType: LeaveType;
  startDate: string;
  endDate: string;
  daysRequested: number;
  reason?: string;
  status: 'pending' | 'approved' | 'rejected' | 'cancelled';
  approvedBy?: string;
  approvedAt?: string;
  rejectionReason?: string;
  createdAt: string;
}

export interface Attendance {
  id: string;
  employee: Employee;
  date: string;
  checkIn?: string;
  checkOut?: string;
  hoursWorked: number;
  overtimeHours: number;
  status: 'present' | 'absent' | 'late' | 'half_day' | 'holiday' | 'leave';
  notes?: string;
}

export interface PayrollPeriod {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
  paymentDate: string;
  status: 'draft' | 'processing' | 'approved' | 'paid' | 'cancelled';
  totalGross: number;
  totalDeductions: number;
  totalNet: number;
}

export interface Payslip {
  id: string;
  payrollPeriod: PayrollPeriod;
  employee: Employee;
  basicSalary: number;
  grossSalary: number;
  totalDeductions: number;
  netSalary: number;
  paymentStatus: 'pending' | 'paid';
  paymentDate?: string;
}

export interface HRFilters {
  search?: string;
  departmentId?: string;
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

class HRService {
  // Departamentos
  async getDepartments(filters: HRFilters = {}): Promise<PaginatedResponse<Department>> {
    const { data } = await api.get('/hr/departments/', { params: filters });
    return data;
  }

  async getDepartment(id: string): Promise<Department> {
    const { data } = await api.get(`/hr/departments/${id}/`);
    return data;
  }

  async createDepartment(department: Partial<Department>): Promise<Department> {
    const { data } = await api.post('/hr/departments/', department);
    return data;
  }

  async updateDepartment(id: string, department: Partial<Department>): Promise<Department> {
    const { data } = await api.put(`/hr/departments/${id}/`, department);
    return data;
  }

  async deleteDepartment(id: string): Promise<void> {
    await api.delete(`/hr/departments/${id}/`);
  }

  // Posiciones
  async getPositions(filters: HRFilters = {}): Promise<PaginatedResponse<Position>> {
    const { data } = await api.get('/hr/positions/', { params: filters });
    return data;
  }

  async getPosition(id: string): Promise<Position> {
    const { data } = await api.get(`/hr/positions/${id}/`);
    return data;
  }

  async createPosition(position: Partial<Position>): Promise<Position> {
    const { data } = await api.post('/hr/positions/', position);
    return data;
  }

  async updatePosition(id: string, position: Partial<Position>): Promise<Position> {
    const { data } = await api.put(`/hr/positions/${id}/`, position);
    return data;
  }

  // Empleados
  async getEmployees(filters: HRFilters = {}): Promise<PaginatedResponse<Employee>> {
    const { data } = await api.get('/hr/employees/', { params: filters });
    return data;
  }

  async getEmployee(id: string): Promise<Employee> {
    const { data } = await api.get(`/hr/employees/${id}/`);
    return data;
  }

  async createEmployee(employee: Partial<Employee>): Promise<Employee> {
    const { data } = await api.post('/hr/employees/', employee);
    return data;
  }

  async updateEmployee(id: string, employee: Partial<Employee>): Promise<Employee> {
    const { data } = await api.put(`/hr/employees/${id}/`, employee);
    return data;
  }

  async getEmployeesByDepartment(departmentId: string): Promise<Employee[]> {
    const { data } = await api.get(`/hr/departments/${departmentId}/employees/`);
    return data;
  }

  // Tipos de Permiso
  async getLeaveTypes(): Promise<LeaveType[]> {
    const { data } = await api.get('/hr/leave-types/');
    return data;
  }

  // Solicitudes de Permiso
  async getLeaveRequests(filters: HRFilters = {}): Promise<PaginatedResponse<LeaveRequest>> {
    const { data } = await api.get('/hr/leave-requests/', { params: filters });
    return data;
  }

  async getLeaveRequest(id: string): Promise<LeaveRequest> {
    const { data } = await api.get(`/hr/leave-requests/${id}/`);
    return data;
  }

  async createLeaveRequest(request: Partial<LeaveRequest>): Promise<LeaveRequest> {
    const { data } = await api.post('/hr/leave-requests/', request);
    return data;
  }

  async approveLeaveRequest(id: string): Promise<LeaveRequest> {
    const { data } = await api.post(`/hr/leave-requests/${id}/approve/`);
    return data;
  }

  async rejectLeaveRequest(id: string, reason: string): Promise<LeaveRequest> {
    const { data } = await api.post(`/hr/leave-requests/${id}/reject/`, { reason });
    return data;
  }

  async cancelLeaveRequest(id: string): Promise<LeaveRequest> {
    const { data } = await api.post(`/hr/leave-requests/${id}/cancel/`);
    return data;
  }

  // Asistencia
  async getAttendance(filters: HRFilters = {}): Promise<PaginatedResponse<Attendance>> {
    const { data } = await api.get('/hr/attendance/', { params: filters });
    return data;
  }

  async checkIn(employeeId?: string): Promise<Attendance> {
    const { data } = await api.post('/hr/attendance/check-in/', { employee_id: employeeId });
    return data;
  }

  async checkOut(employeeId?: string): Promise<Attendance> {
    const { data } = await api.post('/hr/attendance/check-out/', { employee_id: employeeId });
    return data;
  }

  async getTodayAttendance(employeeId?: string): Promise<Attendance | null> {
    try {
      const params = employeeId ? { employee_id: employeeId } : {};
      const { data } = await api.get('/hr/attendance/today/', { params });
      return data;
    } catch {
      return null;
    }
  }

  // Nómina
  async getPayrollPeriods(filters: HRFilters = {}): Promise<PaginatedResponse<PayrollPeriod>> {
    const { data } = await api.get('/hr/payroll-periods/', { params: filters });
    return data;
  }

  async getPayrollPeriod(id: string): Promise<PayrollPeriod> {
    const { data } = await api.get(`/hr/payroll-periods/${id}/`);
    return data;
  }

  async getPayslips(periodId: string): Promise<Payslip[]> {
    const { data } = await api.get(`/hr/payroll-periods/${periodId}/payslips/`);
    return data;
  }

  async getMyPayslips(): Promise<Payslip[]> {
    const { data } = await api.get('/hr/my-payslips/');
    return data;
  }

  async getPayslip(id: string): Promise<Payslip> {
    const { data } = await api.get(`/hr/payslips/${id}/`);
    return data;
  }

  // Reportes
  async getAttendanceReport(startDate: string, endDate: string, departmentId?: string): Promise<any> {
    const params: any = { start_date: startDate, end_date: endDate };
    if (departmentId) params.department_id = departmentId;
    const { data } = await api.get('/hr/reports/attendance/', { params });
    return data;
  }

  async getPayrollReport(periodId: string): Promise<any> {
    const { data } = await api.get(`/hr/reports/payroll/${periodId}/`);
    return data;
  }

  async getHeadcountReport(): Promise<any> {
    const { data } = await api.get('/hr/reports/headcount/');
    return data;
  }
}

export const hrService = new HRService();
export default hrService;
