import { Box, Typography, Button, Paper } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

function PurchaseOrderListPage() {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight={600}>Órdenes de Compra</Typography>
        <Button variant="contained" startIcon={<AddIcon />}>Nueva Orden</Button>
      </Box>
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">Lista de órdenes de compra - Por implementar</Typography>
      </Paper>
    </Box>
  );
}

export default PurchaseOrderListPage;
