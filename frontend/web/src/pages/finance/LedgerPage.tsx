import { Box, Typography, Paper } from '@mui/material';

function LedgerPage() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>Libro Mayor</Typography>
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">Libro mayor general - Por implementar</Typography>
      </Paper>
    </Box>
  );
}

export default LedgerPage;
