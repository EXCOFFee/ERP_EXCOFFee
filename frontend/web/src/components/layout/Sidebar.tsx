// ========================================================
// SISTEMA ERP UNIVERSAL - Componente Sidebar
// ========================================================

import { useLocation, useNavigate } from 'react-router-dom';
import {
  Drawer,
  Box,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Collapse,
  Tooltip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Inventory as InventoryIcon,
  ShoppingCart as SalesIcon,
  LocalShipping as PurchasingIcon,
  AccountBalance as FinanceIcon,
  People as HRIcon,
  Settings as SettingsIcon,
  ExpandLess,
  ExpandMore,
  Category as ProductIcon,
  Warehouse as WarehouseIcon,
  SwapHoriz as MovementIcon,
  Person as CustomerIcon,
  Receipt as OrderIcon,
  Description as InvoiceIcon,
  Store as SupplierIcon,
  AccountTree as AccountIcon,
  Book as JournalIcon,
  Assessment as ReportIcon,
  Badge as EmployeeIcon,
  Business as DepartmentIcon,
  Payments as PayrollIcon,
  Schedule as AttendanceIcon,
} from '@mui/icons-material';
import { useState } from 'react';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  collapsed: boolean;
  width: number;
  collapsedWidth: number;
  variant: 'temporary' | 'permanent';
}

interface NavItem {
  title: string;
  path?: string;
  icon: React.ReactNode;
  children?: NavItem[];
}

const navItems: NavItem[] = [
  {
    title: 'Dashboard',
    path: '/dashboard',
    icon: <DashboardIcon />,
  },
  {
    title: 'Inventario',
    icon: <InventoryIcon />,
    children: [
      { title: 'Productos', path: '/inventory/products', icon: <ProductIcon /> },
      { title: 'Almacenes', path: '/inventory/warehouses', icon: <WarehouseIcon /> },
      { title: 'Movimientos', path: '/inventory/movements', icon: <MovementIcon /> },
    ],
  },
  {
    title: 'Ventas',
    icon: <SalesIcon />,
    children: [
      { title: 'Clientes', path: '/sales/customers', icon: <CustomerIcon /> },
      { title: 'Pedidos', path: '/sales/orders', icon: <OrderIcon /> },
      { title: 'Facturas', path: '/sales/invoices', icon: <InvoiceIcon /> },
    ],
  },
  {
    title: 'Compras',
    icon: <PurchasingIcon />,
    children: [
      { title: 'Proveedores', path: '/purchasing/suppliers', icon: <SupplierIcon /> },
      { title: 'Órdenes', path: '/purchasing/orders', icon: <OrderIcon /> },
      { title: 'Recepciones', path: '/purchasing/receipts', icon: <MovementIcon /> },
    ],
  },
  {
    title: 'Finanzas',
    icon: <FinanceIcon />,
    children: [
      { title: 'Cuentas', path: '/finance/accounts', icon: <AccountIcon /> },
      { title: 'Diarios', path: '/finance/journals', icon: <JournalIcon /> },
      { title: 'Mayor', path: '/finance/ledger', icon: <JournalIcon /> },
      { title: 'Reportes', path: '/finance/reports', icon: <ReportIcon /> },
    ],
  },
  {
    title: 'Recursos Humanos',
    icon: <HRIcon />,
    children: [
      { title: 'Empleados', path: '/hr/employees', icon: <EmployeeIcon /> },
      { title: 'Departamentos', path: '/hr/departments', icon: <DepartmentIcon /> },
      { title: 'Nómina', path: '/hr/payroll', icon: <PayrollIcon /> },
      { title: 'Asistencia', path: '/hr/attendance', icon: <AttendanceIcon /> },
    ],
  },
  {
    title: 'Configuración',
    path: '/settings',
    icon: <SettingsIcon />,
  },
];

function Sidebar({ open, onClose, collapsed, width, collapsedWidth, variant }: SidebarProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const [openMenus, setOpenMenus] = useState<Record<string, boolean>>({});

  const currentWidth = collapsed ? collapsedWidth : width;

  const handleToggleMenu = (title: string) => {
    setOpenMenus((prev) => ({
      ...prev,
      [title]: !prev[title],
    }));
  };

  const handleNavigate = (path: string) => {
    navigate(path);
    if (variant === 'temporary') {
      onClose();
    }
  };

  const isActive = (path: string) => location.pathname === path;
  const isParentActive = (item: NavItem) => {
    if (item.children) {
      return item.children.some((child) => child.path && location.pathname.startsWith(child.path));
    }
    return false;
  };

  const renderNavItem = (item: NavItem, level = 0) => {
    const hasChildren = item.children && item.children.length > 0;
    const isOpen = openMenus[item.title];
    const active = item.path ? isActive(item.path) : isParentActive(item);

    const listItemButton = (
      <ListItemButton
        onClick={() => {
          if (hasChildren) {
            handleToggleMenu(item.title);
          } else if (item.path) {
            handleNavigate(item.path);
          }
        }}
        sx={{
          minHeight: 48,
          px: 2.5,
          pl: level > 0 ? 4 : 2.5,
          borderRadius: 1,
          mx: 1,
          mb: 0.5,
          justifyContent: collapsed ? 'center' : 'initial',
          backgroundColor: active ? 'primary.main' : 'transparent',
          color: active ? 'primary.contrastText' : 'text.primary',
          '&:hover': {
            backgroundColor: active ? 'primary.dark' : 'action.hover',
          },
        }}
      >
        <ListItemIcon
          sx={{
            minWidth: 0,
            mr: collapsed ? 0 : 2,
            justifyContent: 'center',
            color: 'inherit',
          }}
        >
          {item.icon}
        </ListItemIcon>
        {!collapsed && (
          <>
            <ListItemText primary={item.title} />
            {hasChildren && (isOpen ? <ExpandLess /> : <ExpandMore />)}
          </>
        )}
      </ListItemButton>
    );

    return (
      <Box key={item.title}>
        {collapsed && hasChildren ? (
          <Tooltip title={item.title} placement="right">
            {listItemButton}
          </Tooltip>
        ) : (
          listItemButton
        )}
        {hasChildren && !collapsed && (
          <Collapse in={isOpen} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children!.map((child) => renderNavItem(child, level + 1))}
            </List>
          </Collapse>
        )}
      </Box>
    );
  };

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo */}
      <Box
        sx={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'flex-start',
          px: collapsed ? 0 : 3,
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        {collapsed ? (
          <Typography variant="h5" fontWeight={700} color="primary">
            E
          </Typography>
        ) : (
          <Typography variant="h6" fontWeight={700} color="primary">
            ERP Universal
          </Typography>
        )}
      </Box>

      {/* Navigation */}
      <Box sx={{ flexGrow: 1, overflow: 'auto', py: 2 }}>
        <List>
          {navItems.map((item) => renderNavItem(item))}
        </List>
      </Box>

      {/* Footer */}
      {!collapsed && (
        <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary">
            v1.0.0
          </Typography>
        </Box>
      )}
    </Box>
  );

  return (
    <Drawer
      variant={variant}
      open={open}
      onClose={onClose}
      sx={{
        width: currentWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: currentWidth,
          boxSizing: 'border-box',
          transition: (theme) =>
            theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
}

export default Sidebar;
