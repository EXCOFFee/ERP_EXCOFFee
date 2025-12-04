// ========================================================
// SISTEMA ERP UNIVERSAL - Página 403 Forbidden
// ========================================================

import { Box, Typography, Button } from '@mui/material';
import { Lock as LockIcon, ArrowBack as ArrowBackIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

function ForbiddenPage() {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        textAlign: 'center',
        p: 3,
      }}
    >
      <LockIcon sx={{ fontSize: 100, color: 'error.main', mb: 2 }} />
      <Typography variant="h4" fontWeight={600} gutterBottom>
        Acceso Denegado
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 400 }}>
        No tiene permisos para acceder a esta página. Contacte al administrador si cree que esto es un error.
      </Typography>
      <Button
        variant="contained"
        size="large"
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate(-1)}
      >
        Volver
      </Button>
    </Box>
  );
}

export default ForbiddenPage;
