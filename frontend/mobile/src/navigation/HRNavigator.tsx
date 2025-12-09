// ========================================================
// HR Module Navigator
// ========================================================

import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import {
  EmployeeListScreen,
  EmployeeFormScreen,
  DepartmentListScreen,
  AttendanceScreen,
  PayrollScreen,
} from '../screens/hr';

export type HRStackParamList = {
  HRHome: undefined;
  EmployeeList: undefined;
  EmployeeDetail: { employeeId: string };
  EmployeeForm: { employeeId?: string };
  DepartmentList: undefined;
  DepartmentDetail: { departmentId: string };
  DepartmentForm: { departmentId?: string };
  Attendance: undefined;
  Payroll: undefined;
  PayslipDetail: { payslipId: string };
};

const Stack = createNativeStackNavigator<HRStackParamList>();

const HRNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="EmployeeList" component={EmployeeListScreen} />
      <Stack.Screen name="EmployeeForm" component={EmployeeFormScreen} />
      <Stack.Screen name="DepartmentList" component={DepartmentListScreen} />
      <Stack.Screen name="Attendance" component={AttendanceScreen} />
      <Stack.Screen name="Payroll" component={PayrollScreen} />
    </Stack.Navigator>
  );
};

export default HRNavigator;
