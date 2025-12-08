import React, { useEffect, useState, useCallback } from 'react';
import { View, StyleSheet, FlatList, RefreshControl, Alert } from 'react-native';
import { Text, Card, useTheme, Searchbar, FAB, Chip, IconButton, ActivityIndicator } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { InventoryStackParamList } from '../../navigation/types';
import { useAppDispatch, useAppSelector } from '../../hooks/useStore';
import { fetchProducts, setFilters } from '../../store/slices/inventorySlice';
import { Product } from '../../services/inventory.service';

type NavigationProp = NativeStackNavigationProp<InventoryStackParamList, 'ProductList'>;

const ProductListScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<NavigationProp>();
  const dispatch = useAppDispatch();
  
  const { products, loading, error, pagination, filters } = useAppSelector((state) => state.inventory);
  const { isOnline, pendingActions } = useAppSelector((state) => state.offline);
  
  const [searchQuery, setSearchQuery] = useState(filters.search || '');
  const [refreshing, setRefreshing] = useState(false);

  const loadProducts = useCallback(() => {
    dispatch(fetchProducts(filters));
  }, [dispatch, filters]);

  useFocusEffect(
    useCallback(() => {
      loadProducts();
    }, [loadProducts])
  );

  useEffect(() => {
    if (error) {
      Alert.alert('Error', error);
    }
  }, [error]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    dispatch(setFilters({ ...filters, search: query }));
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await dispatch(fetchProducts(filters));
    setRefreshing(false);
  };

  const handleLoadMore = () => {
    if (pagination.page < pagination.totalPages && !loading) {
      dispatch(fetchProducts({ ...filters, page: pagination.page + 1 }));
    }
  };

  const renderProduct = ({ item }: { item: Product }) => {
    const isLowStock = item.stock <= item.minStock;
    
    return (
      <Card 
        style={styles.productCard}
        onPress={() => navigation.navigate('ProductDetail', { id: Number(item.id) })}
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

  const renderFooter = () => {
    if (!loading || products.length === 0) return null;
    return (
      <View style={styles.footerLoader}>
        <ActivityIndicator size="small" />
      </View>
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
        {!isOnline && (
          <Chip compact icon="cloud-off-outline" style={{ backgroundColor: '#fff3e0' }}>
            Offline
          </Chip>
        )}
        {pendingActions.length > 0 && (
          <Chip compact icon="sync" style={{ backgroundColor: '#e3f2fd' }}>
            {pendingActions.length}
          </Chip>
        )}
        <IconButton
          icon="barcode-scan"
          onPress={() => navigation.navigate('BarcodeScanner')}
        />
        <IconButton
          icon="filter-variant"
          onPress={() => {}}
        />
      </View>

      <Searchbar
        placeholder="Buscar por nombre o SKU..."
        value={searchQuery}
        onChangeText={handleSearch}
        style={styles.searchbar}
      />

      {loading && products.length === 0 ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" />
          <Text style={{ marginTop: 16 }}>Cargando productos...</Text>
        </View>
      ) : (
        <FlatList
          data={products}
          renderItem={renderProduct}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.list}
          ItemSeparatorComponent={() => <View style={{ height: 12 }} />}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
          }
          onEndReached={handleLoadMore}
          onEndReachedThreshold={0.3}
          ListFooterComponent={renderFooter}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text variant="bodyLarge" style={{ color: theme.colors.onSurfaceVariant }}>
                No se encontraron productos
              </Text>
            </View>
          }
        />
      )}

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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  footerLoader: {
    padding: 16,
    alignItems: 'center',
  },
  fab: {
    position: 'absolute',
    right: 16,
    bottom: 16,
  },
});

export default ProductListScreen;
