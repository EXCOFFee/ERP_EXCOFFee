import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, useTheme, FAB, Chip } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import { SalesStackParamList } from '../../navigation/types';

type NavigationProp = NativeStackNavigationProp<SalesStackParamList, 'SalesHome'>;

const SalesHomeScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<NavigationProp>();

  const stats = [
    { title: 'Ventas Hoy', value: '$12,450', icon: 'cash', color: theme.colors.primary },
    { title: 'Pedidos', value: '28', icon: 'shopping', color: '#9c27b0' },
    { title: 'Cotizaciones', value: '12', icon: 'file-document', color: '#ff9800' },
    { title: 'Por Cobrar', value: '$8,200', icon: 'credit-card-clock', color: '#f44336' },
  ];

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <Text variant="headlineMedium" style={{ fontWeight: 'bold' }}>
          Ventas
        </Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Estadísticas */}
        <View style={styles.statsGrid}>
          {stats.map((stat, index) => (
            <Card key={index} style={styles.statCard}>
              <Card.Content style={styles.statContent}>
                <View style={[styles.statIcon, { backgroundColor: stat.color + '20' }]}>
                  <MaterialCommunityIcons name={stat.icon} size={24} color={stat.color} />
                </View>
                <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                  {stat.title}
                </Text>
                <Text variant="titleLarge" style={{ fontWeight: 'bold' }}>
                  {stat.value}
                </Text>
              </Card.Content>
            </Card>
          ))}
        </View>

        {/* Menú */}
        <Text variant="titleMedium" style={styles.sectionTitle}>
          Gestión
        </Text>

        <Card style={styles.menuCard} onPress={() => navigation.navigate('CustomerList')}>
          <Card.Content style={styles.menuContent}>
            <MaterialCommunityIcons name="account-group" size={28} color={theme.colors.primary} />
            <View style={styles.menuInfo}>
              <Text variant="titleMedium">Clientes</Text>
              <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                856 clientes registrados
              </Text>
            </View>
            <MaterialCommunityIcons name="chevron-right" size={24} color={theme.colors.onSurfaceVariant} />
          </Card.Content>
        </Card>

        <Card style={styles.menuCard} onPress={() => navigation.navigate('OrderList')}>
          <Card.Content style={styles.menuContent}>
            <MaterialCommunityIcons name="cart" size={28} color="#9c27b0" />
            <View style={styles.menuInfo}>
              <Text variant="titleMedium">Pedidos</Text>
              <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                Ver y gestionar pedidos
              </Text>
            </View>
            <Chip compact>5 nuevos</Chip>
            <MaterialCommunityIcons name="chevron-right" size={24} color={theme.colors.onSurfaceVariant} />
          </Card.Content>
        </Card>

        <Card style={styles.menuCard} onPress={() => navigation.navigate('InvoiceList')}>
          <Card.Content style={styles.menuContent}>
            <MaterialCommunityIcons name="file-document" size={28} color="#ff9800" />
            <View style={styles.menuInfo}>
              <Text variant="titleMedium">Facturas</Text>
              <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                Facturación y cobros
              </Text>
            </View>
            <MaterialCommunityIcons name="chevron-right" size={24} color={theme.colors.onSurfaceVariant} />
          </Card.Content>
        </Card>
      </ScrollView>

      <FAB
        icon="plus"
        label="Nueva Venta"
        style={[styles.fab, { backgroundColor: theme.colors.primary }]}
        onPress={() => navigation.navigate('OrderForm', {})}
        color="#fff"
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: 16,
  },
  content: {
    padding: 16,
    paddingTop: 0,
    paddingBottom: 80,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 24,
  },
  statCard: {
    width: '47%',
  },
  statContent: {
    alignItems: 'center',
    gap: 4,
  },
  statIcon: {
    width: 48,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 4,
  },
  sectionTitle: {
    fontWeight: '600',
    marginBottom: 12,
  },
  menuCard: {
    marginBottom: 12,
  },
  menuContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  menuInfo: {
    flex: 1,
  },
  fab: {
    position: 'absolute',
    right: 16,
    bottom: 16,
  },
});

export default SalesHomeScreen;
