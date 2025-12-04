// ========================================================
// SISTEMA ERP UNIVERSAL - Componente ProtectedRoute
// ========================================================

import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAppSelector } from '@hooks/redux';
import LoadingScreen from '@components/common/LoadingScreen';

function ProtectedRoute() {
  const location = useLocation();
  const { isAuthenticated, isLoading } = useAppSelector((state) => state.auth);

  if (isLoading) {
    return <LoadingScreen message="Verificando sesión..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
}

export default ProtectedRoute;
