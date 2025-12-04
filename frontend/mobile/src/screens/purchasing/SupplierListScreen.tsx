import React from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { Text, Card, useTheme, Searchbar, FAB, Chip, IconButton, Avatar } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { PurchasingStackParamList } from '../../navigation/types';

type NavigationProp = NativeStackNavigationProp<PurchasingStackParamList, 'SupplierList'>;

const mockSuppliers = [
  { id: 1, name: 'Distribuidora Nacional', email: 'ventas@distnac.com', rating: 4.5, totalOrders: 156 },
  { id: 2, name: 'Tech Import SA', email: 'contacto@techimport.com', rating: 4.8, totalOrders: 89 },
  { id: 3, name: 'Suministros Globales', email: 'info@sumglobal.com', rating: 3.9, totalOrders: 45 },
];

const SupplierListScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<NavigationProp>();
  const [searchQuery, setSearchQuery] = React.useState('');

  const renderSupplier = ({ item }: { item: typeof mockSuppliers[0] }) => (
    <Card style={styles.card} onPress={() => navigation.navigate('SupplierDetail', { id: item.id })}>
      <Card.Content style={styles.cardContent}>
        <Avatar.Text size={48} label={item.name.substring(0, 2)} />
        <View style={styles.supplierInfo}>
          <Text variant="titleMedium" style={{ fontWeight: '600' }}>{item.name}</Text>
          <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>{item.email}</Text>
        </View>
        <View style={styles.supplierMeta}>
          <Chip compact icon="star">{item.rating}</Chip>
          <Text variant="bodySmall">{item.totalOrders} órdenes</Text>
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <IconButton icon="arrow-left" onPress={() => navigation.goBack()} />
        <Text variant="titleLarge" style={{ flex: 1, fontWeight: 'bold' }}>Proveedores</Text>
      </View>

      <Searchbar placeholder="Buscar proveedor..." value={searchQuery} onChangeText={setSearchQuery} style={styles.searchbar} />

      <FlatList
        data={mockSuppliers}
        renderItem={renderSupplier}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.list}
        ItemSeparatorComponent={() => <View style={{ height: 12 }} />}
      />

      <FAB icon="plus" style={[styles.fab, { backgroundColor: theme.colors.primary }]} onPress={() => {}} color="#fff" />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center' },
  searchbar: { marginHorizontal: 16, marginBottom: 16 },
  list: { padding: 16, paddingTop: 0 },
  card: {},
  cardContent: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  supplierInfo: { flex: 1, gap: 2 },
  supplierMeta: { alignItems: 'flex-end', gap: 8 },
  fab: { position: 'absolute', right: 16, bottom: 16 },
});

export default SupplierListScreen;
