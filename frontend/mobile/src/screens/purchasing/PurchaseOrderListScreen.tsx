import React from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { Text, Card, useTheme, Searchbar, FAB, Chip, IconButton } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { PurchasingStackParamList } from '../../navigation/types';

type NavigationProp = NativeStackNavigationProp<PurchasingStackParamList, 'PurchaseOrderList'>;

const mockOrders = [
  { id: 1, number: 'PO-001', supplier: 'Distribuidora Nacional', date: '2024-01-20', total: 45000, status: 'pending' },
  { id: 2, number: 'PO-002', supplier: 'Tech Import SA', date: '2024-01-19', total: 23500, status: 'confirmed' },
  { id: 3, number: 'PO-003', supplier: 'Suministros Globales', date: '2024-01-18', total: 12800, status: 'received' },
];

const statusConfig: Record<string, { label: string; color: string }> = {
  pending: { label: 'Pendiente', color: '#ff9800' },
  confirmed: { label: 'Confirmada', color: '#2196f3' },
  received: { label: 'Recibida', color: '#4caf50' },
  cancelled: { label: 'Cancelada', color: '#f44336' },
};

const PurchaseOrderListScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<NavigationProp>();
  const [searchQuery, setSearchQuery] = React.useState('');

  const renderOrder = ({ item }: { item: typeof mockOrders[0] }) => {
    const status = statusConfig[item.status];
    return (
      <Card style={styles.card} onPress={() => navigation.navigate('PurchaseOrderDetail', { id: item.id })}>
        <Card.Content style={styles.cardContent}>
          <View style={styles.orderInfo}>
            <Text variant="titleMedium" style={{ fontWeight: '600' }}>{item.number}</Text>
            <Text variant="bodyMedium">{item.supplier}</Text>
            <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>{item.date}</Text>
          </View>
          <View style={styles.orderMeta}>
            <Text variant="titleMedium" style={{ fontWeight: 'bold', color: theme.colors.primary }}>
              ${item.total.toLocaleString()}
            </Text>
            <Chip compact style={{ backgroundColor: status.color + '20' }} textStyle={{ color: status.color }}>
              {status.label}
            </Chip>
          </View>
        </Card.Content>
      </Card>
    );
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <IconButton icon="arrow-left" onPress={() => navigation.goBack()} />
        <Text variant="titleLarge" style={{ flex: 1, fontWeight: 'bold' }}>Órdenes de Compra</Text>
      </View>

      <Searchbar placeholder="Buscar orden..." value={searchQuery} onChangeText={setSearchQuery} style={styles.searchbar} />

      <FlatList
        data={mockOrders}
        renderItem={renderOrder}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.list}
        ItemSeparatorComponent={() => <View style={{ height: 12 }} />}
      />

      <FAB icon="plus" style={[styles.fab, { backgroundColor: theme.colors.primary }]} onPress={() => navigation.navigate('PurchaseOrderForm', {})} color="#fff" />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center' },
  searchbar: { marginHorizontal: 16, marginBottom: 16 },
  list: { padding: 16, paddingTop: 0 },
  card: {},
  cardContent: { flexDirection: 'row', justifyContent: 'space-between' },
  orderInfo: { gap: 2 },
  orderMeta: { alignItems: 'flex-end', gap: 8 },
  fab: { position: 'absolute', right: 16, bottom: 16 },
});

export default PurchaseOrderListScreen;
