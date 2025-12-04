import { Box, Typography, Paper } from '@mui/material';

function PayrollPage() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>Nómina</Typography>
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">Gestión de nómina - Por implementar</Typography>
      </Paper>
    </Box>
  );
}

export default PayrollPage;
