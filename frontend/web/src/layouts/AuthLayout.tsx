// ========================================================
// SISTEMA ERP UNIVERSAL - Layout de Autenticación
// ========================================================

import { Outlet, Navigate } from 'react-router-dom';
import { Box, Container, Paper, Typography } from '@mui/material';

import { useAppSelector } from '@hooks/redux';

function AuthLayout() {
  const { isAuthenticated } = useAppSelector((state) => state.auth);

  // Si ya está autenticado, redirigir al dashboard
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #1976d2 0%, #0d47a1 100%)',
        py: 4,
      }}
    >
      <Container maxWidth="sm">
        {/* Logo y título */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography
            variant="h3"
            component="h1"
            sx={{
              color: 'white',
              fontWeight: 700,
              mb: 1,
            }}
          >
            ERP Universal
          </Typography>
          <Typography
            variant="subtitle1"
            sx={{ color: 'rgba(255,255,255,0.8)' }}
          >
            Sistema de Gestión Empresarial
          </Typography>
        </Box>

        {/* Card de contenido */}
        <Paper
          elevation={8}
          sx={{
            p: { xs: 3, sm: 4 },
            borderRadius: 3,
          }}
        >
          <Outlet />
        </Paper>

        {/* Footer */}
        <Typography
          variant="body2"
          sx={{
            color: 'rgba(255,255,255,0.6)',
            textAlign: 'center',
            mt: 4,
          }}
        >
          © {new Date().getFullYear()} ERP Universal. Todos los derechos reservados.
        </Typography>
      </Container>
    </Box>
  );
}

export default AuthLayout;
