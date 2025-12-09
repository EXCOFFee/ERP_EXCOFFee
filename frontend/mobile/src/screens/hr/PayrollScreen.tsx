// ========================================================
// HR Module - Payroll Screen
// ========================================================

import React, { useEffect, useState, useCallback } from 'react';
import { View, StyleSheet, FlatList, RefreshControl } from 'react-native';
import { 
  Appbar, 
  Card, 
  Text, 
  Chip,
  ActivityIndicator,
  Divider,
  Surface
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '../../hooks/useStore';
import { 
  fetchMyPayslips,
  selectMyPayslips
} from '../../store/slices/hrSlice';
import { Payslip } from '../../services/hr.service';

const PayrollScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const dispatch = useAppDispatch();
  
  const payslips = useAppSelector(selectMyPayslips);
  
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadPayslips();
  }, []);

  const loadPayslips = useCallback(async () => {
    setLoading(true);
    await dispatch(fetchMyPayslips());
    setLoading(false);
  }, [dispatch]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await dispatch(fetchMyPayslips());
    setRefreshing(false);
  }, [dispatch]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid': return '#4CAF50';
      case 'pending': return '#FF9800';
      default: return '#9E9E9E';
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      'paid': 'Pagado',
      'pending': 'Pendiente',
    };
    return labels[status] || status;
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const latestPayslip = payslips.length > 0 ? payslips[0] : null;

  const renderSummary = () => {
    if (!latestPayslip) return null;
    
    return (
      <Surface style={styles.summaryCard} elevation={2}>
        <Text variant="titleMedium" style={styles.summaryTitle}>
          Último Recibo
        </Text>
        <Text variant="bodySmall" style={styles.periodName}>
          {latestPayslip.payrollPeriod?.name}
        </Text>
        
        <View style={styles.summaryContent}>
          <View style={styles.summaryItem}>
            <Text variant="labelSmall">Salario Bruto</Text>
            <Text variant="titleMedium" style={styles.grossAmount}>
              {formatCurrency(latestPayslip.grossSalary)}
            </Text>
          </View>
          
          <View style={styles.summaryItem}>
            <Text variant="labelSmall">Deducciones</Text>
            <Text variant="titleMedium" style={styles.deductionAmount}>
              -{formatCurrency(latestPayslip.totalDeductions)}
            </Text>
          </View>
          
          <Divider style={styles.summaryDivider} />
          
          <View style={styles.summaryItem}>
            <Text variant="labelSmall">Salario Neto</Text>
            <Text variant="headlineSmall" style={styles.netAmount}>
              {formatCurrency(latestPayslip.netSalary)}
            </Text>
          </View>
        </View>
        
        <Chip 
          compact 
          style={[styles.statusChip, { backgroundColor: getStatusColor(latestPayslip.paymentStatus) }]}
          textStyle={styles.chipText}
        >
          {getStatusLabel(latestPayslip.paymentStatus)}
        </Chip>
      </Surface>
    );
  };

  const renderPayslip = ({ item }: { item: Payslip }) => (
    <Card 
      style={styles.card} 
      mode="outlined"
      onPress={() => navigation.navigate('PayslipDetail', { payslipId: item.id })}
    >
      <Card.Content>
        <View style={styles.cardHeader}>
          <View>
            <Text variant="titleSmall" style={styles.periodTitle}>
              {item.payrollPeriod?.name}
            </Text>
            {item.paymentDate && (
              <Text variant="bodySmall" style={styles.paymentDate}>
                Pagado: {formatDate(item.paymentDate)}
              </Text>
            )}
          </View>
          <Chip 
            compact 
            style={[styles.chip, { backgroundColor: getStatusColor(item.paymentStatus) }]}
            textStyle={styles.chipText}
          >
            {getStatusLabel(item.paymentStatus)}
          </Chip>
        </View>
        
        <Divider style={styles.divider} />
        
        <View style={styles.amounts}>
          <View style={styles.amountItem}>
            <Text variant="bodySmall">Bruto</Text>
            <Text variant="bodyMedium">{formatCurrency(item.grossSalary)}</Text>
          </View>
          <View style={styles.amountItem}>
            <Text variant="bodySmall">Deducciones</Text>
            <Text variant="bodyMedium" style={styles.deduction}>
              -{formatCurrency(item.totalDeductions)}
            </Text>
          </View>
          <View style={styles.amountItem}>
            <Text variant="bodySmall">Neto</Text>
            <Text variant="titleMedium" style={styles.net}>
              {formatCurrency(item.netSalary)}
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
        <Appbar.Content title="Mis Recibos de Pago" />
      </Appbar.Header>

      {loading && !refreshing ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" />
        </View>
      ) : (
        <FlatList
          data={payslips}
          renderItem={renderPayslip}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          ListHeaderComponent={renderSummary}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text variant="bodyLarge">No hay recibos de pago</Text>
            </View>
          }
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  list: {
    padding: 16,
  },
  summaryCard: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    backgroundColor: '#fff',
  },
  summaryTitle: {
    fontWeight: 'bold',
    textAlign: 'center',
  },
  periodName: {
    textAlign: 'center',
    color: '#666',
    marginBottom: 16,
  },
  summaryContent: {
    marginBottom: 12,
  },
  summaryItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  grossAmount: {
    color: '#333',
  },
  deductionAmount: {
    color: '#F44336',
  },
  summaryDivider: {
    marginVertical: 8,
  },
  netAmount: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  statusChip: {
    alignSelf: 'center',
  },
  chipText: {
    fontSize: 11,
    color: '#fff',
  },
  card: {
    marginVertical: 4,
    backgroundColor: '#fff',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  periodTitle: {
    fontWeight: 'bold',
  },
  paymentDate: {
    color: '#666',
  },
  chip: {
    height: 22,
  },
  divider: {
    marginVertical: 12,
  },
  amounts: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  amountItem: {
    alignItems: 'center',
  },
  deduction: {
    color: '#F44336',
  },
  net: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 50,
  },
});

export default PayrollScreen;
