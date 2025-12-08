import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { Text, TextInput, Button, useTheme, IconButton, Card, Divider, Snackbar, Chip } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SalesStackParamList } from '../../navigation/types';
import { useAppDispatch, useAppSelector } from '../../hooks/useStore';
import { createOrder } from '../../store/slices/salesSlice';
import { savePendingAction } from '../../store/slices/offlineSlice';

type NavigationProp = NativeStackNavigationProp<SalesStackParamList, 'OrderForm'>;
type RouteProps = RouteProp<SalesStackParamList, 'OrderForm'>;

interface OrderItem {
  id: string;
  productId: string;
  productName: string;
  productSku: string;
  quantity: number;
  unitPrice: number;
  discount: number;
  total: number;
}

const OrderFormScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<NavigationProp>();
  const route = useRoute<RouteProps>();
  const dispatch = useAppDispatch();
  
  const isEditing = !!route.params?.id;
  const { isOnline, pendingActions } = useAppSelector((state) => state.offline);
  
  const [customerId] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [items, setItems] = useState<OrderItem[]>([]);
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);
  const [snackbarVisible, setSnackbarVisible] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  const subtotal = items.reduce((sum, item) => sum + item.total, 0);
  const tax = subtotal * 0.16; // 16% IVA
  const total = subtotal + tax;

  const handleAddItem = () => {
    // In a real app, this would open a product selector
    const newItem: OrderItem = {
      id: Date.now().toString(),
      productId: '1',
      productName: 'Producto de ejemplo',
      productSku: 'PRD001',
      quantity: 1,
      unitPrice: 100,
      discount: 0,
      total: 100,
    };
    setItems([...items, newItem]);
  };

  const handleRemoveItem = (itemId: string) => {
    setItems(items.filter(item => item.id !== itemId));
  };

  const handleUpdateQuantity = (itemId: string, quantity: number) => {
    setItems(items.map(item => {
      if (item.id === itemId) {
        const newTotal = (item.unitPrice * quantity) - item.discount;
        return { ...item, quantity, total: newTotal };
      }
      return item;
    }));
  };

  const handleSubmit = async () => {
    if (!customerName) {
      Alert.alert('Error', 'Selecciona un cliente');
      return;
    }
    if (items.length === 0) {
      Alert.alert('Error', 'Agrega al menos un producto');
      return;
    }

    setSaving(true);

    const orderData = {
      customerId,
      customerName,
      items: items.map(item => ({
        id: item.id,
        productId: item.productId,
        productName: item.productName,
        productSku: item.productSku,
        quantity: item.quantity,
        unitPrice: item.unitPrice,
        discount: item.discount,
        tax: item.total * 0.16,
        total: item.total,
      })),
      subtotal,
      discount: 0,
      tax,
      total,
      notes,
      status: 'draft' as const,
      paymentStatus: 'pending' as const,
    };

    try {
      if (!isOnline) {
        // Save for offline sync (RF2 requirement)
        await dispatch(savePendingAction({
          type: 'CREATE',
          entity: 'order',
          endpoint: '/sales/orders',
          data: orderData,
        }));
        setSnackbarMessage('Orden guardada localmente. Se sincronizará cuando haya conexión.');
        setSnackbarVisible(true);
        setTimeout(() => navigation.goBack(), 2000);
      } else {
        await dispatch(createOrder(orderData)).unwrap();
        navigation.goBack();
      }
    } catch (error) {
      Alert.alert('Error', 'No se pudo crear la orden');
    } finally {
      setSaving(false);
    }
  };

  const renderItem = (item: OrderItem) => (
    <Card key={item.id} style={styles.itemCard}>
      <Card.Content>
        <View style={styles.itemHeader}>
          <View style={{ flex: 1 }}>
            <Text variant="titleSmall">{item.productName}</Text>
            <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
              {item.productSku}
            </Text>
          </View>
          <IconButton
            icon="delete"
            size={20}
            onPress={() => handleRemoveItem(item.id)}
          />
        </View>
        <View style={styles.itemDetails}>
          <View style={styles.quantityControl}>
            <IconButton
              icon="minus"
              size={16}
              mode="outlined"
              onPress={() => handleUpdateQuantity(item.id, Math.max(1, item.quantity - 1))}
            />
            <Text variant="bodyLarge" style={{ marginHorizontal: 8 }}>
              {item.quantity}
            </Text>
            <IconButton
              icon="plus"
              size={16}
              mode="outlined"
              onPress={() => handleUpdateQuantity(item.id, item.quantity + 1)}
            />
          </View>
          <View style={{ alignItems: 'flex-end' }}>
            <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
              ${item.unitPrice.toFixed(2)} c/u
            </Text>
            <Text variant="titleMedium" style={{ fontWeight: 'bold' }}>
              ${item.total.toFixed(2)}
            </Text>
          </View>
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <IconButton icon="close" onPress={() => navigation.goBack()} />
        <Text variant="titleLarge" style={{ flex: 1, fontWeight: 'bold' }}>
          {isEditing ? 'Editar Orden' : 'Nueva Orden'}
        </Text>
        {!isOnline && (
          <Chip compact icon="cloud-off-outline" style={{ backgroundColor: '#fff3e0', marginRight: 8 }}>
            Offline
          </Chip>
        )}
        {pendingActions.filter(a => a.entity === 'order').length > 0 && (
          <Chip compact icon="sync" style={{ backgroundColor: '#e3f2fd', marginRight: 8 }}>
            {pendingActions.filter(a => a.entity === 'order').length} pendientes
          </Chip>
        )}
      </View>

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
      >
        <ScrollView contentContainerStyle={styles.content}>
          {/* Customer Selection */}
          <Card style={styles.card}>
            <Card.Content>
              <Text variant="titleMedium" style={{ marginBottom: 12 }}>Cliente</Text>
              <TextInput
                label="Nombre del cliente"
                value={customerName}
                onChangeText={setCustomerName}
                mode="outlined"
                right={<TextInput.Icon icon="account-search" />}
              />
            </Card.Content>
          </Card>

          {/* Order Items */}
          <View style={styles.itemsSection}>
            <View style={styles.sectionHeader}>
              <Text variant="titleMedium">Productos</Text>
              <Button 
                mode="outlined" 
                icon="plus" 
                compact 
                onPress={handleAddItem}
              >
                Agregar
              </Button>
            </View>
            
            {items.length === 0 ? (
              <Card style={styles.emptyCard}>
                <Card.Content style={styles.emptyContent}>
                  <IconButton icon="cart-outline" size={48} />
                  <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
                    No hay productos agregados
                  </Text>
                </Card.Content>
              </Card>
            ) : (
              items.map(renderItem)
            )}
          </View>

          {/* Notes */}
          <Card style={styles.card}>
            <Card.Content>
              <TextInput
                label="Notas (opcional)"
                value={notes}
                onChangeText={setNotes}
                mode="outlined"
                multiline
                numberOfLines={2}
              />
            </Card.Content>
          </Card>

          {/* Totals */}
          {items.length > 0 && (
            <Card style={styles.card}>
              <Card.Content>
                <View style={styles.totalRow}>
                  <Text variant="bodyMedium">Subtotal</Text>
                  <Text variant="bodyMedium">${subtotal.toFixed(2)}</Text>
                </View>
                <View style={styles.totalRow}>
                  <Text variant="bodyMedium">IVA (16%)</Text>
                  <Text variant="bodyMedium">${tax.toFixed(2)}</Text>
                </View>
                <Divider style={{ marginVertical: 8 }} />
                <View style={styles.totalRow}>
                  <Text variant="titleMedium" style={{ fontWeight: 'bold' }}>Total</Text>
                  <Text variant="titleMedium" style={{ fontWeight: 'bold', color: theme.colors.primary }}>
                    ${total.toFixed(2)}
                  </Text>
                </View>
              </Card.Content>
            </Card>
          )}

          {/* Submit Button */}
          <Button
            mode="contained"
            onPress={handleSubmit}
            loading={saving}
            disabled={saving || items.length === 0}
            style={styles.submitButton}
            contentStyle={{ paddingVertical: 8 }}
          >
            {isOnline ? 'Crear Orden' : 'Guardar Offline'}
          </Button>
        </ScrollView>
      </KeyboardAvoidingView>

      <Snackbar
        visible={snackbarVisible}
        onDismiss={() => setSnackbarVisible(false)}
        duration={3000}
        action={{
          label: 'OK',
          onPress: () => setSnackbarVisible(false),
        }}
      >
        {snackbarMessage}
      </Snackbar>
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
    paddingBottom: 32,
  },
  card: {
    marginBottom: 16,
  },
  itemsSection: {
    marginBottom: 16,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  itemCard: {
    marginBottom: 8,
  },
  itemHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  itemDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
  },
  quantityControl: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  emptyCard: {
    borderStyle: 'dashed',
    borderWidth: 1,
    borderColor: '#ddd',
    backgroundColor: 'transparent',
  },
  emptyContent: {
    alignItems: 'center',
    padding: 24,
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  submitButton: {
    marginTop: 8,
  },
});

export default OrderFormScreen;
