# ========================================================
# SISTEMA ERP UNIVERSAL - Configuración de App RRHH
# ========================================================

from django.apps import AppConfig


class HRConfig(AppConfig):
    """Configuración del módulo de Recursos Humanos."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.hr'
    verbose_name = 'Recursos Humanos'
    
    def ready(self):
        """Importar señales al iniciar."""
        try:
            import apps.hr.signals  # noqa
        except ImportError:
            pass
