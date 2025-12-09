import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { MoreStackParamList } from './types';

// Screens
import MoreHomeScreen from '../screens/more/MoreHomeScreen';
import ProfileScreen from '../screens/more/ProfileScreen';
import SettingsScreen from '../screens/more/SettingsScreen';

// Finance Screens
import {
  AccountListScreen,
  AccountFormScreen,
  JournalEntryListScreen,
  FinancialReportsScreen,
} from '../screens/finance';

// HR Screens
import {
  EmployeeListScreen,
  EmployeeFormScreen,
  DepartmentListScreen,
  AttendanceScreen,
  PayrollScreen,
} from '../screens/hr';

const Stack = createNativeStackNavigator<MoreStackParamList>();

const MoreNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="MoreHome" component={MoreHomeScreen} />
      <Stack.Screen name="Profile" component={ProfileScreen} />
      <Stack.Screen name="Settings" component={SettingsScreen} />
      
      {/* Finance Screens */}
      <Stack.Screen name="Finance" component={AccountListScreen} />
      <Stack.Screen name="AccountForm" component={AccountFormScreen} />
      <Stack.Screen name="JournalEntryList" component={JournalEntryListScreen} />
      <Stack.Screen name="FinancialReports" component={FinancialReportsScreen} />
      
      {/* HR Screens */}
      <Stack.Screen name="HR" component={EmployeeListScreen} />
      <Stack.Screen name="EmployeeForm" component={EmployeeFormScreen} />
      <Stack.Screen name="DepartmentList" component={DepartmentListScreen} />
      <Stack.Screen name="Attendance" component={AttendanceScreen} />
      <Stack.Screen name="Payroll" component={PayrollScreen} />
    </Stack.Navigator>
  );
};

export default MoreNavigator;
