import React, { useEffect, useState, useCallback } from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Provider as PaperProvider } from 'react-native-paper';
import { Provider as ReduxProvider } from 'react-redux';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import * as SplashScreen from 'expo-splash-screen';
import * as Font from 'expo-font';
import { View, StyleSheet } from 'react-native';

import { store } from './src/store';
import { theme, darkTheme } from './src/theme';
import Navigation from './src/navigation';
import { useAppSelector } from './src/hooks/useStore';
import './src/i18n';

// Mantener splash screen visible mientras cargamos recursos
SplashScreen.preventAutoHideAsync();

const AppContent: React.FC = () => {
  const themeMode = useAppSelector((state) => state.theme.mode);
  const currentTheme = themeMode === 'dark' ? darkTheme : theme;

  return (
    <PaperProvider theme={currentTheme}>
      <StatusBar style={themeMode === 'dark' ? 'light' : 'dark'} />
      <Navigation theme={currentTheme} />
    </PaperProvider>
  );
};

const App: React.FC = () => {
  const [appIsReady, setAppIsReady] = useState(false);

  useEffect(() => {
    async function prepare() {
      try {
        // Cargar fuentes personalizadas si es necesario
        await Font.loadAsync({
          // Puedes agregar fuentes personalizadas aquí
        });
        
        // Simular carga de recursos
        await new Promise(resolve => setTimeout(resolve, 500));
      } catch (e) {
        console.warn(e);
      } finally {
        setAppIsReady(true);
      }
    }

    prepare();
  }, []);

  const onLayoutRootView = useCallback(async () => {
    if (appIsReady) {
      await SplashScreen.hideAsync();
    }
  }, [appIsReady]);

  if (!appIsReady) {
    return null;
  }

  return (
    <GestureHandlerRootView style={styles.container}>
      <View style={styles.container} onLayout={onLayoutRootView}>
        <ReduxProvider store={store}>
          <SafeAreaProvider>
            <AppContent />
          </SafeAreaProvider>
        </ReduxProvider>
      </View>
    </GestureHandlerRootView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});

export default App;
