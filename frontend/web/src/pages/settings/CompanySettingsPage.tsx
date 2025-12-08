// ========================================================
// SISTEMA ERP UNIVERSAL - Configuración de la Empresa
// ========================================================

import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  Avatar,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Save as SaveIcon,
  Business as BusinessIcon,
  Upload as UploadIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { companyService, Company } from '../../services/settings.service';
import { useSnackbar } from 'notistack';

const companySchema = z.object({
  name: z.string().min(1, 'Nombre requerido'),
  legal_name: z.string().min(1, 'Razón social requerida'),
  tax_id: z.string().min(1, 'Identificación fiscal requerida'),
  email: z.string().email('Email inválido').optional().or(z.literal('')),
  phone: z.string().optional(),
  address: z.string().optional(),
  city: z.string().optional(),
  state: z.string().optional(),
  country: z.string().optional(),
  postal_code: z.string().optional(),
  website: z.string().url('URL inválida').optional().or(z.literal('')),
  currency: z.string().min(1, 'Moneda requerida'),
  timezone: z.string().min(1, 'Zona horaria requerida'),
  date_format: z.string().min(1, 'Formato de fecha requerido'),
  fiscal_year_start: z.number().min(1).max(12),
});

type CompanyFormData = z.infer<typeof companySchema>;

const currencies = [
  { code: 'USD', name: 'Dólar Estadounidense' },
  { code: 'EUR', name: 'Euro' },
  { code: 'MXN', name: 'Peso Mexicano' },
  { code: 'COP', name: 'Peso Colombiano' },
  { code: 'ARS', name: 'Peso Argentino' },
  { code: 'CLP', name: 'Peso Chileno' },
  { code: 'PEN', name: 'Sol Peruano' },
];

const timezones = [
  { code: 'America/New_York', name: 'Nueva York (EST)' },
  { code: 'America/Chicago', name: 'Chicago (CST)' },
  { code: 'America/Denver', name: 'Denver (MST)' },
  { code: 'America/Los_Angeles', name: 'Los Angeles (PST)' },
  { code: 'America/Mexico_City', name: 'Ciudad de México' },
  { code: 'America/Bogota', name: 'Bogotá' },
  { code: 'America/Lima', name: 'Lima' },
  { code: 'America/Santiago', name: 'Santiago' },
  { code: 'America/Buenos_Aires', name: 'Buenos Aires' },
  { code: 'Europe/Madrid', name: 'Madrid' },
  { code: 'UTC', name: 'UTC' },
];

const dateFormats = [
  { code: 'DD/MM/YYYY', name: 'DD/MM/YYYY' },
  { code: 'MM/DD/YYYY', name: 'MM/DD/YYYY' },
  { code: 'YYYY-MM-DD', name: 'YYYY-MM-DD' },
];

const months = [
  { value: 1, name: 'Enero' },
  { value: 2, name: 'Febrero' },
  { value: 3, name: 'Marzo' },
  { value: 4, name: 'Abril' },
  { value: 5, name: 'Mayo' },
  { value: 6, name: 'Junio' },
  { value: 7, name: 'Julio' },
  { value: 8, name: 'Agosto' },
  { value: 9, name: 'Septiembre' },
  { value: 10, name: 'Octubre' },
  { value: 11, name: 'Noviembre' },
  { value: 12, name: 'Diciembre' },
];

