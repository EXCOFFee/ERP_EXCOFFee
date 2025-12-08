// ========================================================
// SISTEMA ERP UNIVERSAL - Detalle del Cliente
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
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider,
  Avatar,
  CircularProgress,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  LocationOn as LocationIcon,
  Business as BusinessIcon,
  Person as PersonIcon,
  AttachMoney as MoneyIcon,
  Receipt as ReceiptIcon,
  ShoppingCart as OrderIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { customerService } from '../../services/sales.service';

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

function CustomerDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);

  const { data: customer, isLoading, error } = useQuery({
    queryKey: ['customer', id],
    queryFn: () => customerService.get(id!),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error || !customer) {
    return (
      <Box>
        <Button startIcon={<BackIcon />} onClick={() => navigate('/sales/customers')}>
          Volver
        </Button>
        <Paper sx={{ p: 3, mt: 2, textAlign: 'center' }}>
          <Typography color="error">Error al cargar el cliente</Typography>
        </Paper>
      </Box>
    );
  }

  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'USD' }).format(value);

  const formatDate = (date: string) => 
    format(new Date(date), 'dd/MM/yyyy', { locale: es });

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={3}>
        <Box display="flex" alignItems="center" gap={2}>
          <IconButton onClick={() => navigate('/sales/customers')}>
            <BackIcon />
          </IconButton>
          <Avatar sx={{ width: 56, height: 56, bgcolor: 'primary.main' }}>
            {customer.customer_type === 'company' ? <BusinessIcon /> : <PersonIcon />}
          </Avatar>
          <Box>
            <Typography variant="h4" fontWeight={600}>
              {customer.company_name || `${customer.first_name} ${customer.last_name}`}
            </Typography>
            <Box display="flex" alignItems="center" gap={1} mt={0.5}>
              <Chip 
                size="small" 
                label={customer.customer_type === 'company' ? 'Empresa' : 'Persona'}
                color="primary"
                variant="outlined"
              />
              <Chip 
                size="small" 
                label={customer.is_active ? 'Activo' : 'Inactivo'}
                color={customer.is_active ? 'success' : 'default'}
              />
              <Typography variant="body2" color="text.secondary">
                Código: {customer.customer_code}
              </Typography>
            </Box>
          </Box>
        </Box>
        <Box>
          <Button
            variant="outlined"
            startIcon={<EditIcon />}
            onClick={() => navigate(`/sales/customers/${id}/edit`)}
            sx={{ mr: 1 }}
          >
            Editar
          </Button>
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
          >
            Eliminar
          </Button>
        </Box>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="body2" color="text.secondary">Límite de Crédito</Typography>
                  <Typography variant="h5" fontWeight={600}>
                    {formatCurrency(customer.credit_limit || 0)}
                  </Typography>
                </Box>
                <MoneyIcon sx={{ fontSize: 40, color: 'primary.main', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="body2" color="text.secondary">Saldo Pendiente</Typography>
                  <Typography variant="h5" fontWeight={600} color="warning.main">
                    {formatCurrency(customer.balance || 0)}
                  </Typography>
                </Box>
                <ReceiptIcon sx={{ fontSize: 40, color: 'warning.main', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="body2" color="text.secondary">Total Pedidos</Typography>
                  <Typography variant="h5" fontWeight={600}>
                    {customer.total_orders || 0}
                  </Typography>
                </Box>
                <OrderIcon sx={{ fontSize: 40, color: 'info.main', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="body2" color="text.secondary">Total Compras</Typography>
                  <Typography variant="h5" fontWeight={600} color="success.main">
                    {formatCurrency(customer.total_purchases || 0)}
                  </Typography>
                </Box>
                <MoneyIcon sx={{ fontSize: 40, color: 'success.main', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mt: 2 }}>
        <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
          <Tab label="Información General" />
          <Tab label="Pedidos" />
          <Tab label="Facturas" />
          <Tab label="Historial" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Box px={3}>
            <Grid container spacing={4}>
              {/* Contact Info */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Información de Contacto
                </Typography>
                <Box sx={{ mt: 2 }}>
                  {customer.email && (
                    <Box display="flex" alignItems="center" mb={2}>
                      <EmailIcon sx={{ mr: 2, color: 'text.secondary' }} />
                      <Box>
                        <Typography variant="body2" color="text.secondary">Email</Typography>
                        <Typography>{customer.email}</Typography>
                      </Box>
                    </Box>
                  )}
                  {customer.phone && (
                    <Box display="flex" alignItems="center" mb={2}>
                      <PhoneIcon sx={{ mr: 2, color: 'text.secondary' }} />
                      <Box>
                        <Typography variant="body2" color="text.secondary">Teléfono</Typography>
                        <Typography>{customer.phone}</Typography>
                      </Box>
                    </Box>
                  )}
                  {customer.mobile && (
                    <Box display="flex" alignItems="center" mb={2}>
                      <PhoneIcon sx={{ mr: 2, color: 'text.secondary' }} />
                      <Box>
                        <Typography variant="body2" color="text.secondary">Móvil</Typography>
                        <Typography>{customer.mobile}</Typography>
                      </Box>
                    </Box>
                  )}
                </Box>
              </Grid>

              {/* Address Info */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Dirección
                </Typography>
                <Box display="flex" alignItems="flex-start" mt={2}>
                  <LocationIcon sx={{ mr: 2, color: 'text.secondary', mt: 0.5 }} />
                  <Box>
                    <Typography>{customer.address || 'No especificada'}</Typography>
                    {customer.city && (
                      <Typography color="text.secondary">
                        {customer.city}{customer.state ? `, ${customer.state}` : ''}{customer.postal_code ? ` ${customer.postal_code}` : ''}
                      </Typography>
                    )}
                    {customer.country && (
                      <Typography color="text.secondary">{customer.country}</Typography>
                    )}
                  </Box>
                </Box>
              </Grid>

              {/* Tax Info */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Información Fiscal
                </Typography>
                <Box mt={2}>
                  <Box mb={2}>
                    <Typography variant="body2" color="text.secondary">Identificación Fiscal</Typography>
                    <Typography>{customer.tax_id || 'No especificado'}</Typography>
                  </Box>
                  <Box mb={2}>
                    <Typography variant="body2" color="text.secondary">Términos de Pago</Typography>
                    <Typography>{customer.payment_terms || 'Estándar'}</Typography>
                  </Box>
                </Box>
              </Grid>

              {/* Additional Info */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Información Adicional
                </Typography>
                <Box mt={2}>
                  <Box mb={2}>
                    <Typography variant="body2" color="text.secondary">Grupo de Cliente</Typography>
                    <Typography>{customer.customer_group_name || 'Sin grupo'}</Typography>
                  </Box>
                  <Box mb={2}>
                    <Typography variant="body2" color="text.secondary">Vendedor Asignado</Typography>
                    <Typography>{customer.sales_rep_name || 'No asignado'}</Typography>
                  </Box>
                  <Box mb={2}>
                    <Typography variant="body2" color="text.secondary">Cliente desde</Typography>
                    <Typography>{formatDate(customer.created_at)}</Typography>
                  </Box>
                </Box>
              </Grid>

              {/* Notes */}
              {customer.notes && (
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" fontWeight={600} gutterBottom>
                    Notas
                  </Typography>
                  <Typography color="text.secondary">{customer.notes}</Typography>
                </Grid>
              )}
            </Grid>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box px={3}>
            <Typography color="text.secondary" align="center" py={4}>
              Los pedidos del cliente se mostrarán aquí
            </Typography>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Box px={3}>
            <Typography color="text.secondary" align="center" py={4}>
              Las facturas del cliente se mostrarán aquí
            </Typography>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Box px={3}>
            <Typography color="text.secondary" align="center" py={4}>
              El historial de actividad se mostrará aquí
            </Typography>
          </Box>
        </TabPanel>
      </Paper>
    </Box>
  );
}

export default CustomerDetailPage;
