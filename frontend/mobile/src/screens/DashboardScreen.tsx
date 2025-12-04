import React from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Text, Card, useTheme, Surface, IconButton } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { useAppSelector, useAppDispatch } from '../hooks/useStore';
import { logout } from '../store/slices/authSlice';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: string;
  color: string;
  trend?: number;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, trend }) => {
  const theme = useTheme();
  
  return (
    <Card style={styles.statCard}>
      <Card.Content style={styles.statCardContent}>
        <View style={[styles.iconContainer, { backgroundColor: color + '20' }]}>
          <MaterialCommunityIcons name={icon} size={24} color={color} />
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
    </Card>
  );
};

const DashboardScreen: React.FC = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);
  
  const [refreshing, setRefreshing] = React.useState(false);

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    // TODO: Recargar datos
    setTimeout(() => setRefreshing(false), 1000);
  }, []);

  const handleLogout = () => {
    dispatch(logout());
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
            {user?.fullName || user?.username || 'Usuario'}
          </Text>
        </View>
        <IconButton
          icon="logout"
          mode="contained-tonal"
          onPress={handleLogout}
        />
      </Surface>

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
        <View style={styles.statsGrid}>
          <StatCard
            title="Ventas del día"
            value="$12,450"
            icon="cash"
            color={theme.colors.primary}
            trend={12.5}
          />
          <StatCard
            title="Pedidos"
            value="28"
            icon="shopping"
            color="#9c27b0"
            trend={-3.2}
          />
          <StatCard
            title="Productos"
            value="1,234"
            icon="package-variant"
            color="#ff9800"
          />
          <StatCard
            title="Clientes"
            value="856"
            icon="account-group"
            color="#4caf50"
            trend={8.7}
          />
        </View>

        {/* Acciones rápidas */}
        <Text variant="titleMedium" style={styles.sectionTitle}>
          Acciones Rápidas
        </Text>
        <View style={styles.quickActions}>
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
        </View>

        {/* Alertas */}
        <Text variant="titleMedium" style={styles.sectionTitle}>
          Alertas
        </Text>
        <Card style={styles.alertCard}>
          <Card.Content>
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
                  15 productos con stock crítico
                </Text>
              </View>
            </View>
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
                  8 facturas por cobrar
                </Text>
              </View>
            </View>
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
    width: '23%',
    flexGrow: 1,
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
