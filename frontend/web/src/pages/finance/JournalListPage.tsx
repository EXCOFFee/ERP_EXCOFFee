// ========================================================
// SISTEMA ERP UNIVERSAL - Diarios Contables
// ========================================================

import { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Chip,
  Tooltip,
  Paper,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add as AddIcon,
  Visibility as ViewIcon,
  Refresh as RefreshIcon,
  Print as PrintIcon,
  CheckCircle as ApproveIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import DataTable from '../../components/common/DataTable';
import { financeService, JournalEntry } from '../../services/finance.service';
import { useSnackbar } from 'notistack';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const statusConfig: Record<string, { label: string; color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' }> = {
  draft: { label: 'Borrador', color: 'default' },
  pending: { label: 'Pendiente', color: 'warning' },
  posted: { label: 'Contabilizado', color: 'success' },
  cancelled: { label: 'Anulado', color: 'error' },
};

function JournalListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [tabValue, setTabValue] = useState(0);

  const getStatusFilter = () => {
    switch (tabValue) {
      case 1: return 'draft';
      case 2: return 'pending';
      case 3: return 'posted';
      default: return undefined;
    }
  };

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['journal-entries', page, pageSize, tabValue],
    queryFn: () => financeService.getJournalEntries({
      page: page + 1,
      page_size: pageSize,
      status: getStatusFilter(),
    }),
  });

  const postMutation = useMutation({
    mutationFn: (id: string) => financeService.postJournalEntry(id),
    onSuccess: () => {
      enqueueSnackbar('Asiento contabilizado', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['journal-entries'] });
    },
    onError: () => {
      enqueueSnackbar('Error al contabilizar', { variant: 'error' });
    },
  });

  const columns: GridColDef[] = [
    { field: 'entry_number', headerName: 'Nº Asiento', width: 130 },
    {
      field: 'entry_date',
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
      field: 'period',
      headerName: 'Período',
      width: 120,
      valueGetter: (value: any) => typeof value === 'object' ? value?.name : value,
    },
    { field: 'description', headerName: 'Descripción', flex: 1, minWidth: 250 },
    { field: 'reference', headerName: 'Referencia', width: 130 },
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
      field: 'total_debit',
      headerName: 'Débito',
      width: 120,
      valueFormatter: (value: number) => `$${value?.toFixed(2) || '0.00'}`,
      align: 'right',
    },
    {
      field: 'total_credit',
      headerName: 'Crédito',
      width: 120,
      valueFormatter: (value: number) => `$${value?.toFixed(2) || '0.00'}`,
      align: 'right',
    },
    {
      field: 'actions',
      headerName: 'Acciones',
      width: 150,
      sortable: false,
      renderCell: (params: GridRenderCellParams<JournalEntry>) => (
        <Box>
          <Tooltip title="Ver detalle">
            <IconButton size="small" onClick={() => navigate(`/finance/journals/${params.row.id}`)}>
              <ViewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          {(params.row.status === 'draft' || params.row.status === 'pending') && (
            <Tooltip title="Contabilizar">
              <IconButton
                size="small"
                color="success"
                onClick={() => postMutation.mutate(params.row.id)}
                disabled={postMutation.isPending}
              >
                <ApproveIcon fontSize="small" />
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
        <Typography variant="h4" fontWeight={600}>Diarios Contables</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={() => refetch()}>
            Actualizar
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => navigate('/finance/journals/new')}>
            Nuevo Asiento
          </Button>
        </Box>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, v) => { setTabValue(v); setPage(0); }}>
          <Tab label="Todos" />
          <Tab label="Borradores" />
          <Tab label="Pendientes" />
          <Tab label="Contabilizados" />
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

export default JournalListPage;
