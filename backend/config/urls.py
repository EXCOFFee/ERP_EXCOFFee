# ========================================================
# SISTEMA ERP UNIVERSAL - URLs Principales
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Configurar las rutas principales del API Gateway.
# Cada microservicio tiene su propio namespace para mantener
# la separación de responsabilidades (SRP).
#
# Estructura de URLs:
# /api/v1/auth/      - Microservicio de Autenticación
# /api/v1/inventory/ - Microservicio de Inventario
# /api/v1/sales/     - Microservicio de Ventas
# /api/v1/finance/   - Microservicio de Finanzas
# /api/v1/hr/        - Microservicio de RRHH
# /api/v1/purchases/ - Microservicio de Compras
# /api/v1/notifications/ - Microservicio de Notificaciones
# ========================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# ========================================================
# PREFIJO DE VERSIÓN DE API
# ========================================================
# Por qué versionar: Permite evolucionar el API sin romper clientes existentes
# Los clientes antiguos pueden seguir usando v1 mientras nuevos usan v2
API_VERSION = 'api/v1/'

urlpatterns = [
    # ========================================================
    # ADMIN DE DJANGO
    # ========================================================
    # Panel de administración para superusuarios
    # Por qué mantenerlo: Útil para debugging y operaciones de emergencia
    path('admin/', admin.site.urls),
    
    # ========================================================
    # DOCUMENTACIÓN DE API (OpenAPI/Swagger)
    # ========================================================
    # Cumple con requisito de Documentación de Interfaz (4.8)
    
    # Schema en formato OpenAPI 3.0
    path(f'{API_VERSION}schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Documentación interactiva Swagger UI
    # Por qué Swagger: Permite probar endpoints directamente desde el navegador
    path(
        f'{API_VERSION}docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
    
    # Documentación alternativa ReDoc (más legible para referencia)
    path(
        f'{API_VERSION}redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),
    
    # ========================================================
    # MICROSERVICIOS - APIs REST
    # ========================================================
    # Cada include() conecta un namespace con su módulo de URLs
    # Esto mantiene cada microservicio desacoplado (Principio D de SOLID)
    
    # Microservicio de Autenticación
    # Endpoints: login, logout, register, refresh-token, users, roles, permissions
    path(
        f'{API_VERSION}auth/',
        include('apps.authentication.urls', namespace='authentication')
    ),
    
    # Microservicio de Inventario
    # Endpoints: products, warehouses, stock, transfers, lots, serial-numbers
    path(
        f'{API_VERSION}inventory/',
        include('apps.inventory.urls', namespace='inventory')
    ),
    
    # Microservicio de Ventas
    # Endpoints: orders, customers, quotations, order-items
    path(
        f'{API_VERSION}sales/',
        include('apps.sales.urls', namespace='sales')
    ),
    
    # Microservicio de Finanzas
    # Endpoints: accounts, journal-entries, invoices, reports
    path(
        f'{API_VERSION}finance/',
        include('apps.finance.urls', namespace='finance')
    ),
    
    # Microservicio de Recursos Humanos
    # Endpoints: employees, departments, leaves, payroll
    path(
        f'{API_VERSION}hr/',
        include('apps.hr.urls', namespace='hr')
    ),
    
    # Microservicio de Compras
    # Endpoints: suppliers, purchase-orders, purchase-order-items
    path(
        f'{API_VERSION}purchases/',
        include('apps.purchases.urls', namespace='purchases')
    ),
    
    # Microservicio de Notificaciones
    # Endpoints: notifications, push-tokens, email-templates
    path(
        f'{API_VERSION}notifications/',
        include('apps.notifications.urls', namespace='notifications')
    ),
    
    # Microservicio Core (utilidades compartidas)
    # Endpoints: health-check, system-info
    path(
        f'{API_VERSION}core/',
        include('apps.core.urls', namespace='core')
    ),
]

# ========================================================
# ARCHIVOS ESTÁTICOS Y MEDIA EN DESARROLLO
# ========================================================
# Por qué solo en DEBUG: En producción, nginx/CDN sirve estos archivos
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ========================================================
# CONFIGURACIÓN DEL ADMIN
# ========================================================
admin.site.site_header = 'ERP Universal - Administración'
admin.site.site_title = 'ERP Admin'
admin.site.index_title = 'Panel de Control'
