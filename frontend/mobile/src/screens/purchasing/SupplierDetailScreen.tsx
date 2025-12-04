import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, useTheme, IconButton, Avatar, Card, Divider } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { PurchasingStackParamList } from '../../navigation/types';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

type RouteProps = RouteProp<PurchasingStackParamList, 'SupplierDetail'>;

const SupplierDetailScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation();
  const route = useRoute<RouteProps>();

  const supplier = {
    id: route.params.id,
    name: 'Distribuidora Nacional SA',
    email: 'ventas@distnac.com',
    phone: '+52 555 1234 5678',
    address: 'Av. Industrial 456, Zona Industrial, Monterrey',
    taxId: 'DNA850101XYZ',
    rating: 4.5,
    totalOrders: 156,
    onTimeDelivery: 92,
    qualityScore: 4.3,
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <IconButton icon="arrow-left" onPress={() => navigation.goBack()} />
        <Text variant="titleLarge" style={{ flex: 1, fontWeight: 'bold' }}>Detalle Proveedor</Text>
        <IconButton icon="pencil" onPress={() => {}} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.profileSection}>
          <Avatar.Text size={80} label={supplier.name.substring(0, 2)} style={{ backgroundColor: theme.colors.primary }} />
          <Text variant="headlineSmall" style={{ fontWeight: 'bold', marginTop: 12 }}>{supplier.name}</Text>
          <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>{supplier.taxId}</Text>
        </View>

        <Card style={styles.card}>
          <Card.Content>
            <View style={styles.infoRow}>
              <MaterialCommunityIcons name="email" size={20} color={theme.colors.primary} />
              <Text variant="bodyMedium">{supplier.email}</Text>
            </View>
            <Divider style={{ marginVertical: 12 }} />
            <View style={styles.infoRow}>
              <MaterialCommunityIcons name="phone" size={20} color={theme.colors.primary} />
              <Text variant="bodyMedium">{supplier.phone}</Text>
            </View>
            <Divider style={{ marginVertical: 12 }} />
            <View style={styles.infoRow}>
              <MaterialCommunityIcons name="map-marker" size={20} color={theme.colors.primary} />
              <Text variant="bodyMedium" style={{ flex: 1 }}>{supplier.address}</Text>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={{ fontWeight: '600', marginBottom: 16 }}>Métricas</Text>
            <View style={styles.metricsRow}>
              <View style={styles.metricItem}>
                <MaterialCommunityIcons name="star" size={24} color="#ffc107" />
                <Text variant="titleLarge" style={{ fontWeight: 'bold' }}>{supplier.rating}</Text>
                <Text variant="bodySmall">Calificación</Text>
              </View>
              <View style={styles.metricItem}>
                <MaterialCommunityIcons name="truck-check" size={24} color="#4caf50" />
                <Text variant="titleLarge" style={{ fontWeight: 'bold' }}>{supplier.onTimeDelivery}%</Text>
                <Text variant="bodySmall">A tiempo</Text>
              </View>
              <View style={styles.metricItem}>
                <MaterialCommunityIcons name="clipboard-check" size={24} color={theme.colors.primary} />
                <Text variant="titleLarge" style={{ fontWeight: 'bold' }}>{supplier.totalOrders}</Text>
                <Text variant="bodySmall">Órdenes</Text>
              </View>
            </View>
          </Card.Content>
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', paddingRight: 8 },
  content: { padding: 16, gap: 16 },
  profileSection: { alignItems: 'center', marginBottom: 8 },
  card: {},
  infoRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  metricsRow: { flexDirection: 'row', justifyContent: 'space-around' },
  metricItem: { alignItems: 'center', gap: 4 },
});

export default SupplierDetailScreen;
