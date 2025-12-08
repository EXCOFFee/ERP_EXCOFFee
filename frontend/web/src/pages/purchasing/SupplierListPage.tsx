// ========================================================
// SISTEMA ERP UNIVERSAL - Lista de Proveedores
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
  Rating,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Refresh as RefreshIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import DataTable from '../../components/common/DataTable';
import { purchasingService, Supplier } from '../../services/purchasing.service';
import { useSnackbar } from 'notistack';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const supplierSchema = z.object({
  code: z.string().min(1, 'Código es requerido'),
  business_name: z.string().min(1, 'Razón social es requerida'),
  trade_name: z.string().optional(),
  tax_id: z.string().optional(),
  supplier_type: z.enum(['local', 'international']),
  email: z.string().email('Email inválido').optional().or(z.literal('')),
  phone: z.string().optional(),
  mobile: z.string().optional(),
  address: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  country: z.string().optional(),
  payment_term_days: z.number().min(0),
  is_active: z.boolean(),
});

type SupplierFormData = z.infer<typeof supplierSchema>;

function SupplierListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [formDialogOpen, setFormDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<Supplier | null>(null);

  const { control, handleSubmit, reset, formState: { errors } } = useForm<SupplierFormData>({
    resolver: zodResolver(supplierSchema),
    defaultValues: {
      code: '',
      business_name: '',
      trade_name: '',
      tax_id: '',
      supplier_type: 'local',
      email: '',
      phone: '',
      mobile: '',
      address: '',
      city: '',
      state: '',
      country: '',
      payment_term_days: 30,
      is_active: true,
    },
  });

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['suppliers', page, pageSize],
    queryFn: () => purchasingService.getSuppliers({ page: page + 1, page_size: pageSize }),
  });

  const saveMutation = useMutation({
    mutationFn: (data: SupplierFormData) => {
      if (selectedSupplier) {
        return purchasingService.updateSupplier(selectedSupplier.id, data);
      }
      return purchasingService.createSupplier(data);
    },
    onSuccess: () => {
      enqueueSnackbar(
        selectedSupplier ? 'Proveedor actualizado' : 'Proveedor creado',
        { variant: 'success' }
      );
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
      handleCloseForm();
    },
    onError: () => {
      enqueueSnackbar('Error al guardar el proveedor', { variant: 'error' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => purchasingService.deleteSupplier(id),
    onSuccess: () => {
      enqueueSnackbar('Proveedor eliminado', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
      setDeleteDialogOpen(false);
    },
    onError: () => {
      enqueueSnackbar('Error al eliminar', { variant: 'error' });
    },
  });

  const handleOpenForm = useCallback((supplier?: Supplier) => {
    if (supplier) {
      setSelectedSupplier(supplier);
      reset({
        code: supplier.code,
        business_name: supplier.business_name,
        trade_name: supplier.trade_name || '',
        tax_id: supplier.tax_id || '',
        supplier_type: supplier.supplier_type as 'local' | 'international',
        email: supplier.email || '',
        phone: supplier.phone || '',
        mobile: supplier.mobile || '',
        address: supplier.address || '',
        city: supplier.city || '',
        state: supplier.state || '',
        country: supplier.country || '',
        payment_term_days: supplier.payment_term_days || 30,
        is_active: supplier.is_active,
      });
    } else {
      setSelectedSupplier(null);
      reset();
    }
    setFormDialogOpen(true);
  }, [reset]);

  const handleCloseForm = () => {
    setFormDialogOpen(false);
    setSelectedSupplier(null);
    reset();
  };

  const columns: GridColDef[] = [
    { field: 'code', headerName: 'Código', width: 100 },
    { field: 'business_name', headerName: 'Razón Social', flex: 1, minWidth: 200 },
    { field: 'tax_id', headerName: 'RUC', width: 120 },
    {
      field: 'supplier_type',
      headerName: 'Tipo',
      width: 110,
      valueFormatter: (value: string) => value === 'local' ? 'Local' : 'Internacional',
    },
    { field: 'email', headerName: 'Email', width: 180 },
    { field: 'phone', headerName: 'Teléfono', width: 120 },
    {
      field: 'rating',
      headerName: 'Calificación',
      width: 140,
      renderCell: (params: GridRenderCellParams) => (
        <Rating value={params.value || 0} readOnly size="small" />
      ),
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
      width: 150,
      sortable: false,
      renderCell: (params: GridRenderCellParams<Supplier>) => (
        <Box>
          <Tooltip title="Ver">
            <IconButton size="small" onClick={() => navigate(`/purchasing/suppliers/${params.row.id}`)}>
              <ViewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Editar">
            <IconButton size="small" onClick={() => handleOpenForm(params.row)}>
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Eliminar">
            <IconButton size="small" color="error" onClick={() => {
              setSelectedSupplier(params.row);
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
        <Typography variant="h4" fontWeight={600}>Proveedores</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={() => refetch()}>
            Actualizar
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenForm()}>
            Nuevo Proveedor
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
      <Dialog open={formDialogOpen} onClose={handleCloseForm} maxWidth="md" fullWidth>
        <form onSubmit={handleSubmit((d) => saveMutation.mutate(d))}>
          <DialogTitle>{selectedSupplier ? 'Editar Proveedor' : 'Nuevo Proveedor'}</DialogTitle>
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
              <Grid item xs={12} sm={4}>
                <Controller
                  name="tax_id"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="RUC" fullWidth />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <Controller
                  name="supplier_type"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Tipo</InputLabel>
                      <Select {...field} label="Tipo">
                        <MenuItem value="local">Local</MenuItem>
                        <MenuItem value="international">Internacional</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="business_name"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Razón Social" fullWidth error={!!errors.business_name} helperText={errors.business_name?.message} />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="trade_name"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Nombre Comercial" fullWidth />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <Controller
                  name="email"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Email" type="email" fullWidth error={!!errors.email} helperText={errors.email?.message} />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <Controller
                  name="phone"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Teléfono" fullWidth />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <Controller
                  name="payment_term_days"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Días Crédito" type="number" fullWidth onChange={(e) => field.onChange(parseInt(e.target.value) || 0)} />
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
              <Grid item xs={12} sm={4}>
                <Controller
                  name="city"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Ciudad" fullWidth />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <Controller
                  name="state"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Estado" fullWidth />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <Controller
                  name="country"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="País" fullWidth />
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
            ¿Eliminar proveedor "{selectedSupplier?.business_name}"?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancelar</Button>
          <Button onClick={() => selectedSupplier && deleteMutation.mutate(selectedSupplier.id)} color="error" variant="contained" disabled={deleteMutation.isPending}>
            Eliminar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default SupplierListPage;
