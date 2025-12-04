import { Box, Typography, Paper } from '@mui/material';
import { useParams } from 'react-router-dom';

function SalesOrderDetailPage() {
  const { id } = useParams();
  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>Detalle del Pedido</Typography>
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">Pedido ID: {id} - Por implementar</Typography>
      </Paper>
    </Box>
  );
}

export default SalesOrderDetailPage;
