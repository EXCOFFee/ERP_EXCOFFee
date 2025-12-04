import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { InventoryStackParamList } from './types';

// Screens
import InventoryHomeScreen from '../screens/inventory/InventoryHomeScreen';
import ProductListScreen from '../screens/inventory/ProductListScreen';
import ProductDetailScreen from '../screens/inventory/ProductDetailScreen';
import ProductFormScreen from '../screens/inventory/ProductFormScreen';
import BarcodeScannerScreen from '../screens/inventory/BarcodeScannerScreen';

const Stack = createNativeStackNavigator<InventoryStackParamList>();

const InventoryNavigator: React.FC = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="InventoryHome" component={InventoryHomeScreen} />
      <Stack.Screen name="ProductList" component={ProductListScreen} />
      <Stack.Screen name="ProductDetail" component={ProductDetailScreen} />
      <Stack.Screen name="ProductForm" component={ProductFormScreen} />
      <Stack.Screen name="BarcodeScanner" component={BarcodeScannerScreen} />
    </Stack.Navigator>
  );
};

export default InventoryNavigator;
