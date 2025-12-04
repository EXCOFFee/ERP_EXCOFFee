import { Box, Typography, Button, Paper } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

function CustomerListPage() {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight={600}>Clientes</Typography>
        <Button variant="contained" startIcon={<AddIcon />}>Nuevo Cliente</Button>
      </Box>
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">Lista de clientes - Por implementar</Typography>
      </Paper>
    </Box>
  );
}

export default CustomerListPage;
