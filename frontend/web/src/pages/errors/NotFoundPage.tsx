// ========================================================
// SISTEMA ERP UNIVERSAL - Página 404 Not Found
// ========================================================

import { Box, Typography, Button } from '@mui/material';
import { Home as HomeIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '60vh',
        textAlign: 'center',
      }}
    >
      <Typography
        variant="h1"
        sx={{
          fontSize: '8rem',
          fontWeight: 700,
          color: 'primary.main',
          lineHeight: 1,
        }}
      >
        404
      </Typography>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        Página no encontrada
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 400 }}>
        Lo sentimos, la página que busca no existe o ha sido movida.
      </Typography>
      <Button
        variant="contained"
        size="large"
        startIcon={<HomeIcon />}
        onClick={() => navigate('/dashboard')}
      >
        Ir al Inicio
      </Button>
    </Box>
  );
}

export default NotFoundPage;
