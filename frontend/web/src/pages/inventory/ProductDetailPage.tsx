// ========================================================
// SISTEMA ERP UNIVERSAL - Detalle de Producto
// ========================================================

import { Box, Typography, Paper, Grid, Tabs, Tab, Button } from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { Edit as EditIcon } from '@mui/icons-material';
import { useState } from 'react';

function ProductDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight={600}>
          Detalle del Producto
        </Typography>
        <Button
          variant="contained"
          startIcon={<EditIcon />}
          onClick={() => navigate(`/inventory/products/${id}/edit`)}
        >
          Editar
        </Button>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
          <Tab label="Información General" />
          <Tab label="Stock por Almacén" />
          <Tab label="Historial" />
          <Tab label="Precios" />
        </Tabs>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">
          Contenido del producto ID: {id} - Por implementar
        </Typography>
      </Paper>
    </Box>
  );
}

export default ProductDetailPage;
