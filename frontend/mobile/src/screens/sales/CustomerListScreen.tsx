import React, { useState } from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { Text, Card, useTheme, Searchbar, FAB, Chip, IconButton, Avatar } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { SalesStackParamList } from '../../navigation/types';

type NavigationProp = NativeStackNavigationProp<SalesStackParamList, 'CustomerList'>;

interface Customer {
  id: number;
  name: string;
  email: string;
  phone: string;
  type: 'individual' | 'company';
  totalPurchases: number;
}

const mockCustomers: Customer[] = [
  { id: 1, name: 'Juan Pérez', email: 'juan@email.com', phone: '+52 555 1234', type: 'individual', totalPurchases: 15600 },
  { id: 2, name: 'Tech Solutions SA', email: 'contacto@techsol.com', phone: '+52 555 5678', type: 'company', totalPurchases: 89500 },
  { id: 3, name: 'María García', email: 'maria@email.com', phone: '+52 555 9012', type: 'individual', totalPurchases: 4200 },
  { id: 4, name: 'Comercial ABC', email: 'ventas@abc.com', phone: '+52 555 3456', type: 'company', totalPurchases: 125000 },
];

const CustomerListScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<NavigationProp>();
  const [searchQuery, setSearchQuery] = useState('');

  const filteredCustomers = mockCustomers.filter(c =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const renderCustomer = ({ item }: { item: Customer }) => (
    <Card
      style={styles.card}
      onPress={() => navigation.navigate('CustomerDetail', { id: item.id })}
    >
      <Card.Content style={styles.cardContent}>
        <Avatar.Text
          size={48}
          label={item.name.split(' ').map(n => n[0]).join('').substring(0, 2)}
          style={{ backgroundColor: item.type === 'company' ? '#9c27b0' : theme.colors.primary }}
        />
        <View style={styles.customerInfo}>
          <Text variant="titleMedium" style={{ fontWeight: '600' }}>
            {item.name}
          </Text>
          <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
            {item.email}
          </Text>
          <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
            {item.phone}
          </Text>
        </View>
        <View style={styles.customerMeta}>
          <Chip compact icon={item.type === 'company' ? 'domain' : 'account'}>
            {item.type === 'company' ? 'Empresa' : 'Persona'}
          </Chip>
          <Text variant="bodySmall" style={{ color: theme.colors.primary, fontWeight: '600' }}>
            ${item.totalPurchases.toLocaleString()}
          </Text>
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <IconButton icon="arrow-left" onPress={() => navigation.goBack()} />
        <Text variant="titleLarge" style={{ flex: 1, fontWeight: 'bold' }}>
          Clientes
        </Text>
      </View>

      <Searchbar
        placeholder="Buscar cliente..."
        value={searchQuery}
        onChangeText={setSearchQuery}
        style={styles.searchbar}
      />

      <FlatList
        data={filteredCustomers}
        renderItem={renderCustomer}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.list}
        ItemSeparatorComponent={() => <View style={{ height: 12 }} />}
      />

      <FAB
        icon="plus"
        style={[styles.fab, { backgroundColor: theme.colors.primary }]}
        onPress={() => navigation.navigate('CustomerForm', {})}
        color="#fff"
      />
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
  customerInfo: { flex: 1, gap: 2 },
  customerMeta: { alignItems: 'flex-end', gap: 8 },
  fab: { position: 'absolute', right: 16, bottom: 16 },
});

export default CustomerListScreen;
