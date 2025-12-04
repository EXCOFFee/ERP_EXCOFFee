import { Box, Typography, Paper } from '@mui/material';
import { useParams } from 'react-router-dom';

function CustomerDetailPage() {
  const { id } = useParams();
  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>Detalle del Cliente</Typography>
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">Cliente ID: {id} - Por implementar</Typography>
      </Paper>
    </Box>
  );
}

export default CustomerDetailPage;
