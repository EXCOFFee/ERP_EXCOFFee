import { Box, Typography, Paper, Grid } from '@mui/material';

function FinancialReportsPage() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>Reportes Financieros</Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Balance General</Typography>
            <Typography color="text.secondary">Por implementar</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Estado de Resultados</Typography>
            <Typography color="text.secondary">Por implementar</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Flujo de Efectivo</Typography>
            <Typography color="text.secondary">Por implementar</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Balanza de Comprobación</Typography>
            <Typography color="text.secondary">Por implementar</Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default FinancialReportsPage;
