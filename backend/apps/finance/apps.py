# ========================================================
# SISTEMA ERP UNIVERSAL - Configuración de App Finanzas
# ========================================================

from django.apps import AppConfig


class FinanceConfig(AppConfig):
    """
    Configuración del módulo de finanzas.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.finance'
    verbose_name = 'Finanzas'
    
    def ready(self):
        """
        Ejecutado cuando la aplicación está lista.
        Importa signals para registrarlos.
        """
        try:
            import apps.finance.signals  # noqa
        except ImportError:
            pass
