import { Box, Typography, Button, Paper } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

function InvoiceListPage() {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight={600}>Facturas</Typography>
        <Button variant="contained" startIcon={<AddIcon />}>Nueva Factura</Button>
      </Box>
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">Lista de facturas - Por implementar</Typography>
      </Paper>
    </Box>
  );
}

export default InvoiceListPage;
