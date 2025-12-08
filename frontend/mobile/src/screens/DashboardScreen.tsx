import React, { useEffect, useState, useCallback } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl, TouchableOpacity } from 'react-native';
import { Text, Card, useTheme, Surface, IconButton, ActivityIndicator } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import MaterialCommunityIcons from '@expo/vector-icons/MaterialCommunityIcons';

import { useAppSelector, useAppDispatch } from '../hooks/useStore';
import { logout } from '../store/slices/authSlice';
import { checkNetworkStatus, loadPendingActions } from '../store/slices/offlineSlice';
import OfflineSyncBanner from '../components/OfflineSyncBanner';
import { salesService } from '../services/sales.service';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: string;
  color: string;
  trend?: number;
  onPress?: () => void;
}

interface DashboardStats {
  todaySales: number;
  monthSales: number;
  pendingOrders: number;
  overdueInvoices: number;
  totalProducts: number;
  totalCustomers: number;
  lowStockCount: number;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, trend, onPress }) => {
  const theme = useTheme();
  
  const content = (
    <Card.Content style={styles.statCardContent}>
      <View style={[styles.iconContainer, { backgroundColor: color + '20' }]}>
        <MaterialCommunityIcons name={icon as keyof typeof MaterialCommunityIcons.glyphMap} size={24} color={color} />
      </View>
      <View style={styles.statInfo}>
        <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
          {title}
        </Text>
        <Text variant="titleLarge" style={{ fontWeight: 'bold' }}>
          {value}
        </Text>
        {trend !== undefined && (
          <View style={styles.trendContainer}>
            <MaterialCommunityIcons
              name={trend >= 0 ? 'trending-up' : 'trending-down'}
              size={16}
              color={trend >= 0 ? '#4caf50' : '#f44336'}
            />
            <Text
              variant="bodySmall"
              style={{ color: trend >= 0 ? '#4caf50' : '#f44336' }}
            >
              {Math.abs(trend)}%
            </Text>
          </View>
        )}
      </View>
    </Card.Content>
  );

  return (
    <Card style={styles.statCard} onPress={onPress}>
      {content}
    </Card>
  );
};

const DashboardScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation();
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);
  const { isOnline, pendingActions } = useAppSelector((state) => state.offline);
  
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats>({
    todaySales: 0,
    monthSales: 0,
    pendingOrders: 0,
    overdueInvoices: 0,
    totalProducts: 0,
    totalCustomers: 0,
    lowStockCount: 0,
  });

  const loadStats = useCallback(async () => {
    try {
      if (isOnline) {
        const salesStats = await salesService.getDashboardStats();
        setStats(prev => ({
          ...prev,
          todaySales: salesStats.todaySales,
          monthSales: salesStats.monthSales,
          pendingOrders: salesStats.pendingOrders,
          overdueInvoices: salesStats.overdueInvoices,
        }));
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  }, [isOnline]);

  useEffect(() => {
    dispatch(checkNetworkStatus());
    dispatch(loadPendingActions());
    loadStats();
  }, [dispatch, loadStats]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    dispatch(checkNetworkStatus());
    await loadStats();
    setRefreshing(false);
  }, [dispatch, loadStats]);

  const handleLogout = () => {
    dispatch(logout());
  };

  const navigateToScan = () => {
    (navigation as any).navigate('Inventory', { screen: 'BarcodeScanner' });
  };

  const navigateToNewSale = () => {
    (navigation as any).navigate('Sales', { screen: 'OrderForm', params: {} });
  };

  const navigateToInventory = () => {
    (navigation as any).navigate('Inventory', { screen: 'ProductList' });
  };

  const navigateToOrders = () => {
    (navigation as any).navigate('Sales', { screen: 'OrderList' });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      {/* Header */}
      <Surface style={styles.header} elevation={1}>
        <View>
          <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
            Bienvenido,
          </Text>
          <Text variant="titleLarge" style={{ fontWeight: 'bold' }}>
            {user?.firstName || user?.username || 'Usuario'}
          </Text>
        </View>
        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
          {!isOnline && (
            <MaterialCommunityIcons 
              name="cloud-off-outline" 
              size={24} 
              color="#ff9800" 
              style={{ marginRight: 8 }}
            />
          )}
          <IconButton
            icon="logout"
            mode="contained-tonal"
            onPress={handleLogout}
          />
        </View>
      </Surface>

      {/* Offline Banner */}
      {(pendingActions.length > 0 || !isOnline) && (
        <OfflineSyncBanner compact />
      )}

      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Estadísticas */}
        <Text variant="titleMedium" style={styles.sectionTitle}>
          Resumen
        </Text>
        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator />
          </View>
        ) : (
          <View style={styles.statsGrid}>
            <StatCard
              title="Ventas del día"
              value={formatCurrency(stats.todaySales)}
              icon="cash"
              color={theme.colors.primary}
              onPress={navigateToOrders}
            />
            <StatCard
              title="Pedidos pendientes"
              value={stats.pendingOrders}
              icon="shopping"
              color="#9c27b0"
              onPress={navigateToOrders}
            />
            <StatCard
              title="Ventas del mes"
              value={formatCurrency(stats.monthSales)}
              icon="chart-line"
              color="#ff9800"
            />
            <StatCard
              title="Facturas vencidas"
              value={stats.overdueInvoices}
              icon="file-alert"
              color={stats.overdueInvoices > 0 ? '#f44336' : '#4caf50'}
            />
          </View>
        )}

        {/* Acciones rápidas */}
        <Text variant="titleMedium" style={styles.sectionTitle}>
          Acciones Rápidas
        </Text>
        <View style={styles.quickActions}>
          <TouchableOpacity onPress={navigateToScan} style={{ flex: 1 }}>
            <Card style={styles.actionCard}>
              <Card.Content style={styles.actionContent}>
                <MaterialCommunityIcons
                  name="barcode-scan"
                  size={32}
                  color={theme.colors.primary}
                />
                <Text variant="bodyMedium">Escanear</Text>
              </Card.Content>
            </Card>
          </TouchableOpacity>
          <TouchableOpacity onPress={navigateToNewSale} style={{ flex: 1 }}>
            <Card style={styles.actionCard}>
              <Card.Content style={styles.actionContent}>
                <MaterialCommunityIcons
                  name="plus-circle"
                  size={32}
                  color={theme.colors.primary}
                />
                <Text variant="bodyMedium">Nueva Venta</Text>
              </Card.Content>
            </Card>
          </TouchableOpacity>
          <TouchableOpacity onPress={navigateToInventory} style={{ flex: 1 }}>
            <Card style={styles.actionCard}>
              <Card.Content style={styles.actionContent}>
                <MaterialCommunityIcons
                  name="clipboard-list"
                  size={32}
                  color={theme.colors.primary}
                />
                <Text variant="bodyMedium">Inventario</Text>
              </Card.Content>
            </Card>
          </TouchableOpacity>
          <TouchableOpacity style={{ flex: 1 }}>
            <Card style={styles.actionCard}>
              <Card.Content style={styles.actionContent}>
                <MaterialCommunityIcons
                  name="account-check"
                  size={32}
                  color={theme.colors.primary}
                />
                <Text variant="bodyMedium">Asistencia</Text>
              </Card.Content>
            </Card>
          </TouchableOpacity>
        </View>

        {/* Alertas */}
        <Text variant="titleMedium" style={styles.sectionTitle}>
          Alertas
        </Text>
        <Card style={styles.alertCard}>
          <Card.Content>
            {stats.lowStockCount > 0 && (
              <View style={styles.alertItem}>
                <MaterialCommunityIcons
                  name="alert-circle"
                  size={24}
                  color="#f44336"
                />
                <View style={styles.alertText}>
                  <Text variant="bodyMedium" style={{ fontWeight: '600' }}>
                    Stock bajo
                  </Text>
                  <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                    {stats.lowStockCount} productos con stock crítico
                  </Text>
                </View>
              </View>
            )}
            {stats.overdueInvoices > 0 && (
              <View style={styles.alertItem}>
                <MaterialCommunityIcons
                  name="clock-alert"
                  size={24}
                  color="#ff9800"
                />
                <View style={styles.alertText}>
                  <Text variant="bodyMedium" style={{ fontWeight: '600' }}>
                    Pagos pendientes
                  </Text>
                  <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                    {stats.overdueInvoices} facturas vencidas
                  </Text>
                </View>
              </View>
            )}
            {pendingActions.length > 0 && (
              <View style={styles.alertItem}>
                <MaterialCommunityIcons
                  name="cloud-sync"
                  size={24}
                  color="#2196f3"
                />
                <View style={styles.alertText}>
                  <Text variant="bodyMedium" style={{ fontWeight: '600' }}>
                    Sincronización pendiente
                  </Text>
                  <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                    {pendingActions.length} acciones por sincronizar
                  </Text>
                </View>
              </View>
            )}
            {stats.lowStockCount === 0 && stats.overdueInvoices === 0 && pendingActions.length === 0 && (
              <View style={styles.alertItem}>
                <MaterialCommunityIcons
                  name="check-circle"
                  size={24}
                  color="#4caf50"
                />
                <View style={styles.alertText}>
                  <Text variant="bodyMedium" style={{ fontWeight: '600' }}>
                    Todo en orden
                  </Text>
                  <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                    No hay alertas pendientes
                  </Text>
                </View>
              </View>
            )}
          </Card.Content>
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
  },
  content: {
    padding: 16,
    paddingBottom: 32,
  },
  sectionTitle: {
    marginBottom: 12,
    fontWeight: '600',
  },
  loadingContainer: {
    padding: 32,
    alignItems: 'center',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 24,
  },
  statCard: {
    width: '48%',
    flexGrow: 1,
  },
  statCardContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  statInfo: {
    flex: 1,
  },
  trendContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 4,
  },
  quickActions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 24,
  },
  actionCard: {
    flex: 1,
  },
  actionContent: {
    alignItems: 'center',
    gap: 8,
    paddingVertical: 16,
  },
  alertCard: {
    marginBottom: 16,
  },
  alertItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingVertical: 8,
  },
  alertText: {
    flex: 1,
  },
});

export default DashboardScreen;
