# ========================================================
# SISTEMA ERP UNIVERSAL - WSGI Configuration
# ========================================================
# Versión: 1.0
#
# Propósito: Configuración WSGI para despliegue en producción.
# WSGI (Web Server Gateway Interface) es el estándar para
# servir aplicaciones Python en servidores web como Gunicorn.
#
# Uso en producción:
#   gunicorn config.wsgi:application --bind 0.0.0.0:8000
# ========================================================

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
