// ========================================================
// SISTEMA ERP UNIVERSAL - Gestión de Nómina
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
  Button,
  Chip,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Add as AddIcon,
  Visibility as ViewIcon,
  Print as PrintIcon,
  CheckCircle as ApproveIcon,
  Payment as PayIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import DataTable from '../../components/common/DataTable';
import { hrService, Payroll } from '../../services/hr.service';
import { useSnackbar } from 'notistack';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const statusConfig: Record<string, { label: string; color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' }> = {
  draft: { label: 'Borrador', color: 'default' },
  calculated: { label: 'Calculada', color: 'info' },
  approved: { label: 'Aprobada', color: 'primary' },
  paid: { label: 'Pagada', color: 'success' },
  cancelled: { label: 'Anulada', color: 'error' },
};

function PayrollPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [tabValue, setTabValue] = useState(0);

  const getStatusFilter = () => {
    switch (tabValue) {
      case 1: return 'draft';
      case 2: return 'calculated';
      case 3: return 'approved';
      case 4: return 'paid';
      default: return undefined;
    }
  };

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['payrolls', year, month, tabValue, page, pageSize],
    queryFn: () => hrService.getPayrolls({
      year,
      month,
      status: getStatusFilter(),
      page: page + 1,
      page_size: pageSize,
    }),
  });

  const approveMutation = useMutation({
    mutationFn: (id: string) => hrService.approvePayroll(id),
    onSuccess: () => {
      enqueueSnackbar('Nómina aprobada', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['payrolls'] });
    },
    onError: () => {
      enqueueSnackbar('Error al aprobar', { variant: 'error' });
    },
  });

  const payMutation = useMutation({
    mutationFn: (id: string) => hrService.processPayment(id),
    onSuccess: () => {
      enqueueSnackbar('Pago procesado', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['payrolls'] });
    },
    onError: () => {
      enqueueSnackbar('Error al procesar pago', { variant: 'error' });
    },
  });

  // Calculate totals
  const totals = data?.results?.reduce((acc: any, p: Payroll) => ({
    gross: acc.gross + (p.gross_salary || 0),
    deductions: acc.deductions + (p.total_deductions || 0),
    net: acc.net + (p.net_salary || 0),
  }), { gross: 0, deductions: 0, net: 0 }) || { gross: 0, deductions: 0, net: 0 };

  const months = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];

  const columns: GridColDef[] = [
    { field: 'payroll_number', headerName: 'Nº Nómina', width: 120 },
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
      field: 'gross_salary',
      headerName: 'Bruto',
      width: 120,
      valueFormatter: (value: number) => `$${value?.toFixed(2) || '0.00'}`,
      align: 'right',
    },
    {
      field: 'total_deductions',
      headerName: 'Deducciones',
      width: 120,
      valueFormatter: (value: number) => `$${value?.toFixed(2) || '0.00'}`,
      align: 'right',
    },
    {
      field: 'net_salary',
      headerName: 'Neto',
      width: 120,
      renderCell: (params: GridRenderCellParams) => (
        <Typography fontWeight={600}>${params.value?.toFixed(2) || '0.00'}</Typography>
      ),
      align: 'right',
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
    {
      field: 'actions',
      headerName: 'Acciones',
      width: 150,
      sortable: false,
      renderCell: (params: GridRenderCellParams<Payroll>) => (
        <Box>
          <Tooltip title="Ver detalle">
            <IconButton size="small" onClick={() => navigate(`/hr/payroll/${params.row.id}`)}>
              <ViewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          {params.row.status === 'calculated' && (
            <Tooltip title="Aprobar">
              <IconButton
                size="small"
                color="primary"
                onClick={() => approveMutation.mutate(params.row.id)}
                disabled={approveMutation.isPending}
              >
                <ApproveIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
          {params.row.status === 'approved' && (
            <Tooltip title="Procesar Pago">
              <IconButton
                size="small"
                color="success"
                onClick={() => payMutation.mutate(params.row.id)}
                disabled={payMutation.isPending}
              >
                <PayIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
          <Tooltip title="Imprimir">
            <IconButton size="small">
              <PrintIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight={600}>Nómina</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={() => refetch()}>
            Actualizar
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => navigate('/hr/payroll/new')}>
            Generar Nómina
          </Button>
        </Box>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>Total Bruto</Typography>
              <Typography variant="h5" fontWeight={600}>${totals.gross.toFixed(2)}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card sx={{ bgcolor: 'error.light' }}>
            <CardContent>
              <Typography color="error.contrastText" gutterBottom>Total Deducciones</Typography>
              <Typography variant="h5" fontWeight={600} color="error.contrastText">
                ${totals.deductions.toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card sx={{ bgcolor: 'success.light' }}>
            <CardContent>
              <Typography color="success.contrastText" gutterBottom>Total Neto</Typography>
              <Typography variant="h5" fontWeight={600} color="success.contrastText">
                ${totals.net.toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>Año</InputLabel>
              <Select
                value={year}
                onChange={(e) => setYear(Number(e.target.value))}
                label="Año"
              >
                {[2023, 2024, 2025, 2026].map((y) => (
                  <MenuItem key={y} value={y}>{y}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>Mes</InputLabel>
              <Select
                value={month}
                onChange={(e) => setMonth(Number(e.target.value))}
                label="Mes"
              >
                {months.map((m, i) => (
                  <MenuItem key={i} value={i + 1}>{m}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, v) => { setTabValue(v); setPage(0); }}>
          <Tab label="Todas" />
          <Tab label="Borradores" />
          <Tab label="Calculadas" />
          <Tab label="Aprobadas" />
          <Tab label="Pagadas" />
        </Tabs>
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

export default PayrollPage;
