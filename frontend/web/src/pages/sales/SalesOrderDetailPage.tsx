// ========================================================
// SISTEMA ERP UNIVERSAL - Detalle del Pedido de Venta
// ========================================================

import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  Tabs,
  Tab,
  Card,
  CardContent,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Alert,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Edit as EditIcon,
  Print as PrintIcon,
  Email as EmailIcon,
  CheckCircle as ApproveIcon,
  LocalShipping as ShipIcon,
  Receipt as InvoiceIcon,
  Cancel as CancelIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { useSnackbar } from 'notistack';
import { salesOrderService } from '../../services/sales.service';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const statusConfig: Record<string, { label: string; color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'; step: number }> = {
  draft: { label: 'Borrador', color: 'default', step: 0 },
  confirmed: { label: 'Confirmado', color: 'primary', step: 1 },
  processing: { label: 'Procesando', color: 'info', step: 2 },
  shipped: { label: 'Enviado', color: 'secondary', step: 3 },
  delivered: { label: 'Entregado', color: 'success', step: 4 },
  invoiced: { label: 'Facturado', color: 'success', step: 5 },
  cancelled: { label: 'Cancelado', color: 'error', step: -1 },
};

const orderSteps = ['Borrador', 'Confirmado', 'Procesando', 'Enviado', 'Entregado', 'Facturado'];

function SalesOrderDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [tabValue, setTabValue] = useState(0);

  const { data: order, isLoading, error } = useQuery({
    queryKey: ['salesOrder', id],
    queryFn: () => salesOrderService.get(id!),
    enabled: !!id,
  });

  const confirmMutation = useMutation({
    mutationFn: () => salesOrderService.confirm(id!),
    onSuccess: () => {
      enqueueSnackbar('Pedido confirmado', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['salesOrder', id] });
    },
    onError: () => {
      enqueueSnackbar('Error al confirmar el pedido', { variant: 'error' });
    },
  });

  const cancelMutation = useMutation({
    mutationFn: () => salesOrderService.cancel(id!),
    onSuccess: () => {
      enqueueSnackbar('Pedido cancelado', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['salesOrder', id] });
    },
    onError: () => {
      enqueueSnackbar('Error al cancelar el pedido', { variant: 'error' });
    },
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error || !order) {
    return (
      <Box>
        <Button startIcon={<BackIcon />} onClick={() => navigate('/sales/orders')}>
          Volver
        </Button>
        <Paper sx={{ p: 3, mt: 2, textAlign: 'center' }}>
          <Typography color="error">Error al cargar el pedido</Typography>
        </Paper>
      </Box>
    );
  }

  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'USD' }).format(value);

  const formatDate = (date: string) => 
    format(new Date(date), 'dd/MM/yyyy', { locale: es });

  const status = statusConfig[order.status] || statusConfig.draft;
  const isCancelled = order.status === 'cancelled';

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={3}>
        <Box display="flex" alignItems="center" gap={2}>
          <IconButton onClick={() => navigate('/sales/orders')}>
            <BackIcon />
          </IconButton>
          <Box>
            <Typography variant="h4" fontWeight={600}>
              Pedido {order.order_number}
            </Typography>
            <Box display="flex" alignItems="center" gap={1} mt={0.5}>
              <Chip 
                size="small" 
                label={status.label}
                color={status.color}
              />
              <Typography variant="body2" color="text.secondary">
                Fecha: {formatDate(order.order_date)}
              </Typography>
            </Box>
          </Box>
        </Box>
        <Box display="flex" gap={1}>
          <Button variant="outlined" startIcon={<PrintIcon />}>
            Imprimir
          </Button>
          <Button variant="outlined" startIcon={<EmailIcon />}>
            Enviar
          </Button>
          {order.status === 'draft' && (
            <>
              <Button
                variant="outlined"
                startIcon={<EditIcon />}
                onClick={() => navigate(`/sales/orders/${id}/edit`)}
              >
                Editar
              </Button>
              <Button
                variant="contained"
                color="primary"
                startIcon={<ApproveIcon />}
                onClick={() => confirmMutation.mutate()}
                disabled={confirmMutation.isPending}
              >
                Confirmar
              </Button>
            </>
          )}
          {order.status === 'confirmed' && (
            <Button
              variant="contained"
              color="info"
              startIcon={<ShipIcon />}
            >
              Crear Envío
            </Button>
          )}
          {order.status === 'delivered' && (
            <Button
              variant="contained"
              color="success"
              startIcon={<InvoiceIcon />}
            >
              Facturar
            </Button>
          )}
          {!isCancelled && order.status !== 'invoiced' && (
            <Button
              variant="outlined"
              color="error"
              startIcon={<CancelIcon />}
              onClick={() => cancelMutation.mutate()}
              disabled={cancelMutation.isPending}
            >
              Cancelar
            </Button>
          )}
        </Box>
      </Box>

      {/* Status Stepper */}
      {!isCancelled && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Stepper activeStep={status.step} alternativeLabel>
            {orderSteps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </Paper>
      )}

      {isCancelled && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Este pedido ha sido cancelado
        </Alert>
      )}

      {/* Summary Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Cliente
              </Typography>
              <Typography variant="h6" fontWeight={600}>
                {order.customer_name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {order.customer_email}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Dirección de Envío
              </Typography>
              <Typography variant="body1">
                {order.shipping_address || 'No especificada'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Total del Pedido
              </Typography>
              <Typography variant="h4" fontWeight={700} color="primary.main">
                {formatCurrency(order.total_amount || 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mt: 2 }}>
        <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
          <Tab label="Líneas del Pedido" />
          <Tab label="Información" />
          <Tab label="Envíos" />
          <Tab label="Historial" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Producto</TableCell>
                  <TableCell>SKU</TableCell>
                  <TableCell align="right">Cantidad</TableCell>
                  <TableCell align="right">Precio Unit.</TableCell>
                  <TableCell align="right">Descuento</TableCell>
                  <TableCell align="right">Impuesto</TableCell>
                  <TableCell align="right">Subtotal</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {order.items?.map((item: any, index: number) => (
                  <TableRow key={index}>
                    <TableCell>
                      <Typography fontWeight={500}>{item.product_name}</Typography>
                      {item.description && (
                        <Typography variant="body2" color="text.secondary">
                          {item.description}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>{item.sku}</TableCell>
                    <TableCell align="right">{item.quantity}</TableCell>
                    <TableCell align="right">{formatCurrency(item.unit_price)}</TableCell>
                    <TableCell align="right">{item.discount_percent || 0}%</TableCell>
                    <TableCell align="right">{formatCurrency(item.tax_amount || 0)}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 600 }}>
                      {formatCurrency(item.subtotal)}
                    </TableCell>
                  </TableRow>
                ))}
                {(!order.items || order.items.length === 0) && (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Typography color="text.secondary" py={2}>
                        No hay líneas en este pedido
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Totals */}
          <Box display="flex" justifyContent="flex-end" p={3}>
            <Box sx={{ minWidth: 300 }}>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography>Subtotal:</Typography>
                <Typography>{formatCurrency(order.subtotal || 0)}</Typography>
              </Box>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography>Descuento:</Typography>
                <Typography color="success.main">-{formatCurrency(order.discount_amount || 0)}</Typography>
              </Box>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography>Impuestos:</Typography>
                <Typography>{formatCurrency(order.tax_amount || 0)}</Typography>
              </Box>
              <Divider sx={{ my: 1 }} />
              <Box display="flex" justifyContent="space-between">
                <Typography variant="h6" fontWeight={600}>Total:</Typography>
                <Typography variant="h6" fontWeight={600} color="primary.main">
                  {formatCurrency(order.total_amount || 0)}
                </Typography>
              </Box>
            </Box>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box px={3}>
            <Grid container spacing={4}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Información del Pedido
                </Typography>
                <Box mt={2}>
                  <Box mb={2}>
                    <Typography variant="body2" color="text.secondary">Fecha del Pedido</Typography>
                    <Typography>{formatDate(order.order_date)}</Typography>
                  </Box>
                  <Box mb={2}>
                    <Typography variant="body2" color="text.secondary">Fecha de Entrega Esperada</Typography>
                    <Typography>{order.expected_delivery_date ? formatDate(order.expected_delivery_date) : 'No especificada'}</Typography>
                  </Box>
                  <Box mb={2}>
                    <Typography variant="body2" color="text.secondary">Método de Pago</Typography>
                    <Typography>{order.payment_method || 'No especificado'}</Typography>
                  </Box>
                  <Box mb={2}>
                    <Typography variant="body2" color="text.secondary">Términos de Pago</Typography>
                    <Typography>{order.payment_terms || 'Estándar'}</Typography>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Información de Envío
                </Typography>
                <Box mt={2}>
                  <Box mb={2}>
                    <Typography variant="body2" color="text.secondary">Método de Envío</Typography>
                    <Typography>{order.shipping_method || 'No especificado'}</Typography>
                  </Box>
                  <Box mb={2}>
                    <Typography variant="body2" color="text.secondary">Dirección de Envío</Typography>
                    <Typography>{order.shipping_address || 'No especificada'}</Typography>
                  </Box>
                </Box>
              </Grid>
              {order.notes && (
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" fontWeight={600} gutterBottom>
                    Notas
                  </Typography>
                  <Typography color="text.secondary">{order.notes}</Typography>
                </Grid>
              )}
            </Grid>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Box px={3}>
            <Typography color="text.secondary" align="center" py={4}>
              Los envíos relacionados con este pedido se mostrarán aquí
            </Typography>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Box px={3}>
            <Typography color="text.secondary" align="center" py={4}>
              El historial de cambios se mostrará aquí
            </Typography>
          </Box>
        </TabPanel>
      </Paper>
    </Box>
  );
}

export default SalesOrderDetailPage;
