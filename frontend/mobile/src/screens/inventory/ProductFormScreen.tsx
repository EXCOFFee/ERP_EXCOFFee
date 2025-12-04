import React from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { Text, TextInput, Button, useTheme, IconButton, HelperText, Switch } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useForm, Controller } from 'react-hook-form';
import { InventoryStackParamList } from '../../navigation/types';

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
  isActive: boolean;
}

const ProductFormScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<NavigationProp>();
  const route = useRoute<RouteProps>();
  const isEditing = !!route.params?.id;

  const {
    control,
    handleSubmit,
    formState: { errors },
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
      isActive: true,
    },
  });

  const onSubmit = (data: ProductFormData) => {
    console.log('Form data:', data);
    navigation.goBack();
  };

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
        <Button mode="text" onPress={handleSubmit(onSubmit)}>
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
              name="brand"
              render={({ field: { onChange, value } }) => (
                <View style={[styles.inputContainer, { flex: 1 }]}>
                  <TextInput
                    label="Marca"
                    value={value}
                    onChangeText={onChange}
                    mode="outlined"
                  />
                </View>
              )}
            />
          </View>

          <View style={styles.row}>
            <Controller
              control={control}
              name="price"
              rules={{ required: 'Precio requerido' }}
              render={({ field: { onChange, value } }) => (
                <View style={[styles.inputContainer, { flex: 1 }]}>
                  <TextInput
                    label="Precio *"
                    value={value}
                    onChangeText={onChange}
                    mode="outlined"
                    keyboardType="decimal-pad"
                    left={<TextInput.Affix text="$" />}
                    error={!!errors.price}
                  />
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
                  right={<TextInput.Icon icon="barcode-scan" />}
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
});

export default ProductFormScreen;
