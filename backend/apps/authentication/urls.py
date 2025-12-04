# ========================================================
# SISTEMA ERP UNIVERSAL - URLs de Autenticación
# ========================================================
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    LogoutView,
    ProfileView,
    ChangePasswordView,
    UserViewSet,
    RoleViewSet,
    UserSessionsView,
    RevokeAllSessionsView,
)

app_name = 'authentication'

# Router para ViewSets (genera URLs automáticamente)
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')

urlpatterns = [
    # ========================================================
    # AUTENTICACIÓN JWT
    # ========================================================
    # Login - Obtener tokens
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Refresh - Renovar access token
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Logout - Invalidar refresh token
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # ========================================================
    # PERFIL Y CONTRASEÑA
    # ========================================================
    # Perfil del usuario actual
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Cambiar contraseña
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # ========================================================
    # SESIONES
    # ========================================================
    # Listar sesiones activas
    path('sessions/', UserSessionsView.as_view(), name='sessions'),
    
    # Cerrar todas las sesiones
    path('sessions/revoke-all/', RevokeAllSessionsView.as_view(), name='revoke_all_sessions'),
    
    # ========================================================
    # ViewSets (usuarios y roles)
    # ========================================================
    path('', include(router.urls)),
]
