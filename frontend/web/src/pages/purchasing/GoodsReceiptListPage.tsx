// ========================================================
// SISTEMA ERP UNIVERSAL - Lista de Recepciones de Mercancía
// ========================================================

import { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Chip,
  Tooltip,
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Refresh as RefreshIcon,
  Print as PrintIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import DataTable from '../../components/common/DataTable';
import { purchasingService, GoodsReceipt } from '../../services/purchasing.service';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const statusConfig: Record<string, { label: string; color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' }> = {
  draft: { label: 'Borrador', color: 'default' },
  inspecting: { label: 'En Inspección', color: 'info' },
  accepted: { label: 'Aceptado', color: 'success' },
  rejected: { label: 'Rechazado', color: 'error' },
  partial: { label: 'Parcial', color: 'warning' },
};

function GoodsReceiptListPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['goods-receipts', page, pageSize],
    queryFn: () => purchasingService.getGoodsReceipts({
      page: page + 1,
      page_size: pageSize,
    }),
  });

  const columns: GridColDef[] = [
    { field: 'receipt_number', headerName: 'Nº Recepción', width: 130 },
    {
      field: 'receipt_date',
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
      field: 'purchase_order',
      headerName: 'Orden de Compra',
      width: 150,
      valueGetter: (value: any) => typeof value === 'object' ? value?.order_number : value,
    },
    {
      field: 'supplier',
      headerName: 'Proveedor',
      flex: 1,
      minWidth: 200,
      valueGetter: (value: any) => typeof value === 'object' ? value?.business_name : value,
    },
    {
      field: 'warehouse',
      headerName: 'Almacén',
      width: 150,
      valueGetter: (value: any) => typeof value === 'object' ? value?.name : value,
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
      field: 'received_by',
      headerName: 'Recibido Por',
      width: 150,
      valueGetter: (value: any) => typeof value === 'object' ? `${value?.first_name || ''} ${value?.last_name || ''}`.trim() : value,
    },
    {
      field: 'actions',
      headerName: 'Acciones',
      width: 120,
      sortable: false,
      renderCell: (params: GridRenderCellParams<GoodsReceipt>) => (
        <Box>
          <Tooltip title="Ver detalle">
            <IconButton size="small" onClick={() => navigate(`/purchasing/receipts/${params.row.id}`)}>
              <ViewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
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
        <Typography variant="h4" fontWeight={600}>Recepciones de Mercancía</Typography>
        <Button variant="outlined" startIcon={<RefreshIcon />} onClick={() => refetch()}>
          Actualizar
        </Button>
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
    </Box>
  );
}

export default GoodsReceiptListPage;
