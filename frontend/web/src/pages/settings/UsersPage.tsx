// ========================================================
// SISTEMA ERP UNIVERSAL - Gestión de Usuarios
// ========================================================

import { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Grid,
  Avatar,
  Tooltip,
  InputAdornment,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Lock as LockIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import DataTable from '../../components/common/DataTable';
import { userService, roleService, User, Role } from '../../services/settings.service';
import { useSnackbar } from 'notistack';


const userSchema = z.object({
  email: z.string().email('Email inválido'),
  first_name: z.string().min(1, 'Nombre requerido'),
  last_name: z.string().min(1, 'Apellido requerido'),
  password: z.string().min(8, 'Mínimo 8 caracteres').optional().or(z.literal('')),
  role_id: z.string().optional(),
  is_active: z.boolean(),
});

type UserFormData = z.infer<typeof userSchema>;

function UsersPage() {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [search, setSearch] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<User | null>(null);

  const { control, handleSubmit, reset, formState: { errors } } = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
    defaultValues: {
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      role_id: '',
      is_active: true,
    },
  });

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['users', page, pageSize, search],
    queryFn: () => userService.list({
      page: page + 1,
      page_size: pageSize,
      search: search || undefined,
    }),
  });

  const { data: rolesData } = useQuery({
    queryKey: ['roles'],
    queryFn: () => roleService.list({ page_size: 100 }),
  });

  const createMutation = useMutation({
    mutationFn: (data: UserFormData) => userService.create({
      email: data.email,
      password: data.password || 'TempPass123!',
      first_name: data.first_name,
      last_name: data.last_name,
      role_id: data.role_id || undefined,
      is_active: data.is_active,
    }),
    onSuccess: () => {
      enqueueSnackbar('Usuario creado', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['users'] });
      handleCloseDialog();
    },
    onError: () => {
      enqueueSnackbar('Error al crear usuario', { variant: 'error' });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<User> }) =>
      userService.update(id, data),
    onSuccess: () => {
      enqueueSnackbar('Usuario actualizado', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['users'] });
      handleCloseDialog();
    },
    onError: () => {
      enqueueSnackbar('Error al actualizar usuario', { variant: 'error' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => userService.delete(id),
    onSuccess: () => {
      enqueueSnackbar('Usuario eliminado', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setDeleteDialogOpen(false);
    },
    onError: () => {
      enqueueSnackbar('Error al eliminar usuario', { variant: 'error' });
    },
  });

  const handleOpenDialog = (user?: User) => {
    if (user) {
      setEditingUser(user);
      reset({
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
        password: '',
        role_id: user.role?.id || '',
        is_active: user.is_active,
      });
    } else {
      setEditingUser(null);
      reset({
        email: '',
        first_name: '',
        last_name: '',
        password: '',
        role_id: '',
        is_active: true,
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingUser(null);
    reset();
  };

  const onSubmit = (data: UserFormData) => {
    if (editingUser) {
      updateMutation.mutate({
        id: editingUser.id,
        data: {
          first_name: data.first_name,
          last_name: data.last_name,
          role_id: data.role_id || undefined,
          is_active: data.is_active,
        } as any,
      });
    } else {
      createMutation.mutate(data);
    }
  };

  const formatDate = (date: string) =>
    new Date(date).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });

  const columns: GridColDef[] = [
    {
      field: 'user',
      headerName: 'Usuario',
      flex: 1,
      minWidth: 250,
      renderCell: (params: GridRenderCellParams) => (
        <Box display="flex" alignItems="center" gap={2}>
          <Avatar sx={{ bgcolor: 'primary.main' }}>
            {params.row.first_name?.[0]}{params.row.last_name?.[0]}
          </Avatar>
          <Box>
            <Typography variant="body2" fontWeight={500}>
              {params.row.full_name || `${params.row.first_name} ${params.row.last_name}`}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {params.row.email}
            </Typography>
          </Box>
        </Box>
      ),
    },
    {
      field: 'role',
      headerName: 'Rol',
      width: 150,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.row.role?.name || 'Sin rol'}
          size="small"
          color={params.row.role ? 'primary' : 'default'}
          variant="outlined"
        />
      ),
    },
    {
      field: 'is_active',
      headerName: 'Estado',
      width: 120,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value ? 'Activo' : 'Inactivo'}
          size="small"
          color={params.value ? 'success' : 'default'}
        />
      ),
    },
    {
      field: 'last_login',
      headerName: 'Último Acceso',
      width: 160,
      renderCell: (params: GridRenderCellParams) =>
        params.value ? formatDate(params.value) : 'Nunca',
    },
    {
      field: 'created_at',
      headerName: 'Creado',
      width: 140,
      renderCell: (params: GridRenderCellParams) =>
        params.value ? formatDate(params.value) : '-',
    },
    {
      field: 'actions',
      headerName: 'Acciones',
      width: 150,
      sortable: false,
      renderCell: (params: GridRenderCellParams) => (
        <Box>
          <Tooltip title="Editar">
            <IconButton size="small" onClick={() => handleOpenDialog(params.row)}>
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Restablecer contraseña">
            <IconButton size="small" color="warning">
              <LockIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Eliminar">
            <IconButton
              size="small"
              color="error"
              onClick={() => {
                setUserToDelete(params.row);
                setDeleteDialogOpen(true);
              }}
            >
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight={600}>
          Gestión de Usuarios
        </Typography>
        <Box display="flex" gap={1}>
          <TextField
            size="small"
            placeholder="Buscar usuarios..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ width: 250 }}
          />
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => refetch()}
          >
            Actualizar
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Nuevo Usuario
          </Button>
        </Box>
      </Box>

      <DataTable
        rows={data?.results || []}
        columns={columns}
        loading={isLoading}
        rowCount={data?.count || 0}
        paginationMode="server"
        pageSize={pageSize}
        onPaginationChange={(model) => {
          setPage(model.page);
          setPageSize(model.pageSize);
        }}
        getRowId={(row) => row.id}
      />

      {/* Dialog para crear/editar */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>
            {editingUser ? 'Editar Usuario' : 'Nuevo Usuario'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="first_name"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Nombre"
                      fullWidth
                      error={!!errors.first_name}
                      helperText={errors.first_name?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="last_name"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Apellido"
                      fullWidth
                      error={!!errors.last_name}
                      helperText={errors.last_name?.message}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="email"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Email"
                      type="email"
                      fullWidth
                      disabled={!!editingUser}
                      error={!!errors.email}
                      helperText={errors.email?.message}
                    />
                  )}
                />
              </Grid>
              {!editingUser && (
                <Grid item xs={12}>
                  <Controller
                    name="password"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Contraseña"
                        type="password"
                        fullWidth
                        error={!!errors.password}
                        helperText={errors.password?.message || 'Mínimo 8 caracteres'}
                      />
                    )}
                  />
                </Grid>
              )}
              <Grid item xs={12}>
                <Controller
                  name="role_id"
                  control={control}
                  render={({ field }) => (
                    <FormControl fullWidth>
                      <InputLabel>Rol</InputLabel>
                      <Select {...field} label="Rol">
                        <MenuItem value="">Sin rol</MenuItem>
                        {rolesData?.results?.map((role: Role) => (
                          <MenuItem key={role.id} value={role.id}>
                            {role.name}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Controller
                  name="is_active"
                  control={control}
                  render={({ field }) => (
                    <FormControlLabel
                      control={<Switch {...field} checked={field.value} />}
                      label="Usuario activo"
                    />
                  )}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancelar</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={createMutation.isPending || updateMutation.isPending}
            >
              {editingUser ? 'Guardar' : 'Crear'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Dialog de confirmación de eliminación */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirmar Eliminación</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Está seguro de eliminar al usuario{' '}
            <strong>{userToDelete?.full_name || `${userToDelete?.first_name} ${userToDelete?.last_name}`}</strong>?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancelar</Button>
          <Button
            color="error"
            variant="contained"
            onClick={() => userToDelete && deleteMutation.mutate(userToDelete.id)}
            disabled={deleteMutation.isPending}
          >
            Eliminar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default UsersPage;
