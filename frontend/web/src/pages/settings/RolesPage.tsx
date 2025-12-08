// ========================================================
// SISTEMA ERP UNIVERSAL - Gestión de Roles y Permisos
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
  Grid,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControlLabel,
  Checkbox,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import DataTable from '../../components/common/DataTable';
import { roleService, permissionService, Role, Permission } from '../../services/settings.service';
import { useSnackbar } from 'notistack';


const roleSchema = z.object({
  code: z.string().min(1, 'Código requerido'),
  name: z.string().min(1, 'Nombre requerido'),
  description: z.string().optional(),
  permissions: z.array(z.string()).default([]),
});

type RoleFormData = z.infer<typeof roleSchema>;

function RolesPage() {
  const queryClient = useQueryClient();
  const { enqueueSnackbar } = useSnackbar();
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [roleToDelete, setRoleToDelete] = useState<Role | null>(null);
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);

  const { control, handleSubmit, reset, formState: { errors } } = useForm<RoleFormData>({
    resolver: zodResolver(roleSchema),
    defaultValues: {
      code: '',
      name: '',
      description: '',
      permissions: [],
    },
  });

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['roles', page, pageSize],
    queryFn: () => roleService.list({
      page: page + 1,
      page_size: pageSize,
    }),
  });

  const { data: permissionsData } = useQuery({
    queryKey: ['permissions'],
    queryFn: () => permissionService.list({ page_size: 200 }),
  });

  // Agrupar permisos por módulo
  const permissionsByModule = permissionsData?.results?.reduce((acc: Record<string, Permission[]>, perm) => {
    const module = perm.module || 'general';
    if (!acc[module]) acc[module] = [];
    acc[module].push(perm);
    return acc;
  }, {}) || {};

  const createMutation = useMutation({
    mutationFn: (data: RoleFormData) => roleService.create({
      code: data.code,
      name: data.name,
      description: data.description,
      permissions: selectedPermissions,
    }),
    onSuccess: () => {
      enqueueSnackbar('Rol creado', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      handleCloseDialog();
    },
    onError: () => {
      enqueueSnackbar('Error al crear rol', { variant: 'error' });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Role> }) =>
      roleService.update(id, { ...data, permissions: selectedPermissions } as any),
    onSuccess: () => {
      enqueueSnackbar('Rol actualizado', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      handleCloseDialog();
    },
    onError: () => {
      enqueueSnackbar('Error al actualizar rol', { variant: 'error' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => roleService.delete(id),
    onSuccess: () => {
      enqueueSnackbar('Rol eliminado', { variant: 'success' });
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      setDeleteDialogOpen(false);
    },
    onError: () => {
      enqueueSnackbar('Error al eliminar rol', { variant: 'error' });
    },
  });

  const handleOpenDialog = (role?: Role) => {
    if (role) {
      setEditingRole(role);
      setSelectedPermissions(role.permissions?.map(p => p.id) || []);
      reset({
        code: role.code,
        name: role.name,
        description: role.description || '',
        permissions: role.permissions?.map(p => p.id) || [],
      });
    } else {
      setEditingRole(null);
      setSelectedPermissions([]);
      reset({
        code: '',
        name: '',
        description: '',
        permissions: [],
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingRole(null);
    setSelectedPermissions([]);
    reset();
  };

  const handlePermissionToggle = (permId: string) => {
    setSelectedPermissions(prev =>
      prev.includes(permId)
        ? prev.filter(id => id !== permId)
        : [...prev, permId]
    );
  };

  const handleModuleToggle = (_module: string, permissions: Permission[]) => {
    const modulePermIds = permissions.map(p => p.id);
    const allSelected = modulePermIds.every(id => selectedPermissions.includes(id));
    
    if (allSelected) {
      setSelectedPermissions(prev => prev.filter(id => !modulePermIds.includes(id)));
    } else {
      setSelectedPermissions(prev => [...new Set([...prev, ...modulePermIds])]);
    }
  };

  const onSubmit = (data: RoleFormData) => {
    if (editingRole) {
      updateMutation.mutate({
        id: editingRole.id,
        data: {
          name: data.name,
          description: data.description,
        },
      });
    } else {
      createMutation.mutate(data);
    }
  };

  const formatDate = (date: string) =>
    new Date(date).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' });

  const columns: GridColDef[] = [
    {
      field: 'name',
      headerName: 'Nombre',
      flex: 1,
      minWidth: 200,
      renderCell: (params: GridRenderCellParams) => (
        <Box display="flex" alignItems="center" gap={1}>
          <SecurityIcon color="primary" />
          <Box>
            <Typography variant="body2" fontWeight={500}>
              {params.value}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {params.row.code}
            </Typography>
          </Box>
        </Box>
      ),
    },
    {
      field: 'description',
      headerName: 'Descripción',
      flex: 1,
      minWidth: 200,
    },
    {
      field: 'permissions',
      headerName: 'Permisos',
      width: 120,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value?.length || 0}
          size="small"
          color="primary"
          variant="outlined"
        />
      ),
    },
    {
      field: 'is_active',
      headerName: 'Estado',
      width: 100,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value ? 'Activo' : 'Inactivo'}
          size="small"
          color={params.value ? 'success' : 'default'}
        />
      ),
    },
    {
      field: 'created_at',
      headerName: 'Creado',
      width: 120,
      renderCell: (params: GridRenderCellParams) =>
        params.value ? formatDate(params.value) : '-',
    },
    {
      field: 'actions',
      headerName: 'Acciones',
      width: 120,
      sortable: false,
      renderCell: (params: GridRenderCellParams) => (
        <Box>
          <Tooltip title="Editar">
            <IconButton size="small" onClick={() => handleOpenDialog(params.row)}>
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Eliminar">
            <IconButton
              size="small"
              color="error"
              onClick={() => {
                setRoleToDelete(params.row);
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
          Roles y Permisos
        </Typography>
        <Box display="flex" gap={1}>
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
            Nuevo Rol
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
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>
            {editingRole ? 'Editar Rol' : 'Nuevo Rol'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="code"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Código"
                      fullWidth
                      disabled={!!editingRole}
                      error={!!errors.code}
                      helperText={errors.code?.message || 'Identificador único (ej: admin, ventas)'}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="name"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Nombre"
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
                      rows={2}
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12}>
                <Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Permisos ({selectedPermissions.length} seleccionados)
                </Typography>
                {Object.entries(permissionsByModule).map(([module, perms]) => {
                  const modulePermIds = perms.map(p => p.id);
                  const allSelected = modulePermIds.every(id => selectedPermissions.includes(id));
                  const someSelected = modulePermIds.some(id => selectedPermissions.includes(id));

                  return (
                    <Accordion key={module} defaultExpanded={false}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <FormControlLabel
                          onClick={(e) => e.stopPropagation()}
                          control={
                            <Checkbox
                              checked={allSelected}
                              indeterminate={someSelected && !allSelected}
                              onChange={() => handleModuleToggle(module, perms)}
                            />
                          }
                          label={
                            <Typography fontWeight={500} textTransform="capitalize">
                              {module}
                            </Typography>
                          }
                        />
                      </AccordionSummary>
                      <AccordionDetails>
                        <Grid container spacing={1}>
                          {perms.map((perm) => (
                            <Grid item xs={12} sm={6} md={4} key={perm.id}>
                              <FormControlLabel
                                control={
                                  <Checkbox
                                    checked={selectedPermissions.includes(perm.id)}
                                    onChange={() => handlePermissionToggle(perm.id)}
                                    size="small"
                                  />
                                }
                                label={
                                  <Box>
                                    <Typography variant="body2">{perm.name}</Typography>
                                    <Typography variant="caption" color="text.secondary">
                                      {perm.code}
                                    </Typography>
                                  </Box>
                                }
                              />
                            </Grid>
                          ))}
                        </Grid>
                      </AccordionDetails>
                    </Accordion>
                  );
                })}
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
              {editingRole ? 'Guardar' : 'Crear'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Dialog de confirmación de eliminación */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirmar Eliminación</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Está seguro de eliminar el rol <strong>{roleToDelete?.name}</strong>?
          </Typography>
          <Typography variant="body2" color="error" sx={{ mt: 1 }}>
            Los usuarios con este rol perderán sus permisos asociados.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancelar</Button>
          <Button
            color="error"
            variant="contained"
            onClick={() => roleToDelete && deleteMutation.mutate(roleToDelete.id)}
            disabled={deleteMutation.isPending}
          >
            Eliminar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default RolesPage;
