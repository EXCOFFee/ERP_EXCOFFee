import React, { useEffect, useCallback } from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Card, Button, useTheme, IconButton, ProgressBar, List, Divider } from 'react-native-paper';
import { useAppDispatch, useAppSelector } from '../hooks/useStore';
import { 
  syncPendingActions, 
  loadPendingActions, 
  checkNetworkStatus,
  removePendingAction
} from '../store/slices/offlineSlice';
import type { PendingAction } from '../store/slices/offlineSlice';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

import type { RootState } from '../store';

interface OfflineSyncBannerProps {
  compact?: boolean;
}

const OfflineSyncBanner: React.FC<OfflineSyncBannerProps> = ({ compact = false }) => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  
  const { isOnline, pendingActions, syncInProgress, lastSyncTime } = useAppSelector(
    (state: RootState) => state.offline
  );

  useEffect(() => {
    dispatch(loadPendingActions());
    dispatch(checkNetworkStatus());
  }, [dispatch]);

  // Auto-sync when coming online
  useEffect(() => {
    if (isOnline && pendingActions.length > 0 && !syncInProgress) {
      dispatch(syncPendingActions());
    }
  }, [isOnline, pendingActions.length, syncInProgress, dispatch]);

  const handleSync = useCallback(() => {
    if (isOnline && !syncInProgress) {
      dispatch(syncPendingActions());
    }
  }, [dispatch, isOnline, syncInProgress]);

  const handleRemoveAction = useCallback((actionId: string) => {
    dispatch(removePendingAction(actionId));
  }, [dispatch]);

  const getEntityLabel = (entity: string): string => {
    const labels: Record<string, string> = {
      product: 'Producto',
      customer: 'Cliente',
      order: 'Orden',
      supplier: 'Proveedor',
    };
    return labels[entity] || entity;
  };

  const getActionLabel = (type: string): string => {
    const labels: Record<string, string> = {
      CREATE: 'Crear',
      UPDATE: 'Actualizar',
      DELETE: 'Eliminar',
    };
    return labels[type] || type;
  };

  if (pendingActions.length === 0 && isOnline) {
    return null;
  }

  if (compact) {
    return (
      <View style={[styles.compactBanner, { backgroundColor: !isOnline ? '#fff3e0' : '#e3f2fd' }]}>
        <IconButton
          icon={!isOnline ? 'cloud-off-outline' : 'cloud-sync-outline'}
          size={20}
          iconColor={!isOnline ? '#ff9800' : '#2196f3'}
        />
        <Text variant="bodySmall" style={{ flex: 1 }}>
          {!isOnline 
            ? `Sin conexión • ${pendingActions.length} pendientes`
            : syncInProgress 
              ? 'Sincronizando...'
              : `${pendingActions.length} por sincronizar`
          }
        </Text>
        {isOnline && pendingActions.length > 0 && !syncInProgress && (
          <Button compact mode="text" onPress={handleSync}>
            Sincronizar
          </Button>
        )}
      </View>
    );
  }

  return (
    <Card style={styles.card}>
      <Card.Content>
        {/* Status Header */}
        <View style={styles.header}>
          <View style={styles.statusContainer}>
            <IconButton
              icon={isOnline ? 'wifi' : 'wifi-off'}
              size={24}
              iconColor={isOnline ? '#4caf50' : '#f44336'}
              style={{ margin: 0 }}
            />
            <View>
              <Text variant="titleMedium" style={{ fontWeight: '600' }}>
                {isOnline ? 'Conectado' : 'Sin Conexión'}
              </Text>
              {lastSyncTime && (
                <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                  Última sync: {format(lastSyncTime, "dd/MM HH:mm", { locale: es })}
                </Text>
              )}
            </View>
          </View>
          {isOnline && pendingActions.length > 0 && (
            <Button 
              mode="contained-tonal" 
              onPress={handleSync}
              loading={syncInProgress}
              disabled={syncInProgress}
              compact
            >
              Sincronizar
            </Button>
          )}
        </View>

        {syncInProgress && (
          <ProgressBar 
            indeterminate 
            style={{ marginVertical: 12, borderRadius: 4 }} 
          />
        )}

        {/* Pending Actions List */}
        {pendingActions.length > 0 && (
          <View style={styles.pendingSection}>
            <Text variant="labelLarge" style={{ marginBottom: 8 }}>
              Acciones Pendientes ({pendingActions.length})
            </Text>
            {pendingActions.slice(0, 5).map((action: PendingAction, index: number) => (
              <React.Fragment key={action.id}>
                {index > 0 && <Divider />}
                <List.Item
                  title={`${getActionLabel(action.type)} ${getEntityLabel(action.entity)}`}
                  description={format(action.timestamp, "dd/MM/yyyy HH:mm", { locale: es })}
                  left={(props) => (
                    <List.Icon 
                      {...props} 
                      icon={
                        action.type === 'CREATE' ? 'plus-circle' :
                        action.type === 'UPDATE' ? 'pencil-circle' : 'minus-circle'
                      } 
                    />
                  )}
                  right={() => (
                    <View style={styles.actionButtons}>
                      {action.retryCount > 0 && (
                        <Text variant="bodySmall" style={{ color: '#f44336' }}>
                          {action.retryCount} intentos
                        </Text>
                      )}
                      <IconButton
                        icon="delete"
                        size={18}
                        onPress={() => handleRemoveAction(action.id)}
                      />
                    </View>
                  )}
                  style={{ paddingVertical: 4 }}
                />
              </React.Fragment>
            ))}
            {pendingActions.length > 5 && (
              <Text variant="bodySmall" style={{ textAlign: 'center', marginTop: 8, color: theme.colors.onSurfaceVariant }}>
                +{pendingActions.length - 5} más
              </Text>
            )}
          </View>
        )}

        {!isOnline && pendingActions.length === 0 && (
          <Text variant="bodyMedium" style={{ marginTop: 12, color: theme.colors.onSurfaceVariant }}>
            Las acciones que realices se guardarán localmente y se sincronizarán cuando vuelvas a tener conexión.
          </Text>
        )}
      </Card.Content>
    </Card>
  );
};

const styles = StyleSheet.create({
  card: {
    margin: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  pendingSection: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  actionButtons: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  compactBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    marginHorizontal: 16,
    marginBottom: 8,
    borderRadius: 8,
  },
});

export default OfflineSyncBanner;
