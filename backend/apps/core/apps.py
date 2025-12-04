# ========================================================
# SISTEMA ERP UNIVERSAL - Core App Configuration
# ========================================================
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuración de la aplicación Core.
    
    Propósito:
        Define la configuración de la app Core que contiene
        modelos base, utilidades y lógica compartida.
    
    Por qué:
        Centralizar funcionalidad común reduce duplicación (DRY)
        y facilita el mantenimiento del sistema.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core - Utilidades Base'
