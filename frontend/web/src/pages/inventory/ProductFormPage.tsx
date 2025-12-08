// ========================================================
// SISTEMA ERP UNIVERSAL - Formulario de Producto
// ========================================================

import { useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  InputAdornment,
  CircularProgress,
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { Save as SaveIcon, Cancel as CancelIcon } from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from 'notistack';
import { inventoryService } from '../../services/inventory.service';

const productSchema = z.object({
  sku: z.string().min(1, 'SKU es requerido'),
  barcode: z.string().optional(),
  name: z.string().min(1, 'Nombre es requerido'),
  description: z.string().optional(),
  category: z.string().optional(),
  brand: z.string().optional(),
  unit: z.string().min(1, 'Unidad de medida es requerida'),
  cost_price: z.number().min(0, 'El costo debe ser mayor o igual a 0'),
  sale_price: z.number().min(0, 'El precio debe ser mayor o igual a 0'),
  min_stock: z.number().min(0, 'Stock mínimo debe ser mayor o igual a 0'),
  max_stock: z.number().min(0, 'Stock máximo debe ser mayor o igual a 0'),
  reorder_point: z.number().min(0, 'Punto de reorden debe ser mayor o igual a 0'),
  is_active: z.boolean(),
  track_inventory: z.boolean(),
  track_lots: z.boolean(),
  track_serials: z.boolean(),
});

type ProductFormData = z.infer<typeof productSchema>;

function ProductFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const isEdit = Boolean(id);

  const { control, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<ProductFormData>({
    resolver: zodResolver(productSchema),
    defaultValues: {
      sku: '',
      barcode: '',
      name: '',
      description: '',
      category: '',
      brand: '',
      unit: '',
      cost_price: 0,
      sale_price: 0,
      min_stock: 0,
      max_stock: 0,
      reorder_point: 0,
      is_active: true,
      track_inventory: true,
      track_lots: false,
      track_serials: false,
    },
  });

  // Query para obtener producto existente
  const { data: product, isLoading: loadingProduct } = useQuery({
    queryKey: ['product', id],
    queryFn: () => inventoryService.getProduct(id!),
    enabled: isEdit,
  });

  // Queries para datos de referencia
  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: () => inventoryService.getCategories(),
  });

  const { data: brands } = useQuery({
    queryKey: ['brands'],
    queryFn: () => inventoryService.getBrands(),
  });

  const { data: units } = useQuery({
    queryKey: ['units'],
    queryFn: () => inventoryService.getUnits(),
  });

  // Cargar datos del producto cuando se edita
  useEffect(() => {
    if (product) {
      reset({
        sku: product.sku,
        barcode: product.barcode || '',
        name: product.name,
        description: product.description || '',
        category: typeof product.category === 'object' ? product.category?.id : product.category || '',
        brand: typeof product.brand === 'object' ? product.brand?.id : product.brand || '',
        unit: typeof product.unit === 'object' ? product.unit?.id : product.unit || '',
        cost_price: product.cost_price,
        sale_price: product.sale_price,
        min_stock: product.min_stock,
        max_stock: product.max_stock,
        reorder_point: product.reorder_point,
        is_active: product.is_active,
        track_inventory: product.track_inventory,
        track_lots: product.track_lots,
        track_serials: product.track_serials,
      });
    }
  }, [product, reset]);

  // Mutation para crear/actualizar
  const mutation = useMutation({
    mutationFn: (data: ProductFormData) => {
      if (isEdit) {
        return inventoryService.updateProduct(id!, data);
      }
      return inventoryService.createProduct(data);
    },
    onSuccess: () => {
      enqueueSnackbar(
        isEdit ? 'Producto actualizado correctamente' : 'Producto creado correctamente',
        { variant: 'success' }
      );
      queryClient.invalidateQueries({ queryKey: ['products'] });
      navigate('/inventory/products');
    },
    onError: () => {
      enqueueSnackbar('Error al guardar el producto', { variant: 'error' });
    },
  });

  const onSubmit = (data: ProductFormData) => {
    mutation.mutate(data);
  };

  if (isEdit && loadingProduct) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        {isEdit ? 'Editar Producto' : 'Nuevo Producto'}
      </Typography>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Información Básica
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Controller
                name="sku"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="SKU"
                    fullWidth
                    error={!!errors.sku}
                    helperText={errors.sku?.message}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Controller
                name="barcode"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Código de Barras"
                    fullWidth
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Controller
                name="unit"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.unit}>
                    <InputLabel>Unidad de Medida</InputLabel>
                    <Select {...field} label="Unidad de Medida">
                      {units?.results?.map((unit) => (
                        <MenuItem key={unit.id} value={unit.id}>
                          {unit.name} ({unit.symbol})
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
            <Grid item xs={12}>
              <Controller
                name="name"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Nombre del Producto"
                    fullWidth
                    error={!!errors.name}
                    helperText={errors.name?.message}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12}>
              <Controller
                name="description"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Descripción"
                    fullWidth
                    multiline
                    rows={3}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Controller
                name="category"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>Categoría</InputLabel>
                    <Select {...field} label="Categoría">
                      <MenuItem value="">Sin categoría</MenuItem>
                      {categories?.results?.map((cat) => (
                        <MenuItem key={cat.id} value={cat.id}>
                          {cat.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Controller
                name="brand"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>Marca</InputLabel>
                    <Select {...field} label="Marca">
                      <MenuItem value="">Sin marca</MenuItem>
                      {brands?.results?.map((brand) => (
                        <MenuItem key={brand.id} value={brand.id}>
                          {brand.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>
          </Grid>
        </Paper>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Precios
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Controller
                name="cost_price"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Precio de Costo"
                    type="number"
                    fullWidth
                    InputProps={{
                      startAdornment: <InputAdornment position="start">$</InputAdornment>,
                    }}
                    onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                    error={!!errors.cost_price}
                    helperText={errors.cost_price?.message}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Controller
                name="sale_price"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Precio de Venta"
                    type="number"
                    fullWidth
                    InputProps={{
                      startAdornment: <InputAdornment position="start">$</InputAdornment>,
                    }}
                    onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                    error={!!errors.sale_price}
                    helperText={errors.sale_price?.message}
                  />
                )}
              />
            </Grid>
          </Grid>
        </Paper>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Control de Stock
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Controller
                name="min_stock"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Stock Mínimo"
                    type="number"
                    fullWidth
                    onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                    error={!!errors.min_stock}
                    helperText={errors.min_stock?.message}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Controller
                name="max_stock"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Stock Máximo"
                    type="number"
                    fullWidth
                    onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                    error={!!errors.max_stock}
                    helperText={errors.max_stock?.message}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Controller
                name="reorder_point"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Punto de Reorden"
                    type="number"
                    fullWidth
                    onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                    error={!!errors.reorder_point}
                    helperText={errors.reorder_point?.message}
                  />
                )}
              />
            </Grid>
          </Grid>
        </Paper>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Configuración
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Controller
                name="is_active"
                control={control}
                render={({ field }) => (
                  <FormControlLabel
                    control={<Switch checked={field.value} onChange={field.onChange} />}
                    label="Activo"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Controller
                name="track_inventory"
                control={control}
                render={({ field }) => (
                  <FormControlLabel
                    control={<Switch checked={field.value} onChange={field.onChange} />}
                    label="Controlar Inventario"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Controller
                name="track_lots"
                control={control}
                render={({ field }) => (
                  <FormControlLabel
                    control={<Switch checked={field.value} onChange={field.onChange} />}
                    label="Manejar Lotes"
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Controller
                name="track_serials"
                control={control}
                render={({ field }) => (
                  <FormControlLabel
                    control={<Switch checked={field.value} onChange={field.onChange} />}
                    label="Manejar Seriales"
                  />
                )}
              />
            </Grid>
          </Grid>
        </Paper>

        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          <Button
            variant="outlined"
            startIcon={<CancelIcon />}
            onClick={() => navigate(-1)}
          >
            Cancelar
          </Button>
          <Button
            type="submit"
            variant="contained"
            startIcon={<SaveIcon />}
            disabled={isSubmitting || mutation.isPending}
          >
            {mutation.isPending ? 'Guardando...' : isEdit ? 'Guardar Cambios' : 'Crear Producto'}
          </Button>
        </Box>
      </form>
    </Box>
  );
}

export default ProductFormPage;
