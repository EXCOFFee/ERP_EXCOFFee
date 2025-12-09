// ========================================================
// HR Module - Department List Screen
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
  IconButton,
  useTheme,
  ActivityIndicator,
  Portal,
  Dialog,
  Button
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '../../hooks/useStore';
import { 
  fetchDepartments, 
  deleteDepartment,
  selectDepartments, 
  selectDepartmentsLoading 
} from '../../store/slices/hrSlice';
import { Department } from '../../services/hr.service';

const DepartmentListScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<any>();
  const dispatch = useAppDispatch();
  
  const departments = useAppSelector(selectDepartments);
  const loading = useAppSelector(selectDepartmentsLoading);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [deleteDialogVisible, setDeleteDialogVisible] = useState(false);
  const [selectedDeptId, setSelectedDeptId] = useState<string | null>(null);

  useEffect(() => {
    loadDepartments();
  }, []);

  const loadDepartments = useCallback(async () => {
    await dispatch(fetchDepartments({ search: searchQuery }));
  }, [dispatch, searchQuery]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadDepartments();
    setRefreshing(false);
  }, [loadDepartments]);

  const handleSearch = useCallback(() => {
    loadDepartments();
  }, [loadDepartments]);

  const handleDelete = async () => {
    if (selectedDeptId) {
      await dispatch(deleteDepartment(selectedDeptId));
      setDeleteDialogVisible(false);
      setSelectedDeptId(null);
    }
  };

  const confirmDelete = (id: string) => {
    setSelectedDeptId(id);
    setDeleteDialogVisible(true);
  };

  const renderDepartment = ({ item }: { item: Department }) => (
    <Card 
      style={styles.card} 
      mode="outlined"
      onPress={() => navigation.navigate('DepartmentDetail', { departmentId: item.id })}
    >
      <Card.Content>
        <View style={styles.cardHeader}>
          <View style={styles.codeContainer}>
            <Text variant="labelSmall" style={styles.code}>{item.code}</Text>
            {!item.isActive && (
              <Chip compact style={styles.inactiveChip} textStyle={styles.inactiveText}>
                Inactivo
              </Chip>
            )}
          </View>
          <View style={styles.actions}>
            <IconButton
              icon="pencil"
              size={20}
              onPress={() => navigation.navigate('DepartmentForm', { departmentId: item.id })}
            />
            <IconButton
              icon="delete"
              size={20}
              iconColor={theme.colors.error}
              onPress={() => confirmDelete(item.id)}
            />
          </View>
        </View>
        
        <Text variant="titleMedium" style={styles.name}>{item.name}</Text>
        
        {item.description && (
          <Text variant="bodySmall" style={styles.description} numberOfLines={2}>
            {item.description}
          </Text>
        )}
        
        {item.manager && (
          <Text variant="bodySmall" style={styles.manager}>
            Gerente: {item.manager}
          </Text>
        )}
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title="Departamentos" />
      </Appbar.Header>

      <Searchbar
        placeholder="Buscar departamento..."
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
          data={departments}
          renderItem={renderDepartment}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text variant="bodyLarge">No se encontraron departamentos</Text>
            </View>
          }
        />
      )}

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => navigation.navigate('DepartmentForm')}
      />

      <Portal>
        <Dialog visible={deleteDialogVisible} onDismiss={() => setDeleteDialogVisible(false)}>
          <Dialog.Title>Confirmar eliminación</Dialog.Title>
          <Dialog.Content>
            <Text>¿Está seguro de que desea eliminar este departamento?</Text>
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setDeleteDialogVisible(false)}>Cancelar</Button>
            <Button onPress={handleDelete} textColor={theme.colors.error}>Eliminar</Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>
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
    alignItems: 'center',
  },
  codeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  code: {
    backgroundColor: '#e3f2fd',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    color: '#1976d2',
  },
  inactiveChip: {
    backgroundColor: '#ffcdd2',
    height: 22,
  },
  inactiveText: {
    fontSize: 10,
  },
  actions: {
    flexDirection: 'row',
  },
  name: {
    fontWeight: 'bold',
    marginTop: 8,
  },
  description: {
    color: '#666',
    marginTop: 4,
  },
  manager: {
    color: '#999',
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

export default DepartmentListScreen;
