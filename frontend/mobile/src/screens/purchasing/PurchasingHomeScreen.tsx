import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, useTheme, FAB, Chip } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import { PurchasingStackParamList } from '../../navigation/types';

type NavigationProp = NativeStackNavigationProp<PurchasingStackParamList, 'PurchasingHome'>;

const PurchasingHomeScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<NavigationProp>();

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <Text variant="headlineMedium" style={{ fontWeight: 'bold' }}>
          Compras
        </Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.statsRow}>
          <Card style={styles.statCard}>
            <Card.Content style={styles.statContent}>
              <MaterialCommunityIcons name="file-document-edit" size={32} color={theme.colors.primary} />
              <Text variant="headlineMedium" style={{ fontWeight: 'bold' }}>8</Text>
              <Text variant="bodySmall">Órdenes pendientes</Text>
            </Card.Content>
          </Card>
          <Card style={styles.statCard}>
            <Card.Content style={styles.statContent}>
              <MaterialCommunityIcons name="truck-delivery" size={32} color="#ff9800" />
              <Text variant="headlineMedium" style={{ fontWeight: 'bold' }}>3</Text>
              <Text variant="bodySmall">Por recibir</Text>
            </Card.Content>
          </Card>
        </View>

        <Text variant="titleMedium" style={styles.sectionTitle}>Gestión</Text>

        <Card style={styles.menuCard} onPress={() => navigation.navigate('SupplierList')}>
          <Card.Content style={styles.menuContent}>
            <MaterialCommunityIcons name="account-group" size={28} color={theme.colors.primary} />
            <View style={styles.menuInfo}>
              <Text variant="titleMedium">Proveedores</Text>
              <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                124 proveedores registrados
              </Text>
            </View>
            <MaterialCommunityIcons name="chevron-right" size={24} color={theme.colors.onSurfaceVariant} />
          </Card.Content>
        </Card>

        <Card style={styles.menuCard} onPress={() => navigation.navigate('PurchaseOrderList')}>
          <Card.Content style={styles.menuContent}>
            <MaterialCommunityIcons name="clipboard-list" size={28} color="#9c27b0" />
            <View style={styles.menuInfo}>
              <Text variant="titleMedium">Órdenes de Compra</Text>
              <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                Gestionar órdenes
              </Text>
            </View>
            <Chip compact>8 nuevas</Chip>
            <MaterialCommunityIcons name="chevron-right" size={24} color={theme.colors.onSurfaceVariant} />
          </Card.Content>
        </Card>

        <Card style={styles.menuCard} onPress={() => navigation.navigate('GoodsReceiptList')}>
          <Card.Content style={styles.menuContent}>
            <MaterialCommunityIcons name="package-down" size={28} color="#4caf50" />
            <View style={styles.menuInfo}>
              <Text variant="titleMedium">Recepciones</Text>
              <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                Recepción de mercancías
              </Text>
            </View>
            <MaterialCommunityIcons name="chevron-right" size={24} color={theme.colors.onSurfaceVariant} />
          </Card.Content>
        </Card>
      </ScrollView>

      <FAB
        icon="plus"
        label="Nueva Orden"
        style={[styles.fab, { backgroundColor: theme.colors.primary }]}
        onPress={() => navigation.navigate('PurchaseOrderForm', {})}
        color="#fff"
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { padding: 16 },
  content: { padding: 16, paddingTop: 0, paddingBottom: 80 },
  statsRow: { flexDirection: 'row', gap: 12, marginBottom: 24 },
  statCard: { flex: 1 },
  statContent: { alignItems: 'center', gap: 4 },
  sectionTitle: { fontWeight: '600', marginBottom: 12 },
  menuCard: { marginBottom: 12 },
  menuContent: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  menuInfo: { flex: 1 },
  fab: { position: 'absolute', right: 16, bottom: 16 },
});

export default PurchasingHomeScreen;
