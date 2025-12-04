import { Box, Typography, Paper } from '@mui/material';

function DepartmentListPage() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>Departamentos</Typography>
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">Estructura organizacional - Por implementar</Typography>
      </Paper>
    </Box>
  );
}

export default DepartmentListPage;
