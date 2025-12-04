// ========================================================
// SISTEMA ERP UNIVERSAL - Lista de Almacenes
// ========================================================

import { Box, Typography, Button, Paper } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

function WarehouseListPage() {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight={600}>
          Almacenes
        </Typography>
        <Button variant="contained" startIcon={<AddIcon />}>
          Nuevo Almacén
        </Button>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">
          Lista de almacenes - Por implementar
        </Typography>
      </Paper>
    </Box>
  );
}

export default WarehouseListPage;
