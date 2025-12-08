// ========================================================
// SISTEMA ERP UNIVERSAL - Lista de Departamentos
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
  TextField,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Business as DeptIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import DataTable from '../../components/common/DataTable';
import { hrService, Department } from '../../services/hr.service';
import { useSnackbar } from 'notistack';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const departmentSchema = z.object({
  code: z.string().min(1, 'Código es requerido'),
  name: z.string().min(1, 'Nombre es requerido'),
  description: z.string().optional(),
  parent: z.string().optional(),
  manager: z.string().optional(),
  is_active: z.boolean(),
});

type DepartmentFormData = z.infer<typeof departmentSchema>;

function DepartmentListPage() {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [formDialogOpen, setFormDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedDept, setSelectedDept] = useState<Department | null>(null);

  const { control, handleSubmit, reset, formState: { errors } } = useForm<DepartmentFormData>({
    resolver: zodResolver(departmentSchema),
    defaultValues: {
      code: '',
      name: '',
      description: '',
      parent: '',
      manager: '',
      is_active: true,
    },
  });

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['departments', page, pageSize],
    queryFn: () => hrService.getDepartments({ page: page + 1, page_size: pageSize }),
  });

  const { data: employees } = useQuery({
    queryKey: ['employees-select'],
    queryFn: () => hrService.getEmployees({ page_size: 100 }),
  });

  const saveMutation = useMutation({
    mutationFn: (data: DepartmentFormData) => {
      if (selectedDept) {
        return hrService.updateDepartment(selectedDept.id, data);
      }
      return hrService.createDepartment(data);
    },
    onSuccess: () => {
      enqueueSnackbar(selectedDept ? 'Departamento actualizado' : 'Departamento creado', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['departments'] });
      handleCloseForm();
    },
    onError: () => {
      enqueueSnackbar('Error al guardar', { variant: 'error' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => hrService.deleteDepartment(id),
    onSuccess: () => {
      enqueueSnackbar('Departamento eliminado', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['departments'] });
      setDeleteDialogOpen(false);
    },
    onError: () => {
      enqueueSnackbar('Error al eliminar', { variant: 'error' });
    },
  });

  const handleOpenForm = useCallback((dept?: Department) => {
    if (dept) {
      setSelectedDept(dept);
      reset({
        code: dept.code,
        name: dept.name,
        description: dept.description || '',
        parent: typeof dept.parent === 'object' ? dept.parent?.id : dept.parent || '',
        manager: typeof dept.manager === 'object' ? dept.manager?.id : dept.manager || '',
        is_active: dept.is_active,
      });
    } else {
      setSelectedDept(null);
      reset();
    }
    setFormDialogOpen(true);
  }, [reset]);

  const handleCloseForm = () => {
    setFormDialogOpen(false);
    setSelectedDept(null);
    reset();
  };

  const columns: GridColDef[] = [
    { field: 'code', headerName: 'Código', width: 100 },
    { field: 'name', headerName: 'Nombre', flex: 1, minWidth: 200 },
    {
      field: 'parent',
      headerName: 'Departamento Padre',
      width: 180,
      valueGetter: (value: any) => typeof value === 'object' ? value?.name : value || '-',
    },
    {
      field: 'manager',
      headerName: 'Jefe',
      width: 180,
      valueGetter: (value: any) => {
        if (typeof value === 'object' && value) {
          return `${value.first_name || ''} ${value.last_name || ''}`.trim() || '-';
        }
        return value || '-';
      },
    },
    {
      field: 'employee_count',
      headerName: 'Empleados',
      width: 100,
      align: 'center',
    },
    {
      field: 'is_active',
      headerName: 'Estado',
      width: 100,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value ? 'Activo' : 'Inactivo'}
          color={params.value ? 'success' : 'default'}
          size="small"
        />
      ),
    },
    {
      field: 'actions',
      headerName: 'Acciones',
      width: 120,
      sortable: false,
      renderCell: (params: GridRenderCellParams<Department>) => (
        <Box>
          <Tooltip title="Editar">
            <IconButton size="small" onClick={() => handleOpenForm(params.row)}>
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Eliminar">
            <IconButton size="small" color="error" onClick={() => {
              setSelectedDept(params.row);
              setDeleteDialogOpen(true);
            }}>
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
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <DeptIcon color="primary" />
          <Typography variant="h4" fontWeight={600}>Departamentos</Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={() => refetch()}>
            Actualizar
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenForm()}>
            Nuevo Departamento
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

      {/* Dialog de Formulario */}
      <Dialog open={formDialogOpen} onClose={handleCloseForm} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit((d) => saveMutation.mutate(d))}>
          <DialogTitle>{selectedDept ? 'Editar Departamento' : 'Nuevo Departamento'}</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={4}>
                <Controller
                  name="code"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Código" fullWidth error={!!errors.code} helperText={errors.code?.message} />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={8}>
                <Controller
                  name="name"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Nombre" fullWidth error={!!errors.name} helperText={errors.name?.message} />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="description"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Descripción" fullWidth multiline rows={2} />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="parent"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Departamento Padre</InputLabel>
                      <Select {...field} label="Departamento Padre">
                        <MenuItem value="">Ninguno</MenuItem>
                        {data?.results?.filter(d => d.id !== selectedDept?.id).map((dept) => (
                          <MenuItem key={dept.id} value={dept.id}>{dept.name}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="manager"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Jefe de Departamento</InputLabel>
                      <Select {...field} label="Jefe de Departamento">
                        <MenuItem value="">Sin asignar</MenuItem>
                        {employees?.results?.map((emp) => (
                          <MenuItem key={emp.id} value={emp.id}>{emp.first_name} {emp.last_name}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseForm} startIcon={<CancelIcon />}>Cancelar</Button>
            <Button type="submit" variant="contained" startIcon={<SaveIcon />} disabled={saveMutation.isPending}>
              {saveMutation.isPending ? 'Guardando...' : 'Guardar'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Dialog de Eliminación */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirmar Eliminación</DialogTitle>
        <DialogContent>
          <DialogContentText>
            ¿Eliminar departamento "{selectedDept?.name}"?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancelar</Button>
          <Button onClick={() => selectedDept && deleteMutation.mutate(selectedDept.id)} color="error" variant="contained">
            Eliminar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default DepartmentListPage;
