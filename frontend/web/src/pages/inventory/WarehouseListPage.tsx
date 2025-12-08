// ========================================================
// SISTEMA ERP UNIVERSAL - Lista de Almacenes
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
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import DataTable from '../../components/common/DataTable';
import { inventoryService, Warehouse } from '../../services/inventory.service';
import { useSnackbar } from 'notistack';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const warehouseSchema = z.object({
  code: z.string().min(1, 'Código es requerido'),
  name: z.string().min(1, 'Nombre es requerido'),
  address: z.string().optional(),
  city: z.string().optional(),
  manager: z.string().optional(),
  is_active: z.boolean(),
});

type WarehouseFormData = z.infer<typeof warehouseSchema>;

function WarehouseListPage() {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [formDialogOpen, setFormDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedWarehouse, setSelectedWarehouse] = useState<Warehouse | null>(null);

  const { control, handleSubmit, reset, formState: { errors } } = useForm<WarehouseFormData>({
    resolver: zodResolver(warehouseSchema),
    defaultValues: {
      code: '',
      name: '',
      address: '',
      city: '',
      manager: '',
      is_active: true,
    },
  });

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['warehouses', page, pageSize],
    queryFn: () => inventoryService.getWarehouses({ page: page + 1, page_size: pageSize }),
  });

  const saveMutation = useMutation({
    mutationFn: (data: WarehouseFormData) => {
      if (selectedWarehouse) {
        return inventoryService.updateWarehouse(selectedWarehouse.id, data);
      }
      return inventoryService.createWarehouse(data);
    },
    onSuccess: () => {
      enqueueSnackbar(
        selectedWarehouse ? 'Almacén actualizado correctamente' : 'Almacén creado correctamente',
        { variant: 'success' }
      );
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      handleCloseForm();
    },
    onError: () => {
      enqueueSnackbar('Error al guardar el almacén', { variant: 'error' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => inventoryService.deleteWarehouse(id),
    onSuccess: () => {
      enqueueSnackbar('Almacén eliminado correctamente', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      setDeleteDialogOpen(false);
      setSelectedWarehouse(null);
    },
    onError: () => {
      enqueueSnackbar('Error al eliminar el almacén', { variant: 'error' });
    },
  });

  const handleOpenForm = useCallback((warehouse?: Warehouse) => {
    if (warehouse) {
      setSelectedWarehouse(warehouse);
      reset({
        code: warehouse.code,
        name: warehouse.name,
        address: warehouse.address || '',
        city: warehouse.city || '',
        manager: warehouse.manager || '',
        is_active: warehouse.is_active,
      });
    } else {
      setSelectedWarehouse(null);
      reset({
        code: '',
        name: '',
        address: '',
        city: '',
        manager: '',
        is_active: true,
      });
    }
    setFormDialogOpen(true);
  }, [reset]);

  const handleCloseForm = () => {
    setFormDialogOpen(false);
    setSelectedWarehouse(null);
    reset();
  };

  const handleDelete = useCallback((warehouse: Warehouse) => {
    setSelectedWarehouse(warehouse);
    setDeleteDialogOpen(true);
  }, []);

  const onSubmit = (data: WarehouseFormData) => {
    saveMutation.mutate(data);
  };

  const columns: GridColDef[] = [
    { field: 'code', headerName: 'Código', width: 120 },
    { field: 'name', headerName: 'Nombre', flex: 1, minWidth: 200 },
    { field: 'city', headerName: 'Ciudad', width: 150 },
    { field: 'manager', headerName: 'Encargado', width: 150 },
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
      renderCell: (params: GridRenderCellParams<Warehouse>) => (
        <Box>
          <Tooltip title="Editar">
            <IconButton size="small" onClick={() => handleOpenForm(params.row)}>
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
        <Typography variant="h4" fontWeight={600}>
          Almacenes
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={() => refetch()}>
            Actualizar
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenForm()}>
            Nuevo Almacén
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
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>
            {selectedWarehouse ? 'Editar Almacén' : 'Nuevo Almacén'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="code"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Código"
                      fullWidth
                      error={!!errors.code}
                      helperText={errors.code?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="name"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Nombre"
                      fullWidth
                      error={!!errors.name}
                      helperText={errors.name?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="address"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Dirección" fullWidth />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="city"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Ciudad" fullWidth />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="manager"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Encargado" fullWidth />
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseForm} startIcon={<CancelIcon />}>
              Cancelar
            </Button>
            <Button
              type="submit"
              variant="contained"
              startIcon={<SaveIcon />}
              disabled={saveMutation.isPending}
            >
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
            ¿Está seguro que desea eliminar el almacén "{selectedWarehouse?.name}"?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancelar</Button>
          <Button
            onClick={() => selectedWarehouse && deleteMutation.mutate(selectedWarehouse.id)}
            color="error"
            variant="contained"
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? 'Eliminando...' : 'Eliminar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default WarehouseListPage;
