// ========================================================
// SISTEMA ERP UNIVERSAL - Página de Dashboard
// ========================================================

import { Grid, Card, CardContent, Typography, Box, Paper } from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  ShoppingCart as SalesIcon,
  People as CustomersIcon,
  Inventory as InventoryIcon,
  AccountBalance as BalanceIcon,
} from '@mui/icons-material';

// Componente de tarjeta de estadísticas
interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
  color: string;
}

function StatCard({ title, value, change, icon, color }: StatCardProps) {
  const isPositive = change && change > 0;
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography color="text.secondary" variant="body2" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" fontWeight={600}>
              {value}
            </Typography>
            {change !== undefined && (
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
  // Datos de ejemplo - en producción vendrían de la API
  const stats = [
    {
      title: 'Ventas del Mes',
      value: '$125,430',
      change: 12.5,
      icon: <SalesIcon sx={{ fontSize: 28 }} />,
      color: '#1976d2',
    },
    {
      title: 'Clientes Activos',
      value: '1,254',
      change: 5.2,
      icon: <CustomersIcon sx={{ fontSize: 28 }} />,
      color: '#2e7d32',
    },
    {
      title: 'Productos en Stock',
      value: '3,847',
      change: -2.1,
      icon: <InventoryIcon sx={{ fontSize: 28 }} />,
      color: '#ed6c02',
    },
    {
      title: 'Cuentas por Cobrar',
      value: '$45,200',
      change: -8.3,
      icon: <BalanceIcon sx={{ fontSize: 28 }} />,
      color: '#9c27b0',
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
          <Grid item xs={12} sm={6} lg={3} key={index}>
            <StatCard {...stat} />
          </Grid>
        ))}
      </Grid>

      {/* Sección de gráficos y actividad reciente */}
      <Grid container spacing={3}>
        {/* Gráfico de ventas */}
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Ventas Mensuales
            </Typography>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: 'calc(100% - 40px)',
                color: 'text.secondary',
              }}
            >
              <Typography>Gráfico de ventas (requiere datos de la API)</Typography>
            </Box>
          </Paper>
        </Grid>

        {/* Actividad reciente */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Actividad Reciente
            </Typography>
            <Box sx={{ mt: 2 }}>
              {[
                { action: 'Nueva orden de venta', time: 'Hace 5 minutos' },
                { action: 'Pago recibido #1234', time: 'Hace 15 minutos' },
                { action: 'Stock actualizado', time: 'Hace 1 hora' },
                { action: 'Cliente nuevo registrado', time: 'Hace 2 horas' },
                { action: 'Factura emitida #567', time: 'Hace 3 horas' },
              ].map((item, index) => (
                <Box
                  key={index}
                  sx={{
                    py: 1.5,
                    borderBottom: index < 4 ? '1px solid' : 'none',
                    borderColor: 'divider',
                  }}
                >
                  <Typography variant="body2">{item.action}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {item.time}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* Top productos */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Top Productos Vendidos
            </Typography>
            <Box sx={{ mt: 2 }}>
              {[
                { name: 'Producto A', quantity: 150, revenue: '$12,500' },
                { name: 'Producto B', quantity: 120, revenue: '$9,800' },
                { name: 'Producto C', quantity: 95, revenue: '$7,600' },
                { name: 'Producto D', quantity: 80, revenue: '$6,400' },
                { name: 'Producto E', quantity: 65, revenue: '$5,200' },
              ].map((product, index) => (
                <Box
                  key={index}
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    py: 1.5,
                    borderBottom: index < 4 ? '1px solid' : 'none',
                    borderColor: 'divider',
                  }}
                >
                  <Box>
                    <Typography variant="body2">{product.name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {product.quantity} unidades
                    </Typography>
                  </Box>
                  <Typography variant="body2" fontWeight={600}>
                    {product.revenue}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* Órdenes pendientes */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Órdenes Pendientes
            </Typography>
            <Box sx={{ mt: 2 }}>
              {[
                { order: 'ORD-001', customer: 'Cliente A', status: 'Procesando', total: '$1,250' },
                { order: 'ORD-002', customer: 'Cliente B', status: 'En espera', total: '$890' },
                { order: 'ORD-003', customer: 'Cliente C', status: 'Procesando', total: '$2,100' },
                { order: 'ORD-004', customer: 'Cliente D', status: 'En espera', total: '$450' },
                { order: 'ORD-005', customer: 'Cliente E', status: 'Procesando', total: '$1,800' },
              ].map((order, index) => (
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
                    <Typography variant="body2">{order.order}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {order.customer} - {order.status}
                    </Typography>
                  </Box>
                  <Typography variant="body2" fontWeight={600}>
                    {order.total}
                  </Typography>
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
