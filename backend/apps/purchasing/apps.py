# ========================================================
# SISTEMA ERP UNIVERSAL - Configuración de App de Compras
# ========================================================

from django.apps import AppConfig


class PurchasingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.purchasing'
    verbose_name = 'Compras'
    
    def ready(self):
        try:
            import apps.purchasing.signals  # noqa
        except ImportError:
            pass
