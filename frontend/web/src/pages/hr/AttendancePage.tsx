// ========================================================
// SISTEMA ERP UNIVERSAL - Control de Asistencia
// ========================================================

import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Chip,
  IconButton,
  Tooltip,
  Card,
  CardContent,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  CheckCircle as CheckInIcon,
  Cancel as CheckOutIcon,
  Today as TodayIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import DataTable from '../../components/common/DataTable';
import { hrService, Attendance, Employee } from '../../services/hr.service';
import { useSnackbar } from 'notistack';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const statusConfig: Record<string, { label: string; color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' }> = {
  present: { label: 'Presente', color: 'success' },
  absent: { label: 'Ausente', color: 'error' },
  late: { label: 'Tardanza', color: 'warning' },
  half_day: { label: 'Medio Día', color: 'info' },
  on_leave: { label: 'Permiso', color: 'secondary' },
};

function AttendancePage() {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [date, setDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [departmentId, setDepartmentId] = useState('');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  const { data: departments } = useQuery({
    queryKey: ['departments-select'],
    queryFn: () => hrService.getDepartments({ page_size: 100 }),
  });

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['attendance', date, departmentId, page, pageSize],
    queryFn: () => hrService.getAttendance({
      date,
      department: departmentId || undefined,
      page: page + 1,
      page_size: pageSize,
    }),
  });

  const checkInMutation = useMutation({
    mutationFn: (employeeId: string) => hrService.checkIn(employeeId),
    onSuccess: () => {
      enqueueSnackbar('Entrada registrada', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['attendance'] });
    },
    onError: () => {
      enqueueSnackbar('Error al registrar entrada', { variant: 'error' });
    },
  });

  const checkOutMutation = useMutation({
    mutationFn: (employeeId: string) => hrService.checkOut(employeeId),
    onSuccess: () => {
      enqueueSnackbar('Salida registrada', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['attendance'] });
    },
    onError: () => {
      enqueueSnackbar('Error al registrar salida', { variant: 'error' });
    },
  });

  // Stats cards
  const stats = {
    total: data?.results?.length || 0,
    present: data?.results?.filter((a: Attendance) => a.status === 'present').length || 0,
    absent: data?.results?.filter((a: Attendance) => a.status === 'absent').length || 0,
    late: data?.results?.filter((a: Attendance) => a.status === 'late').length || 0,
  };

  const columns: GridColDef[] = [
    {
      field: 'employee',
      headerName: 'Empleado',
      flex: 1,
      minWidth: 200,
      valueGetter: (value: any) => {
        if (typeof value === 'object' && value) {
          return `${value.first_name || ''} ${value.last_name || ''}`.trim();
        }
        return value || '-';
      },
    },
    {
      field: 'department',
      headerName: 'Departamento',
      width: 150,
      valueGetter: (_, row) => {
        const emp = row.employee;
        if (typeof emp === 'object' && emp?.department) {
          return typeof emp.department === 'object' ? emp.department.name : emp.department;
        }
        return '-';
      },
    },
    {
      field: 'check_in',
      headerName: 'Entrada',
      width: 100,
      valueFormatter: (value: string) => value ? format(new Date(value), 'HH:mm') : '-',
    },
    {
      field: 'check_out',
      headerName: 'Salida',
      width: 100,
      valueFormatter: (value: string) => value ? format(new Date(value), 'HH:mm') : '-',
    },
    {
      field: 'hours_worked',
      headerName: 'Horas',
      width: 80,
      valueFormatter: (value: number) => value ? `${value.toFixed(1)}h` : '-',
    },
    {
      field: 'status',
      headerName: 'Estado',
      width: 120,
      renderCell: (params: GridRenderCellParams) => {
        const config = statusConfig[params.value] || { label: params.value, color: 'default' };
        return <Chip label={config.label} color={config.color} size="small" />;
      },
    },
    { field: 'notes', headerName: 'Observaciones', flex: 1, minWidth: 150 },
    {
      field: 'actions',
      headerName: 'Acciones',
      width: 120,
      sortable: false,
      renderCell: (params: GridRenderCellParams<Attendance>) => {
        const employeeId = typeof params.row.employee === 'object' 
          ? params.row.employee?.id 
          : params.row.employee;
        
        return (
          <Box>
            {!params.row.check_in && (
              <Tooltip title="Marcar Entrada">
                <IconButton
                  size="small"
                  color="success"
                  onClick={() => checkInMutation.mutate(employeeId)}
                  disabled={checkInMutation.isPending}
                >
                  <CheckInIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            {params.row.check_in && !params.row.check_out && (
              <Tooltip title="Marcar Salida">
                <IconButton
                  size="small"
                  color="error"
                  onClick={() => checkOutMutation.mutate(employeeId)}
                  disabled={checkOutMutation.isPending}
                >
                  <CheckOutIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        );
      },
    },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TodayIcon color="primary" />
          <Typography variant="h4" fontWeight={600}>Control de Asistencia</Typography>
        </Box>
        <Button variant="outlined" startIcon={<RefreshIcon />} onClick={() => refetch()}>
          Actualizar
        </Button>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography color="text.secondary" variant="body2">Total</Typography>
              <Typography variant="h4" fontWeight={600}>{stats.total}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card sx={{ bgcolor: 'success.light' }}>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography color="success.contrastText" variant="body2">Presentes</Typography>
              <Typography variant="h4" fontWeight={600} color="success.contrastText">{stats.present}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card sx={{ bgcolor: 'error.light' }}>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography color="error.contrastText" variant="body2">Ausentes</Typography>
              <Typography variant="h4" fontWeight={600} color="error.contrastText">{stats.absent}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card sx={{ bgcolor: 'warning.light' }}>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography color="warning.contrastText" variant="body2">Tardanzas</Typography>
              <Typography variant="h4" fontWeight={600} color="warning.contrastText">{stats.late}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={4}>
            <TextField
              label="Fecha"
              type="date"
              fullWidth
              value={date}
              onChange={(e) => setDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>Departamento</InputLabel>
              <Select
                value={departmentId}
                onChange={(e) => setDepartmentId(e.target.value)}
                label="Departamento"
              >
                <MenuItem value="">Todos</MenuItem>
                {departments?.results?.map((dept) => (
                  <MenuItem key={dept.id} value={dept.id}>{dept.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      <DataTable
        rows={data?.results || []}
        columns={columns}
        loading={isLoading}
        rowCount={data?.count || 0}
        paginationMode="server"
        onPaginationChange={(model) => {
          setPage(model.page);
          setPageSize(model.pageSize);
        }}
        getRowId={(row) => row.id}
      />
    </Box>
  );
}

export default AttendancePage;
