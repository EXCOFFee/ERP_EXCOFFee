import React, { useState } from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { Text, Card, useTheme, Searchbar, FAB, Chip, IconButton } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SalesStackParamList } from '../../navigation/types';

type NavigationProp = NativeStackNavigationProp<SalesStackParamList, 'OrderList'>;

interface Order {
  id: number;
  number: string;
  customer: string;
  date: string;
  total: number;
  status: 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled';
}

const mockOrders: Order[] = [
  { id: 1, number: 'ORD-001', customer: 'Tech Solutions SA', date: '2024-01-20', total: 12500, status: 'pending' },
  { id: 2, number: 'ORD-002', customer: 'Juan Pérez', date: '2024-01-19', total: 850, status: 'confirmed' },
  { id: 3, number: 'ORD-003', customer: 'Comercial ABC', date: '2024-01-18', total: 45000, status: 'shipped' },
  { id: 4, number: 'ORD-004', customer: 'María García', date: '2024-01-17', total: 1200, status: 'delivered' },
];

const statusConfig = {
  pending: { label: 'Pendiente', color: '#ff9800' },
  confirmed: { label: 'Confirmado', color: '#2196f3' },
  shipped: { label: 'Enviado', color: '#9c27b0' },
  delivered: { label: 'Entregado', color: '#4caf50' },
  cancelled: { label: 'Cancelado', color: '#f44336' },
};

const OrderListScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<NavigationProp>();
  const [searchQuery, setSearchQuery] = useState('');

  const filteredOrders = mockOrders.filter(o =>
    o.number.toLowerCase().includes(searchQuery.toLowerCase()) ||
    o.customer.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const renderOrder = ({ item }: { item: Order }) => {
    const status = statusConfig[item.status];
    
    return (
      <Card
        style={styles.card}
        onPress={() => navigation.navigate('OrderDetail', { id: item.id })}
      >
        <Card.Content style={styles.cardContent}>
          <View style={styles.orderInfo}>
            <Text variant="titleMedium" style={{ fontWeight: '600' }}>
              {item.number}
            </Text>
            <Text variant="bodyMedium">{item.customer}</Text>
            <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
              {item.date}
            </Text>
          </View>
          <View style={styles.orderMeta}>
            <Text variant="titleMedium" style={{ fontWeight: 'bold', color: theme.colors.primary }}>
              ${item.total.toLocaleString()}
            </Text>
            <Chip
              compact
              style={{ backgroundColor: status.color + '20' }}
              textStyle={{ color: status.color }}
            >
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
        <Text variant="titleLarge" style={{ flex: 1, fontWeight: 'bold' }}>
          Pedidos
        </Text>
        <IconButton icon="filter-variant" onPress={() => {}} />
      </View>

      <Searchbar
        placeholder="Buscar pedido..."
        value={searchQuery}
        onChangeText={setSearchQuery}
        style={styles.searchbar}
      />

      <FlatList
        data={filteredOrders}
        renderItem={renderOrder}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.list}
        ItemSeparatorComponent={() => <View style={{ height: 12 }} />}
      />

      <FAB
        icon="plus"
        style={[styles.fab, { backgroundColor: theme.colors.primary }]}
        onPress={() => navigation.navigate('OrderForm', {})}
        color="#fff"
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', paddingRight: 8 },
  searchbar: { marginHorizontal: 16, marginBottom: 16 },
  list: { padding: 16, paddingTop: 0 },
  card: {},
  cardContent: { flexDirection: 'row', justifyContent: 'space-between' },
  orderInfo: { gap: 2 },
  orderMeta: { alignItems: 'flex-end', gap: 8 },
  fab: { position: 'absolute', right: 16, bottom: 16 },
});

export default OrderListScreen;
