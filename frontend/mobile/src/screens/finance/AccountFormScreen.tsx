// ========================================================
// Finance Module - Account Form Screen
// ========================================================

import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { 
  Appbar, 
  TextInput, 
  Button, 
  HelperText,
  Switch,
  Text,
  Menu,
  Divider
} from 'react-native-paper';
import { useNavigation, useRoute } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '../../hooks/useStore';
import { 
  createAccount, 
  updateAccount, 
  fetchAccount,
  selectSelectedAccount,
  selectAccounts
} from '../../store/slices/financeSlice';
import { Account } from '../../services/finance.service';

const AccountFormScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const route = useRoute<any>();
  const dispatch = useAppDispatch();
  
  const accountId = route.params?.accountId;
  const isEditing = !!accountId;
  
  const selectedAccount = useAppSelector(selectSelectedAccount);
  const accounts = useAppSelector(selectAccounts);
  
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    accountTypeId: '',
    parent: '',
    isActive: true,
    allowsTransactions: true,
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [typeMenuVisible, setTypeMenuVisible] = useState(false);
  const [parentMenuVisible, setParentMenuVisible] = useState(false);

  const accountTypes = [
    { id: '1', name: 'Activo Corriente', classification: 'asset' },
    { id: '2', name: 'Activo No Corriente', classification: 'asset' },
    { id: '3', name: 'Pasivo Corriente', classification: 'liability' },
    { id: '4', name: 'Pasivo No Corriente', classification: 'liability' },
    { id: '5', name: 'Patrimonio', classification: 'equity' },
    { id: '6', name: 'Ingresos Operacionales', classification: 'income' },
    { id: '7', name: 'Gastos Operacionales', classification: 'expense' },
  ];

  useEffect(() => {
    if (isEditing) {
      dispatch(fetchAccount(accountId));
    }
  }, [accountId]);

  useEffect(() => {
    if (isEditing && selectedAccount) {
      setFormData({
        code: selectedAccount.code,
        name: selectedAccount.name,
        accountTypeId: selectedAccount.accountType?.id || '',
        parent: selectedAccount.parent || '',
        isActive: selectedAccount.isActive,
        allowsTransactions: selectedAccount.allowsTransactions,
      });
    }
  }, [selectedAccount, isEditing]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.code.trim()) {
      newErrors.code = 'El código es requerido';
    }
    
    if (!formData.name.trim()) {
      newErrors.name = 'El nombre es requerido';
    }
    
    if (!formData.accountTypeId) {
      newErrors.accountTypeId = 'El tipo de cuenta es requerido';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;
    
    setLoading(true);
    try {
      const accountData: Partial<Account> = {
        code: formData.code,
        name: formData.name,
        isActive: formData.isActive,
        allowsTransactions: formData.allowsTransactions,
      };
      
      if (isEditing) {
        await dispatch(updateAccount({ id: accountId, account: accountData }));
      } else {
        await dispatch(createAccount(accountData));
      }
      
      navigation.goBack();
    } catch (error) {
      console.error('Error saving account:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectedType = accountTypes.find(t => t.id === formData.accountTypeId);
  const selectedParent = accounts.find(a => a.id === formData.parent);

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title={isEditing ? 'Editar Cuenta' : 'Nueva Cuenta'} />
      </Appbar.Header>

      <ScrollView style={styles.content} contentContainerStyle={styles.scrollContent}>
        <TextInput
          label="Código *"
          value={formData.code}
          onChangeText={(text) => setFormData({ ...formData, code: text })}
          mode="outlined"
          style={styles.input}
          error={!!errors.code}
        />
        <HelperText type="error" visible={!!errors.code}>
          {errors.code}
        </HelperText>

        <TextInput
          label="Nombre *"
          value={formData.name}
          onChangeText={(text) => setFormData({ ...formData, name: text })}
          mode="outlined"
          style={styles.input}
          error={!!errors.name}
        />
        <HelperText type="error" visible={!!errors.name}>
          {errors.name}
        </HelperText>

        <Menu
          visible={typeMenuVisible}
          onDismiss={() => setTypeMenuVisible(false)}
          anchor={
            <TextInput
              label="Tipo de Cuenta *"
              value={selectedType?.name || ''}
              mode="outlined"
              style={styles.input}
              editable={false}
              right={<TextInput.Icon icon="chevron-down" onPress={() => setTypeMenuVisible(true)} />}
              onPressIn={() => setTypeMenuVisible(true)}
              error={!!errors.accountTypeId}
            />
          }
        >
          {accountTypes.map((type) => (
            <Menu.Item
              key={type.id}
              onPress={() => {
                setFormData({ ...formData, accountTypeId: type.id });
                setTypeMenuVisible(false);
              }}
              title={type.name}
            />
          ))}
        </Menu>
        <HelperText type="error" visible={!!errors.accountTypeId}>
          {errors.accountTypeId}
        </HelperText>

        <Menu
          visible={parentMenuVisible}
          onDismiss={() => setParentMenuVisible(false)}
          anchor={
            <TextInput
              label="Cuenta Padre (opcional)"
              value={selectedParent ? `${selectedParent.code} - ${selectedParent.name}` : ''}
              mode="outlined"
              style={styles.input}
              editable={false}
              right={<TextInput.Icon icon="chevron-down" onPress={() => setParentMenuVisible(true)} />}
              onPressIn={() => setParentMenuVisible(true)}
            />
          }
        >
          <Menu.Item
            onPress={() => {
              setFormData({ ...formData, parent: '' });
              setParentMenuVisible(false);
            }}
            title="Sin cuenta padre"
          />
          <Divider />
          {accounts.filter(a => a.id !== accountId).map((account) => (
            <Menu.Item
              key={account.id}
              onPress={() => {
                setFormData({ ...formData, parent: account.id });
                setParentMenuVisible(false);
              }}
              title={`${account.code} - ${account.name}`}
            />
          ))}
        </Menu>

        <View style={styles.switchRow}>
          <Text variant="bodyLarge">Cuenta Activa</Text>
          <Switch
            value={formData.isActive}
            onValueChange={(value) => setFormData({ ...formData, isActive: value })}
          />
        </View>

        <View style={styles.switchRow}>
          <Text variant="bodyLarge">Permite Transacciones</Text>
          <Switch
            value={formData.allowsTransactions}
            onValueChange={(value) => setFormData({ ...formData, allowsTransactions: value })}
          />
        </View>

        <Button
          mode="contained"
          onPress={handleSubmit}
          loading={loading}
          disabled={loading}
          style={styles.button}
        >
          {isEditing ? 'Actualizar' : 'Crear'} Cuenta
        </Button>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
  },
  input: {
    marginBottom: 4,
    backgroundColor: '#fff',
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
    backgroundColor: '#fff',
    borderRadius: 8,
    marginVertical: 8,
  },
  button: {
    marginTop: 24,
    paddingVertical: 8,
  },
});

export default AccountFormScreen;
