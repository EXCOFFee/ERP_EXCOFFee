// ========================================================
// SISTEMA ERP UNIVERSAL - Formulario de Producto
// ========================================================

import { Box, Typography, Paper, Button } from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { Save as SaveIcon, Cancel as CancelIcon } from '@mui/icons-material';

function ProductFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);

  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        {isEdit ? 'Editar Producto' : 'Nuevo Producto'}
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography color="text.secondary">
          Formulario de producto - Por implementar
        </Typography>
      </Paper>

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
        <Button
          variant="outlined"
          startIcon={<CancelIcon />}
          onClick={() => navigate(-1)}
        >
          Cancelar
        </Button>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
        >
          {isEdit ? 'Guardar Cambios' : 'Crear Producto'}
        </Button>
      </Box>
    </Box>
  );
}

export default ProductFormPage;
