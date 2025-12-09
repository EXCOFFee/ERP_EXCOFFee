// ========================================================
// HR Module - Employee Form Screen
// ========================================================

import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { 
  Appbar, 
  TextInput, 
  Button, 
  HelperText,
  Menu
} from 'react-native-paper';
import { useNavigation, useRoute } from '@react-navigation/native';
import { useAppDispatch, useAppSelector } from '../../hooks/useStore';
import { 
  createEmployee, 
  updateEmployee, 
  fetchEmployee,
  fetchDepartments,
  fetchPositions,
  selectSelectedEmployee,
  selectDepartments,
  selectPositions
} from '../../store/slices/hrSlice';
import { Employee } from '../../services/hr.service';

const EmployeeFormScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const route = useRoute<any>();
  const dispatch = useAppDispatch();
  
  const employeeId = route.params?.employeeId;
  const isEditing = !!employeeId;
  
  const selectedEmployee = useAppSelector(selectSelectedEmployee);
  const departments = useAppSelector(selectDepartments);
  const positions = useAppSelector(selectPositions);
  
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    mobile: '',
    departmentId: '',
    positionId: '',
    hireDate: '',
    baseSalary: '',
    employmentType: 'full_time',
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [deptMenuVisible, setDeptMenuVisible] = useState(false);
  const [posMenuVisible, setPosMenuVisible] = useState(false);
  const [typeMenuVisible, setTypeMenuVisible] = useState(false);

  const employmentTypes = [
    { id: 'full_time', name: 'Tiempo Completo' },
    { id: 'part_time', name: 'Medio Tiempo' },
    { id: 'contract', name: 'Contrato' },
    { id: 'intern', name: 'Pasante' },
  ];

  useEffect(() => {
    dispatch(fetchDepartments({}));
    dispatch(fetchPositions({}));
    if (isEditing) {
      dispatch(fetchEmployee(employeeId));
    }
  }, [employeeId]);

  useEffect(() => {
    if (isEditing && selectedEmployee) {
      setFormData({
        firstName: selectedEmployee.firstName,
        lastName: selectedEmployee.lastName,
        email: selectedEmployee.email,
        phone: selectedEmployee.phone || '',
        mobile: selectedEmployee.mobile || '',
        departmentId: selectedEmployee.department?.id || '',
        positionId: selectedEmployee.position?.id || '',
        hireDate: selectedEmployee.hireDate,
        baseSalary: String(selectedEmployee.baseSalary),
        employmentType: selectedEmployee.employmentType,
      });
    }
  }, [selectedEmployee, isEditing]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.firstName.trim()) {
      newErrors.firstName = 'El nombre es requerido';
    }
    
    if (!formData.lastName.trim()) {
      newErrors.lastName = 'El apellido es requerido';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'El email es requerido';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }
    
    if (!formData.departmentId) {
      newErrors.departmentId = 'El departamento es requerido';
    }
    
    if (!formData.positionId) {
      newErrors.positionId = 'El puesto es requerido';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;
    
    setLoading(true);
    try {
      const employeeData: Partial<Employee> = {
        firstName: formData.firstName,
        lastName: formData.lastName,
        email: formData.email,
        phone: formData.phone || undefined,
        mobile: formData.mobile || undefined,
        hireDate: formData.hireDate,
        baseSalary: parseFloat(formData.baseSalary) || 0,
        employmentType: formData.employmentType as Employee['employmentType'],
      };
      
      if (isEditing) {
        await dispatch(updateEmployee({ id: employeeId, employee: employeeData }));
      } else {
        await dispatch(createEmployee(employeeData));
      }
      
      navigation.goBack();
    } catch (error) {
      console.error('Error saving employee:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectedDept = departments.find(d => d.id === formData.departmentId);
  const selectedPos = positions.find(p => p.id === formData.positionId);
  const selectedType = employmentTypes.find(t => t.id === formData.employmentType);

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title={isEditing ? 'Editar Empleado' : 'Nuevo Empleado'} />
      </Appbar.Header>

      <ScrollView style={styles.content} contentContainerStyle={styles.scrollContent}>
        <TextInput
          label="Nombre *"
          value={formData.firstName}
          onChangeText={(text) => setFormData({ ...formData, firstName: text })}
          mode="outlined"
          style={styles.input}
          error={!!errors.firstName}
        />
        <HelperText type="error" visible={!!errors.firstName}>
          {errors.firstName}
        </HelperText>

        <TextInput
          label="Apellido *"
          value={formData.lastName}
          onChangeText={(text) => setFormData({ ...formData, lastName: text })}
          mode="outlined"
          style={styles.input}
          error={!!errors.lastName}
        />
        <HelperText type="error" visible={!!errors.lastName}>
          {errors.lastName}
        </HelperText>

        <TextInput
          label="Email *"
          value={formData.email}
          onChangeText={(text) => setFormData({ ...formData, email: text })}
          mode="outlined"
          style={styles.input}
          keyboardType="email-address"
          autoCapitalize="none"
          error={!!errors.email}
        />
        <HelperText type="error" visible={!!errors.email}>
          {errors.email}
        </HelperText>

        <TextInput
          label="Teléfono"
          value={formData.phone}
          onChangeText={(text) => setFormData({ ...formData, phone: text })}
          mode="outlined"
          style={styles.input}
          keyboardType="phone-pad"
        />

        <TextInput
          label="Móvil"
          value={formData.mobile}
          onChangeText={(text) => setFormData({ ...formData, mobile: text })}
          mode="outlined"
          style={styles.input}
          keyboardType="phone-pad"
        />

        <Menu
          visible={deptMenuVisible}
          onDismiss={() => setDeptMenuVisible(false)}
          anchor={
            <TextInput
              label="Departamento *"
              value={selectedDept?.name || ''}
              mode="outlined"
              style={styles.input}
              editable={false}
              right={<TextInput.Icon icon="chevron-down" onPress={() => setDeptMenuVisible(true)} />}
              onPressIn={() => setDeptMenuVisible(true)}
              error={!!errors.departmentId}
            />
          }
        >
          {departments.map((dept) => (
            <Menu.Item
              key={dept.id}
              onPress={() => {
                setFormData({ ...formData, departmentId: dept.id });
                setDeptMenuVisible(false);
              }}
              title={dept.name}
            />
          ))}
        </Menu>
        <HelperText type="error" visible={!!errors.departmentId}>
          {errors.departmentId}
        </HelperText>

        <Menu
          visible={posMenuVisible}
          onDismiss={() => setPosMenuVisible(false)}
          anchor={
            <TextInput
              label="Puesto *"
              value={selectedPos?.name || ''}
              mode="outlined"
              style={styles.input}
              editable={false}
              right={<TextInput.Icon icon="chevron-down" onPress={() => setPosMenuVisible(true)} />}
              onPressIn={() => setPosMenuVisible(true)}
              error={!!errors.positionId}
            />
          }
        >
          {positions.map((pos) => (
            <Menu.Item
              key={pos.id}
              onPress={() => {
                setFormData({ ...formData, positionId: pos.id });
                setPosMenuVisible(false);
              }}
              title={pos.name}
            />
          ))}
        </Menu>
        <HelperText type="error" visible={!!errors.positionId}>
          {errors.positionId}
        </HelperText>

        <Menu
          visible={typeMenuVisible}
          onDismiss={() => setTypeMenuVisible(false)}
          anchor={
            <TextInput
              label="Tipo de Empleo"
              value={selectedType?.name || ''}
              mode="outlined"
              style={styles.input}
              editable={false}
              right={<TextInput.Icon icon="chevron-down" onPress={() => setTypeMenuVisible(true)} />}
              onPressIn={() => setTypeMenuVisible(true)}
            />
          }
        >
          {employmentTypes.map((type) => (
            <Menu.Item
              key={type.id}
              onPress={() => {
                setFormData({ ...formData, employmentType: type.id });
                setTypeMenuVisible(false);
              }}
              title={type.name}
            />
          ))}
        </Menu>

        <TextInput
          label="Fecha de Contratación"
          value={formData.hireDate}
          onChangeText={(text) => setFormData({ ...formData, hireDate: text })}
          mode="outlined"
          style={styles.input}
          placeholder="YYYY-MM-DD"
        />

        <TextInput
          label="Salario Base"
          value={formData.baseSalary}
          onChangeText={(text) => setFormData({ ...formData, baseSalary: text })}
          mode="outlined"
          style={styles.input}
          keyboardType="decimal-pad"
          left={<TextInput.Affix text="$" />}
        />

        <Button
          mode="contained"
          onPress={handleSubmit}
          loading={loading}
          disabled={loading}
          style={styles.button}
        >
          {isEditing ? 'Actualizar' : 'Crear'} Empleado
        </Button>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
  },
  input: {
    marginBottom: 4,
    backgroundColor: '#fff',
  },
  button: {
    marginTop: 24,
    paddingVertical: 8,
  },
});

export default EmployeeFormScreen;
