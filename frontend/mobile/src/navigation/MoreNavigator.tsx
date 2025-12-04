import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { MoreStackParamList } from './types';

// Screens
import MoreHomeScreen from '../screens/more/MoreHomeScreen';
import ProfileScreen from '../screens/more/ProfileScreen';
import SettingsScreen from '../screens/more/SettingsScreen';

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
    </Stack.Navigator>
  );
};

export default MoreNavigator;
