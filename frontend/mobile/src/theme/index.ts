import {
  MD3LightTheme,
  MD3DarkTheme,
  configureFonts,
  MD3Theme,
} from 'react-native-paper';

// Configuración de fuentes
const fontConfig = {
  fontFamily: 'System',
};

// Colores personalizados
const colors = {
  primary: '#1976d2',
  primaryLight: '#42a5f5',
  primaryDark: '#1565c0',
  secondary: '#9c27b0',
  secondaryLight: '#ba68c8',
  secondaryDark: '#7b1fa2',
  success: '#4caf50',
  warning: '#ff9800',
  error: '#f44336',
  info: '#2196f3',
};

// Tema claro
export const theme: MD3Theme = {
  ...MD3LightTheme,
  roundness: 8,
  colors: {
    ...MD3LightTheme.colors,
    primary: colors.primary,
    primaryContainer: colors.primaryLight,
    secondary: colors.secondary,
    secondaryContainer: colors.secondaryLight,
    tertiary: colors.info,
    error: colors.error,
    errorContainer: '#ffcdd2',
    background: '#ffffff',
    surface: '#ffffff',
    surfaceVariant: '#f5f5f5',
    onPrimary: '#ffffff',
    onPrimaryContainer: colors.primaryDark,
    onSecondary: '#ffffff',
    onSecondaryContainer: colors.secondaryDark,
    onTertiary: '#ffffff',
    onSurface: '#212121',
    onSurfaceVariant: '#757575',
    onError: '#ffffff',
    outline: '#bdbdbd',
    outlineVariant: '#e0e0e0',
    inverseSurface: '#212121',
    inverseOnSurface: '#ffffff',
    inversePrimary: colors.primaryLight,
    elevation: {
      level0: 'transparent',
      level1: '#ffffff',
      level2: '#f5f5f5',
      level3: '#eeeeee',
      level4: '#e0e0e0',
      level5: '#bdbdbd',
    },
    surfaceDisabled: '#e0e0e0',
    onSurfaceDisabled: '#9e9e9e',
    backdrop: 'rgba(0, 0, 0, 0.5)',
  },
  fonts: configureFonts({ config: fontConfig }),
};

// Tema oscuro
export const darkTheme: MD3Theme = {
  ...MD3DarkTheme,
  roundness: 8,
  colors: {
    ...MD3DarkTheme.colors,
    primary: colors.primaryLight,
    primaryContainer: colors.primary,
    secondary: colors.secondaryLight,
    secondaryContainer: colors.secondary,
    tertiary: colors.info,
    error: '#ef5350',
    errorContainer: '#b71c1c',
    background: '#121212',
    surface: '#1e1e1e',
    surfaceVariant: '#2c2c2c',
    onPrimary: '#000000',
    onPrimaryContainer: '#ffffff',
    onSecondary: '#000000',
    onSecondaryContainer: '#ffffff',
    onTertiary: '#000000',
    onSurface: '#ffffff',
    onSurfaceVariant: '#b0b0b0',
    onError: '#ffffff',
    outline: '#616161',
    outlineVariant: '#424242',
    inverseSurface: '#ffffff',
    inverseOnSurface: '#212121',
    inversePrimary: colors.primary,
    elevation: {
      level0: 'transparent',
      level1: '#1e1e1e',
      level2: '#232323',
      level3: '#282828',
      level4: '#2c2c2c',
      level5: '#333333',
    },
    surfaceDisabled: '#424242',
    onSurfaceDisabled: '#757575',
    backdrop: 'rgba(0, 0, 0, 0.7)',
  },
  fonts: configureFonts({ config: fontConfig }),
};

// Colores adicionales para usar en componentes
export const customColors = {
  ...colors,
  lightGray: '#f5f5f5',
  gray: '#9e9e9e',
  darkGray: '#616161',
  white: '#ffffff',
  black: '#000000',
  transparent: 'transparent',
};

// Espaciado
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

// Tamaños de fuente
export const fontSize = {
  xs: 10,
  sm: 12,
  md: 14,
  lg: 16,
  xl: 20,
  xxl: 24,
  xxxl: 32,
};

// Bordes
export const borderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999,
};

export default theme;
