# ========================================================
# SISTEMA ERP UNIVERSAL - Vistas del Microservicio Core
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Endpoints de utilidad como health check y
# información del sistema para monitoreo y DevOps.
# ========================================================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework import status
from django.conf import settings
from django.db import connection
from django.core.cache import cache
import time


class HealthCheckView(APIView):
    """
    Endpoint de verificación de salud del sistema.
    
    Propósito:
        Permitir que balanceadores de carga y sistemas de monitoreo
        verifiquen que el servicio está funcionando correctamente.
    
    Por qué público:
        Los health checks no requieren autenticación para permitir
        monitoreo desde sistemas externos sin credenciales.
    
    Verifica:
        - Conectividad a la base de datos PostgreSQL
        - Conectividad a Redis (cache)
        - Tiempo de respuesta general
    
    Uso:
        GET /api/v1/core/health/
    
    Respuesta exitosa:
        {
            "status": "healthy",
            "database": "connected",
            "cache": "connected",
            "response_time_ms": 15
        }
    """
    
    permission_classes = [AllowAny]  # Público para monitoreo
    authentication_classes = []  # Sin autenticación requerida
    
    def get(self, request):
        """
        Verifica el estado de salud del sistema.
        
        Returns:
            Response: Estado de cada componente del sistema
        """
        # Medir tiempo de respuesta total
        start_time = time.time()
        
        # Estado inicial
        health_status = {
            'status': 'healthy',
            'database': 'unknown',
            'cache': 'unknown',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
        }
        
        # Variable para tracking de errores
        has_error = False
        
        # ========================================================
        # Verificar conexión a PostgreSQL
        # ========================================================
        try:
            # Ejecutar query simple para verificar conexión
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            health_status['database'] = 'connected'
        except Exception as e:
            health_status['database'] = f'error: {str(e)}'
            has_error = True
        
        # ========================================================
        # Verificar conexión a Redis
        # ========================================================
        try:
            # Intentar set/get en cache
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                health_status['cache'] = 'connected'
            else:
                health_status['cache'] = 'error: could not read back'
                has_error = True
        except Exception as e:
            health_status['cache'] = f'error: {str(e)}'
            has_error = True
        
        # ========================================================
        # Calcular tiempo de respuesta
        # ========================================================
        end_time = time.time()
        health_status['response_time_ms'] = round((end_time - start_time) * 1000, 2)
        
        # Determinar status final
        if has_error:
            health_status['status'] = 'unhealthy'
            return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return Response(health_status, status=status.HTTP_200_OK)


class SystemInfoView(APIView):
    """
    Endpoint de información del sistema (solo admin).
    
    Propósito:
        Proporcionar información detallada del sistema para
        debugging y administración.
    
    Por qué requiere admin:
        Contiene información sensible como versión de Django,
        configuraciones y dependencias.
    
    Uso:
        GET /api/v1/core/system-info/
        Authorization: Bearer <admin_token>
    """
    
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """
        Retorna información detallada del sistema.
        
        Returns:
            Response: Configuración y estado del sistema
        """
        import django
        import sys
        
        system_info = {
            'application': 'Sistema ERP Universal',
            'version': '1.0.0',
            'environment': 'development' if settings.DEBUG else 'production',
            'python_version': sys.version,
            'django_version': django.get_version(),
            'database': {
                'engine': settings.DATABASES['default']['ENGINE'],
                'host': settings.DATABASES['default']['HOST'],
                'name': settings.DATABASES['default']['NAME'],
            },
            'features': {
                'debug_mode': settings.DEBUG,
                'timezone': settings.TIME_ZONE,
                'language': settings.LANGUAGE_CODE,
            },
            'api': {
                'pagination_size': settings.REST_FRAMEWORK.get('PAGE_SIZE', 25),
                'throttle_rates': settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_RATES', {}),
            },
        }
        
        return Response(system_info, status=status.HTTP_200_OK)
