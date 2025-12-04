import React from 'react';
import { View, StyleSheet, ScrollView, Dimensions } from 'react-native';
import { Text, Card, useTheme, IconButton, Avatar, FAB, Divider, Chip } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';

const { width } = Dimensions.get('window');
const cardWidth = (width - 48) / 2;

const HRHomeScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation();

  const statsData = [
    { label: 'Empleados', value: '48', icon: 'account-group', color: '#2196f3' },
    { label: 'Departamentos', value: '6', icon: 'office-building', color: '#9c27b0' },
    { label: 'Vacaciones', value: '5', icon: 'beach', color: '#ff9800' },
    { label: 'Ausencias', value: '2', icon: 'account-off', color: '#f44336' },
  ];

  const recentEmployees = [
    { id: '1', name: 'María García', position: 'Desarrolladora Senior', department: 'IT', status: 'active' },
    { id: '2', name: 'Carlos López', position: 'Contador', department: 'Finanzas', status: 'active' },
    { id: '3', name: 'Ana Martínez', position: 'Vendedora', department: 'Ventas', status: 'vacation' },
    { id: '4', name: 'Luis Rodríguez', position: 'Gerente de Compras', department: 'Compras', status: 'active' },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return '#4caf50';
      case 'vacation':
        return '#ff9800';
      case 'absent':
        return '#f44336';
      default:
        return '#9e9e9e';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active':
        return 'Activo';
      case 'vacation':
        return 'Vacaciones';
      case 'absent':
        return 'Ausente';
      default:
        return status;
    }
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={styles.header}>
        <IconButton icon="arrow-left" onPress={() => navigation.goBack()} />
        <Text variant="titleLarge" style={{ flex: 1, fontWeight: 'bold' }}>Recursos Humanos</Text>
        <IconButton icon="account-plus" onPress={() => {}} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.statsGrid}>
          {statsData.map((stat, index) => (
            <Card key={index} style={[styles.statCard, { width: cardWidth }]}>
              <Card.Content style={styles.statContent}>
                <IconButton
                  icon={stat.icon}
                  iconColor={stat.color}
                  size={24}
                  style={{ backgroundColor: `${stat.color}20`, margin: 0 }}
                />
                <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                  {stat.label}
                </Text>
                <Text variant="titleMedium" style={{ fontWeight: 'bold' }}>
                  {stat.value}
                </Text>
              </Card.Content>
            </Card>
          ))}
        </View>

        <Card style={styles.card}>
          <Card.Content>
            <View style={styles.sectionHeader}>
              <Text variant="titleMedium" style={{ fontWeight: '600' }}>
                Empleados Recientes
              </Text>
              <Text variant="bodySmall" style={{ color: theme.colors.primary }}>
                Ver todos
              </Text>
            </View>
          </Card.Content>
          {recentEmployees.map((employee, index) => (
            <React.Fragment key={employee.id}>
              {index > 0 && <Divider />}
              <View style={styles.employeeItem}>
                <Avatar.Text
                  size={40}
                  label={employee.name.split(' ').map(n => n[0]).join('')}
                  style={{ backgroundColor: theme.colors.primary }}
                />
                <View style={{ flex: 1 }}>
                  <Text variant="bodyMedium" style={{ fontWeight: '600' }}>
                    {employee.name}
                  </Text>
                  <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                    {employee.position}
                  </Text>
                </View>
                <Chip
                  compact
                  textStyle={{ fontSize: 10 }}
                  style={{ backgroundColor: `${getStatusColor(employee.status)}20` }}
                >
                  {getStatusLabel(employee.status)}
                </Chip>
              </View>
            </React.Fragment>
          ))}
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={{ fontWeight: '600', marginBottom: 16 }}>
              Acciones Rápidas
            </Text>
            <View style={styles.quickActions}>
              <View style={styles.quickAction}>
                <IconButton
                  icon="account-plus"
                  mode="contained"
                  containerColor={`${theme.colors.primary}20`}
                  iconColor={theme.colors.primary}
                  onPress={() => {}}
                />
                <Text variant="bodySmall">Nuevo</Text>
              </View>
              <View style={styles.quickAction}>
                <IconButton
                  icon="calendar-check"
                  mode="contained"
                  containerColor="#4caf5020"
                  iconColor="#4caf50"
                  onPress={() => {}}
                />
                <Text variant="bodySmall">Asistencia</Text>
              </View>
              <View style={styles.quickAction}>
                <IconButton
                  icon="beach"
                  mode="contained"
                  containerColor="#ff980020"
                  iconColor="#ff9800"
                  onPress={() => {}}
                />
                <Text variant="bodySmall">Vacaciones</Text>
              </View>
              <View style={styles.quickAction}>
                <IconButton
                  icon="file-document"
                  mode="contained"
                  containerColor="#9c27b020"
                  iconColor="#9c27b0"
                  onPress={() => {}}
                />
                <Text variant="bodySmall">Nómina</Text>
              </View>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={{ fontWeight: '600', marginBottom: 16 }}>
              Departamentos
            </Text>
          </Card.Content>
          {['IT', 'Finanzas', 'Ventas', 'Compras', 'Producción', 'Administración'].map((dept, index) => (
            <React.Fragment key={dept}>
              {index > 0 && <Divider />}
              <View style={styles.departmentItem}>
                <View>
                  <Text variant="bodyMedium" style={{ fontWeight: '500' }}>{dept}</Text>
                  <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                    {Math.floor(Math.random() * 15) + 5} empleados
                  </Text>
                </View>
                <IconButton icon="chevron-right" onPress={() => {}} />
              </View>
            </React.Fragment>
          ))}
        </Card>
      </ScrollView>

      <FAB
        icon="plus"
        style={[styles.fab, { backgroundColor: theme.colors.primary }]}
        onPress={() => {}}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { flexDirection: 'row', alignItems: 'center', paddingRight: 8 },
  content: { padding: 16, gap: 16, paddingBottom: 80 },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 16 },
  statCard: {},
  statContent: { alignItems: 'center', gap: 4 },
  card: {},
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  employeeItem: { flexDirection: 'row', alignItems: 'center', padding: 16, gap: 12 },
  quickActions: { flexDirection: 'row', justifyContent: 'space-around' },
  quickAction: { alignItems: 'center', gap: 4 },
  departmentItem: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 8 },
  fab: { position: 'absolute', margin: 16, right: 0, bottom: 0 },
});

export default HRHomeScreen;
