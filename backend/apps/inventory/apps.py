# ========================================================
# SISTEMA ERP UNIVERSAL - Inventory App Configuration
# ========================================================
from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """
    Configuración del microservicio de Inventario.
    
    Propósito:
        Gestionar productos, almacenes, stock y movimientos de inventario.
        Implementa RF2 y RU2 del SRS.
    
    Responsabilidades:
        - Gestión de productos y categorías
        - Control de inventario multi-almacén
        - Gestión de lotes y números de serie
        - Transferencias entre almacenes
        - Alertas de stock bajo
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventory'
    verbose_name = 'Inventario - Productos y Stock'
