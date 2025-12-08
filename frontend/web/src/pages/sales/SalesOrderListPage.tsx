// ========================================================
// SISTEMA ERP UNIVERSAL - Lista de Pedidos de Venta
// ========================================================

import { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Chip,
  Tooltip,
  Tabs,
  Tab,
  Paper,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Refresh as RefreshIcon,
  Print as PrintIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import DataTable from '../../components/common/DataTable';
import { salesService, SalesOrder } from '../../services/sales.service';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const statusConfig: Record<string, { label: string; color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' }> = {
  draft: { label: 'Borrador', color: 'default' },
  confirmed: { label: 'Confirmado', color: 'primary' },
  processing: { label: 'Procesando', color: 'info' },
  shipped: { label: 'Enviado', color: 'secondary' },
  delivered: { label: 'Entregado', color: 'success' },
  cancelled: { label: 'Cancelado', color: 'error' },
};

function SalesOrderListPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [tabValue, setTabValue] = useState(0);

  const getStatusFilter = () => {
    switch (tabValue) {
      case 1: return 'draft';
      case 2: return 'confirmed';
      case 3: return 'processing';
      case 4: return 'delivered';
      default: return undefined;
    }
  };

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['sales-orders', page, pageSize, tabValue],
    queryFn: () => salesService.getSalesOrders({
      page: page + 1,
      page_size: pageSize,
      status: getStatusFilter(),
    }),
  });

  const columns: GridColDef[] = [
    { field: 'order_number', headerName: 'Nº Pedido', width: 130 },
    {
      field: 'order_date',
      headerName: 'Fecha',
      width: 120,
      valueFormatter: (value: string) => {
        try {
          return format(new Date(value), 'dd/MM/yyyy', { locale: es });
        } catch {
          return value;
        }
      },
    },
    {
      field: 'customer',
      headerName: 'Cliente',
      flex: 1,
      minWidth: 200,
      valueGetter: (value: any) => typeof value === 'object' ? value?.business_name : value,
    },
    {
      field: 'status',
      headerName: 'Estado',
      width: 130,
      renderCell: (params: GridRenderCellParams) => {
        const config = statusConfig[params.value] || { label: params.value, color: 'default' };
        return <Chip label={config.label} color={config.color} size="small" />;
      },
    },
    {
      field: 'subtotal',
      headerName: 'Subtotal',
      width: 110,
      valueFormatter: (value: number) => `$${value?.toFixed(2) || '0.00'}`,
    },
    {
      field: 'tax_amount',
      headerName: 'Impuesto',
      width: 100,
      valueFormatter: (value: number) => `$${value?.toFixed(2) || '0.00'}`,
    },
    {
      field: 'total',
      headerName: 'Total',
      width: 120,
      renderCell: (params: GridRenderCellParams) => (
        <Typography fontWeight={600}>${params.value?.toFixed(2) || '0.00'}</Typography>
      ),
    },
    {
      field: 'actions',
      headerName: 'Acciones',
      width: 150,
      sortable: false,
      renderCell: (params: GridRenderCellParams<SalesOrder>) => (
        <Box>
          <Tooltip title="Ver detalle">
            <IconButton
              size="small"
              onClick={() => navigate(`/sales/orders/${params.row.id}`)}
            >
              <ViewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          {params.row.status === 'draft' && (
            <Tooltip title="Editar">
              <IconButton
                size="small"
                onClick={() => navigate(`/sales/orders/${params.row.id}/edit`)}
              >
                <EditIcon fontSize="small" />
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
        <Typography variant="h4" fontWeight={600}>Pedidos de Venta</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={() => refetch()}>
            Actualizar
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/sales/orders/new')}
          >
            Nuevo Pedido
          </Button>
        </Box>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, v) => { setTabValue(v); setPage(0); }}>
          <Tab label="Todos" />
          <Tab label="Borradores" />
          <Tab label="Confirmados" />
          <Tab label="Procesando" />
          <Tab label="Entregados" />
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

export default SalesOrderListPage;
