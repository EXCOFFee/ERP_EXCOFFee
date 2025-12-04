import { Box, Typography, Paper } from '@mui/material';

function AttendancePage() {
  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>Control de Asistencia</Typography>
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">Registro de asistencia - Por implementar</Typography>
      </Paper>
    </Box>
  );
}

export default AttendancePage;
