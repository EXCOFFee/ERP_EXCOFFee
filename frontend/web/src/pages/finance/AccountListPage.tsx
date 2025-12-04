import { Box, Typography, Paper } from '@mui/material';

function AccountListPage() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>Plan de Cuentas</Typography>
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">Catálogo de cuentas contables - Por implementar</Typography>
      </Paper>
    </Box>
  );
}

export default AccountListPage;
