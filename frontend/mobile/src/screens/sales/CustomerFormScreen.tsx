import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { Text, TextInput, Button, useTheme, IconButton, HelperText, Switch, Snackbar, SegmentedButtons } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useForm, Controller } from 'react-hook-form';
import { SalesStackParamList } from '../../navigation/types';
import { useAppDispatch, useAppSelector } from '../../hooks/useStore';
import { createCustomer, updateCustomer, fetchCustomer, clearSelectedCustomer } from '../../store/slices/salesSlice';
import { savePendingAction } from '../../store/slices/offlineSlice';

type NavigationProp = NativeStackNavigationProp<SalesStackParamList, 'CustomerForm'>;
type RouteProps = RouteProp<SalesStackParamList, 'CustomerForm'>;

interface CustomerFormData {
  code: string;
  name: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  taxId: string;
  creditLimit: string;
  type: 'individual' | 'company';
  isActive: boolean;
}

const CustomerFormScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<NavigationProp>();
  const route = useRoute<RouteProps>();
  const dispatch = useAppDispatch();
  
  const customerId = route.params?.id;
  const isEditing = !!customerId;
  
  const { selectedCustomer } = useAppSelector((state) => state.sales);
  const { isOnline } = useAppSelector((state) => state.offline);
  
  const [saving, setSaving] = useState(false);
  const [snackbarVisible, setSnackbarVisible] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  const {
    control,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<CustomerFormData>({
    defaultValues: {
      code: '',
      name: '',
      email: '',
      phone: '',
      address: '',
      city: '',
      taxId: '',
      creditLimit: '0',
      type: 'individual',
      isActive: true,
    },
  });

  const customerType = watch('type');

  useEffect(() => {
    if (isEditing && customerId) {
      dispatch(fetchCustomer(String(customerId)));
    }
    return () => {
      dispatch(clearSelectedCustomer());
    };
  }, [dispatch, isEditing, customerId]);

  useEffect(() => {
    if (selectedCustomer && isEditing) {
      reset({
        code: selectedCustomer.code,
        name: selectedCustomer.name,
        email: selectedCustomer.email || '',
        phone: selectedCustomer.phone || '',
        address: selectedCustomer.address || '',
        city: selectedCustomer.city || '',
        taxId: selectedCustomer.taxId || '',
        creditLimit: String(selectedCustomer.creditLimit || 0),
        type: 'individual',
        isActive: selectedCustomer.isActive,
      });
    }
  }, [selectedCustomer, isEditing, reset]);

  const onSubmit = async (data: CustomerFormData) => {
    setSaving(true);
    
    const customerData = {
      code: data.code,
      name: data.name,
      email: data.email,
      phone: data.phone,
      address: data.address,
      city: data.city,
      taxId: data.taxId,
      creditLimit: parseFloat(data.creditLimit) || 0,
      isActive: data.isActive,
    };

    try {
      if (!isOnline) {
        await dispatch(savePendingAction({
          type: isEditing ? 'UPDATE' : 'CREATE',
          entity: 'customer',
          endpoint: isEditing ? `/sales/customers/${customerId}` : '/sales/customers',
          data: customerData,
        }));
        setSnackbarMessage('Guardado para sincronizar cuando haya conexión');
        setSnackbarVisible(true);
        setTimeout(() => navigation.goBack(), 1500);
      } else {
        if (isEditing && customerId) {
          await dispatch(updateCustomer({ id: String(customerId), data: customerData })).unwrap();
        } else {
          await dispatch(createCustomer(customerData)).unwrap();
        }
        navigation.goBack();
      }
    } catch (error) {
      Alert.alert('Error', 'No se pudo guardar el cliente');
    } finally {
      setSaving(false);
    }
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <IconButton icon="close" onPress={() => navigation.goBack()} />
        <Text variant="titleLarge" style={{ flex: 1, fontWeight: 'bold' }}>
          {isEditing ? 'Editar Cliente' : 'Nuevo Cliente'}
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
          {/* Customer Type */}
          <Controller
            control={control}
            name="type"
            render={({ field: { onChange, value } }) => (
              <View style={styles.inputContainer}>
                <Text variant="labelLarge" style={{ marginBottom: 8 }}>Tipo de Cliente</Text>
                <SegmentedButtons
                  value={value}
                  onValueChange={onChange}
                  buttons={[
                    { value: 'individual', label: 'Persona', icon: 'account' },
                    { value: 'company', label: 'Empresa', icon: 'domain' },
                  ]}
                />
              </View>
            )}
          />

          {/* Code */}
          <Controller
            control={control}
            name="code"
            rules={{ required: 'El código es requerido' }}
            render={({ field: { onChange, value } }) => (
              <View style={styles.inputContainer}>
                <TextInput
                  label="Código *"
                  value={value}
                  onChangeText={onChange}
                  mode="outlined"
                  error={!!errors.code}
                  disabled={isEditing}
                />
                {errors.code && (
                  <HelperText type="error">{errors.code.message}</HelperText>
                )}
              </View>
            )}
          />

          {/* Name */}
          <Controller
            control={control}
            name="name"
            rules={{ required: 'El nombre es requerido' }}
            render={({ field: { onChange, value } }) => (
              <View style={styles.inputContainer}>
                <TextInput
                  label={customerType === 'company' ? 'Razón Social *' : 'Nombre Completo *'}
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

          {/* Tax ID */}
          <Controller
            control={control}
            name="taxId"
            render={({ field: { onChange, value } }) => (
              <View style={styles.inputContainer}>
                <TextInput
                  label={customerType === 'company' ? 'RFC' : 'RFC / CURP'}
                  value={value}
                  onChangeText={onChange}
                  mode="outlined"
                  autoCapitalize="characters"
                />
              </View>
            )}
          />

          {/* Contact Info */}
          <View style={styles.row}>
            <Controller
              control={control}
              name="email"
              rules={{
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Email inválido',
                },
              }}
              render={({ field: { onChange, value } }) => (
                <View style={[styles.inputContainer, { flex: 1 }]}>
                  <TextInput
                    label="Email"
                    value={value}
                    onChangeText={onChange}
                    mode="outlined"
                    keyboardType="email-address"
                    autoCapitalize="none"
                    error={!!errors.email}
                  />
                  {errors.email && (
                    <HelperText type="error">{errors.email.message}</HelperText>
                  )}
                </View>
              )}
            />
          </View>

          <Controller
            control={control}
            name="phone"
            render={({ field: { onChange, value } }) => (
              <View style={styles.inputContainer}>
                <TextInput
                  label="Teléfono"
                  value={value}
                  onChangeText={onChange}
                  mode="outlined"
                  keyboardType="phone-pad"
                  left={<TextInput.Icon icon="phone" />}
                />
              </View>
            )}
          />

          {/* Address */}
          <Controller
            control={control}
            name="address"
            render={({ field: { onChange, value } }) => (
              <View style={styles.inputContainer}>
                <TextInput
                  label="Dirección"
                  value={value}
                  onChangeText={onChange}
                  mode="outlined"
                  multiline
                  numberOfLines={2}
                />
              </View>
            )}
          />

          <Controller
            control={control}
            name="city"
            render={({ field: { onChange, value } }) => (
              <View style={styles.inputContainer}>
                <TextInput
                  label="Ciudad"
                  value={value}
                  onChangeText={onChange}
                  mode="outlined"
                />
              </View>
            )}
          />

          {/* Credit Limit */}
          <Controller
            control={control}
            name="creditLimit"
            render={({ field: { onChange, value } }) => (
              <View style={styles.inputContainer}>
                <TextInput
                  label="Límite de Crédito"
                  value={value}
                  onChangeText={onChange}
                  mode="outlined"
                  keyboardType="decimal-pad"
                  left={<TextInput.Affix text="$" />}
                />
              </View>
            )}
          />

          {/* Active Status */}
          <Controller
            control={control}
            name="isActive"
            render={({ field: { onChange, value } }) => (
              <View style={styles.switchRow}>
                <Text variant="bodyLarge">Cliente activo</Text>
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
    marginBottom: 8,
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

export default CustomerFormScreen;
