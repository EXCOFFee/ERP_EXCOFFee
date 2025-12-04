import React, { useState } from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { Text, Card, useTheme, Searchbar, FAB, Chip, IconButton } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { InventoryStackParamList } from '../../navigation/types';

type NavigationProp = NativeStackNavigationProp<InventoryStackParamList, 'ProductList'>;

interface Product {
  id: number;
  sku: string;
  name: string;
  category: string;
  price: number;
  stock: number;
  minStock: number;
}

// Datos de ejemplo
const mockProducts: Product[] = [
  { id: 1, sku: 'PRD001', name: 'Laptop HP ProBook', category: 'Electrónica', price: 899.99, stock: 15, minStock: 5 },
  { id: 2, sku: 'PRD002', name: 'Mouse Inalámbrico', category: 'Accesorios', price: 29.99, stock: 3, minStock: 10 },
  { id: 3, sku: 'PRD003', name: 'Teclado Mecánico', category: 'Accesorios', price: 79.99, stock: 25, minStock: 8 },
  { id: 4, sku: 'PRD004', name: 'Monitor 24"', category: 'Electrónica', price: 299.99, stock: 8, minStock: 3 },
  { id: 5, sku: 'PRD005', name: 'Cable HDMI 2m', category: 'Cables', price: 12.99, stock: 50, minStock: 20 },
];

const ProductListScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<NavigationProp>();
  const [searchQuery, setSearchQuery] = useState('');
  const [products] = useState<Product[]>(mockProducts);

  const filteredProducts = products.filter(p => 
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.sku.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const renderProduct = ({ item }: { item: Product }) => {
    const isLowStock = item.stock <= item.minStock;
    
    return (
      <Card 
        style={styles.productCard}
        onPress={() => navigation.navigate('ProductDetail', { id: item.id })}
      >
        <Card.Content style={styles.productContent}>
          <View style={styles.productInfo}>
            <Text variant="labelSmall" style={{ color: theme.colors.onSurfaceVariant }}>
              {item.sku}
            </Text>
            <Text variant="titleMedium" style={{ fontWeight: '600' }}>
              {item.name}
            </Text>
            <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
              {item.category}
            </Text>
          </View>
          <View style={styles.productMeta}>
            <Text variant="titleMedium" style={{ fontWeight: 'bold', color: theme.colors.primary }}>
              ${item.price.toFixed(2)}
            </Text>
            <Chip
              compact
              style={[
                styles.stockChip,
                { backgroundColor: isLowStock ? '#ffebee' : '#e8f5e9' }
              ]}
              textStyle={{ color: isLowStock ? '#f44336' : '#4caf50' }}
            >
              Stock: {item.stock}
            </Chip>
          </View>
        </Card.Content>
      </Card>
    );
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <IconButton
          icon="arrow-left"
          onPress={() => navigation.goBack()}
        />
        <Text variant="titleLarge" style={{ flex: 1, fontWeight: 'bold' }}>
          Productos
        </Text>
        <IconButton
          icon="filter-variant"
          onPress={() => {}}
        />
      </View>

      <Searchbar
        placeholder="Buscar por nombre o SKU..."
        value={searchQuery}
        onChangeText={setSearchQuery}
        style={styles.searchbar}
      />

      <FlatList
        data={filteredProducts}
        renderItem={renderProduct}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.list}
        ItemSeparatorComponent={() => <View style={{ height: 12 }} />}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text variant="bodyLarge" style={{ color: theme.colors.onSurfaceVariant }}>
              No se encontraron productos
            </Text>
          </View>
        }
      />

      <FAB
        icon="plus"
        style={[styles.fab, { backgroundColor: theme.colors.primary }]}
        onPress={() => navigation.navigate('ProductForm', {})}
        color="#fff"
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingRight: 8,
  },
  searchbar: {
    marginHorizontal: 16,
    marginBottom: 16,
  },
  list: {
    padding: 16,
    paddingTop: 0,
  },
  productCard: {},
  productContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  productInfo: {
    flex: 1,
    gap: 2,
  },
  productMeta: {
    alignItems: 'flex-end',
    gap: 8,
  },
  stockChip: {},
  emptyContainer: {
    padding: 32,
    alignItems: 'center',
  },
  fab: {
    position: 'absolute',
    right: 16,
    bottom: 16,
  },
});

export default ProductListScreen;
