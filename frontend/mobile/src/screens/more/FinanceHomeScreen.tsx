import React from 'react';
import { View, StyleSheet, ScrollView, Dimensions } from 'react-native';
import { Text, Card, useTheme, IconButton, FAB, Divider } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';

const { width } = Dimensions.get('window');
const cardWidth = (width - 48) / 2;

const FinanceHomeScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation();

  const statsData = [
    { label: 'Ingresos', value: '$125,430.00', icon: 'trending-up', color: '#4caf50' },
    { label: 'Gastos', value: '$78,320.00', icon: 'trending-down', color: '#f44336' },
    { label: 'Balance', value: '$47,110.00', icon: 'wallet', color: '#2196f3' },
    { label: 'Cuentas', value: '12', icon: 'bank', color: '#9c27b0' },
  ];

  const recentTransactions = [
    { id: '1', description: 'Venta #1234', amount: 2500.00, type: 'income', date: '2024-01-15' },
    { id: '2', description: 'Compra materiales', amount: -850.00, type: 'expense', date: '2024-01-15' },
    { id: '3', description: 'Venta #1235', amount: 1800.00, type: 'income', date: '2024-01-14' },
    { id: '4', description: 'Servicios públicos', amount: -350.00, type: 'expense', date: '2024-01-14' },
  ];

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <IconButton icon="arrow-left" onPress={() => navigation.goBack()} />
        <Text variant="titleLarge" style={{ flex: 1, fontWeight: 'bold' }}>Finanzas</Text>
        <IconButton icon="chart-bar" onPress={() => {}} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.statsGrid}>
          {statsData.map((stat, index) => (
            <Card key={index} style={[styles.statCard, { width: cardWidth }]}>
              <Card.Content style={styles.statContent}>
                <IconButton
                  icon={stat.icon}
                  iconColor={stat.color}
                  size={24}
                  style={{ backgroundColor: `${stat.color}20`, margin: 0 }}
                />
                <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                  {stat.label}
                </Text>
                <Text variant="titleMedium" style={{ fontWeight: 'bold' }}>
                  {stat.value}
                </Text>
              </Card.Content>
            </Card>
          ))}
        </View>

        <Card style={styles.card}>
          <Card.Content>
            <View style={styles.sectionHeader}>
              <Text variant="titleMedium" style={{ fontWeight: '600' }}>
                Resumen Mensual
              </Text>
              <Text variant="bodySmall" style={{ color: theme.colors.primary }}>
                Enero 2024
              </Text>
            </View>
            <View style={styles.summaryRow}>
              <Text variant="bodyMedium">Ingresos totales</Text>
              <Text variant="bodyMedium" style={{ color: '#4caf50', fontWeight: '600' }}>
                $125,430.00
              </Text>
            </View>
            <Divider style={{ marginVertical: 8 }} />
            <View style={styles.summaryRow}>
              <Text variant="bodyMedium">Gastos totales</Text>
              <Text variant="bodyMedium" style={{ color: '#f44336', fontWeight: '600' }}>
                $78,320.00
              </Text>
            </View>
            <Divider style={{ marginVertical: 8 }} />
            <View style={styles.summaryRow}>
              <Text variant="titleSmall" style={{ fontWeight: '600' }}>Balance neto</Text>
              <Text variant="titleSmall" style={{ color: '#4caf50', fontWeight: 'bold' }}>
                $47,110.00
              </Text>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <View style={styles.sectionHeader}>
              <Text variant="titleMedium" style={{ fontWeight: '600' }}>
                Transacciones Recientes
              </Text>
              <Text variant="bodySmall" style={{ color: theme.colors.primary }}>
                Ver todas
              </Text>
            </View>
          </Card.Content>
          {recentTransactions.map((transaction, index) => (
            <React.Fragment key={transaction.id}>
              {index > 0 && <Divider />}
              <View style={styles.transactionItem}>
                <View>
                  <Text variant="bodyMedium">{transaction.description}</Text>
                  <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                    {transaction.date}
                  </Text>
                </View>
                <Text
                  variant="bodyMedium"
                  style={{
                    fontWeight: '600',
                    color: transaction.type === 'income' ? '#4caf50' : '#f44336',
                  }}
                >
                  {transaction.type === 'income' ? '+' : ''}${Math.abs(transaction.amount).toFixed(2)}
                </Text>
              </View>
            </React.Fragment>
          ))}
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={{ fontWeight: '600', marginBottom: 16 }}>
              Acciones Rápidas
            </Text>
            <View style={styles.quickActions}>
              <View style={styles.quickAction}>
                <IconButton
                  icon="plus-circle"
                  mode="contained"
                  containerColor={`${theme.colors.primary}20`}
                  iconColor={theme.colors.primary}
                  onPress={() => {}}
                />
                <Text variant="bodySmall">Nuevo Ingreso</Text>
              </View>
              <View style={styles.quickAction}>
                <IconButton
                  icon="minus-circle"
                  mode="contained"
                  containerColor="#f4433620"
                  iconColor="#f44336"
                  onPress={() => {}}
                />
                <Text variant="bodySmall">Nuevo Gasto</Text>
              </View>
              <View style={styles.quickAction}>
                <IconButton
                  icon="bank-transfer"
                  mode="contained"
                  containerColor="#2196f320"
                  iconColor="#2196f3"
                  onPress={() => {}}
                />
                <Text variant="bodySmall">Transferencia</Text>
              </View>
              <View style={styles.quickAction}>
                <IconButton
                  icon="file-document"
                  mode="contained"
                  containerColor="#9c27b020"
                  iconColor="#9c27b0"
                  onPress={() => {}}
                />
                <Text variant="bodySmall">Reportes</Text>
              </View>
            </View>
          </Card.Content>
        </Card>
      </ScrollView>

      <FAB
        icon="plus"
        style={[styles.fab, { backgroundColor: theme.colors.primary }]}
        onPress={() => {}}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', paddingRight: 8 },
  content: { padding: 16, gap: 16, paddingBottom: 80 },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 16 },
  statCard: {},
  statContent: { alignItems: 'center', gap: 4 },
  card: {},
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  summaryRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  transactionItem: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16 },
  quickActions: { flexDirection: 'row', justifyContent: 'space-around' },
  quickAction: { alignItems: 'center', gap: 4 },
  fab: { position: 'absolute', margin: 16, right: 0, bottom: 0 },
});

export default FinanceHomeScreen;
