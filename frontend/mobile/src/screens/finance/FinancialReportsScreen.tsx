// ========================================================
// Finance Module - Financial Reports Screen
// ========================================================

import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { 
  Appbar, 
  Card, 
  Text, 
  ActivityIndicator,
  Divider,
  SegmentedButtons
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '../../hooks/useStore';
import { fetchCurrentPeriod, selectCurrentPeriod } from '../../store/slices/financeSlice';
import financeService from '../../services/finance.service';

type ReportType = 'balance' | 'income' | 'trial';

const FinancialReportsScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const dispatch = useAppDispatch();
  
  const currentPeriod = useAppSelector(selectCurrentPeriod);
  
  const [reportType, setReportType] = useState<ReportType>('balance');
  const [loading, setLoading] = useState(false);
  const [reportData, setReportData] = useState<any>(null);

  useEffect(() => {
    dispatch(fetchCurrentPeriod());
  }, []);

  useEffect(() => {
    loadReport();
  }, [reportType, currentPeriod]);

  const loadReport = async () => {
    if (!currentPeriod) return;
    
    setLoading(true);
    try {
      let data;
      switch (reportType) {
        case 'balance':
          data = await financeService.getBalanceSheet(currentPeriod.id);
          break;
        case 'income':
          data = await financeService.getIncomeStatement(currentPeriod.id);
          break;
        case 'trial':
          data = await financeService.getTrialBalance(currentPeriod.id);
          break;
      }
      setReportData(data);
    } catch (error) {
      console.error('Error loading report:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const renderBalanceSheet = () => (
    <View>
      <Card style={styles.sectionCard}>
        <Card.Title title="ACTIVOS" />
        <Card.Content>
          {reportData?.assets?.map((item: any, index: number) => (
            <View key={index} style={styles.reportRow}>
              <Text style={[styles.accountName, { paddingLeft: item.level * 16 }]}>
                {item.name}
              </Text>
              <Text style={styles.amount}>{formatCurrency(item.balance)}</Text>
            </View>
          ))}
          <Divider style={styles.divider} />
          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>Total Activos</Text>
            <Text style={styles.totalAmount}>{formatCurrency(reportData?.totalAssets || 0)}</Text>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.sectionCard}>
        <Card.Title title="PASIVOS" />
        <Card.Content>
          {reportData?.liabilities?.map((item: any, index: number) => (
            <View key={index} style={styles.reportRow}>
              <Text style={[styles.accountName, { paddingLeft: item.level * 16 }]}>
                {item.name}
              </Text>
              <Text style={styles.amount}>{formatCurrency(item.balance)}</Text>
            </View>
          ))}
          <Divider style={styles.divider} />
          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>Total Pasivos</Text>
            <Text style={styles.totalAmount}>{formatCurrency(reportData?.totalLiabilities || 0)}</Text>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.sectionCard}>
        <Card.Title title="PATRIMONIO" />
        <Card.Content>
          {reportData?.equity?.map((item: any, index: number) => (
            <View key={index} style={styles.reportRow}>
              <Text style={[styles.accountName, { paddingLeft: item.level * 16 }]}>
                {item.name}
              </Text>
              <Text style={styles.amount}>{formatCurrency(item.balance)}</Text>
            </View>
          ))}
          <Divider style={styles.divider} />
          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>Total Patrimonio</Text>
            <Text style={styles.totalAmount}>{formatCurrency(reportData?.totalEquity || 0)}</Text>
          </View>
        </Card.Content>
      </Card>
    </View>
  );

  const renderIncomeStatement = () => (
    <View>
      <Card style={styles.sectionCard}>
        <Card.Title title="INGRESOS" />
        <Card.Content>
          {reportData?.income?.map((item: any, index: number) => (
            <View key={index} style={styles.reportRow}>
              <Text style={styles.accountName}>{item.name}</Text>
              <Text style={[styles.amount, styles.income]}>{formatCurrency(item.balance)}</Text>
            </View>
          ))}
          <Divider style={styles.divider} />
          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>Total Ingresos</Text>
            <Text style={[styles.totalAmount, styles.income]}>{formatCurrency(reportData?.totalIncome || 0)}</Text>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.sectionCard}>
        <Card.Title title="GASTOS" />
        <Card.Content>
          {reportData?.expenses?.map((item: any, index: number) => (
            <View key={index} style={styles.reportRow}>
              <Text style={styles.accountName}>{item.name}</Text>
              <Text style={[styles.amount, styles.expense]}>{formatCurrency(item.balance)}</Text>
            </View>
          ))}
          <Divider style={styles.divider} />
          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>Total Gastos</Text>
            <Text style={[styles.totalAmount, styles.expense]}>{formatCurrency(reportData?.totalExpenses || 0)}</Text>
          </View>
        </Card.Content>
      </Card>

      <Card style={[styles.sectionCard, styles.resultCard]}>
        <Card.Content>
          <View style={styles.totalRow}>
            <Text style={styles.resultLabel}>RESULTADO NETO</Text>
            <Text style={[
              styles.resultAmount, 
              (reportData?.netIncome || 0) >= 0 ? styles.income : styles.expense
            ]}>
              {formatCurrency(reportData?.netIncome || 0)}
            </Text>
          </View>
        </Card.Content>
      </Card>
    </View>
  );

  const renderTrialBalance = () => (
    <Card style={styles.sectionCard}>
      <Card.Title title="BALANCE DE COMPROBACIÓN" />
      <Card.Content>
        <View style={styles.trialHeader}>
          <Text style={styles.trialHeaderText}>Cuenta</Text>
          <Text style={styles.trialHeaderText}>Débito</Text>
          <Text style={styles.trialHeaderText}>Crédito</Text>
        </View>
        <Divider />
        {reportData?.accounts?.map((item: any, index: number) => (
          <View key={index} style={styles.trialRow}>
            <Text style={styles.trialAccount} numberOfLines={1}>{item.name}</Text>
            <Text style={styles.trialDebit}>{formatCurrency(item.debit)}</Text>
            <Text style={styles.trialCredit}>{formatCurrency(item.credit)}</Text>
          </View>
        ))}
        <Divider style={styles.divider} />
        <View style={styles.trialRow}>
          <Text style={[styles.trialAccount, styles.totalLabel]}>TOTALES</Text>
          <Text style={[styles.trialDebit, styles.totalAmount]}>{formatCurrency(reportData?.totalDebit || 0)}</Text>
          <Text style={[styles.trialCredit, styles.totalAmount]}>{formatCurrency(reportData?.totalCredit || 0)}</Text>
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title="Reportes Financieros" />
        <Appbar.Action icon="refresh" onPress={loadReport} />
      </Appbar.Header>

      <View style={styles.segmentContainer}>
        <SegmentedButtons
          value={reportType}
          onValueChange={(value) => setReportType(value as ReportType)}
          buttons={[
            { value: 'balance', label: 'Balance' },
            { value: 'income', label: 'Resultados' },
            { value: 'trial', label: 'Comprobación' },
          ]}
        />
      </View>

      {currentPeriod && (
        <View style={styles.periodInfo}>
          <Text variant="bodySmall">
            Período: {currentPeriod.name}
          </Text>
        </View>
      )}

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" />
        </View>
      ) : (
        <ScrollView style={styles.content} contentContainerStyle={styles.scrollContent}>
          {reportType === 'balance' && renderBalanceSheet()}
          {reportType === 'income' && renderIncomeStatement()}
          {reportType === 'trial' && renderTrialBalance()}
        </ScrollView>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  segmentContainer: {
    padding: 16,
    backgroundColor: '#fff',
  },
  periodInfo: {
    paddingHorizontal: 16,
    paddingBottom: 8,
    backgroundColor: '#fff',
  },
  content: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 32,
  },
  sectionCard: {
    marginBottom: 16,
    backgroundColor: '#fff',
  },
  reportRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
  },
  accountName: {
    flex: 1,
  },
  amount: {
    fontWeight: '500',
  },
  income: {
    color: '#4CAF50',
  },
  expense: {
    color: '#F44336',
  },
  divider: {
    marginVertical: 8,
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
  },
  totalLabel: {
    fontWeight: 'bold',
  },
  totalAmount: {
    fontWeight: 'bold',
  },
  resultCard: {
    backgroundColor: '#e3f2fd',
  },
  resultLabel: {
    fontWeight: 'bold',
    fontSize: 16,
  },
  resultAmount: {
    fontWeight: 'bold',
    fontSize: 18,
  },
  trialHeader: {
    flexDirection: 'row',
    paddingVertical: 8,
  },
  trialHeaderText: {
    flex: 1,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  trialRow: {
    flexDirection: 'row',
    paddingVertical: 6,
  },
  trialAccount: {
    flex: 2,
  },
  trialDebit: {
    flex: 1,
    textAlign: 'right',
    color: '#4CAF50',
  },
  trialCredit: {
    flex: 1,
    textAlign: 'right',
    color: '#F44336',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default FinancialReportsScreen;
