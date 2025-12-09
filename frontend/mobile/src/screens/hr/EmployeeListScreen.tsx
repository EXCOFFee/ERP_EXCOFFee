// ========================================================
// HR Module - Employee List Screen
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
  Avatar,
  ActivityIndicator
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '../../hooks/useStore';
import { 
  fetchEmployees, 
  selectEmployees, 
  selectEmployeesLoading 
} from '../../store/slices/hrSlice';
import { Employee } from '../../services/hr.service';

const EmployeeListScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const dispatch = useAppDispatch();
  
  const employees = useAppSelector(selectEmployees);
  const loading = useAppSelector(selectEmployeesLoading);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadEmployees();
  }, []);

  const loadEmployees = useCallback(async () => {
    await dispatch(fetchEmployees({ search: searchQuery }));
  }, [dispatch, searchQuery]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadEmployees();
    setRefreshing(false);
  }, [loadEmployees]);

  const handleSearch = useCallback(() => {
    loadEmployees();
  }, [loadEmployees]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#4CAF50';
      case 'on_leave': return '#FF9800';
      case 'terminated': return '#F44336';
      case 'suspended': return '#9E9E9E';
      default: return '#9E9E9E';
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      'active': 'Activo',
      'on_leave': 'En Permiso',
      'terminated': 'Desvinculado',
      'suspended': 'Suspendido',
    };
    return labels[status] || status;
  };

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName?.charAt(0) || ''}${lastName?.charAt(0) || ''}`.toUpperCase();
  };

  const renderEmployee = ({ item }: { item: Employee }) => (
    <Card 
      style={styles.card} 
      mode="outlined"
      onPress={() => navigation.navigate('EmployeeDetail', { employeeId: item.id })}
    >
      <Card.Content style={styles.cardContent}>
        <Avatar.Text 
          size={50} 
          label={getInitials(item.firstName, item.lastName)}
          style={styles.avatar}
        />
        <View style={styles.info}>
          <View style={styles.nameRow}>
            <Text variant="titleMedium" style={styles.name}>
              {item.fullName || `${item.firstName} ${item.lastName}`}
            </Text>
            <Chip 
              compact 
              style={[styles.chip, { backgroundColor: getStatusColor(item.employmentStatus) }]}
              textStyle={styles.chipText}
            >
              {getStatusLabel(item.employmentStatus)}
            </Chip>
          </View>
          
          <Text variant="bodyMedium" style={styles.position}>
            {item.position?.name}
          </Text>
          
          <Text variant="bodySmall" style={styles.department}>
            {item.department?.name}
          </Text>
          
          <View style={styles.footer}>
            <Text variant="bodySmall" style={styles.employeeNumber}>
              #{item.employeeNumber}
            </Text>
            <Text variant="bodySmall" style={styles.email}>
              {item.email}
            </Text>
          </View>
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title="Empleados" />
      </Appbar.Header>

      <Searchbar
        placeholder="Buscar empleado..."
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
          data={employees}
          renderItem={renderEmployee}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text variant="bodyLarge">No se encontraron empleados</Text>
            </View>
          }
        />
      )}

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => navigation.navigate('EmployeeForm')}
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
  cardContent: {
    flexDirection: 'row',
  },
  avatar: {
    marginRight: 12,
  },
  info: {
    flex: 1,
  },
  nameRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  name: {
    fontWeight: 'bold',
    flex: 1,
  },
  chip: {
    height: 22,
  },
  chipText: {
    fontSize: 10,
    color: '#fff',
  },
  position: {
    color: '#333',
  },
  department: {
    color: '#666',
    marginBottom: 8,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  employeeNumber: {
    color: '#999',
  },
  email: {
    color: '#666',
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

export default EmployeeListScreen;
