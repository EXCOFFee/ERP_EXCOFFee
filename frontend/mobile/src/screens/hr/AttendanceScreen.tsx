// ========================================================
// HR Module - Attendance Screen
// ========================================================

import React, { useEffect, useState, useCallback } from 'react';
import { View, StyleSheet, FlatList, RefreshControl } from 'react-native';
import { 
  Appbar, 
  Card, 
  Text, 
  Button,
  Chip,
  useTheme,
  ActivityIndicator,
  Surface,
  Divider
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '../../hooks/useStore';
import { 
  fetchAttendance, 
  fetchTodayAttendance,
  checkIn,
  checkOut,
  selectAttendanceRecords, 
  selectTodayAttendance
} from '../../store/slices/hrSlice';
import { Attendance } from '../../services/hr.service';

const AttendanceScreen: React.FC = () => {
  const theme = useTheme();
  const navigation = useNavigation<any>();
  const dispatch = useAppDispatch();
  
  const attendanceRecords = useAppSelector(selectAttendanceRecords);
  const todayAttendance = useAppSelector(selectTodayAttendance);
  
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = useCallback(async () => {
    setLoading(true);
    await Promise.all([
      dispatch(fetchTodayAttendance()),
      dispatch(fetchAttendance({}))
    ]);
    setLoading(false);
  }, [dispatch]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  }, [loadData]);

  const handleCheckIn = async () => {
    setActionLoading(true);
    try {
      await dispatch(checkIn());
    } finally {
      setActionLoading(false);
    }
  };

  const handleCheckOut = async () => {
    setActionLoading(true);
    try {
      await dispatch(checkOut());
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'present': return '#4CAF50';
      case 'absent': return '#F44336';
      case 'late': return '#FF9800';
      case 'half_day': return '#FF9800';
      case 'holiday': return '#2196F3';
      case 'leave': return '#9C27B0';
      default: return '#9E9E9E';
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      'present': 'Presente',
      'absent': 'Ausente',
      'late': 'Tardanza',
      'half_day': 'Medio Día',
      'holiday': 'Feriado',
      'leave': 'Permiso',
    };
    return labels[status] || status;
  };

  const formatTime = (time?: string) => {
    if (!time) return '--:--';
    return new Date(`2000-01-01T${time}`).toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    });
  };

  const renderTodayCard = () => (
    <Surface style={styles.todayCard} elevation={2}>
      <Text variant="titleMedium" style={styles.todayTitle}>Asistencia de Hoy</Text>
      
      <View style={styles.todayContent}>
        <View style={styles.timeBox}>
          <Text variant="labelSmall">Entrada</Text>
          <Text variant="headlineMedium" style={styles.timeText}>
            {formatTime(todayAttendance?.checkIn)}
          </Text>
        </View>
        
        <Divider style={styles.verticalDivider} />
        
        <View style={styles.timeBox}>
          <Text variant="labelSmall">Salida</Text>
          <Text variant="headlineMedium" style={styles.timeText}>
            {formatTime(todayAttendance?.checkOut)}
          </Text>
        </View>
      </View>
      
      {todayAttendance?.hoursWorked !== undefined && (
        <Text variant="bodySmall" style={styles.hoursWorked}>
          Horas trabajadas: {todayAttendance.hoursWorked.toFixed(2)}h
        </Text>
      )}
      
      <View style={styles.buttonRow}>
        <Button
          mode="contained"
          onPress={handleCheckIn}
          disabled={!!todayAttendance?.checkIn || actionLoading}
          loading={actionLoading}
          style={styles.actionButton}
          icon="login"
        >
          Marcar Entrada
        </Button>
        
        <Button
          mode="contained"
          onPress={handleCheckOut}
          disabled={!todayAttendance?.checkIn || !!todayAttendance?.checkOut || actionLoading}
          loading={actionLoading}
          style={styles.actionButton}
          icon="logout"
          buttonColor={theme.colors.error}
        >
          Marcar Salida
        </Button>
      </View>
    </Surface>
  );

  const renderAttendance = ({ item }: { item: Attendance }) => (
    <Card style={styles.card} mode="outlined">
      <Card.Content style={styles.cardContent}>
        <View style={styles.dateColumn}>
          <Text variant="bodyMedium" style={styles.date}>
            {formatDate(item.date)}
          </Text>
          <Chip 
            compact 
            style={[styles.chip, { backgroundColor: getStatusColor(item.status) }]}
            textStyle={styles.chipText}
          >
            {getStatusLabel(item.status)}
          </Chip>
        </View>
        
        <View style={styles.timesColumn}>
          <Text variant="bodySmall">
            Entrada: {formatTime(item.checkIn)}
          </Text>
          <Text variant="bodySmall">
            Salida: {formatTime(item.checkOut)}
          </Text>
        </View>
        
        <View style={styles.hoursColumn}>
          <Text variant="titleSmall" style={styles.hours}>
            {item.hoursWorked.toFixed(1)}h
          </Text>
          {item.overtimeHours > 0 && (
            <Text variant="bodySmall" style={styles.overtime}>
              +{item.overtimeHours.toFixed(1)}h extra
            </Text>
          )}
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title="Asistencia" />
      </Appbar.Header>

      {loading && !refreshing ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" />
        </View>
      ) : (
        <FlatList
          data={attendanceRecords}
          renderItem={renderAttendance}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          ListHeaderComponent={renderTodayCard}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text variant="bodyLarge">No hay registros de asistencia</Text>
            </View>
          }
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  list: {
    padding: 16,
  },
  todayCard: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    backgroundColor: '#fff',
  },
  todayTitle: {
    fontWeight: 'bold',
    marginBottom: 16,
    textAlign: 'center',
  },
  todayContent: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  timeBox: {
    alignItems: 'center',
    flex: 1,
  },
  timeText: {
    fontWeight: 'bold',
  },
  verticalDivider: {
    width: 1,
    height: 60,
    marginHorizontal: 16,
  },
  hoursWorked: {
    textAlign: 'center',
    color: '#666',
    marginBottom: 16,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 12,
  },
  actionButton: {
    flex: 1,
  },
  card: {
    marginVertical: 4,
    backgroundColor: '#fff',
  },
  cardContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dateColumn: {
    flex: 2,
  },
  date: {
    fontWeight: '500',
    marginBottom: 4,
  },
  chip: {
    alignSelf: 'flex-start',
    height: 22,
  },
  chipText: {
    fontSize: 10,
    color: '#fff',
  },
  timesColumn: {
    flex: 2,
  },
  hoursColumn: {
    flex: 1,
    alignItems: 'flex-end',
  },
  hours: {
    fontWeight: 'bold',
  },
  overtime: {
    color: '#4CAF50',
    fontSize: 11,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 50,
  },
});

export default AttendanceScreen;
