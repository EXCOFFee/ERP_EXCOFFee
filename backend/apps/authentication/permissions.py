# ========================================================
# SISTEMA ERP UNIVERSAL - Permisos Personalizados
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Definir clases de permisos personalizadas para
# controlar el acceso a recursos basado en roles y módulos.
#
# Implementa: RU4 - Permisos específicos por rol y módulo
# ========================================================

from rest_framework.permissions import BasePermission
from typing import Optional


class HasModulePermission(BasePermission):
    """
    Permiso que verifica acceso a un módulo específico.
    
    Propósito:
        Controlar acceso a endpoints basado en permisos por módulo.
        Cada ViewSet define su 'module' y este permiso verifica
        si el usuario tiene la acción correspondiente.
    
    Mapeo de acciones HTTP a acciones de permiso:
        GET (list, retrieve) -> 'view'
        POST (create) -> 'create'
        PUT/PATCH (update, partial_update) -> 'update'
        DELETE (destroy) -> 'delete'
    
    Uso en ViewSet:
        class ProductViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, HasModulePermission]
            module = 'inventory'  # Define el módulo
    
    Por qué:
        - Centraliza la lógica de permisos
        - Consistente con el modelo de roles y permisos
        - Fácil de entender y mantener
    """
    
    # Mapeo de acciones de DRF a acciones de permiso
    ACTION_MAP = {
        'list': 'view',
        'retrieve': 'view',
        'create': 'create',
        'update': 'update',
        'partial_update': 'update',
        'destroy': 'delete',
    }
    
    def has_permission(self, request, view) -> bool:
        """
        Verifica si el usuario tiene permiso para la acción.
        
        Args:
            request: Request HTTP con el usuario autenticado
            view: Vista/ViewSet que está siendo accedida
        
        Returns:
            bool: True si tiene permiso, False si no
        
        Cómo funciona:
            1. Obtiene el módulo del ViewSet
            2. Mapea la acción HTTP a acción de permiso
            3. Verifica en el modelo de permisos del usuario
        """
        # El usuario debe estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusuarios tienen todos los permisos
        if request.user.is_superuser:
            return True
        
        # Obtener el módulo del ViewSet
        module = getattr(view, 'module', None)
        if not module:
            # Si no hay módulo definido, permitir por defecto
            # Esto es para vistas que no requieren permisos de módulo
            return True
        
        # Obtener la acción de DRF
        action = getattr(view, 'action', None)
        
        # Para vistas que no son ViewSets, usar método HTTP
        if not action:
            method = request.method.lower()
            action = {
                'get': 'view',
                'post': 'create',
                'put': 'update',
                'patch': 'update',
                'delete': 'delete',
            }.get(method, 'view')
        else:
            # Mapear acción de DRF a acción de permiso
            action = self.ACTION_MAP.get(action, action)
        
        # Verificar permiso
        return request.user.has_module_permission(module, action)
    
    def has_object_permission(self, request, view, obj) -> bool:
        """
        Verifica permisos a nivel de objeto individual.
        
        Args:
            request: Request HTTP
            view: Vista siendo accedida
            obj: Objeto específico siendo accedido
        
        Returns:
            bool: True si tiene permiso
        
        Por qué:
            Permite implementar reglas adicionales como:
            - Solo el creador puede editar
            - Solo el supervisor puede aprobar
        """
        # Por defecto, usar el mismo permiso que has_permission
        return self.has_permission(request, view)


class IsOwnerOrAdmin(BasePermission):
    """
    Permiso que permite acceso al propietario del recurso o admin.
    
    Propósito:
        Permitir que usuarios editen solo sus propios recursos,
        pero admins puedan editar cualquiera.
    
    Uso:
        class ProfileView(APIView):
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    Cómo funciona:
        Verifica si el objeto tiene un campo 'user' o 'created_by'
        que coincida con el usuario autenticado.
    """
    
    def has_object_permission(self, request, view, obj) -> bool:
        """
        Verifica si el usuario es propietario o admin.
        
        Args:
            request: Request HTTP
            view: Vista
            obj: Objeto siendo accedido
        
        Returns:
            bool: True si es propietario o admin
        """
        # Admin tiene acceso total
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # Verificar si el objeto tiene campo 'user'
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Verificar si el objeto tiene campo 'created_by'
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        # Si el objeto ES un usuario, verificar si es el mismo
        if hasattr(obj, 'email') and hasattr(request.user, 'email'):
            return obj.email == request.user.email
        
        return False


class IsSuperUser(BasePermission):
    """
    Permiso que solo permite acceso a superusuarios.
    
    Propósito:
        Restringir funcionalidades críticas solo a superadmins.
    
    Uso:
        - Configuración del sistema
        - Operaciones de mantenimiento
        - Acciones irreversibles
    """
    
    def has_permission(self, request, view) -> bool:
        """
        Verifica si el usuario es superusuario.
        
        Returns:
            bool: True si es superusuario
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_superuser
        )


class CanApprove(BasePermission):
    """
    Permiso para aprobar recursos (órdenes, licencias, etc.).
    
    Propósito:
        Controlar quién puede aprobar documentos.
        Requiere permiso 'approve' en el módulo correspondiente.
    
    Uso:
        class ApproveOrderView(APIView):
            permission_classes = [IsAuthenticated, CanApprove]
            module = 'sales'
    """
    
    def has_permission(self, request, view) -> bool:
        """
        Verifica permiso de aprobación.
        
        Returns:
            bool: True si puede aprobar
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        module = getattr(view, 'module', None)
        if not module:
            return False
        
        return request.user.has_module_permission(module, 'approve')


class CanExport(BasePermission):
    """
    Permiso para exportar datos (PDF, CSV, Excel).
    
    Propósito:
        Controlar quién puede exportar reportes y datos.
        Implementa RU3 - Exportar reportes.
    
    Uso:
        class ExportReportView(APIView):
            permission_classes = [IsAuthenticated, CanExport]
            module = 'finance'
    """
    
    def has_permission(self, request, view) -> bool:
        """
        Verifica permiso de exportación.
        
        Returns:
            bool: True si puede exportar
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        module = getattr(view, 'module', None)
        if not module:
            return False
        
        return request.user.has_module_permission(module, 'export')


def check_module_permission(user, module: str, action: str) -> bool:
    """
    Función helper para verificar permisos fuera de vistas.
    
    Propósito:
        Verificar permisos en código de negocio (services, tasks).
    
    Args:
        user: Usuario a verificar
        module: Código del módulo
        action: Código de la acción
    
    Returns:
        bool: True si tiene permiso
    
    Uso:
        from apps.authentication.permissions import check_module_permission
        
        if check_module_permission(user, 'inventory', 'update'):
            # Realizar acción
    """
    if not user or not user.is_authenticated:
        return False
    
    return user.has_module_permission(module, action)
