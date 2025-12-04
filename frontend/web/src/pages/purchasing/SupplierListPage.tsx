import { Box, Typography, Button, Paper } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

function SupplierListPage() {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight={600}>Proveedores</Typography>
        <Button variant="contained" startIcon={<AddIcon />}>Nuevo Proveedor</Button>
      </Box>
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">Lista de proveedores - Por implementar</Typography>
      </Paper>
    </Box>
  );
}

export default SupplierListPage;
