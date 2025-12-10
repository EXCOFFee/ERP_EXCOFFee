// ========================================================
// SISTEMA ERP UNIVERSAL - Lista de Productos
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
import { inventoryService, Product } from '../../services/inventory.service';
import { useSnackbar } from 'notistack';

function ProductListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  // Query para obtener productos
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['products', page, pageSize],
    queryFn: () => inventoryService.getProducts({ page: page + 1, page_size: pageSize }),
  });

  // Mutation para eliminar producto
  const deleteMutation = useMutation({
    mutationFn: (id: string) => inventoryService.deleteProduct(id),
    onSuccess: () => {
      enqueueSnackbar('Producto eliminado correctamente', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['products'] });
      setDeleteDialogOpen(false);
      setSelectedProduct(null);
    },
    onError: () => {
      enqueueSnackbar('Error al eliminar el producto', { variant: 'error' });
    },
  });

  const handleDelete = useCallback((product: Product) => {
    setSelectedProduct(product);
    setDeleteDialogOpen(true);
  }, []);

  const confirmDelete = () => {
    if (selectedProduct) {
      deleteMutation.mutate(selectedProduct.id);
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'image',
      headerName: '',
      width: 60,
      sortable: false,
      renderCell: (params: GridRenderCellParams) => (
        <Avatar
          src={params.value}
          variant="rounded"
          sx={{ width: 40, height: 40 }}
        >
          {params.row.name?.charAt(0)}
        </Avatar>
      ),
    },
    { field: 'sku', headerName: 'SKU', width: 120 },
    { field: 'name', headerName: 'Nombre', flex: 1, minWidth: 200 },
    {
      field: 'category',
      headerName: 'Categoría',
      width: 150,
      valueGetter: (value: any) => value?.name || '-',
    },
    {
      field: 'brand',
      headerName: 'Marca',
      width: 120,
      valueGetter: (value: any) => value?.name || '-',
    },
    {
      field: 'cost_price',
      headerName: 'Costo',
      width: 100,
      valueFormatter: (value: any) => {
        const num = typeof value === 'number' ? value : parseFloat(value) || 0;
        return `$${num.toFixed(2)}`;
      },
    },
    {
      field: 'sale_price',
      headerName: 'Precio',
      width: 100,
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
      renderCell: (params: GridRenderCellParams<Product>) => (
        <Box>
          <Tooltip title="Ver detalle">
            <IconButton
              size="small"
              onClick={() => navigate(`/inventory/products/${params.row.id}`)}
            >
              <ViewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Editar">
            <IconButton
              size="small"
              onClick={() => navigate(`/inventory/products/${params.row.id}/edit`)}
            >
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Eliminar">
            <IconButton
              size="small"
              color="error"
              onClick={() => handleDelete(params.row)}
            >
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
          Productos
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => refetch()}
          >
            Actualizar
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/inventory/products/new')}
          >
            Nuevo Producto
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

      {/* Dialog de confirmación de eliminación */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirmar Eliminación</DialogTitle>
        <DialogContent>
          <DialogContentText>
            ¿Está seguro que desea eliminar el producto "{selectedProduct?.name}"?
            Esta acción no se puede deshacer.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancelar</Button>
          <Button
            onClick={confirmDelete}
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

export default ProductListPage;
