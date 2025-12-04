# ========================================================
# SISTEMA ERP UNIVERSAL - Authentication App Configuration
# ========================================================
from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Configuración del microservicio de Autenticación.
    
    Propósito:
        Gestionar usuarios, roles, permisos y autenticación JWT.
        Implementa RF5 del SRS.
    
    Responsabilidades:
        - Modelo de usuario personalizado
        - Autenticación JWT
        - Gestión de roles y permisos por módulo
        - Control de acceso basado en roles (RBAC)
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    verbose_name = 'Autenticación - Usuarios y Permisos'
    
    def ready(self):
        """
        Se ejecuta cuando la app está lista.
        Importa señales para crear permisos automáticamente.
        """
        import apps.authentication.signals  # noqa
