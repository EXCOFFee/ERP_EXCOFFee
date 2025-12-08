// ========================================================
// SISTEMA ERP UNIVERSAL - Libro Mayor
// ========================================================

import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
} from '@mui/material';
import { Search as SearchIcon, Print as PrintIcon, Download as DownloadIcon } from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { financeService } from '../../services/finance.service';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

function LedgerPage() {
  const [accountId, setAccountId] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const { data: accounts } = useQuery({
    queryKey: ['accounts-select'],
    queryFn: () => financeService.getAccounts({ page_size: 500, allows_transactions: true }),
  });

  const { data: ledgerData, isLoading, refetch } = useQuery({
    queryKey: ['ledger', accountId, startDate, endDate],
    queryFn: () => financeService.getGeneralLedger({
      account: accountId,
      start_date: startDate,
      end_date: endDate,
    }),
    enabled: !!accountId && !!startDate && !!endDate,
  });

  const handleSearch = () => {
    refetch();
  };

  const selectedAccount = accounts?.results?.find(a => a.id === accountId);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight={600}>Libro Mayor</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<PrintIcon />} disabled={!ledgerData}>
            Imprimir
          </Button>
          <Button variant="outlined" startIcon={<DownloadIcon />} disabled={!ledgerData}>
            Exportar
          </Button>
        </Box>
      </Box>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="flex-end">
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Cuenta Contable</InputLabel>
              <Select
                value={accountId}
                onChange={(e) => setAccountId(e.target.value)}
                label="Cuenta Contable"
              >
                {accounts?.results?.map((account) => (
                  <MenuItem key={account.id} value={account.id}>
                    {account.code} - {account.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              label="Fecha Inicio"
              type="date"
              fullWidth
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              label="Fecha Fin"
              type="date"
              fullWidth
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              variant="contained"
              fullWidth
              startIcon={<SearchIcon />}
              onClick={handleSearch}
              disabled={!accountId || !startDate || !endDate}
            >
              Buscar
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {ledgerData && (
        <Paper>
          <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
            <Typography variant="h6">{selectedAccount?.code} - {selectedAccount?.name}</Typography>
            <Typography color="text.secondary">
              Período: {format(new Date(startDate), 'dd/MM/yyyy', { locale: es })} al {format(new Date(endDate), 'dd/MM/yyyy', { locale: es })}
            </Typography>
          </Box>

          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Fecha</TableCell>
                  <TableCell>Nº Asiento</TableCell>
                  <TableCell>Descripción</TableCell>
                  <TableCell align="right">Débito</TableCell>
                  <TableCell align="right">Crédito</TableCell>
                  <TableCell align="right">Saldo</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {/* Saldo inicial */}
                <TableRow sx={{ bgcolor: 'action.hover' }}>
                  <TableCell colSpan={3}><strong>Saldo Inicial</strong></TableCell>
                  <TableCell align="right">-</TableCell>
                  <TableCell align="right">-</TableCell>
                  <TableCell align="right">
                    <strong>${ledgerData.opening_balance?.toFixed(2) || '0.00'}</strong>
                  </TableCell>
                </TableRow>

                {/* Movimientos */}
                {ledgerData.movements?.map((mov: any, index: number) => (
                  <TableRow key={index}>
                    <TableCell>
                      {format(new Date(mov.date), 'dd/MM/yyyy', { locale: es })}
                    </TableCell>
                    <TableCell>{mov.entry_number}</TableCell>
                    <TableCell>{mov.description}</TableCell>
                    <TableCell align="right">
                      {mov.debit > 0 ? `$${mov.debit.toFixed(2)}` : '-'}
                    </TableCell>
                    <TableCell align="right">
                      {mov.credit > 0 ? `$${mov.credit.toFixed(2)}` : '-'}
                    </TableCell>
                    <TableCell align="right">${mov.balance?.toFixed(2)}</TableCell>
                  </TableRow>
                ))}

                {/* Totales y saldo final */}
                <TableRow sx={{ bgcolor: 'action.hover' }}>
                  <TableCell colSpan={3}><strong>Totales del Período</strong></TableCell>
                  <TableCell align="right">
                    <strong>${ledgerData.total_debit?.toFixed(2) || '0.00'}</strong>
                  </TableCell>
                  <TableCell align="right">
                    <strong>${ledgerData.total_credit?.toFixed(2) || '0.00'}</strong>
                  </TableCell>
                  <TableCell align="right">-</TableCell>
                </TableRow>
                <TableRow sx={{ bgcolor: 'primary.light' }}>
                  <TableCell colSpan={3}><strong>Saldo Final</strong></TableCell>
                  <TableCell align="right">-</TableCell>
                  <TableCell align="right">-</TableCell>
                  <TableCell align="right">
                    <Typography fontWeight={700} color="primary.contrastText">
                      ${ledgerData.closing_balance?.toFixed(2) || '0.00'}
                    </Typography>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {!ledgerData && !isLoading && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            Seleccione una cuenta y un rango de fechas para ver el libro mayor
          </Typography>
        </Paper>
      )}
    </Box>
  );
}

export default LedgerPage;
