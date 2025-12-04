import { Box, Typography, Paper } from '@mui/material';

function GoodsReceiptListPage() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>Recepciones de Mercancía</Typography>
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">Lista de recepciones - Por implementar</Typography>
      </Paper>
    </Box>
  );
}

export default GoodsReceiptListPage;
