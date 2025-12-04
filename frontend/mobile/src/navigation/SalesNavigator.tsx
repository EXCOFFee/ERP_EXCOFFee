import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { SalesStackParamList } from './types';

// Screens
import SalesHomeScreen from '../screens/sales/SalesHomeScreen';
import CustomerListScreen from '../screens/sales/CustomerListScreen';
import CustomerDetailScreen from '../screens/sales/CustomerDetailScreen';
import OrderListScreen from '../screens/sales/OrderListScreen';
import OrderDetailScreen from '../screens/sales/OrderDetailScreen';

const Stack = createNativeStackNavigator<SalesStackParamList>();

const SalesNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="SalesHome" component={SalesHomeScreen} />
      <Stack.Screen name="CustomerList" component={CustomerListScreen} />
      <Stack.Screen name="CustomerDetail" component={CustomerDetailScreen} />
      <Stack.Screen name="OrderList" component={OrderListScreen} />
      <Stack.Screen name="OrderDetail" component={OrderDetailScreen} />
    </Stack.Navigator>
  );
};

export default SalesNavigator;