function CompanySettingsPage() {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [_logoFile, setLogoFile] = useState<File | null>(null);

  const { control, handleSubmit, reset, formState: { errors, isDirty } } = useForm<CompanyFormData>({
    resolver: zodResolver(companySchema),
    defaultValues: {
      name: '',
      legal_name: '',
      tax_id: '',
      email: '',
      phone: '',
      address: '',
      city: '',
      state: '',
      country: '',
      postal_code: '',
      website: '',
      currency: 'USD',
      timezone: 'America/New_York',
      date_format: 'DD/MM/YYYY',
      fiscal_year_start: 1,
    },
  });

  const { data: company, isLoading, error, refetch } = useQuery({
    queryKey: ['company'],
    queryFn: companyService.get,
    retry: false,
  });

  // Actualizar form cuando llegan los datos
  if (company && !isDirty) {
    reset({
      name: company.name || '',
      legal_name: company.legal_name || '',
      tax_id: company.tax_id || '',
      email: company.email || '',
      phone: company.phone || '',
      address: company.address || '',
      city: company.city || '',
      state: company.state || '',
      country: company.country || '',
      postal_code: company.postal_code || '',
      website: company.website || '',
      currency: company.currency || 'USD',
      timezone: company.timezone || 'America/New_York',
      date_format: company.date_format || 'DD/MM/YYYY',
      fiscal_year_start: company.fiscal_year_start || 1,
    });
  }

  const updateMutation = useMutation({
    mutationFn: (data: Partial<Company>) => companyService.update(data),
    onSuccess: () => {
      enqueueSnackbar('Configuración guardada', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['company'] });
    },
    onError: () => {
      enqueueSnackbar('Error al guardar', { variant: 'error' });
    },
  });

  const onSubmit = (data: CompanyFormData) => {
    updateMutation.mutate(data as any);
  };

  const handleLogoChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setLogoFile(file);
      // Upload logo immediately
      companyService.uploadLogo(file).then(() => {
        enqueueSnackbar('Logo actualizado', { variant: 'success' });
        queryClient.invalidateQueries({ queryKey: ['company'] });
      }).catch(() => {
        enqueueSnackbar('Error al subir logo', { variant: 'error' });
      });
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight={600}>
          Configuración de la Empresa
        </Typography>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => refetch()}
          >
            Recargar
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSubmit(onSubmit)}
            disabled={updateMutation.isPending}
          >
            Guardar Cambios
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="info" sx={{ mb: 3 }}>
          No se encontró configuración de empresa. Complete los datos para crear una.
        </Alert>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        <Grid container spacing={3}>
          {/* Logo y datos básicos */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
                  <Avatar
                    src={company?.logo || undefined}
                    sx={{ width: 120, height: 120, bgcolor: 'primary.main' }}
                  >
                    <BusinessIcon sx={{ fontSize: 60 }} />
                  </Avatar>
                  <input
                    type="file"
                    accept="image/*"
                    id="logo-upload"
                    style={{ display: 'none' }}
                    onChange={handleLogoChange}
                  />
                  <label htmlFor="logo-upload">
                    <Button
                      variant="outlined"
                      component="span"
                      startIcon={<UploadIcon />}
                      size="small"
                    >
                      Cambiar Logo
                    </Button>
                  </label>
                  <Typography variant="caption" color="text.secondary" align="center">
                    Formatos: JPG, PNG. Tamaño máximo: 2MB
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Información de la empresa */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Información de la Empresa
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Controller
                    name="name"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Nombre Comercial"
                        fullWidth
                        error={!!errors.name}
                        helperText={errors.name?.message}
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Controller
                    name="legal_name"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Razón Social"
                        fullWidth
                        error={!!errors.legal_name}
                        helperText={errors.legal_name?.message}
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Controller
                    name="tax_id"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Identificación Fiscal (NIF/RUC/RFC)"
                        fullWidth
                        error={!!errors.tax_id}
                        helperText={errors.tax_id?.message}
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Controller
                    name="email"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Email"
                        type="email"
                        fullWidth
                        error={!!errors.email}
                        helperText={errors.email?.message}
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Controller
                    name="phone"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Teléfono"
                        fullWidth
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Controller
                    name="website"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Sitio Web"
                        fullWidth
                        error={!!errors.website}
                        helperText={errors.website?.message}
                      />
                    )}
                  />
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Dirección */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Dirección
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Controller
                    name="address"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Dirección"
                        fullWidth
                        multiline
                        rows={2}
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Controller
                    name="city"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Ciudad"
                        fullWidth
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Controller
                    name="state"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Estado/Provincia"
                        fullWidth
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Controller
                    name="country"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="País"
                        fullWidth
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Controller
                    name="postal_code"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Código Postal"
                        fullWidth
                      />
                    )}
                  />
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Configuración Regional */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Configuración Regional
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Controller
                    name="currency"
                    control={control}
                    render={({ field }) => (
                      <FormControl fullWidth error={!!errors.currency}>
                        <InputLabel>Moneda</InputLabel>
                        <Select {...field} label="Moneda">
                          {currencies.map((currency) => (
                            <MenuItem key={currency.code} value={currency.code}>
                              {currency.code} - {currency.name}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    )}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Controller
                    name="timezone"
                    control={control}
                    render={({ field }) => (
                      <FormControl fullWidth error={!!errors.timezone}>
                        <InputLabel>Zona Horaria</InputLabel>
                        <Select {...field} label="Zona Horaria">
                          {timezones.map((tz) => (
                            <MenuItem key={tz.code} value={tz.code}>
                              {tz.name}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    )}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Controller
                    name="date_format"
                    control={control}
                    render={({ field }) => (
                      <FormControl fullWidth error={!!errors.date_format}>
                        <InputLabel>Formato de Fecha</InputLabel>
                        <Select {...field} label="Formato de Fecha">
                          {dateFormats.map((df) => (
                            <MenuItem key={df.code} value={df.code}>
                              {df.name}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    )}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Controller
                    name="fiscal_year_start"
                    control={control}
                    render={({ field }) => (
                      <FormControl fullWidth error={!!errors.fiscal_year_start}>
                        <InputLabel>Inicio Año Fiscal</InputLabel>
                        <Select {...field} label="Inicio Año Fiscal">
                          {months.map((month) => (
                            <MenuItem key={month.value} value={month.value}>
                              {month.name}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    )}
                  />
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      </form>
    </Box>
  );
}

export default CompanySettingsPage;
