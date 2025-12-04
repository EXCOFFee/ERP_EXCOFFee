# ========================================================
# SISTEMA ERP UNIVERSAL - Configuración de App Ventas
# ========================================================

from django.apps import AppConfig


class SalesConfig(AppConfig):
    """Configuración del módulo de Ventas."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sales'
    verbose_name = 'Ventas'
    
    def ready(self):
        """Importar señales al iniciar."""
        try:
            import apps.sales.signals  # noqa
        except ImportError:
            pass
