# ========================================================
# SISTEMA ERP UNIVERSAL - Vistas de Autenticación
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Definir endpoints del API de autenticación.
# Implementa el patrón Repository indirectamente a través
# de los serializers y managers de Django.
# ========================================================

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import User, Role, ModulePermission, UserSession
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    RoleSerializer,
    RoleDetailSerializer,
    ModulePermissionSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    UserSessionSerializer,
    ProfileSerializer,
)
from .permissions import HasModulePermission


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Endpoint para obtener tokens JWT (login).
    
    Propósito:
        Autenticar usuarios y emitir tokens de acceso.
    
    Endpoint:
        POST /api/v1/auth/login/
    
    Request Body:
        {
            "email": "usuario@empresa.com",
            "password": "contraseña_segura"
        }
    
    Response:
        {
            "access": "eyJ0eXAiOiJKV1QiLCJh...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJh...",
            "user": {
                "id": "uuid",
                "email": "usuario@empresa.com",
                "full_name": "Juan Pérez",
                "role": "uuid-del-rol",
                "role_code": "sales_manager"
            }
        }
    
    Por qué JWT:
        - Stateless: No requiere almacenar sesiones en servidor
        - Escalable: Funciona con múltiples servidores
        - Móvil-friendly: Fácil de almacenar y enviar
    """
    
    serializer_class = CustomTokenObtainPairSerializer
    
    @extend_schema(
        summary="Iniciar sesión",
        description="Autentica un usuario y retorna tokens JWT",
        tags=['Autenticación']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    """
    Endpoint para cerrar sesión (invalidar refresh token).
    
    Propósito:
        Invalidar el refresh token para que no pueda usarse más.
    
    Endpoint:
        POST /api/v1/auth/logout/
    
    Request Body:
        {
            "refresh": "eyJ0eXAiOiJKV1QiLCJh..."
        }
    
    Por qué invalidar:
        Aunque los access tokens expiran rápidamente (30 min),
        los refresh tokens duran más (7 días). Invalidarlos
        asegura que no puedan usarse para obtener nuevos tokens.
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Cerrar sesión",
        description="Invalida el refresh token actual",
        tags=['Autenticación']
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Se requiere el refresh token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Crear objeto token y agregarlo a la blacklist
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {'message': 'Sesión cerrada exitosamente'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Endpoint para ver y editar el perfil propio.
    
    Propósito:
        Permitir al usuario ver y actualizar su propia información.
    
    Endpoints:
        GET /api/v1/auth/profile/
        PATCH /api/v1/auth/profile/
    
    Por qué separado de UserViewSet:
        - No requiere ID en la URL (usa usuario autenticado)
        - Permisos diferentes (solo puede editar el suyo)
        - Incluye información de permisos
    """
    
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """
        Retorna el usuario autenticado actual.
        
        Returns:
            User: Usuario que hace la petición
        """
        return self.request.user
    
    @extend_schema(
        summary="Obtener perfil",
        description="Retorna el perfil del usuario autenticado",
        tags=['Autenticación']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Actualizar perfil",
        description="Actualiza el perfil del usuario autenticado",
        tags=['Autenticación']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class ChangePasswordView(APIView):
    """
    Endpoint para cambiar la contraseña.
    
    Propósito:
        Permitir al usuario cambiar su contraseña.
    
    Endpoint:
        POST /api/v1/auth/change-password/
    
    Request Body:
        {
            "current_password": "contraseña_actual",
            "new_password": "nueva_contraseña",
            "new_password_confirm": "nueva_contraseña"
        }
    
    Validaciones:
        - Contraseña actual correcta
        - Nueva contraseña cumple requisitos
        - Confirmación coincide
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Cambiar contraseña",
        description="Cambia la contraseña del usuario autenticado",
        tags=['Autenticación']
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.password_changed_at = timezone.now()
            user.save()
            
            return Response(
                {'message': 'Contraseña actualizada exitosamente'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de usuarios (CRUD completo).
    
    Propósito:
        Proporcionar endpoints CRUD para administración de usuarios.
        Solo accesible por administradores.
    
    Endpoints:
        GET    /api/v1/auth/users/           - Listar usuarios
        POST   /api/v1/auth/users/           - Crear usuario
        GET    /api/v1/auth/users/{id}/      - Detalle de usuario
        PATCH  /api/v1/auth/users/{id}/      - Actualizar usuario
        DELETE /api/v1/auth/users/{id}/      - Eliminar usuario (soft delete)
    
    Permisos:
        - Listar/Ver: Permiso 'users:view'
        - Crear: Permiso 'users:create'
        - Actualizar: Permiso 'users:update'
        - Eliminar: Permiso 'users:delete'
    """
    
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, HasModulePermission]
    
    # Configuración para permisos por acción
    module = 'users'
    
    def get_serializer_class(self):
        """
        Retorna el serializer adecuado según la acción.
        
        Returns:
            Serializer class apropiado
        
        Por qué diferentes serializers:
            - create: Incluye campos de contraseña
            - update: No permite cambiar email/contraseña
            - list/retrieve: Solo lectura
        """
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """
        Filtra usuarios según parámetros de búsqueda.
        
        Query params disponibles:
            - search: Buscar por nombre, apellido o email
            - role: Filtrar por ID de rol
            - is_active: Filtrar por estado activo
        
        Returns:
            QuerySet filtrado
        """
        queryset = User.objects.select_related('role').all()
        
        # Búsqueda por texto
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(email__icontains=search)
            )
        
        # Filtro por rol
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role_id=role)
        
        # Filtro por estado
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    def perform_destroy(self, instance):
        """
        Elimina el usuario (soft delete).
        
        Args:
            instance: Usuario a eliminar
        
        Por qué soft delete:
            - Mantiene historial de auditoría
            - Permite recuperar usuarios eliminados
            - Mantiene integridad referencial
        """
        instance.soft_delete(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Restaurar usuario",
        description="Restaura un usuario eliminado",
        tags=['Usuarios']
    )
    def restore(self, request, pk=None):
        """
        Restaura un usuario eliminado.
        
        Endpoint:
            POST /api/v1/auth/users/{id}/restore/
        """
        try:
            user = User.all_objects.get(pk=pk, is_deleted=True)
            user.restore()
            return Response(
                {'message': 'Usuario restaurado exitosamente'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado o no está eliminado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Resetear contraseña",
        description="Resetea la contraseña de un usuario (admin)",
        tags=['Usuarios']
    )
    def reset_password(self, request, pk=None):
        """
        Resetea la contraseña de un usuario (solo admin).
        
        Endpoint:
            POST /api/v1/auth/users/{id}/reset_password/
        
        Request Body:
            {
                "new_password": "nueva_contraseña"
            }
        """
        user = self.get_object()
        new_password = request.data.get('new_password')
        
        if not new_password:
            return Response(
                {'error': 'Se requiere new_password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.password_changed_at = timezone.now()
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save()
        
        return Response(
            {'message': 'Contraseña reseteada exitosamente'},
            status=status.HTTP_200_OK
        )


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de roles.
    
    Propósito:
        CRUD de roles y sus permisos.
        Implementa RU4 - Permisos por rol y módulo.
    
    Endpoints:
        GET    /api/v1/auth/roles/           - Listar roles
        POST   /api/v1/auth/roles/           - Crear rol
        GET    /api/v1/auth/roles/{id}/      - Detalle de rol (con permisos)
        PATCH  /api/v1/auth/roles/{id}/      - Actualizar rol
        DELETE /api/v1/auth/roles/{id}/      - Eliminar rol
    """
    
    queryset = Role.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_serializer_class(self):
        """
        Retorna serializer con o sin permisos según la acción.
        """
        if self.action == 'retrieve':
            return RoleDetailSerializer
        return RoleSerializer
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Agregar permiso a rol",
        description="Agrega un permiso de módulo a un rol",
        tags=['Roles']
    )
    def add_permission(self, request, pk=None):
        """
        Agrega un permiso a un rol.
        
        Endpoint:
            POST /api/v1/auth/roles/{id}/add_permission/
        
        Request Body:
            {
                "module": "sales",
                "action": "create"
            }
        """
        role = self.get_object()
        module = request.data.get('module')
        action = request.data.get('action')
        
        if not module or not action:
            return Response(
                {'error': 'Se requieren module y action'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que son valores válidos
        if module not in ModulePermission.Module.values:
            return Response(
                {'error': f'Módulo inválido. Opciones: {ModulePermission.Module.values}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if action not in ModulePermission.Action.values:
            return Response(
                {'error': f'Acción inválida. Opciones: {ModulePermission.Action.values}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear o ignorar si ya existe
        permission, created = ModulePermission.objects.get_or_create(
            role=role,
            module=module,
            action=action
        )
        
        if created:
            return Response(
                {'message': 'Permiso agregado exitosamente'},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'El permiso ya existía'},
                status=status.HTTP_200_OK
            )
    
    @action(detail=True, methods=['post'])
    @extend_schema(
        summary="Remover permiso de rol",
        description="Remueve un permiso de módulo de un rol",
        tags=['Roles']
    )
    def remove_permission(self, request, pk=None):
        """
        Remueve un permiso de un rol.
        
        Endpoint:
            POST /api/v1/auth/roles/{id}/remove_permission/
        
        Request Body:
            {
                "module": "sales",
                "action": "create"
            }
        """
        role = self.get_object()
        module = request.data.get('module')
        action = request.data.get('action')
        
        deleted, _ = ModulePermission.objects.filter(
            role=role,
            module=module,
            action=action
        ).delete()
        
        if deleted:
            return Response(
                {'message': 'Permiso removido exitosamente'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Permiso no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserSessionsView(generics.ListAPIView):
    """
    Endpoint para ver sesiones activas del usuario.
    
    Propósito:
        Mostrar dispositivos donde el usuario está logueado.
    
    Endpoint:
        GET /api/v1/auth/sessions/
    """
    
    serializer_class = UserSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Retorna sesiones del usuario actual.
        """
        return UserSession.objects.filter(
            user=self.request.user,
            is_active=True
        )


class RevokeAllSessionsView(APIView):
    """
    Endpoint para cerrar todas las sesiones.
    
    Propósito:
        Permitir al usuario cerrar sesión en todos los dispositivos.
    
    Endpoint:
        POST /api/v1/auth/sessions/revoke-all/
    
    Por qué:
        Si el usuario sospecha que su cuenta está comprometida,
        puede cerrar todas las sesiones remotamente.
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Cerrar todas las sesiones",
        description="Cierra sesión en todos los dispositivos",
        tags=['Autenticación']
    )
    def post(self, request):
        UserSession.objects.filter(
            user=request.user,
            is_active=True
        ).update(is_active=False)
        
        return Response(
            {'message': 'Todas las sesiones han sido cerradas'},
            status=status.HTTP_200_OK
        )
