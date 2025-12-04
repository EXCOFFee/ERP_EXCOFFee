import { Box, Typography, Button, Paper } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

function SalesOrderListPage() {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight={600}>Pedidos de Venta</Typography>
        <Button variant="contained" startIcon={<AddIcon />}>Nuevo Pedido</Button>
      </Box>
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">Lista de pedidos - Por implementar</Typography>
      </Paper>
    </Box>
  );
}

export default SalesOrderListPage;
