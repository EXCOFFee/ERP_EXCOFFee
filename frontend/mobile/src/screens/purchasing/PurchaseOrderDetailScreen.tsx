import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, useTheme, IconButton, Chip, Button, Divider, DataTable } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { PurchasingStackParamList } from '../../navigation/types';

type RouteProps = RouteProp<PurchasingStackParamList, 'PurchaseOrderDetail'>;

const PurchaseOrderDetailScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation();
  const route = useRoute<RouteProps>();

  const order = {
    id: route.params.id,
    number: 'PO-001',
    supplier: 'Distribuidora Nacional SA',
    date: '2024-01-20',
    expectedDate: '2024-01-27',
    status: 'pending',
    subtotal: 38793.10,
    tax: 6206.90,
    total: 45000,
    items: [
      { id: 1, product: 'Laptop HP ProBook', qty: 10, price: 720.00, total: 7200.00 },
      { id: 2, product: 'Monitor 24"', qty: 20, price: 245.00, total: 4900.00 },
      { id: 3, product: 'Teclado Mecánico', qty: 50, price: 65.00, total: 3250.00 },
    ],
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <IconButton icon="arrow-left" onPress={() => navigation.goBack()} />
        <Text variant="titleLarge" style={{ flex: 1, fontWeight: 'bold' }}>{order.number}</Text>
        <IconButton icon="printer" onPress={() => {}} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <Card style={styles.card}>
          <Card.Content>
            <View style={styles.orderHeader}>
              <View>
                <Text variant="titleMedium" style={{ fontWeight: '600' }}>{order.supplier}</Text>
                <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                  Fecha: {order.date}
                </Text>
                <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                  Entrega esperada: {order.expectedDate}
                </Text>
              </View>
              <Chip style={{ backgroundColor: '#fff3e0' }} textStyle={{ color: '#ff9800' }}>Pendiente</Chip>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={{ fontWeight: '600', marginBottom: 12 }}>Productos</Text>
            <DataTable>
              <DataTable.Header>
                <DataTable.Title>Producto</DataTable.Title>
                <DataTable.Title numeric>Cant</DataTable.Title>
                <DataTable.Title numeric>Total</DataTable.Title>
              </DataTable.Header>
              {order.items.map((item) => (
                <DataTable.Row key={item.id}>
                  <DataTable.Cell>{item.product}</DataTable.Cell>
                  <DataTable.Cell numeric>{item.qty}</DataTable.Cell>
                  <DataTable.Cell numeric>${item.total.toFixed(2)}</DataTable.Cell>
                </DataTable.Row>
              ))}
            </DataTable>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <View style={styles.totalRow}>
              <Text variant="bodyMedium">Subtotal</Text>
              <Text variant="bodyMedium">${order.subtotal.toFixed(2)}</Text>
            </View>
            <View style={styles.totalRow}>
              <Text variant="bodyMedium">IVA (16%)</Text>
              <Text variant="bodyMedium">${order.tax.toFixed(2)}</Text>
            </View>
            <Divider style={{ marginVertical: 12 }} />
            <View style={styles.totalRow}>
              <Text variant="titleMedium" style={{ fontWeight: 'bold' }}>Total</Text>
              <Text variant="titleLarge" style={{ fontWeight: 'bold', color: theme.colors.primary }}>
                ${order.total.toFixed(2)}
              </Text>
            </View>
          </Card.Content>
        </Card>

        <View style={styles.actions}>
          <Button mode="contained" icon="package-down" style={styles.actionButton}>
            Registrar Recepción
          </Button>
          <Button mode="outlined" icon="close" style={styles.actionButton}>
            Cancelar Orden
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
  card: {},
  orderHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  totalRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  actions: { flexDirection: 'row', gap: 12 },
  actionButton: { flex: 1 },
});

export default PurchaseOrderDetailScreen;
