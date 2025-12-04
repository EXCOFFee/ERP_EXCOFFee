# ========================================================
# SISTEMA ERP UNIVERSAL - Configuración Package Init
# ========================================================
# Este archivo hace que 'config' sea un paquete de Python.
# También inicializa Celery cuando Django se carga.
# ========================================================

from .celery import app as celery_app

__all__ = ('celery_app',)
