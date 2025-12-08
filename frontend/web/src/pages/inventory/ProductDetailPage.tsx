// ========================================================
// SISTEMA ERP UNIVERSAL - Detalle de Producto
// ========================================================

import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  Button,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Avatar,
  Divider,
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { Edit as EditIcon, ArrowBack as BackIcon } from '@mui/icons-material';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { inventoryService } from '../../services/inventory.service';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

function ProductDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);

  const { data: product, isLoading } = useQuery({
    queryKey: ['product', id],
    queryFn: () => inventoryService.getProduct(id!),
    enabled: !!id,
  });

  const { data: stocks } = useQuery({
    queryKey: ['product-stocks', id],
    queryFn: () => inventoryService.getStock({ product: id }),
    enabled: !!id,
  });

  const { data: movements } = useQuery({
    queryKey: ['product-movements', id],
    queryFn: () => inventoryService.getStockMovements({ product: id, page_size: 20 }),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!product) {
    return (
      <Box sx={{ textAlign: 'center', p: 4 }}>
        <Typography>Producto no encontrado</Typography>
        <Button onClick={() => navigate('/inventory/products')}>Volver a la lista</Button>
      </Box>
    );
  }

  const InfoRow = ({ label, value }: { label: string; value: React.ReactNode }) => (
    <Box sx={{ display: 'flex', py: 1.5, borderBottom: '1px solid', borderColor: 'divider' }}>
      <Typography sx={{ width: 200, color: 'text.secondary', fontWeight: 500 }}>{label}</Typography>
      <Typography sx={{ flex: 1 }}>{value || '-'}</Typography>
    </Box>
  );

  const movementTypes: Record<string, string> = {
    in: 'Entrada',
    out: 'Salida',
    adjustment: 'Ajuste',
    transfer: 'Transferencia',
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<BackIcon />}
            onClick={() => navigate('/inventory/products')}
          >
            Volver
          </Button>
          <Typography variant="h4" fontWeight={600}>
            {product.name}
          </Typography>
          <Chip
            label={product.is_active ? 'Activo' : 'Inactivo'}
            color={product.is_active ? 'success' : 'default'}
          />
        </Box>
        <Button
          variant="contained"
          startIcon={<EditIcon />}
          onClick={() => navigate(`/inventory/products/${id}/edit`)}
        >
          Editar
        </Button>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
          <Tab label="Información General" />
          <Tab label="Stock por Almacén" />
          <Tab label="Historial de Movimientos" />
        </Tabs>
      </Paper>

      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Avatar
                src={product.image}
                variant="rounded"
                sx={{ width: 200, height: 200, mx: 'auto', mb: 2, fontSize: 60 }}
              >
                {product.name?.charAt(0)}
              </Avatar>
              <Typography variant="h6" gutterBottom>{product.name}</Typography>
              <Typography color="text.secondary">SKU: {product.sku}</Typography>
              {product.barcode && (
                <Typography color="text.secondary">Código: {product.barcode}</Typography>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>Información del Producto</Typography>
              <Divider sx={{ mb: 2 }} />
              <InfoRow label="Descripción" value={product.description} />
              <InfoRow
                label="Categoría"
                value={typeof product.category === 'object' ? product.category?.name : '-'}
              />
              <InfoRow
                label="Marca"
                value={typeof product.brand === 'object' ? product.brand?.name : '-'}
              />
              <InfoRow
                label="Unidad de Medida"
                value={typeof product.unit === 'object' ? `${product.unit?.name} (${product.unit?.symbol})` : '-'}
              />
            </Paper>

            <Paper sx={{ p: 3, mt: 3 }}>
              <Typography variant="h6" gutterBottom>Precios</Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={3}>
                <Grid item xs={6}>
                  <Typography color="text.secondary">Precio de Costo</Typography>
                  <Typography variant="h5" fontWeight={600}>
                    ${product.cost_price?.toFixed(2)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography color="text.secondary">Precio de Venta</Typography>
                  <Typography variant="h5" fontWeight={600} color="primary">
                    ${product.sale_price?.toFixed(2)}
                  </Typography>
                </Grid>
              </Grid>
            </Paper>

            <Paper sx={{ p: 3, mt: 3 }}>
              <Typography variant="h6" gutterBottom>Control de Stock</Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={3}>
                <Grid item xs={4}>
                  <Typography color="text.secondary">Stock Mínimo</Typography>
                  <Typography variant="h6">{product.min_stock}</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography color="text.secondary">Stock Máximo</Typography>
                  <Typography variant="h6">{product.max_stock}</Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography color="text.secondary">Punto de Reorden</Typography>
                  <Typography variant="h6">{product.reorder_point}</Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Almacén</TableCell>
                  <TableCell align="right">En Stock</TableCell>
                  <TableCell align="right">Reservado</TableCell>
                  <TableCell align="right">Disponible</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {stocks?.results?.length ? (
                  stocks.results.map((stock) => (
                    <TableRow key={stock.id}>
                      <TableCell>
                        {typeof stock.warehouse === 'object' ? stock.warehouse?.name : stock.warehouse}
                      </TableCell>
                      <TableCell align="right">{stock.quantity}</TableCell>
                      <TableCell align="right">{stock.reserved_quantity}</TableCell>
                      <TableCell align="right">
                        <Typography fontWeight={600} color="primary">
                          {stock.available_quantity}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={4} align="center">
                      <Typography color="text.secondary" sx={{ py: 3 }}>
                        No hay stock registrado para este producto
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Fecha</TableCell>
                  <TableCell>Tipo</TableCell>
                  <TableCell>Almacén</TableCell>
                  <TableCell align="right">Cantidad</TableCell>
                  <TableCell>Referencia</TableCell>
                  <TableCell>Notas</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {movements?.results?.length ? (
                  movements.results.map((mov) => (
                    <TableRow key={mov.id}>
                      <TableCell>
                        {format(new Date(mov.created_at), 'dd/MM/yyyy HH:mm', { locale: es })}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={movementTypes[mov.movement_type] || mov.movement_type}
                          size="small"
                          color={
                            mov.movement_type === 'in' ? 'success' :
                            mov.movement_type === 'out' ? 'error' :
                            mov.movement_type === 'adjustment' ? 'warning' : 'info'
                          }
                        />
                      </TableCell>
                      <TableCell>{mov.warehouse}</TableCell>
                      <TableCell align="right">
                        <Typography
                          fontWeight={600}
                          color={mov.movement_type === 'out' ? 'error.main' : 'success.main'}
                        >
                          {mov.movement_type === 'out' ? '-' : '+'}{mov.quantity}
                        </Typography>
                      </TableCell>
                      <TableCell>{mov.reference || '-'}</TableCell>
                      <TableCell>{mov.notes || '-'}</TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography color="text.secondary" sx={{ py: 3 }}>
                        No hay movimientos registrados para este producto
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </TabPanel>
    </Box>
  );
}

export default ProductDetailPage;
