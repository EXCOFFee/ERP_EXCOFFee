import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { PurchasingStackParamList } from './types';

// Screens
import PurchasingHomeScreen from '../screens/purchasing/PurchasingHomeScreen';
import SupplierListScreen from '../screens/purchasing/SupplierListScreen';
import SupplierDetailScreen from '../screens/purchasing/SupplierDetailScreen';
import PurchaseOrderListScreen from '../screens/purchasing/PurchaseOrderListScreen';
import PurchaseOrderDetailScreen from '../screens/purchasing/PurchaseOrderDetailScreen';

const Stack = createNativeStackNavigator<PurchasingStackParamList>();

const PurchasingNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="PurchasingHome" component={PurchasingHomeScreen} />
      <Stack.Screen name="SupplierList" component={SupplierListScreen} />
      <Stack.Screen name="SupplierDetail" component={SupplierDetailScreen} />
      <Stack.Screen name="PurchaseOrderList" component={PurchaseOrderListScreen} />
      <Stack.Screen name="PurchaseOrderDetail" component={PurchaseOrderDetailScreen} />
    </Stack.Navigator>
  );
};

export default PurchasingNavigator;
