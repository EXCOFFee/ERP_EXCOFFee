// ========================================================
// SISTEMA ERP UNIVERSAL - Movimientos de Stock
// ========================================================

import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { Add as AddIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import DataTable from '../../components/common/DataTable';
import { inventoryService, StockMovement } from '../../services/inventory.service';
import { useSnackbar } from 'notistack';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const movementSchema = z.object({
  product: z.string().min(1, 'Producto es requerido'),
  warehouse: z.string().min(1, 'Almacén es requerido'),
  movement_type: z.enum(['in', 'out', 'adjustment', 'transfer']),
  quantity: z.number().min(1, 'Cantidad debe ser mayor a 0'),
  reference: z.string().optional(),
  notes: z.string().optional(),
});

type MovementFormData = z.infer<typeof movementSchema>;

function StockMovementsPage() {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [tabValue, setTabValue] = useState(0);
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [formDialogOpen, setFormDialogOpen] = useState(false);

  const { control, handleSubmit, reset, formState: { errors } } = useForm<MovementFormData>({
    resolver: zodResolver(movementSchema),
    defaultValues: {
      product: '',
      warehouse: '',
      movement_type: 'in',
      quantity: 1,
      reference: '',
      notes: '',
    },
  });

  const movementTypes: Record<string, string> = {
    in: 'Entrada',
    out: 'Salida',
    adjustment: 'Ajuste',
    transfer: 'Transferencia',
  };

  const getFilterType = () => {
    switch (tabValue) {
      case 1: return 'in';
      case 2: return 'out';
      case 3: return 'transfer';
      case 4: return 'adjustment';
      default: return undefined;
    }
  };

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['stock-movements', page, pageSize, tabValue],
    queryFn: () => inventoryService.getStockMovements({
      page: page + 1,
      page_size: pageSize,
      movement_type: getFilterType(),
    }),
  });

  const { data: products } = useQuery({
    queryKey: ['products-list'],
    queryFn: () => inventoryService.getProducts({ page_size: 100 }),
  });

  const { data: warehouses } = useQuery({
    queryKey: ['warehouses-list'],
    queryFn: () => inventoryService.getWarehouses({ page_size: 100 }),
  });

  const createMutation = useMutation({
    mutationFn: (data: MovementFormData) => inventoryService.createStockMovement(data),
    onSuccess: () => {
      enqueueSnackbar('Movimiento registrado correctamente', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['stock-movements'] });
      setFormDialogOpen(false);
      reset();
    },
    onError: () => {
      enqueueSnackbar('Error al registrar el movimiento', { variant: 'error' });
    },
  });

  const onSubmit = (data: MovementFormData) => {
    createMutation.mutate(data);
  };

  const getMovementColor = (type: string) => {
    switch (type) {
      case 'in': return 'success';
      case 'out': return 'error';
      case 'adjustment': return 'warning';
      case 'transfer': return 'info';
      default: return 'default';
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'created_at',
      headerName: 'Fecha',
      width: 150,
      valueFormatter: (value: string) => {
        try {
          return format(new Date(value), 'dd/MM/yyyy HH:mm', { locale: es });
        } catch {
          return value;
        }
      },
    },
    {
      field: 'movement_type',
      headerName: 'Tipo',
      width: 130,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={movementTypes[params.value] || params.value}
          color={getMovementColor(params.value) as any}
          size="small"
        />
      ),
    },
    {
      field: 'product',
      headerName: 'Producto',
      flex: 1,
      minWidth: 200,
      valueGetter: (value: any) => {
        if (typeof value === 'object') return value?.name || '-';
        const product = products?.results?.find(p => p.id === value);
        return product?.name || value;
      },
    },
    {
      field: 'warehouse',
      headerName: 'Almacén',
      width: 150,
      valueGetter: (value: any) => {
        if (typeof value === 'object') return value?.name || '-';
        const warehouse = warehouses?.results?.find(w => w.id === value);
        return warehouse?.name || value;
      },
    },
    {
      field: 'quantity',
      headerName: 'Cantidad',
      width: 100,
      renderCell: (params: GridRenderCellParams) => {
        const isOut = params.row.movement_type === 'out';
        return (
          <Typography
            color={isOut ? 'error.main' : 'success.main'}
            fontWeight={600}
          >
            {isOut ? '-' : '+'}{params.value}
          </Typography>
        );
      },
    },
    { field: 'reference', headerName: 'Referencia', width: 150 },
    { field: 'notes', headerName: 'Notas', flex: 1, minWidth: 150 },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight={600}>
          Movimientos de Inventario
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={() => refetch()}>
            Actualizar
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setFormDialogOpen(true)}
          >
            Nuevo Movimiento
          </Button>
        </Box>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, v) => { setTabValue(v); setPage(0); }}>
          <Tab label="Todos" />
          <Tab label="Entradas" />
          <Tab label="Salidas" />
          <Tab label="Transferencias" />
          <Tab label="Ajustes" />
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

      {/* Dialog de nuevo movimiento */}
      <Dialog open={formDialogOpen} onClose={() => setFormDialogOpen(false)} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>Nuevo Movimiento de Stock</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <Controller
                  name="product"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.product}>
                      <InputLabel>Producto</InputLabel>
                      <Select {...field} label="Producto">
                        {products?.results?.map((p) => (
                          <MenuItem key={p.id} value={p.id}>{p.name}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="warehouse"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth error={!!errors.warehouse}>
                      <InputLabel>Almacén</InputLabel>
                      <Select {...field} label="Almacén">
                        {warehouses?.results?.map((w) => (
                          <MenuItem key={w.id} value={w.id}>{w.name}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="movement_type"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Tipo de Movimiento</InputLabel>
                      <Select {...field} label="Tipo de Movimiento">
                        <MenuItem value="in">Entrada</MenuItem>
                        <MenuItem value="out">Salida</MenuItem>
                        <MenuItem value="adjustment">Ajuste</MenuItem>
                        <MenuItem value="transfer">Transferencia</MenuItem>
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="quantity"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Cantidad"
                      type="number"
                      fullWidth
                      onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                      error={!!errors.quantity}
                      helperText={errors.quantity?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="reference"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Referencia" fullWidth />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="notes"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} label="Notas" fullWidth multiline rows={2} />
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setFormDialogOpen(false)}>Cancelar</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={createMutation.isPending}
            >
              {createMutation.isPending ? 'Guardando...' : 'Registrar'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
}

export default StockMovementsPage;
