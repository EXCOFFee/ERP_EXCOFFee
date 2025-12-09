// ========================================================
// Finance Module Navigator
// ========================================================

import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import {
  AccountListScreen,
  AccountFormScreen,
  JournalEntryListScreen,
  FinancialReportsScreen,
} from '../screens/finance';

export type FinanceStackParamList = {
  FinanceHome: undefined;
  AccountList: undefined;
  AccountDetail: { accountId: string };
  AccountForm: { accountId?: string };
  JournalEntryList: undefined;
  JournalEntryDetail: { entryId: string };
  JournalEntryForm: { entryId?: string };
  FinancialReports: undefined;
};

const Stack = createNativeStackNavigator<FinanceStackParamList>();

const FinanceNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="AccountList" component={AccountListScreen} />
      <Stack.Screen name="AccountForm" component={AccountFormScreen} />
      <Stack.Screen name="JournalEntryList" component={JournalEntryListScreen} />
      <Stack.Screen name="FinancialReports" component={FinancialReportsScreen} />
    </Stack.Navigator>
  );
};

export default FinanceNavigator;
