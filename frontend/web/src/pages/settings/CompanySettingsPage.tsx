import { Box, Typography, Paper } from '@mui/material';

function CompanySettingsPage() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>Configuración de la Empresa</Typography>
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">Datos de la empresa - Por implementar</Typography>
      </Paper>
    </Box>
  );
}

export default CompanySettingsPage;
