// ========================================================
// SISTEMA ERP UNIVERSAL - Lista de Facturas
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
  Visibility as ViewIcon,
  Refresh as RefreshIcon,
  Print as PrintIcon,
  Payment as PaymentIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import DataTable from '../../components/common/DataTable';
import { salesService, SalesInvoice } from '../../services/sales.service';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const statusConfig: Record<string, { label: string; color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' }> = {
  draft: { label: 'Borrador', color: 'default' },
  issued: { label: 'Emitida', color: 'primary' },
  sent: { label: 'Enviada', color: 'info' },
  partial: { label: 'Pago Parcial', color: 'warning' },
  paid: { label: 'Pagada', color: 'success' },
  cancelled: { label: 'Anulada', color: 'error' },
  overdue: { label: 'Vencida', color: 'error' },
};

function InvoiceListPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [tabValue, setTabValue] = useState(0);

  const getStatusFilter = () => {
    switch (tabValue) {
      case 1: return 'issued';
      case 2: return 'partial';
      case 3: return 'paid';
      case 4: return 'overdue';
      default: return undefined;
    }
  };

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['sales-invoices', page, pageSize, tabValue],
    queryFn: () => salesService.getInvoices({
      page: page + 1,
      page_size: pageSize,
      status: getStatusFilter(),
    }),
  });

  const columns: GridColDef[] = [
    { field: 'invoice_number', headerName: 'Nº Factura', width: 130 },
    {
      field: 'invoice_date',
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
      field: 'due_date',
      headerName: 'Vencimiento',
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
      field: 'total',
      headerName: 'Total',
      width: 120,
      renderCell: (params: GridRenderCellParams) => (
        <Typography fontWeight={600}>${params.value?.toFixed(2) || '0.00'}</Typography>
      ),
    },
    {
      field: 'paid_amount',
      headerName: 'Pagado',
      width: 110,
      valueFormatter: (value: number) => `$${value?.toFixed(2) || '0.00'}`,
    },
    {
      field: 'balance_due',
      headerName: 'Saldo',
      width: 110,
      renderCell: (params: GridRenderCellParams) => (
        <Typography
          fontWeight={600}
          color={params.value > 0 ? 'error.main' : 'success.main'}
        >
          ${params.value?.toFixed(2) || '0.00'}
        </Typography>
      ),
    },
    {
      field: 'actions',
      headerName: 'Acciones',
      width: 150,
      sortable: false,
      renderCell: (params: GridRenderCellParams<SalesInvoice>) => (
        <Box>
          <Tooltip title="Ver detalle">
            <IconButton
              size="small"
              onClick={() => navigate(`/sales/invoices/${params.row.id}`)}
            >
              <ViewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          {params.row.status !== 'paid' && params.row.status !== 'cancelled' && (
            <Tooltip title="Registrar Pago">
              <IconButton
                size="small"
                color="primary"
                onClick={() => navigate(`/sales/invoices/${params.row.id}/payment`)}
              >
                <PaymentIcon fontSize="small" />
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
        <Typography variant="h4" fontWeight={600}>Facturas</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={() => refetch()}>
            Actualizar
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/sales/invoices/new')}
          >
            Nueva Factura
          </Button>
        </Box>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, v) => { setTabValue(v); setPage(0); }}>
          <Tab label="Todas" />
          <Tab label="Emitidas" />
          <Tab label="Pago Parcial" />
          <Tab label="Pagadas" />
          <Tab label="Vencidas" />
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

export default InvoiceListPage;
