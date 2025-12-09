import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, useTheme, List, Switch, Divider, Avatar } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import { useAppSelector, useAppDispatch } from '../../hooks/useStore';
import { logout } from '../../store/slices/authSlice';
import { toggleTheme } from '../../store/slices/themeSlice';

const MoreHomeScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation();
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);
  const { mode } = useAppSelector((state) => state.theme);

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <Text variant="headlineMedium" style={{ fontWeight: 'bold' }}>
          Más
        </Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Perfil */}
        <Card style={styles.profileCard} onPress={() => navigation.navigate('Profile' as never)}>
          <Card.Content style={styles.profileContent}>
            <Avatar.Text
              size={56}
              label={user?.fullName?.split(' ').map(n => n[0]).join('').substring(0, 2) || 'U'}
              style={{ backgroundColor: theme.colors.primary }}
            />
            <View style={styles.profileInfo}>
              <Text variant="titleMedium" style={{ fontWeight: '600' }}>
                {user?.fullName || 'Usuario'}
              </Text>
              <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                {user?.email || 'usuario@email.com'}
              </Text>
            </View>
            <MaterialCommunityIcons name="chevron-right" size={24} color={theme.colors.onSurfaceVariant} />
          </Card.Content>
        </Card>

        {/* Módulos */}
        <Text variant="titleMedium" style={styles.sectionTitle}>Módulos</Text>
        <Card style={styles.menuCard}>
          <List.Item
            title="Finanzas"
            description="Contabilidad y reportes"
            left={props => <List.Icon {...props} icon="finance" color={theme.colors.primary} />}
            right={props => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => navigation.navigate('Finance' as never)}
          />
          <Divider />
          <List.Item
            title="Recursos Humanos"
            description="Empleados y nómina"
            left={props => <List.Icon {...props} icon="account-group" color="#9c27b0" />}
            right={props => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => navigation.navigate('HR' as never)}
          />
        </Card>

        {/* Configuración */}
        <Text variant="titleMedium" style={styles.sectionTitle}>Configuración</Text>
        <Card style={styles.menuCard}>
          <List.Item
            title="Modo oscuro"
            description={mode === 'dark' ? 'Activado' : 'Desactivado'}
            left={props => <List.Icon {...props} icon="theme-light-dark" />}
            right={() => (
              <Switch
                value={mode === 'dark'}
                onValueChange={() => { dispatch(toggleTheme()); }}
              />
            )}
          />
          <Divider />
          <List.Item
            title="Idioma"
            description="Español"
            left={props => <List.Icon {...props} icon="translate" />}
            right={props => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {}}
          />
          <Divider />
          <List.Item
            title="Notificaciones"
            description="Configurar alertas"
            left={props => <List.Icon {...props} icon="bell" />}
            right={props => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => navigation.navigate('Settings' as never)}
          />
        </Card>

        {/* Soporte */}
        <Text variant="titleMedium" style={styles.sectionTitle}>Soporte</Text>
        <Card style={styles.menuCard}>
          <List.Item
            title="Ayuda"
            left={props => <List.Icon {...props} icon="help-circle" />}
            right={props => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {}}
          />
          <Divider />
          <List.Item
            title="Acerca de"
            description="Versión 1.0.0"
            left={props => <List.Icon {...props} icon="information" />}
            right={props => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {}}
          />
        </Card>

        {/* Cerrar sesión */}
        <Card style={[styles.menuCard, { marginTop: 8 }]}>
          <List.Item
            title="Cerrar sesión"
            titleStyle={{ color: '#f44336' }}
            left={props => <List.Icon {...props} icon="logout" color="#f44336" />}
            onPress={handleLogout}
          />
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { padding: 16, paddingBottom: 8 },
  content: { padding: 16, paddingTop: 0, paddingBottom: 32 },
  profileCard: { marginBottom: 24 },
  profileContent: { flexDirection: 'row', alignItems: 'center', gap: 16 },
  profileInfo: { flex: 1 },
  sectionTitle: { fontWeight: '600', marginBottom: 8, marginTop: 8 },
  menuCard: { marginBottom: 8 },
});

export default MoreHomeScreen;
