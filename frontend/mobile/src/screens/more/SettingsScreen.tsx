import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, useTheme, IconButton, List, Switch, Divider, RadioButton, Dialog, Portal, Button } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '../../hooks/useStore';
import { setThemeMode } from '../../store/slices/themeSlice';
import i18n from '../../i18n';

const SettingsScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation();
  const dispatch = useAppDispatch();
  const themeMode = useAppSelector((state) => state.theme.mode);
  
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [biometricEnabled, setBiometricEnabled] = useState(false);
  const [languageDialogVisible, setLanguageDialogVisible] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState(i18n.language || 'es');

  const handleThemeChange = (value: 'light' | 'dark' | 'system') => {
    dispatch(setThemeMode(value));
  };

  const handleLanguageChange = (lang: string) => {
    setSelectedLanguage(lang);
    i18n.changeLanguage(lang);
    setLanguageDialogVisible(false);
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <IconButton icon="arrow-left" onPress={() => navigation.goBack()} />
        <Text variant="titleLarge" style={{ flex: 1, fontWeight: 'bold' }}>Configuración</Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={{ fontWeight: '600', marginBottom: 8 }}>
              Apariencia
            </Text>
          </Card.Content>
          <RadioButton.Group onValueChange={(value) => handleThemeChange(value as any)} value={themeMode}>
            <List.Item
              title="Claro"
              left={() => <RadioButton value="light" />}
              onPress={() => handleThemeChange('light')}
            />
            <List.Item
              title="Oscuro"
              left={() => <RadioButton value="dark" />}
              onPress={() => handleThemeChange('dark')}
            />
            <List.Item
              title="Sistema"
              left={() => <RadioButton value="system" />}
              onPress={() => handleThemeChange('system')}
            />
          </RadioButton.Group>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={{ fontWeight: '600', marginBottom: 8 }}>
              Idioma
            </Text>
          </Card.Content>
          <List.Item
            title="Idioma de la aplicación"
            description={selectedLanguage === 'es' ? 'Español' : 'English'}
            left={(props: any) => <List.Icon {...props} icon="translate" />}
            right={(props: any) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => setLanguageDialogVisible(true)}
          />
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={{ fontWeight: '600', marginBottom: 8 }}>
              Notificaciones
            </Text>
          </Card.Content>
          <List.Item
            title="Notificaciones push"
            description="Recibir notificaciones de la app"
            left={(props: any) => <List.Icon {...props} icon="bell" />}
            right={() => (
              <Switch value={notificationsEnabled} onValueChange={setNotificationsEnabled} />
            )}
          />
          <Divider />
          <List.Item
            title="Sonido"
            description="Reproducir sonido con notificaciones"
            left={(props: any) => <List.Icon {...props} icon="volume-high" />}
            right={() => <Switch value={true} />}
          />
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={{ fontWeight: '600', marginBottom: 8 }}>
              Seguridad
            </Text>
          </Card.Content>
          <List.Item
            title="Autenticación biométrica"
            description="Usar huella o Face ID"
            left={(props: any) => <List.Icon {...props} icon="fingerprint" />}
            right={() => (
              <Switch value={biometricEnabled} onValueChange={setBiometricEnabled} />
            )}
          />
          <Divider />
          <List.Item
            title="Bloqueo automático"
            description="Bloquear después de 5 minutos"
            left={(props: any) => <List.Icon {...props} icon="lock-clock" />}
            right={(props: any) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {}}
          />
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={{ fontWeight: '600', marginBottom: 8 }}>
              Datos y almacenamiento
            </Text>
          </Card.Content>
          <List.Item
            title="Limpiar caché"
            description="25.4 MB"
            left={(props: any) => <List.Icon {...props} icon="broom" />}
            onPress={() => {}}
          />
          <Divider />
          <List.Item
            title="Descargar datos offline"
            left={(props: any) => <List.Icon {...props} icon="cloud-download" />}
            right={(props: any) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {}}
          />
        </Card>
      </ScrollView>

      <Portal>
        <Dialog visible={languageDialogVisible} onDismiss={() => setLanguageDialogVisible(false)}>
          <Dialog.Title>Seleccionar idioma</Dialog.Title>
          <Dialog.Content>
            <RadioButton.Group onValueChange={handleLanguageChange} value={selectedLanguage}>
              <RadioButton.Item label="Español" value="es" />
              <RadioButton.Item label="English" value="en" />
            </RadioButton.Group>
          </Dialog.Content>
          <Dialog.Actions>
            <Button onPress={() => setLanguageDialogVisible(false)}>Cancelar</Button>
          </Dialog.Actions>
        </Dialog>
      </Portal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', paddingRight: 8 },
  content: { padding: 16, gap: 16 },
  card: {},
});

export default SettingsScreen;
