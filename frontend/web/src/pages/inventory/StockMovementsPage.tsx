// ========================================================
// SISTEMA ERP UNIVERSAL - Movimientos de Stock
// ========================================================

import { Box, Typography, Paper, Tabs, Tab } from '@mui/material';
import { useState } from 'react';

function StockMovementsPage() {
  const [tabValue, setTabValue] = useState(0);

  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        Movimientos de Inventario
      </Typography>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
          <Tab label="Todos" />
          <Tab label="Entradas" />
          <Tab label="Salidas" />
          <Tab label="Transferencias" />
          <Tab label="Ajustes" />
        </Tabs>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary">
          Historial de movimientos - Por implementar
        </Typography>
      </Paper>
    </Box>
  );
}

export default StockMovementsPage;
