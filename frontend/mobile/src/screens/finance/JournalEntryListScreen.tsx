// ========================================================
// Finance Module - Journal Entry List Screen
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
  ActivityIndicator,
  Divider
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '../../hooks/useStore';
import { 
  fetchJournalEntries, 
  selectJournalEntries, 
  selectJournalEntriesLoading 
} from '../../store/slices/financeSlice';
import { JournalEntry } from '../../services/finance.service';

const JournalEntryListScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const dispatch = useAppDispatch();
  
  const entries = useAppSelector(selectJournalEntries);
  const loading = useAppSelector(selectJournalEntriesLoading);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadEntries();
  }, []);

  const loadEntries = useCallback(async () => {
    await dispatch(fetchJournalEntries({ search: searchQuery }));
  }, [dispatch, searchQuery]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadEntries();
    setRefreshing(false);
  }, [loadEntries]);

  const handleSearch = useCallback(() => {
    loadEntries();
  }, [loadEntries]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'posted': return '#4CAF50';
      case 'draft': return '#FF9800';
      case 'reversed': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      'posted': 'Contabilizado',
      'draft': 'Borrador',
      'reversed': 'Reversado',
    };
    return labels[status] || status;
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const renderEntry = ({ item }: { item: JournalEntry }) => (
    <Card 
      style={styles.card} 
      mode="outlined"
      onPress={() => navigation.navigate('JournalEntryDetail', { entryId: item.id })}
    >
      <Card.Content>
        <View style={styles.cardHeader}>
          <View>
            <Text variant="titleMedium" style={styles.entryNumber}>
              {item.entryNumber}
            </Text>
            <Text variant="bodySmall" style={styles.date}>
              {formatDate(item.entryDate)}
            </Text>
          </View>
          <Chip 
            compact 
            style={[styles.chip, { backgroundColor: getStatusColor(item.status) }]}
            textStyle={styles.chipText}
          >
            {getStatusLabel(item.status)}
          </Chip>
        </View>
        
        <Text variant="bodyMedium" style={styles.description} numberOfLines={2}>
          {item.description}
        </Text>
        
        <Divider style={styles.divider} />
        
        <View style={styles.amounts}>
          <View style={styles.amountColumn}>
            <Text variant="bodySmall" style={styles.amountLabel}>Débito</Text>
            <Text variant="titleSmall" style={styles.debit}>
              {formatCurrency(item.totalDebit)}
            </Text>
          </View>
          <View style={styles.amountColumn}>
            <Text variant="bodySmall" style={styles.amountLabel}>Crédito</Text>
            <Text variant="titleSmall" style={styles.credit}>
              {formatCurrency(item.totalCredit)}
            </Text>
          </View>
        </View>
        
        {item.reference && (
          <Text variant="bodySmall" style={styles.reference}>
            Ref: {item.reference}
          </Text>
        )}
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title="Asientos Contables" />
      </Appbar.Header>

      <Searchbar
        placeholder="Buscar asiento..."
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
          data={entries}
          renderItem={renderEntry}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text variant="bodyLarge">No se encontraron asientos</Text>
            </View>
          }
        />
      )}

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => navigation.navigate('JournalEntryForm')}
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
  entryNumber: {
    fontWeight: 'bold',
  },
  date: {
    color: '#666',
  },
  chip: {
    height: 24,
  },
  chipText: {
    fontSize: 10,
    color: '#fff',
  },
  description: {
    marginBottom: 8,
  },
  divider: {
    marginVertical: 8,
  },
  amounts: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  amountColumn: {
    alignItems: 'center',
  },
  amountLabel: {
    color: '#666',
  },
  debit: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  credit: {
    color: '#F44336',
    fontWeight: 'bold',
  },
  reference: {
    color: '#666',
    marginTop: 8,
    fontStyle: 'italic',
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

export default JournalEntryListScreen;
