// ========================================================
// SISTEMA ERP UNIVERSAL - Plan de Cuentas
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
  FormControlLabel,
  Switch,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  AccountTree as TreeIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import DataTable from '../../components/common/DataTable';
import { financeService, Account } from '../../services/finance.service';
import { useSnackbar } from 'notistack';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const accountSchema = z.object({
  code: z.string().min(1, 'Código es requerido'),
  name: z.string().min(1, 'Nombre es requerido'),
  account_type: z.string().min(1, 'Tipo es requerido'),
  parent: z.string().optional(),
  description: z.string().optional(),
  is_active: z.boolean(),
  allows_transactions: z.boolean(),
});

type AccountFormData = z.infer<typeof accountSchema>;

function AccountListPage() {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(25);
  const [formDialogOpen, setFormDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);

  const { control, handleSubmit, reset, formState: { errors } } = useForm<AccountFormData>({
    resolver: zodResolver(accountSchema),
    defaultValues: {
      code: '',
      name: '',
      account_type: '',
      parent: '',
      description: '',
      is_active: true,
      allows_transactions: true,
    },
  });

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['accounts', page, pageSize],
    queryFn: () => financeService.getAccounts({ page: page + 1, page_size: pageSize }),
  });

  const { data: accountTypes } = useQuery({
    queryKey: ['account-types'],
    queryFn: () => financeService.getAccountTypes(),
  });

  const saveMutation = useMutation({
    mutationFn: (data: AccountFormData) => {
      if (selectedAccount) {
        return financeService.updateAccount(selectedAccount.id, data);
      }
      return financeService.createAccount(data);
    },
    onSuccess: () => {
      enqueueSnackbar(selectedAccount ? 'Cuenta actualizada' : 'Cuenta creada', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      handleCloseForm();
    },
    onError: () => {
      enqueueSnackbar('Error al guardar', { variant: 'error' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => financeService.deleteAccount(id),
    onSuccess: () => {
      enqueueSnackbar('Cuenta eliminada', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      setDeleteDialogOpen(false);
    },
    onError: () => {
      enqueueSnackbar('Error al eliminar', { variant: 'error' });
    },
  });

  const handleOpenForm = useCallback((account?: Account) => {
    if (account) {
      setSelectedAccount(account);
      reset({
        code: account.code,
        name: account.name,
        account_type: typeof account.account_type === 'object' ? account.account_type?.id : account.account_type || '',
        parent: typeof account.parent === 'object' ? account.parent?.id : account.parent || '',
        description: account.description || '',
        is_active: account.is_active,
        allows_transactions: account.allows_transactions,
      });
    } else {
      setSelectedAccount(null);
      reset();
    }
    setFormDialogOpen(true);
  }, [reset]);

  const handleCloseForm = () => {
    setFormDialogOpen(false);
    setSelectedAccount(null);
    reset();
  };

  const getAccountTypeColor = (type: string) => {
    switch (type) {
      case 'asset': return 'primary';
      case 'liability': return 'error';
      case 'equity': return 'secondary';
      case 'income': return 'success';
      case 'expense': return 'warning';
      default: return 'default';
    }
  };

  const accountTypeLabels: Record<string, string> = {
    asset: 'Activo',
    liability: 'Pasivo',
    equity: 'Patrimonio',
    income: 'Ingreso',
    expense: 'Gasto',
  };

  const columns: GridColDef[] = [
    { field: 'code', headerName: 'Código', width: 130 },
    { field: 'name', headerName: 'Nombre', flex: 1, minWidth: 250 },
    {
      field: 'account_type',
      headerName: 'Tipo',
      width: 130,
      renderCell: (params: GridRenderCellParams) => {
        const typeName = typeof params.value === 'object' ? params.value?.name : params.value;
        return (
          <Chip
            label={accountTypeLabels[typeName] || typeName}
            color={getAccountTypeColor(typeName) as any}
            size="small"
          />
        );
      },
    },
    {
      field: 'parent',
      headerName: 'Cuenta Padre',
      width: 150,
      valueGetter: (value: any) => typeof value === 'object' ? value?.name : value || '-',
    },
    {
      field: 'level',
      headerName: 'Nivel',
      width: 80,
      align: 'center',
    },
    {
      field: 'balance',
      headerName: 'Saldo',
      width: 130,
      valueFormatter: (value: any) => {
        const num = typeof value === 'number' ? value : parseFloat(value) || 0;
        return `$${num.toFixed(2)}`;
      },
      align: 'right',
    },
    {
      field: 'allows_transactions',
      headerName: 'Movimientos',
      width: 110,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value ? 'Sí' : 'No'}
          color={params.value ? 'success' : 'default'}
          size="small"
          variant="outlined"
        />
      ),
    },
    {
      field: 'is_active',
      headerName: 'Estado',
      width: 100,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value ? 'Activa' : 'Inactiva'}
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
      renderCell: (params: GridRenderCellParams<Account>) => (
        <Box>
          <Tooltip title="Editar">
            <IconButton size="small" onClick={() => handleOpenForm(params.row)}>
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Eliminar">
            <IconButton size="small" color="error" onClick={() => {
              setSelectedAccount(params.row);
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
          <TreeIcon color="primary" />
          <Typography variant="h4" fontWeight={600}>Plan de Cuentas</Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={() => refetch()}>
            Actualizar
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenForm()}>
            Nueva Cuenta
          </Button>
        </Box>
      </Box>

      <DataTable
        rows={data?.results || []}
        columns={columns}
        loading={isLoading}
        rowCount={data?.count || 0}
        paginationMode="server"
        pageSize={25}
        onPaginationChange={(model) => {
          setPage(model.page);
          setPageSize(model.pageSize);
        }}
        getRowId={(row) => row.id}
      />

      {/* Dialog de Formulario */}
      <Dialog open={formDialogOpen} onClose={handleCloseForm} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit((d) => saveMutation.mutate(d))}>
          <DialogTitle>{selectedAccount ? 'Editar Cuenta' : 'Nueva Cuenta'}</DialogTitle>
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
              <Grid item xs={12} sm={6}>
                <Controller
                  name="account_type"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.account_type}>
                      <InputLabel>Tipo de Cuenta</InputLabel>
                      <Select {...field} label="Tipo de Cuenta">
                        {accountTypes?.results?.map((type) => (
                          <MenuItem key={type.id} value={type.id}>{type.name}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="parent"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Cuenta Padre</InputLabel>
                      <Select {...field} label="Cuenta Padre">
                        <MenuItem value="">Sin padre</MenuItem>
                        {data?.results?.filter(a => !a.allows_transactions).map((acc) => (
                          <MenuItem key={acc.id} value={acc.id}>{acc.code} - {acc.name}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
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
                  name="allows_transactions"
                  control={control}
                  render={({ field }) => (
                    <FormControlLabel
                      control={<Switch checked={field.value} onChange={field.onChange} />}
                      label="Permite Movimientos"
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="is_active"
                  control={control}
                  render={({ field }) => (
                    <FormControlLabel
                      control={<Switch checked={field.value} onChange={field.onChange} />}
                      label="Activa"
                    />
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
            ¿Eliminar cuenta "{selectedAccount?.code} - {selectedAccount?.name}"?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancelar</Button>
          <Button onClick={() => selectedAccount && deleteMutation.mutate(selectedAccount.id)} color="error" variant="contained">
            Eliminar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default AccountListPage;
