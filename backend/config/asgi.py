# ========================================================
# SISTEMA ERP UNIVERSAL - ASGI Configuration
# ========================================================
# Versión: 1.0
#
# Propósito: Configuración ASGI para funcionalidades asíncronas.
# ASGI permite WebSockets para notificaciones en tiempo real.
#
# Uso:
#   daphne config.asgi:application
#   uvicorn config.asgi:application
# ========================================================

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
