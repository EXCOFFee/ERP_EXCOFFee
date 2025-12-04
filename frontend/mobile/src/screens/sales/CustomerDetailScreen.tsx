import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, useTheme, IconButton, Avatar, Card, Button, Divider } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { SalesStackParamList } from '../../navigation/types';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

type RouteProps = RouteProp<SalesStackParamList, 'CustomerDetail'>;

const CustomerDetailScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation();
  const route = useRoute<RouteProps>();
  const { id } = route.params;

  const customer = {
    id,
    name: 'Tech Solutions SA',
    email: 'contacto@techsol.com',
    phone: '+52 555 5678',
    type: 'company',
    taxId: 'TSO850101ABC',
    address: 'Av. Reforma 123, Col. Centro, CDMX',
    creditLimit: 50000,
    balance: 12500,
    totalPurchases: 89500,
    lastPurchase: '2024-01-15',
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <IconButton icon="arrow-left" onPress={() => navigation.goBack()} />
        <Text variant="titleLarge" style={{ flex: 1, fontWeight: 'bold' }}>
          Detalle Cliente
        </Text>
        <IconButton icon="pencil" onPress={() => {}} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.profileSection}>
          <Avatar.Text
            size={80}
            label={customer.name.split(' ').map(n => n[0]).join('').substring(0, 2)}
            style={{ backgroundColor: theme.colors.primary }}
          />
          <Text variant="headlineSmall" style={{ fontWeight: 'bold', marginTop: 12 }}>
            {customer.name}
          </Text>
          <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
            {customer.taxId}
          </Text>
        </View>

        <Card style={styles.card}>
          <Card.Content>
            <View style={styles.infoRow}>
              <MaterialCommunityIcons name="email" size={20} color={theme.colors.primary} />
              <Text variant="bodyMedium">{customer.email}</Text>
            </View>
            <Divider style={{ marginVertical: 12 }} />
            <View style={styles.infoRow}>
              <MaterialCommunityIcons name="phone" size={20} color={theme.colors.primary} />
              <Text variant="bodyMedium">{customer.phone}</Text>
            </View>
            <Divider style={{ marginVertical: 12 }} />
            <View style={styles.infoRow}>
              <MaterialCommunityIcons name="map-marker" size={20} color={theme.colors.primary} />
              <Text variant="bodyMedium" style={{ flex: 1 }}>{customer.address}</Text>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={{ fontWeight: '600', marginBottom: 16 }}>
              Información Financiera
            </Text>
            <View style={styles.statsRow}>
              <View style={styles.statItem}>
                <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                  Total Compras
                </Text>
                <Text variant="titleLarge" style={{ fontWeight: 'bold', color: theme.colors.primary }}>
                  ${customer.totalPurchases.toLocaleString()}
                </Text>
              </View>
              <View style={styles.statItem}>
                <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                  Saldo Pendiente
                </Text>
                <Text variant="titleLarge" style={{ fontWeight: 'bold', color: '#f44336' }}>
                  ${customer.balance.toLocaleString()}
                </Text>
              </View>
              <View style={styles.statItem}>
                <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                  Límite Crédito
                </Text>
                <Text variant="titleLarge" style={{ fontWeight: 'bold' }}>
                  ${customer.creditLimit.toLocaleString()}
                </Text>
              </View>
            </View>
          </Card.Content>
        </Card>

        <View style={styles.actions}>
          <Button mode="contained" icon="cart-plus" style={styles.actionButton}>
            Nueva Venta
          </Button>
          <Button mode="outlined" icon="file-document" style={styles.actionButton}>
            Ver Facturas
          </Button>
        </View>
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
  statsRow: { flexDirection: 'row', justifyContent: 'space-between' },
  statItem: { alignItems: 'center' },
  actions: { flexDirection: 'row', gap: 12 },
  actionButton: { flex: 1 },
});

export default CustomerDetailScreen;
