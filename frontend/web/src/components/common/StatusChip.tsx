import React from 'react';
import { Chip, ChipProps } from '@mui/material';

interface StatusChipProps {
  status: string;
  size?: ChipProps['size'];
  variant?: ChipProps['variant'];
}

const statusConfig: Record<string, { label: string; color: ChipProps['color'] }> = {
  // General
  active: { label: 'Activo', color: 'success' },
  inactive: { label: 'Inactivo', color: 'default' },
  pending: { label: 'Pendiente', color: 'warning' },
  completed: { label: 'Completado', color: 'success' },
  cancelled: { label: 'Cancelado', color: 'error' },
  
  // Orders
  draft: { label: 'Borrador', color: 'default' },
  confirmed: { label: 'Confirmado', color: 'info' },
  processing: { label: 'Procesando', color: 'warning' },
  shipped: { label: 'Enviado', color: 'secondary' },
  delivered: { label: 'Entregado', color: 'success' },
  
  // Payments
  paid: { label: 'Pagado', color: 'success' },
  partial: { label: 'Parcial', color: 'warning' },
  overdue: { label: 'Vencido', color: 'error' },
  
  // Purchasing
  sent: { label: 'Enviado', color: 'info' },
  received: { label: 'Recibido', color: 'success' },
  
  // HR
  vacation: { label: 'Vacaciones', color: 'warning' },
  absent: { label: 'Ausente', color: 'error' },
  present: { label: 'Presente', color: 'success' },
};

const StatusChip: React.FC<StatusChipProps> = ({
  status,
  size = 'small',
  variant = 'filled',
}) => {
  const config = statusConfig[status.toLowerCase()] || {
    label: status,
    color: 'default' as ChipProps['color'],
  };

  return (
    <Chip
      label={config.label}
      color={config.color}
      size={size}
      variant={variant}
    />
  );
};

export default StatusChip;
