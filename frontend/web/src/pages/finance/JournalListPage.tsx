import { Box, Typography, Paper } from '@mui/material';

function JournalListPage() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>Diarios Contables</Typography>
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">Lista de diarios - Por implementar</Typography>
      </Paper>
    </Box>
  );
}

export default JournalListPage;
