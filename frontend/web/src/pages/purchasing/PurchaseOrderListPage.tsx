// ========================================================
// SISTEMA ERP UNIVERSAL - Lista de Órdenes de Compra
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
  LocalShipping as ReceiveIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import DataTable from '../../components/common/DataTable';
import { purchasingService, PurchaseOrder } from '../../services/purchasing.service';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const statusConfig: Record<string, { label: string; color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' }> = {
  draft: { label: 'Borrador', color: 'default' },
  pending: { label: 'Pendiente', color: 'warning' },
  approved: { label: 'Aprobada', color: 'primary' },
  sent: { label: 'Enviada', color: 'info' },
  partial: { label: 'Recep. Parcial', color: 'secondary' },
  received: { label: 'Recibida', color: 'success' },
  cancelled: { label: 'Cancelada', color: 'error' },
};

function PurchaseOrderListPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [tabValue, setTabValue] = useState(0);

  const getStatusFilter = () => {
    switch (tabValue) {
      case 1: return 'draft';
      case 2: return 'approved';
      case 3: return 'sent';
      case 4: return 'received';
      default: return undefined;
    }
  };

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['purchase-orders', page, pageSize, tabValue],
    queryFn: () => purchasingService.getPurchaseOrders({
      page: page + 1,
      page_size: pageSize,
      status: getStatusFilter(),
    }),
  });

  const columns: GridColDef[] = [
    { field: 'order_number', headerName: 'Nº Orden', width: 130 },
    {
      field: 'order_date',
      headerName: 'Fecha',
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
      field: 'supplier',
      headerName: 'Proveedor',
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
      field: 'expected_date',
      headerName: 'Fecha Esperada',
      width: 120,
      valueFormatter: (value: string) => {
        try {
          return value ? format(new Date(value), 'dd/MM/yyyy', { locale: es }) : '-';
        } catch {
          return value || '-';
        }
      },
    },
    {
      field: 'subtotal',
      headerName: 'Subtotal',
      width: 110,
      valueFormatter: (value: any) => {
        const num = typeof value === 'number' ? value : parseFloat(value) || 0;
        return `$${num.toFixed(2)}`;
      },
    },
    {
      field: 'total',
      headerName: 'Total',
      width: 120,
      renderCell: (params: GridRenderCellParams) => {
        const value = params.value;
        const num = typeof value === 'number' ? value : parseFloat(value) || 0;
        return <Typography fontWeight={600}>${num.toFixed(2)}</Typography>;
      },
    },
    {
      field: 'actions',
      headerName: 'Acciones',
      width: 150,
      sortable: false,
      renderCell: (params: GridRenderCellParams<PurchaseOrder>) => (
        <Box>
          <Tooltip title="Ver detalle">
            <IconButton size="small" onClick={() => navigate(`/purchasing/orders/${params.row.id}`)}>
              <ViewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          {params.row.status === 'draft' && (
            <Tooltip title="Editar">
              <IconButton size="small" onClick={() => navigate(`/purchasing/orders/${params.row.id}/edit`)}>
                <EditIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
          {['approved', 'sent', 'partial'].includes(params.row.status) && (
            <Tooltip title="Registrar Recepción">
              <IconButton size="small" color="primary" onClick={() => navigate(`/purchasing/orders/${params.row.id}/receive`)}>
                <ReceiveIcon fontSize="small" />
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
        <Typography variant="h4" fontWeight={600}>Órdenes de Compra</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={() => refetch()}>
            Actualizar
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => navigate('/purchasing/orders/new')}>
            Nueva Orden
          </Button>
        </Box>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, v) => { setTabValue(v); setPage(0); }}>
          <Tab label="Todas" />
          <Tab label="Borradores" />
          <Tab label="Aprobadas" />
          <Tab label="Enviadas" />
          <Tab label="Recibidas" />
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

export default PurchaseOrderListPage;
