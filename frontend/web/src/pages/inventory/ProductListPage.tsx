// ========================================================
// SISTEMA ERP UNIVERSAL - Lista de Productos
// ========================================================

import { Box, Typography, Button, Paper } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

function ProductListPage() {
  const navigate = useNavigate();

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight={600}>
          Productos
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/inventory/products/new')}
        >
          Nuevo Producto
        </Button>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">
          Tabla de productos - Por implementar con datos de la API
        </Typography>
      </Paper>
    </Box>
  );
}

export default ProductListPage;
