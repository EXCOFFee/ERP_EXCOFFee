// ========================================================
// Finance Module - Account List Screen
// ========================================================

import React, { useEffect, useState, useCallback } from 'react';
import { View, StyleSheet, FlatList, RefreshControl } from 'react-native';
import { 
  Appbar, 
  Card, 
  Text, 
  Searchbar, 
  FAB, 
  Chip,
  useTheme,
  ActivityIndicator,
  Divider
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '../../hooks/useStore';
import { 
  fetchAccounts, 
  selectAccounts, 
  selectAccountsLoading 
} from '../../store/slices/financeSlice';
import { Account } from '../../services/finance.service';

const AccountListScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<any>();
  const dispatch = useAppDispatch();
  
  const accounts = useAppSelector(selectAccounts);
  const loading = useAppSelector(selectAccountsLoading);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = useCallback(async () => {
    await dispatch(fetchAccounts({ search: searchQuery }));
  }, [dispatch, searchQuery]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadAccounts();
    setRefreshing(false);
  }, [loadAccounts]);

  const handleSearch = useCallback(() => {
    loadAccounts();
  }, [loadAccounts]);

  const getClassificationColor = (classification: string) => {
    switch (classification) {
      case 'asset': return '#4CAF50';
      case 'liability': return '#F44336';
      case 'equity': return '#2196F3';
      case 'income': return '#8BC34A';
      case 'expense': return '#FF9800';
      default: return '#9E9E9E';
    }
  };

  const getClassificationLabel = (classification: string) => {
    const labels: Record<string, string> = {
      'asset': 'Activo',
      'liability': 'Pasivo',
      'equity': 'Patrimonio',
      'income': 'Ingreso',
      'expense': 'Gasto',
    };
    return labels[classification] || classification;
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const renderAccount = ({ item }: { item: Account }) => (
    <Card 
      style={styles.card} 
      mode="outlined"
      onPress={() => navigation.navigate('AccountDetail', { accountId: item.id })}
    >
      <Card.Content>
        <View style={styles.cardHeader}>
          <View style={styles.codeContainer}>
            <Text variant="titleMedium" style={styles.code}>{item.code}</Text>
            <Chip 
              compact 
              style={[styles.chip, { backgroundColor: getClassificationColor(item.accountType?.classification) }]}
              textStyle={styles.chipText}
            >
              {getClassificationLabel(item.accountType?.classification)}
            </Chip>
          </View>
          <Text 
            variant="titleMedium" 
            style={[
              styles.balance,
              { color: item.balance >= 0 ? theme.colors.primary : theme.colors.error }
            ]}
          >
            {formatCurrency(item.balance)}
          </Text>
        </View>
        
        <Text variant="bodyLarge" style={styles.name}>{item.name}</Text>
        
        <View style={styles.footer}>
          <Text variant="bodySmall" style={styles.type}>
            {item.accountType?.name}
          </Text>
          {!item.isActive && (
            <Chip compact style={styles.inactiveChip}>
              Inactiva
            </Chip>
          )}
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title="Cuentas Contables" />
      </Appbar.Header>

      <Searchbar
        placeholder="Buscar cuenta..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        onSubmitEditing={handleSearch}
        style={styles.searchbar}
      />

      {loading && !refreshing ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" />
        </View>
      ) : (
        <FlatList
          data={accounts}
          renderItem={renderAccount}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          ItemSeparatorComponent={() => <Divider />}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text variant="bodyLarge">No se encontraron cuentas</Text>
            </View>
          }
        />
      )}

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => navigation.navigate('AccountForm')}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  searchbar: {
    margin: 16,
    elevation: 2,
  },
  list: {
    paddingHorizontal: 16,
    paddingBottom: 80,
  },
  card: {
    marginVertical: 4,
    backgroundColor: '#fff',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  codeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  code: {
    fontWeight: 'bold',
  },
  chip: {
    height: 24,
  },
  chipText: {
    fontSize: 10,
    color: '#fff',
  },
  balance: {
    fontWeight: 'bold',
  },
  name: {
    marginBottom: 8,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  type: {
    color: '#666',
  },
  inactiveChip: {
    backgroundColor: '#ffcdd2',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 100,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
});

export default AccountListScreen;
