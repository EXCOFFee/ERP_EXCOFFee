// ========================================================
// SISTEMA ERP UNIVERSAL - Lista de Empleados
// ========================================================

import { useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Tooltip,
  Avatar,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import DataTable from '../../components/common/DataTable';
import { hrService, Employee } from '../../services/hr.service';
import { useSnackbar } from 'notistack';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const statusConfig: Record<string, { label: string; color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' }> = {
  active: { label: 'Activo', color: 'success' },
  on_leave: { label: 'Con Permiso', color: 'warning' },
  suspended: { label: 'Suspendido', color: 'error' },
  terminated: { label: 'Desvinculado', color: 'default' },
};

function EmployeeListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['employees', page, pageSize],
    queryFn: () => hrService.getEmployees({ page: page + 1, page_size: pageSize }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => hrService.deleteEmployee(id),
    onSuccess: () => {
      enqueueSnackbar('Empleado eliminado', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      setDeleteDialogOpen(false);
    },
    onError: () => {
      enqueueSnackbar('Error al eliminar', { variant: 'error' });
    },
  });

  const handleDelete = useCallback((employee: Employee) => {
    setSelectedEmployee(employee);
    setDeleteDialogOpen(true);
  }, []);

  const columns: GridColDef[] = [
    {
      field: 'photo',
      headerName: '',
      width: 60,
      sortable: false,
      renderCell: (params: GridRenderCellParams) => (
        <Avatar src={params.value} sx={{ width: 40, height: 40 }}>
          {params.row.first_name?.charAt(0)}{params.row.last_name?.charAt(0)}
        </Avatar>
      ),
    },
    { field: 'employee_code', headerName: 'Código', width: 100 },
    {
      field: 'full_name',
      headerName: 'Nombre',
      flex: 1,
      minWidth: 200,
      valueGetter: (_, row) => `${row.first_name} ${row.last_name}`,
    },
    { field: 'document_number', headerName: 'Documento', width: 120 },
    {
      field: 'department',
      headerName: 'Departamento',
      width: 150,
      valueGetter: (value: any) => typeof value === 'object' ? value?.name : value,
    },
    {
      field: 'position',
      headerName: 'Cargo',
      width: 150,
      valueGetter: (value: any) => typeof value === 'object' ? value?.name : value,
    },
    { field: 'email', headerName: 'Email', width: 200 },
    {
      field: 'hire_date',
      headerName: 'F. Ingreso',
      width: 110,
      valueFormatter: (value: string) => {
        try {
          return format(new Date(value), 'dd/MM/yyyy', { locale: es });
        } catch {
          return value;
        }
      },
    },
    {
      field: 'employment_status',
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
      renderCell: (params: GridRenderCellParams<Employee>) => (
        <Box>
          <Tooltip title="Ver">
            <IconButton size="small" onClick={() => navigate(`/hr/employees/${params.row.id}`)}>
              <ViewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Editar">
            <IconButton size="small" onClick={() => navigate(`/hr/employees/${params.row.id}/edit`)}>
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Eliminar">
            <IconButton size="small" color="error" onClick={() => handleDelete(params.row)}>
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight={600}>Empleados</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={() => refetch()}>
            Actualizar
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => navigate('/hr/employees/new')}>
            Nuevo Empleado
          </Button>
        </Box>
      </Box>

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

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirmar Eliminación</DialogTitle>
        <DialogContent>
          <DialogContentText>
            ¿Eliminar empleado "{selectedEmployee?.first_name} {selectedEmployee?.last_name}"?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancelar</Button>
          <Button
            onClick={() => selectedEmployee && deleteMutation.mutate(selectedEmployee.id)}
            color="error"
            variant="contained"
          >
            Eliminar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default EmployeeListPage;
