import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, useTheme, IconButton, Avatar, Button, Divider, List } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { useAppSelector } from '../../hooks/useStore';

const ProfileScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation();
  const { user } = useAppSelector((state) => state.auth);

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <IconButton icon="arrow-left" onPress={() => navigation.goBack()} />
        <Text variant="titleLarge" style={{ flex: 1, fontWeight: 'bold' }}>Mi Perfil</Text>
        <IconButton icon="pencil" onPress={() => {}} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.avatarSection}>
          <Avatar.Text
            size={100}
            label={user?.fullName?.split(' ').map((n: string) => n[0]).join('').substring(0, 2) || 'U'}
            style={{ backgroundColor: theme.colors.primary }}
          />
          <Text variant="headlineSmall" style={{ fontWeight: 'bold', marginTop: 16 }}>
            {user?.fullName || 'Usuario'}
          </Text>
          <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
            {user?.email || 'usuario@email.com'}
          </Text>
        </View>

        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={{ fontWeight: '600', marginBottom: 16 }}>
              Información Personal
            </Text>
            <View style={styles.infoRow}>
              <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                Nombre completo
              </Text>
              <Text variant="bodyMedium">{user?.fullName || 'N/A'}</Text>
            </View>
            <Divider style={{ marginVertical: 12 }} />
            <View style={styles.infoRow}>
              <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                Correo electrónico
              </Text>
              <Text variant="bodyMedium">{user?.email || 'N/A'}</Text>
            </View>
            <Divider style={{ marginVertical: 12 }} />
            <View style={styles.infoRow}>
              <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                Usuario
              </Text>
              <Text variant="bodyMedium">{user?.username || 'N/A'}</Text>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <List.Item
            title="Cambiar contraseña"
            left={(props: any) => <List.Icon {...props} icon="lock" />}
            right={(props: any) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {}}
          />
          <Divider />
          <List.Item
            title="Verificación en dos pasos"
            description="No configurado"
            left={(props: any) => <List.Icon {...props} icon="shield-check" />}
            right={(props: any) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {}}
          />
        </Card>

        <Button mode="outlined" style={styles.deleteButton} textColor="#f44336">
          Eliminar cuenta
        </Button>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', paddingRight: 8 },
  content: { padding: 16, gap: 16 },
  avatarSection: { alignItems: 'center', marginVertical: 16 },
  card: {},
  infoRow: { gap: 4 },
  deleteButton: { marginTop: 16, borderColor: '#f44336' },
});

export default ProfileScreen;
