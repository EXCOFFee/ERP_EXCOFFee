import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, useTheme, Button, Chip, IconButton, Divider } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import { InventoryStackParamList } from '../../navigation/types';

type NavigationProp = NativeStackNavigationProp<InventoryStackParamList, 'ProductDetail'>;
type RouteProps = RouteProp<InventoryStackParamList, 'ProductDetail'>;

const ProductDetailScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<NavigationProp>();
  const route = useRoute<RouteProps>();
  const { id } = route.params;

  // Datos de ejemplo
  const product = {
    id,
    sku: 'PRD001',
    name: 'Laptop HP ProBook 450 G8',
    description: 'Laptop empresarial con procesador Intel Core i5, 8GB RAM, 256GB SSD',
    category: 'Electrónica',
    brand: 'HP',
    price: 899.99,
    cost: 720.00,
    stock: 15,
    minStock: 5,
    maxStock: 50,
    unit: 'Unidad',
    barcode: '7501234567890',
    location: 'Almacén Principal - A1-B2',
  };

  const isLowStock = product.stock <= product.minStock;

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <IconButton
          icon="arrow-left"
          onPress={() => navigation.goBack()}
        />
        <Text variant="titleLarge" style={{ flex: 1, fontWeight: 'bold' }}>
          Detalle del Producto
        </Text>
        <IconButton
          icon="pencil"
          onPress={() => navigation.navigate('ProductForm', { id: product.id })}
        />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Info Principal */}
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="labelMedium" style={{ color: theme.colors.onSurfaceVariant }}>
              {product.sku}
            </Text>
            <Text variant="headlineSmall" style={{ fontWeight: 'bold', marginVertical: 8 }}>
              {product.name}
            </Text>
            <View style={styles.chips}>
              <Chip compact icon="shape">{product.category}</Chip>
              <Chip compact icon="tag">{product.brand}</Chip>
            </View>
            <Text variant="bodyMedium" style={{ marginTop: 12, color: theme.colors.onSurfaceVariant }}>
              {product.description}
            </Text>
          </Card.Content>
        </Card>

        {/* Precios */}
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={{ fontWeight: '600', marginBottom: 12 }}>
              Precios
            </Text>
            <View style={styles.priceRow}>
              <View style={styles.priceItem}>
                <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                  Precio de Venta
                </Text>
                <Text variant="headlineSmall" style={{ fontWeight: 'bold', color: theme.colors.primary }}>
                  ${product.price.toFixed(2)}
                </Text>
              </View>
              <View style={styles.priceItem}>
                <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                  Costo
                </Text>
                <Text variant="headlineSmall" style={{ fontWeight: 'bold' }}>
                  ${product.cost.toFixed(2)}
                </Text>
              </View>
              <View style={styles.priceItem}>
                <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                  Margen
                </Text>
                <Text variant="headlineSmall" style={{ fontWeight: 'bold', color: '#4caf50' }}>
                  {(((product.price - product.cost) / product.cost) * 100).toFixed(1)}%
                </Text>
              </View>
            </View>
          </Card.Content>
        </Card>

        {/* Stock */}
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={{ fontWeight: '600', marginBottom: 12 }}>
              Inventario
            </Text>
            <View style={styles.stockInfo}>
              <View style={[styles.stockIndicator, { backgroundColor: isLowStock ? '#ffebee' : '#e8f5e9' }]}>
                <MaterialCommunityIcons
                  name={isLowStock ? 'alert-circle' : 'check-circle'}
                  size={32}
                  color={isLowStock ? '#f44336' : '#4caf50'}
                />
                <Text
                  variant="headlineMedium"
                  style={{ fontWeight: 'bold', color: isLowStock ? '#f44336' : '#4caf50' }}
                >
                  {product.stock}
                </Text>
                <Text variant="bodySmall">en stock</Text>
              </View>
              <View style={styles.stockDetails}>
                <View style={styles.stockRow}>
                  <Text variant="bodyMedium">Stock mínimo:</Text>
                  <Text variant="bodyMedium" style={{ fontWeight: '600' }}>{product.minStock}</Text>
                </View>
                <Divider style={{ marginVertical: 8 }} />
                <View style={styles.stockRow}>
                  <Text variant="bodyMedium">Stock máximo:</Text>
                  <Text variant="bodyMedium" style={{ fontWeight: '600' }}>{product.maxStock}</Text>
                </View>
                <Divider style={{ marginVertical: 8 }} />
                <View style={styles.stockRow}>
                  <Text variant="bodyMedium">Ubicación:</Text>
                  <Text variant="bodyMedium" style={{ fontWeight: '600' }}>{product.location}</Text>
                </View>
              </View>
            </View>
          </Card.Content>
        </Card>

        {/* Código de barras */}
        <Card style={styles.card}>
          <Card.Content>
            <View style={styles.barcodeSection}>
              <MaterialCommunityIcons name="barcode" size={32} color={theme.colors.primary} />
              <View style={{ marginLeft: 12 }}>
                <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                  Código de barras
                </Text>
                <Text variant="titleMedium" style={{ fontWeight: '600' }}>
                  {product.barcode}
                </Text>
              </View>
            </View>
          </Card.Content>
        </Card>

        {/* Acciones */}
        <View style={styles.actions}>
          <Button mode="contained" icon="plus" style={styles.actionButton}>
            Entrada de Stock
          </Button>
          <Button mode="outlined" icon="minus" style={styles.actionButton}>
            Salida de Stock
          </Button>
        </View>
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
    alignItems: 'center',
    paddingRight: 8,
  },
  content: {
    padding: 16,
    gap: 16,
  },
  card: {},
  chips: {
    flexDirection: 'row',
    gap: 8,
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  priceItem: {
    alignItems: 'center',
  },
  stockInfo: {
    flexDirection: 'row',
    gap: 16,
  },
  stockIndicator: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    minWidth: 100,
  },
  stockDetails: {
    flex: 1,
  },
  stockRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  barcodeSection: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actions: {
    flexDirection: 'row',
    gap: 12,
  },
  actionButton: {
    flex: 1,
  },
});

export default ProductDetailScreen;
