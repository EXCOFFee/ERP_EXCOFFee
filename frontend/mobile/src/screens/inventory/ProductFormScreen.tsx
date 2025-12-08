import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { Text, TextInput, Button, useTheme, IconButton, HelperText, Switch, ActivityIndicator, Snackbar } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useForm, Controller } from 'react-hook-form';
import { InventoryStackParamList } from '../../navigation/types';
import { useAppDispatch, useAppSelector } from '../../hooks/useStore';
import { createProduct, updateProduct, fetchProduct, clearSelectedProduct } from '../../store/slices/inventorySlice';
import { savePendingAction } from '../../store/slices/offlineSlice';

type NavigationProp = NativeStackNavigationProp<InventoryStackParamList, 'ProductForm'>;
type RouteProps = RouteProp<InventoryStackParamList, 'ProductForm'>;

interface ProductFormData {
  sku: string;
  name: string;
  description: string;
  category: string;
  brand: string;
  price: string;
  cost: string;
  minStock: string;
  maxStock: string;
  barcode: string;
  unit: string;
  isActive: boolean;
}

const ProductFormScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<NavigationProp>();
  const route = useRoute<RouteProps>();
  const dispatch = useAppDispatch();
  
  const productId = route.params?.id;
  const isEditing = !!productId;
  
  const { selectedProduct, loading } = useAppSelector((state) => state.inventory);
  const { isOnline } = useAppSelector((state) => state.offline);
  
  const [saving, setSaving] = useState(false);
  const [snackbarVisible, setSnackbarVisible] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  const {
    control,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ProductFormData>({
    defaultValues: {
      sku: '',
      name: '',
      description: '',
      category: '',
      brand: '',
      price: '',
      cost: '',
      minStock: '0',
      maxStock: '100',
      barcode: '',
      unit: 'unit',
      isActive: true,
    },
  });

  useEffect(() => {
    if (isEditing && productId) {
      dispatch(fetchProduct(String(productId)));
    }
    return () => {
      dispatch(clearSelectedProduct());
    };
  }, [dispatch, isEditing, productId]);

  useEffect(() => {
    if (selectedProduct && isEditing) {
      reset({
        sku: selectedProduct.sku,
        name: selectedProduct.name,
        description: selectedProduct.description || '',
        category: selectedProduct.category,
        brand: '',
        price: String(selectedProduct.price),
        cost: String(selectedProduct.cost),
        minStock: String(selectedProduct.minStock),
        maxStock: '100',
        barcode: selectedProduct.barcode || '',
        unit: selectedProduct.unit,
        isActive: selectedProduct.isActive,
      });
    }
  }, [selectedProduct, isEditing, reset]);

  const onSubmit = async (data: ProductFormData) => {
    setSaving(true);
    
    const productData = {
      sku: data.sku,
      name: data.name,
      description: data.description,
      category: data.category,
      price: parseFloat(data.price),
      cost: parseFloat(data.cost) || 0,
      minStock: parseInt(data.minStock, 10),
      barcode: data.barcode,
      unit: data.unit,
      isActive: data.isActive,
    };

    try {
      if (!isOnline) {
        // Save for offline sync
        await dispatch(savePendingAction({
          type: isEditing ? 'UPDATE' : 'CREATE',
          entity: 'product',
          endpoint: isEditing ? `/inventory/products/${productId}` : '/inventory/products',
          data: productData,
        }));
        setSnackbarMessage('Guardado para sincronizar cuando haya conexión');
        setSnackbarVisible(true);
        setTimeout(() => navigation.goBack(), 1500);
      } else {
        if (isEditing && productId) {
          await dispatch(updateProduct({ id: String(productId), data: productData })).unwrap();
        } else {
          await dispatch(createProduct(productData)).unwrap();
        }
        navigation.goBack();
      }
    } catch (error) {
      Alert.alert('Error', 'No se pudo guardar el producto');
    } finally {
      setSaving(false);
    }
  };

  const handleScanBarcode = () => {
    navigation.navigate('BarcodeScanner');
  };

  if (loading && isEditing) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" />
          <Text style={{ marginTop: 16 }}>Cargando producto...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <IconButton
          icon="close"
          onPress={() => navigation.goBack()}
        />
        <Text variant="titleLarge" style={{ flex: 1, fontWeight: 'bold' }}>
          {isEditing ? 'Editar Producto' : 'Nuevo Producto'}
        </Text>
        {!isOnline && (
          <Text style={{ color: '#ff9800', marginRight: 8 }}>Offline</Text>
        )}
        <Button 
          mode="text" 
          onPress={handleSubmit(onSubmit)}
          loading={saving}
          disabled={saving}
        >
          Guardar
        </Button>
      </View>

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
      >
        <ScrollView contentContainerStyle={styles.content}>
          <Controller
            control={control}
            name="sku"
            rules={{ required: 'El SKU es requerido' }}
            render={({ field: { onChange, value } }) => (
              <View style={styles.inputContainer}>
                <TextInput
                  label="SKU *"
                  value={value}
                  onChangeText={onChange}
                  mode="outlined"
                  error={!!errors.sku}
                  disabled={isEditing}
                />
                {errors.sku && (
                  <HelperText type="error">{errors.sku.message}</HelperText>
                )}
              </View>
            )}
          />

          <Controller
            control={control}
            name="name"
            rules={{ required: 'El nombre es requerido' }}
            render={({ field: { onChange, value } }) => (
              <View style={styles.inputContainer}>
                <TextInput
                  label="Nombre *"
                  value={value}
                  onChangeText={onChange}
                  mode="outlined"
                  error={!!errors.name}
                />
                {errors.name && (
                  <HelperText type="error">{errors.name.message}</HelperText>
                )}
              </View>
            )}
          />

          <Controller
            control={control}
            name="description"
            render={({ field: { onChange, value } }) => (
              <View style={styles.inputContainer}>
                <TextInput
                  label="Descripción"
                  value={value}
                  onChangeText={onChange}
                  mode="outlined"
                  multiline
                  numberOfLines={3}
                />
              </View>
            )}
          />

          <View style={styles.row}>
            <Controller
              control={control}
              name="category"
              render={({ field: { onChange, value } }) => (
                <View style={[styles.inputContainer, { flex: 1 }]}>
                  <TextInput
                    label="Categoría"
                    value={value}
                    onChangeText={onChange}
                    mode="outlined"
                  />
                </View>
              )}
            />
            <Controller
              control={control}
              name="unit"
              render={({ field: { onChange, value } }) => (
                <View style={[styles.inputContainer, { flex: 1 }]}>
                  <TextInput
                    label="Unidad"
                    value={value}
                    onChangeText={onChange}
                    mode="outlined"
                    placeholder="pz, kg, lt..."
                  />
                </View>
              )}
            />
          </View>

          <View style={styles.row}>
            <Controller
              control={control}
              name="price"
              rules={{ 
                required: 'Precio requerido',
                pattern: { value: /^\d+(\.\d{1,2})?$/, message: 'Precio inválido' }
              }}
              render={({ field: { onChange, value } }) => (
                <View style={[styles.inputContainer, { flex: 1 }]}>
                  <TextInput
                    label="Precio Venta *"
                    value={value}
                    onChangeText={onChange}
                    mode="outlined"
                    keyboardType="decimal-pad"
                    left={<TextInput.Affix text="$" />}
                    error={!!errors.price}
                  />
                  {errors.price && (
                    <HelperText type="error">{errors.price.message}</HelperText>
                  )}
                </View>
              )}
            />
            <Controller
              control={control}
              name="cost"
              render={({ field: { onChange, value } }) => (
                <View style={[styles.inputContainer, { flex: 1 }]}>
                  <TextInput
                    label="Costo"
                    value={value}
                    onChangeText={onChange}
                    mode="outlined"
                    keyboardType="decimal-pad"
                    left={<TextInput.Affix text="$" />}
                  />
                </View>
              )}
            />
          </View>

          <View style={styles.row}>
            <Controller
              control={control}
              name="minStock"
              render={({ field: { onChange, value } }) => (
                <View style={[styles.inputContainer, { flex: 1 }]}>
                  <TextInput
                    label="Stock Mínimo"
                    value={value}
                    onChangeText={onChange}
                    mode="outlined"
                    keyboardType="number-pad"
                  />
                </View>
              )}
            />
            <Controller
              control={control}
              name="maxStock"
              render={({ field: { onChange, value } }) => (
                <View style={[styles.inputContainer, { flex: 1 }]}>
                  <TextInput
                    label="Stock Máximo"
                    value={value}
                    onChangeText={onChange}
                    mode="outlined"
                    keyboardType="number-pad"
                  />
                </View>
              )}
            />
          </View>

          <Controller
            control={control}
            name="barcode"
            render={({ field: { onChange, value } }) => (
              <View style={styles.inputContainer}>
                <TextInput
                  label="Código de Barras"
                  value={value}
                  onChangeText={onChange}
                  mode="outlined"
                  right={
                    <TextInput.Icon 
                      icon="barcode-scan" 
                      onPress={handleScanBarcode}
                    />
                  }
                />
              </View>
            )}
          />

          <Controller
            control={control}
            name="isActive"
            render={({ field: { onChange, value } }) => (
              <View style={styles.switchRow}>
                <Text variant="bodyLarge">Producto activo</Text>
                <Switch value={value} onValueChange={onChange} />
              </View>
            )}
          />
        </ScrollView>
      </KeyboardAvoidingView>

      <Snackbar
        visible={snackbarVisible}
        onDismiss={() => setSnackbarVisible(false)}
        duration={3000}
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
    gap: 8,
  },
  inputContainer: {
    marginBottom: 4,
  },
  row: {
    flexDirection: 'row',
    gap: 12,
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default ProductFormScreen;
