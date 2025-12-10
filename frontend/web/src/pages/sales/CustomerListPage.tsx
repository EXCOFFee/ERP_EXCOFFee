// ========================================================
// SISTEMA ERP UNIVERSAL - Lista de Clientes
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
  Visibility as ViewIcon,
  Refresh as RefreshIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import DataTable from '../../components/common/DataTable';
import { salesService, Customer } from '../../services/sales.service';
import { useSnackbar } from 'notistack';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const customerSchema = z.object({
  code: z.string().min(1, 'Código es requerido'),
  business_name: z.string().min(1, 'Razón social es requerida'),
  trade_name: z.string().optional(),
  tax_id: z.string().optional(),
  customer_type: z.enum(['individual', 'company']),
  email: z.string().email('Email inválido').optional().or(z.literal('')),
  phone: z.string().optional(),
  mobile: z.string().optional(),
  address: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  country: z.string().optional(),
  credit_limit: z.number().min(0),
  payment_term_days: z.number().min(0),
  is_active: z.boolean(),
});

type CustomerFormData = z.infer<typeof customerSchema>;

function CustomerListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [formDialogOpen, setFormDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);

  const { control, handleSubmit, reset, formState: { errors } } = useForm<CustomerFormData>({
    resolver: zodResolver(customerSchema),
    defaultValues: {
      code: '',
      business_name: '',
      trade_name: '',
      tax_id: '',
      customer_type: 'individual',
      email: '',
      phone: '',
      mobile: '',
      address: '',
      city: '',
      state: '',
      country: '',
      credit_limit: 0,
      payment_term_days: 30,
      is_active: true,
    },
  });

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['customers', page, pageSize],
    queryFn: () => salesService.getCustomers({ page: page + 1, page_size: pageSize }),
  });

  const { data: customerGroups } = useQuery({
    queryKey: ['customer-groups'],
    queryFn: () => salesService.getCustomerGroups(),
  });

  const saveMutation = useMutation({
    mutationFn: (data: CustomerFormData) => {
      if (selectedCustomer) {
        return salesService.updateCustomer(selectedCustomer.id, data);
      }
      return salesService.createCustomer(data);
    },
    onSuccess: () => {
      enqueueSnackbar(
        selectedCustomer ? 'Cliente actualizado correctamente' : 'Cliente creado correctamente',
        { variant: 'success' }
      );
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      handleCloseForm();
    },
    onError: () => {
      enqueueSnackbar('Error al guardar el cliente', { variant: 'error' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => salesService.deleteCustomer(id),
    onSuccess: () => {
      enqueueSnackbar('Cliente eliminado correctamente', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      setDeleteDialogOpen(false);
      setSelectedCustomer(null);
    },
    onError: () => {
      enqueueSnackbar('Error al eliminar el cliente', { variant: 'error' });
    },
  });

  const handleOpenForm = useCallback((customer?: Customer) => {
    if (customer) {
      setSelectedCustomer(customer);
      reset({
        code: customer.code,
        business_name: customer.business_name,
        trade_name: customer.trade_name || '',
        tax_id: customer.tax_id || '',
        customer_type: customer.customer_type as 'individual' | 'company',
        email: customer.email || '',
        phone: customer.phone || '',
        mobile: customer.mobile || '',
        address: customer.address || '',
        city: customer.city || '',
        state: customer.state || '',
        country: customer.country || '',
        credit_limit: customer.credit_limit || 0,
        payment_term_days: customer.payment_term_days || 30,
        is_active: customer.is_active,
      });
    } else {
      setSelectedCustomer(null);
      reset({
        code: '',
        business_name: '',
        trade_name: '',
        tax_id: '',
        customer_type: 'individual',
        email: '',
        phone: '',
        mobile: '',
        address: '',
        city: '',
        state: '',
        country: '',
        credit_limit: 0,
        payment_term_days: 30,
        is_active: true,
      });
    }
    setFormDialogOpen(true);
  }, [reset]);

  const handleCloseForm = () => {
    setFormDialogOpen(false);
    setSelectedCustomer(null);
    reset();
  };

  const handleDelete = useCallback((customer: Customer) => {
    setSelectedCustomer(customer);
    setDeleteDialogOpen(true);
  }, []);

  const onSubmit = (data: CustomerFormData) => {
    saveMutation.mutate(data);
  };

  const columns: GridColDef[] = [
    { field: 'code', headerName: 'Código', width: 100 },
    { field: 'business_name', headerName: 'Razón Social', flex: 1, minWidth: 200 },
    { field: 'tax_id', headerName: 'RUC/DNI', width: 120 },
    {
      field: 'customer_type',
      headerName: 'Tipo',
      width: 100,
      valueFormatter: (value: string) => value === 'company' ? 'Empresa' : 'Persona',
    },
    { field: 'email', headerName: 'Email', width: 180 },
    { field: 'phone', headerName: 'Teléfono', width: 120 },
    { field: 'city', headerName: 'Ciudad', width: 120 },
    {
      field: 'credit_limit',
      headerName: 'Límite Crédito',
      width: 120,
      valueFormatter: (value: any) => {
        const num = typeof value === 'number' ? value : parseFloat(value) || 0;
        return `$${num.toFixed(2)}`;
      },
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
      renderCell: (params: GridRenderCellParams<Customer>) => (
        <Box>
          <Tooltip title="Ver detalle">
            <IconButton
              size="small"
              onClick={() => navigate(`/sales/customers/${params.row.id}`)}
            >
              <ViewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
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
        <Typography variant="h4" fontWeight={600}>Clientes</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={() => refetch()}>
            Actualizar
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenForm()}>
            Nuevo Cliente
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
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>
            {selectedCustomer ? 'Editar Cliente' : 'Nuevo Cliente'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={4}>
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
              <Grid item xs={12} sm={4}>
                <Controller
                  name="tax_id"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="RUC/DNI" fullWidth />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <Controller
                  name="customer_type"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Tipo de Cliente</InputLabel>
                      <Select {...field} label="Tipo de Cliente">
                        <MenuItem value="individual">Persona Natural</MenuItem>
                        <MenuItem value="company">Empresa</MenuItem>
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
                    <TextField
                      {...field}
                      label="Razón Social"
                      fullWidth
                      error={!!errors.business_name}
                      helperText={errors.business_name?.message}
                    />
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
                    <TextField
                      {...field}
                      label="Email"
                      type="email"
                      fullWidth
                      error={!!errors.email}
                      helperText={errors.email?.message}
                    />
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
                  name="mobile"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Celular" fullWidth />
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
                    <TextField {...field} label="Estado/Provincia" fullWidth />
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
              <Grid item xs={12} sm={6}>
                <Controller
                  name="credit_limit"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Límite de Crédito"
                      type="number"
                      fullWidth
                      onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="payment_term_days"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Días de Crédito"
                      type="number"
                      fullWidth
                      onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                    />
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
            ¿Está seguro que desea eliminar el cliente "{selectedCustomer?.business_name}"?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancelar</Button>
          <Button
            onClick={() => selectedCustomer && deleteMutation.mutate(selectedCustomer.id)}
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

export default CustomerListPage;
