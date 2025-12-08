// ========================================================
// SISTEMA ERP UNIVERSAL - Reportes Financieros
// ========================================================

import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  AccountBalance as BalanceIcon,
  TrendingUp as IncomeIcon,
  SwapVert as CashFlowIcon,
  Assessment as TrialIcon,
  Print as PrintIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { financeService } from '../../services/finance.service';

interface ReportCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  onGenerate: () => void;
}

function ReportCard({ title, description, icon, color, onGenerate }: ReportCardProps) {
  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              p: 1.5,
              borderRadius: 2,
              bgcolor: `${color}15`,
              color: color,
              mr: 2,
            }}
          >
            {icon}
          </Box>
          <Typography variant="h6" fontWeight={600}>{title}</Typography>
        </Box>
        <Typography color="text.secondary" variant="body2">
          {description}
        </Typography>
      </CardContent>
      <CardActions sx={{ p: 2, pt: 0 }}>
        <Button variant="contained" fullWidth onClick={onGenerate}>
          Generar Reporte
        </Button>
      </CardActions>
    </Card>
  );
}

function FinancialReportsPage() {
  const [reportDialog, setReportDialog] = useState<string | null>(null);
  const [periodId, setPeriodId] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [reportData, setReportData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const { data: periods } = useQuery({
    queryKey: ['fiscal-periods'],
    queryFn: () => financeService.getFiscalPeriods(),
  });

  const handleGenerateReport = async () => {
    setIsLoading(true);
    try {
      let data;
      switch (reportDialog) {
        case 'balance':
          data = await financeService.getBalanceSheet({ period: periodId, as_of_date: endDate });
          break;
        case 'income':
          data = await financeService.getIncomeStatement({ period: periodId, start_date: startDate, end_date: endDate });
          break;
        case 'cashflow':
          data = await financeService.getCashFlowStatement({ period: periodId, start_date: startDate, end_date: endDate });
          break;
        case 'trial':
          data = await financeService.getTrialBalance({ period: periodId, as_of_date: endDate });
          break;
      }
      setReportData(data);
    } catch (error) {
      console.error('Error generating report:', error);
    }
    setIsLoading(false);
  };

  const reports = [
    {
      key: 'balance',
      title: 'Balance General',
      description: 'Estado de situación financiera que muestra activos, pasivos y patrimonio en una fecha específica.',
      icon: <BalanceIcon sx={{ fontSize: 32 }} />,
      color: '#1976d2',
    },
    {
      key: 'income',
      title: 'Estado de Resultados',
      description: 'Resumen de ingresos, costos y gastos que muestra la utilidad o pérdida del período.',
      icon: <IncomeIcon sx={{ fontSize: 32 }} />,
      color: '#2e7d32',
    },
    {
      key: 'cashflow',
      title: 'Flujo de Efectivo',
      description: 'Movimientos de entradas y salidas de efectivo por actividades operativas, de inversión y financiamiento.',
      icon: <CashFlowIcon sx={{ fontSize: 32 }} />,
      color: '#ed6c02',
    },
    {
      key: 'trial',
      title: 'Balanza de Comprobación',
      description: 'Lista de todas las cuentas con sus saldos deudores y acreedores para verificar el equilibrio contable.',
      icon: <TrialIcon sx={{ fontSize: 32 }} />,
      color: '#9c27b0',
    },
  ];

  const reportTitles: Record<string, string> = {
    balance: 'Balance General',
    income: 'Estado de Resultados',
    cashflow: 'Flujo de Efectivo',
    trial: 'Balanza de Comprobación',
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>Reportes Financieros</Typography>
      <Typography color="text.secondary" sx={{ mb: 4 }}>
        Seleccione un reporte para generar
      </Typography>

      <Grid container spacing={3}>
        {reports.map((report) => (
          <Grid item xs={12} sm={6} lg={3} key={report.key}>
            <ReportCard
              {...report}
              onGenerate={() => {
                setReportDialog(report.key);
                setReportData(null);
              }}
            />
          </Grid>
        ))}
      </Grid>

      {/* Dialog de generación de reporte */}
      <Dialog
        open={!!reportDialog}
        onClose={() => setReportDialog(null)}
        maxWidth={reportData ? 'lg' : 'sm'}
        fullWidth
      >
        <DialogTitle>
          {reportTitles[reportDialog || ''] || 'Reporte'}
        </DialogTitle>
        <DialogContent>
          {!reportData ? (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Período Fiscal</InputLabel>
                  <Select
                    value={periodId}
                    onChange={(e) => setPeriodId(e.target.value)}
                    label="Período Fiscal"
                  >
                    {periods?.results?.map((period) => (
                      <MenuItem key={period.id} value={period.id}>{period.name}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              {reportDialog !== 'balance' && reportDialog !== 'trial' && (
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Fecha Inicio"
                    type="date"
                    fullWidth
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
              )}
              <Grid item xs={12} sm={reportDialog === 'balance' || reportDialog === 'trial' ? 12 : 6}>
                <TextField
                  label={reportDialog === 'balance' || reportDialog === 'trial' ? 'A la Fecha' : 'Fecha Fin'}
                  type="date"
                  fullWidth
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
            </Grid>
          ) : (
            <Box sx={{ mt: 2 }}>
              {isLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                  <CircularProgress />
                </Box>
              ) : reportDialog === 'trial' ? (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Código</TableCell>
                        <TableCell>Cuenta</TableCell>
                        <TableCell align="right">Débito</TableCell>
                        <TableCell align="right">Crédito</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {reportData.accounts?.map((acc: any) => (
                        <TableRow key={acc.id}>
                          <TableCell>{acc.code}</TableCell>
                          <TableCell>{acc.name}</TableCell>
                          <TableCell align="right">
                            {acc.debit_balance > 0 ? `$${acc.debit_balance.toFixed(2)}` : '-'}
                          </TableCell>
                          <TableCell align="right">
                            {acc.credit_balance > 0 ? `$${acc.credit_balance.toFixed(2)}` : '-'}
                          </TableCell>
                        </TableRow>
                      ))}
                      <TableRow sx={{ bgcolor: 'action.hover' }}>
                        <TableCell colSpan={2}><strong>TOTALES</strong></TableCell>
                        <TableCell align="right"><strong>${reportData.total_debit?.toFixed(2)}</strong></TableCell>
                        <TableCell align="right"><strong>${reportData.total_credit?.toFixed(2)}</strong></TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Box>
                  {/* Renderizado genérico para otros reportes */}
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Datos del reporte generado. En producción, aquí se mostraría el reporte completo con el formato adecuado.
                  </Typography>
                  <pre style={{ overflow: 'auto', maxHeight: 400 }}>
                    {JSON.stringify(reportData, null, 2)}
                  </pre>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          {reportData && (
            <>
              <Button startIcon={<PrintIcon />}>Imprimir</Button>
              <Button startIcon={<DownloadIcon />}>Exportar PDF</Button>
            </>
          )}
          <Button onClick={() => { setReportDialog(null); setReportData(null); }}>
            Cerrar
          </Button>
          {!reportData && (
            <Button
              variant="contained"
              onClick={handleGenerateReport}
              disabled={!periodId || !endDate || isLoading}
            >
              {isLoading ? 'Generando...' : 'Generar'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default FinancialReportsPage;
