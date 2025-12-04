import { Box, Typography, Paper, Grid } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import {
  Business as CompanyIcon,
  People as UsersIcon,
  Security as RolesIcon,
  Tune as GeneralIcon,
} from '@mui/icons-material';

function SettingsPage() {
  const navigate = useNavigate();

  const settingsCards = [
    { title: 'Empresa', description: 'Configuración de la empresa', icon: <CompanyIcon sx={{ fontSize: 40 }} />, path: '/settings/company' },
    { title: 'Usuarios', description: 'Gestión de usuarios', icon: <UsersIcon sx={{ fontSize: 40 }} />, path: '/settings/users' },
    { title: 'Roles y Permisos', description: 'Control de acceso', icon: <RolesIcon sx={{ fontSize: 40 }} />, path: '/settings/roles' },
    { title: 'General', description: 'Preferencias del sistema', icon: <GeneralIcon sx={{ fontSize: 40 }} />, path: '/settings' },
  ];

  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>Configuración</Typography>
      <Grid container spacing={3}>
        {settingsCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Paper 
              sx={{ p: 3, textAlign: 'center', cursor: 'pointer', '&:hover': { boxShadow: 6 } }}
              onClick={() => navigate(card.path)}
            >
              <Box sx={{ color: 'primary.main', mb: 2 }}>{card.icon}</Box>
              <Typography variant="h6">{card.title}</Typography>
              <Typography variant="body2" color="text.secondary">{card.description}</Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default SettingsPage;
