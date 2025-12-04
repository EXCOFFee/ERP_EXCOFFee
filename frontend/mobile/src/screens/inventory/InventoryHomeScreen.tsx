import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, useTheme, FAB, Searchbar, Chip } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import { InventoryStackParamList } from '../../navigation/types';

type NavigationProp = NativeStackNavigationProp<InventoryStackParamList, 'InventoryHome'>;

interface MenuItemProps {
  title: string;
  subtitle: string;
  icon: string;
  color: string;
  badge?: number;
  onPress: () => void;
}

const MenuItem: React.FC<MenuItemProps> = ({ title, subtitle, icon, color, badge, onPress }) => {
  const theme = useTheme();
  
  return (
    <Card style={styles.menuCard} onPress={onPress}>
      <Card.Content style={styles.menuContent}>
        <View style={[styles.menuIcon, { backgroundColor: color + '20' }]}>
          <MaterialCommunityIcons name={icon} size={28} color={color} />
        </View>
        <View style={styles.menuInfo}>
          <Text variant="titleMedium" style={{ fontWeight: '600' }}>
            {title}
          </Text>
          <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
            {subtitle}
          </Text>
        </View>
        {badge !== undefined && badge > 0 && (
          <Chip compact style={styles.badge}>{badge}</Chip>
        )}
        <MaterialCommunityIcons
          name="chevron-right"
          size={24}
          color={theme.colors.onSurfaceVariant}
        />
      </Card.Content>
    </Card>
  );
};

const InventoryHomeScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<NavigationProp>();
  const [searchQuery, setSearchQuery] = React.useState('');

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <Text variant="headlineMedium" style={{ fontWeight: 'bold' }}>
          Inventario
        </Text>
      </View>

      <Searchbar
        placeholder="Buscar productos..."
        value={searchQuery}
        onChangeText={setSearchQuery}
        style={styles.searchbar}
      />

      <ScrollView contentContainerStyle={styles.content}>
        <MenuItem
          title="Productos"
          subtitle="1,234 productos activos"
          icon="package-variant"
          color={theme.colors.primary}
          onPress={() => navigation.navigate('ProductList')}
        />
        <MenuItem
          title="Categorías"
          subtitle="45 categorías"
          icon="shape"
          color="#9c27b0"
          onPress={() => navigation.navigate('CategoryList')}
        />
        <MenuItem
          title="Almacenes"
          subtitle="3 ubicaciones"
          icon="warehouse"
          color="#ff9800"
          onPress={() => navigation.navigate('WarehouseList')}
        />
        <MenuItem
          title="Movimientos"
          subtitle="Ver historial"
          icon="swap-horizontal"
          color="#4caf50"
          onPress={() => navigation.navigate('StockMovements')}
        />
        <MenuItem
          title="Stock Bajo"
          subtitle="Productos críticos"
          icon="alert-circle"
          color="#f44336"
          badge={15}
          onPress={() => navigation.navigate('ProductList')}
        />
      </ScrollView>

      <FAB
        icon="barcode-scan"
        style={[styles.fab, { backgroundColor: theme.colors.primary }]}
        onPress={() => navigation.navigate('BarcodeScanner')}
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
    paddingBottom: 8,
  },
  searchbar: {
    marginHorizontal: 16,
    marginBottom: 16,
  },
  content: {
    padding: 16,
    paddingTop: 0,
    gap: 12,
  },
  menuCard: {},
  menuContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  menuIcon: {
    width: 48,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  menuInfo: {
    flex: 1,
  },
  badge: {
    marginRight: 8,
  },
  fab: {
    position: 'absolute',
    right: 16,
    bottom: 16,
  },
});

export default InventoryHomeScreen;
