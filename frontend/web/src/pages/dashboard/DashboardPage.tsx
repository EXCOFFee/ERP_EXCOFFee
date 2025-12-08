// ========================================================
// SISTEMA ERP UNIVERSAL - Página de Dashboard
// ========================================================

import { Grid, Card, CardContent, Typography, Box, Paper, Skeleton } from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  ShoppingCart as SalesIcon,
  People as CustomersIcon,
  Inventory as InventoryIcon,
  LocalShipping as ShippingIcon,
  Receipt as InvoiceIcon,
  Business as BusinessIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { customerService, salesOrderService, salesInvoiceService } from '../../services/sales.service';
import { productService } from '../../services/inventory.service';
import { employeeService } from '../../services/hr.service';
import { supplierService, purchaseOrderService } from '../../services/purchasing.service';

// Componente de tarjeta de estadísticas
interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
  color: string;
  loading?: boolean;
}

function StatCard({ title, value, change, icon, color, loading }: StatCardProps) {
  const isPositive = change && change > 0;
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box sx={{ flex: 1 }}>
            <Typography color="text.secondary" variant="body2" gutterBottom>
              {title}
            </Typography>
            {loading ? (
              <Skeleton variant="text" width={100} height={40} />
            ) : (
              <Typography variant="h4" fontWeight={600}>
                {value}
              </Typography>
            )}
            {change !== undefined && !loading && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                {isPositive ? (
                  <TrendingUpIcon sx={{ color: 'success.main', fontSize: 20, mr: 0.5 }} />
                ) : (
                  <TrendingDownIcon sx={{ color: 'error.main', fontSize: 20, mr: 0.5 }} />
                )}
                <Typography
                  variant="body2"
                  sx={{ color: isPositive ? 'success.main' : 'error.main' }}
                >
                  {isPositive ? '+' : ''}{change}% vs mes anterior
                </Typography>
              </Box>
            )}
          </Box>
          <Box
            sx={{
              p: 1.5,
              borderRadius: 2,
              backgroundColor: `${color}15`,
              color: color,
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

function DashboardPage() {
  // Queries para obtener datos reales
  const { data: customersData, isLoading: customersLoading } = useQuery({
    queryKey: ['dashboard-customers'],
    queryFn: () => customerService.list({ page_size: 1 }),
  });

  const { data: productsData, isLoading: productsLoading } = useQuery({
    queryKey: ['dashboard-products'],
    queryFn: () => productService.list({ page_size: 1 }),
  });

  const { data: ordersData, isLoading: ordersLoading } = useQuery({
    queryKey: ['dashboard-orders'],
    queryFn: () => salesOrderService.list({ page_size: 5 }),
  });

  const { data: invoicesData, isLoading: invoicesLoading } = useQuery({
    queryKey: ['dashboard-invoices'],
    queryFn: () => salesInvoiceService.list({ page_size: 1 }),
  });

  const { data: suppliersData, isLoading: suppliersLoading } = useQuery({
    queryKey: ['dashboard-suppliers'],
    queryFn: () => supplierService.list({ page_size: 1 }),
  });

  const { data: purchaseOrdersData } = useQuery({
    queryKey: ['dashboard-purchase-orders'],
    queryFn: () => purchaseOrderService.list({ page_size: 5 }),
  });

  const { data: employeesData, isLoading: employeesLoading } = useQuery({
    queryKey: ['dashboard-employees'],
    queryFn: () => employeeService.list({ page_size: 1 }),
  });

  // Calcular totales de ventas
  const totalSales = ordersData?.results?.reduce((acc: number, order: any) => 
    acc + (order.total_amount || 0), 0) || 0;

  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'USD' }).format(value);

  const formatNumber = (value: number) => 
    new Intl.NumberFormat('es-ES').format(value);

  // Estadísticas con datos reales
  const stats = [
    {
      title: 'Clientes',
      value: customersLoading ? '...' : formatNumber(customersData?.count || 0),
      icon: <CustomersIcon sx={{ fontSize: 28 }} />,
      color: '#1976d2',
      loading: customersLoading,
    },
    {
      title: 'Productos',
      value: productsLoading ? '...' : formatNumber(productsData?.count || 0),
      icon: <InventoryIcon sx={{ fontSize: 28 }} />,
      color: '#2e7d32',
      loading: productsLoading,
    },
    {
      title: 'Pedidos',
      value: ordersLoading ? '...' : formatNumber(ordersData?.count || 0),
      icon: <SalesIcon sx={{ fontSize: 28 }} />,
      color: '#ed6c02',
      loading: ordersLoading,
    },
    {
      title: 'Facturas',
      value: invoicesLoading ? '...' : formatNumber(invoicesData?.count || 0),
      icon: <InvoiceIcon sx={{ fontSize: 28 }} />,
      color: '#9c27b0',
      loading: invoicesLoading,
    },
    {
      title: 'Proveedores',
      value: suppliersLoading ? '...' : formatNumber(suppliersData?.count || 0),
      icon: <ShippingIcon sx={{ fontSize: 28 }} />,
      color: '#0288d1',
      loading: suppliersLoading,
    },
    {
      title: 'Empleados',
      value: employeesLoading ? '...' : formatNumber(employeesData?.count || 0),
      icon: <BusinessIcon sx={{ fontSize: 28 }} />,
      color: '#7b1fa2',
      loading: employeesLoading,
    },
  ];

  return (
    <Box>
      {/* Título */}
      <Typography variant="h4" fontWeight={600} gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Bienvenido al Sistema ERP Universal
      </Typography>

      {/* Tarjetas de estadísticas */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} lg={2} key={index}>
            <StatCard {...stat} />
          </Grid>
        ))}
      </Grid>

      {/* Sección de gráficos y actividad reciente */}
      <Grid container spacing={3}>
        {/* Resumen de ventas */}
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Resumen del Sistema
            </Typography>
            <Grid container spacing={3} sx={{ mt: 2 }}>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" fontWeight={700} color="primary.main">
                    {customersData?.count || 0}
                  </Typography>
                  <Typography color="text.secondary">Clientes</Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" fontWeight={700} color="success.main">
                    {productsData?.count || 0}
                  </Typography>
                  <Typography color="text.secondary">Productos</Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" fontWeight={700} color="warning.main">
                    {ordersData?.count || 0}
                  </Typography>
                  <Typography color="text.secondary">Pedidos</Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" fontWeight={700} color="secondary.main">
                    {invoicesData?.count || 0}
                  </Typography>
                  <Typography color="text.secondary">Facturas</Typography>
                </Box>
              </Grid>
            </Grid>
            <Box sx={{ mt: 4, p: 3, bgcolor: 'background.default', borderRadius: 2 }}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Total en Pedidos Recientes
              </Typography>
              <Typography variant="h3" fontWeight={700} color="primary.main">
                {formatCurrency(totalSales)}
              </Typography>
            </Box>
          </Paper>
        </Grid>

        {/* Actividad reciente */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3, height: 400, overflow: 'auto' }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Pedidos Recientes
            </Typography>
            <Box sx={{ mt: 2 }}>
              {ordersLoading ? (
                Array.from({ length: 5 }).map((_, index) => (
                  <Box key={index} sx={{ py: 1.5, borderBottom: '1px solid', borderColor: 'divider' }}>
                    <Skeleton variant="text" width="80%" />
                    <Skeleton variant="text" width="40%" />
                  </Box>
                ))
              ) : ordersData?.results?.length ? (
                ordersData.results.map((order: any, index: number) => (
                  <Box
                    key={order.id || index}
                    sx={{
                      py: 1.5,
                      borderBottom: index < 4 ? '1px solid' : 'none',
                      borderColor: 'divider',
                    }}
                  >
                    <Box display="flex" justifyContent="space-between">
                      <Typography variant="body2" fontWeight={500}>
                        {order.order_number}
                      </Typography>
                      <Typography variant="body2" fontWeight={600} color="primary.main">
                        {formatCurrency(order.total_amount || 0)}
                      </Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      {order.customer_name || 'Cliente'}
                    </Typography>
                  </Box>
                ))
              ) : (
                <Typography color="text.secondary" align="center" py={4}>
                  No hay pedidos recientes
                </Typography>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Órdenes de compra */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Órdenes de Compra Recientes
            </Typography>
            <Box sx={{ mt: 2 }}>
              {purchaseOrdersData?.results?.length ? (
                purchaseOrdersData.results.slice(0, 5).map((order: any, index: number) => (
                  <Box
                    key={order.id || index}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      py: 1.5,
                      borderBottom: index < 4 ? '1px solid' : 'none',
                      borderColor: 'divider',
                    }}
                  >
                    <Box>
                      <Typography variant="body2">{order.order_number}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {order.supplier_name || 'Proveedor'} - {order.status}
                      </Typography>
                    </Box>
                    <Typography variant="body2" fontWeight={600}>
                      {formatCurrency(order.total_amount || 0)}
                    </Typography>
                  </Box>
                ))
              ) : (
                <Typography color="text.secondary" align="center" py={4}>
                  No hay órdenes de compra recientes
                </Typography>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Módulos del sistema */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Módulos del Sistema
            </Typography>
            <Box sx={{ mt: 2 }}>
              {[
                { name: 'Inventario', description: 'Productos, almacenes y movimientos', color: '#2e7d32' },
                { name: 'Ventas', description: 'Clientes, pedidos y facturas', color: '#1976d2' },
                { name: 'Compras', description: 'Proveedores y órdenes de compra', color: '#ed6c02' },
                { name: 'Finanzas', description: 'Contabilidad y reportes', color: '#9c27b0' },
                { name: 'Recursos Humanos', description: 'Empleados, nómina y asistencia', color: '#0288d1' },
              ].map((module, index) => (
                <Box
                  key={index}
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    py: 1.5,
                    borderBottom: index < 4 ? '1px solid' : 'none',
                    borderColor: 'divider',
                  }}
                >
                  <Box>
                    <Typography variant="body2" fontWeight={500} sx={{ color: module.color }}>
                      {module.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {module.description}
                    </Typography>
                  </Box>
                  <Box
                    sx={{
                      width: 10,
                      height: 10,
                      borderRadius: '50%',
                      bgcolor: 'success.main',
                    }}
                  />
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default DashboardPage;
