# ========================================================
# SISTEMA ERP UNIVERSAL - Configuración Principal de Django
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Configuración central del proyecto Django que orquesta
# todos los microservicios del ERP (Autenticación, Inventario, 
# Ventas, Finanzas, RRHH, Compras).
#
# Principios: Este archivo sigue el principio SRP (Single Responsibility)
# al centralizar únicamente la configuración, delegando la lógica
# de negocio a cada microservicio (app).
# ========================================================

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
# Por qué: Separar configuración sensible del código fuente
load_dotenv()

# ========================================================
# RUTAS BASE DEL PROYECTO
# ========================================================
# BASE_DIR: Directorio raíz del proyecto Django
# Se usa Path para compatibilidad multiplataforma (Windows/Linux/Mac)
BASE_DIR = Path(__file__).resolve().parent.parent

# ========================================================
# CONFIGURACIÓN DE SEGURIDAD
# ========================================================
# SECRET_KEY: Clave secreta para firmas criptográficas (JWT, CSRF, etc.)
# IMPORTANTE: En producción, NUNCA incluir esta clave en el código
# Debe ser una variable de entorno única por ambiente
SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    'dev-secret-key-change-in-production-erp-2025'
)

# DEBUG: Modo de depuración
# Por qué False por defecto: Seguridad en producción
# El valor se lee del entorno para flexibilidad entre ambientes
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'

# ALLOWED_HOSTS: Lista de dominios permitidos para acceder al sistema
# Por qué: Previene ataques de host header injection
ALLOWED_HOSTS = os.getenv(
    'DJANGO_ALLOWED_HOSTS',
    'localhost,127.0.0.1,0.0.0.0'
).split(',')

# ========================================================
# DEFINICIÓN DE APLICACIONES (MICROSERVICIOS)
# ========================================================
# Cada app representa un microservicio del ERP
# Principio: ISP (Interface Segregation) - Cada módulo tiene su propia interfaz

DJANGO_APPS = [
    # Apps nativas de Django
    'django.contrib.admin',          # Panel de administración
    'django.contrib.auth',           # Sistema de autenticación base
    'django.contrib.contenttypes',   # Framework de tipos de contenido
    'django.contrib.sessions',       # Manejo de sesiones
    'django.contrib.messages',       # Sistema de mensajes flash
    'django.contrib.staticfiles',    # Archivos estáticos
]

THIRD_PARTY_APPS = [
    # Apps de terceros
    'rest_framework',                # Django REST Framework para APIs
    'rest_framework_simplejwt',      # Autenticación JWT
    'corsheaders',                   # CORS para frontend separado
    'django_filters',                # Filtrado avanzado en APIs
    'drf_spectacular',               # Documentación OpenAPI/Swagger
    'django_celery_beat',            # Celery Beat scheduler para tareas programadas
]

# MICROSERVICIOS ERP
# Por qué están separados: Principio de arquitectura de microservicios
# Cada app puede escalar, desplegarse y probarse de forma independiente
ERP_MICROSERVICES = [
    'apps.core',           # Microservicio Core: Modelos base, utilidades compartidas
    'apps.authentication', # Microservicio Auth: Usuarios, roles, permisos, JWT
    'apps.inventory',      # Microservicio Inventario: Productos, almacenes, stock
    'apps.sales',          # Microservicio Ventas: Órdenes, clientes, cotizaciones
    'apps.finance',        # Microservicio Finanzas: Contabilidad, facturas, reportes
    'apps.hr',             # Microservicio RRHH: Empleados, licencias, nómina
    'apps.purchasing',     # Microservicio Compras: Proveedores, órdenes de compra
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + ERP_MICROSERVICES

# ========================================================
# MIDDLEWARE
# ========================================================
# Middleware: Procesadores que interceptan cada request/response
# Orden importa: Se ejecutan de arriba hacia abajo en request,
# y de abajo hacia arriba en response

MIDDLEWARE = [
    # CORS debe ir primero para procesar headers de origen cruzado
    'corsheaders.middleware.CorsMiddleware',
    
    # Seguridad general de Django
    'django.middleware.security.SecurityMiddleware',
    
    # WhiteNoise para servir archivos estáticos en producción
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    # Sesiones (necesario para admin)
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # Cache de respuestas
    'django.middleware.common.CommonMiddleware',
    
    # Protección CSRF (Cross-Site Request Forgery)
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # Autenticación de usuarios
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # Mensajes flash
    'django.contrib.messages.middleware.MessageMiddleware',
    
    # Protección contra clickjacking
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ========================================================
# CONFIGURACIÓN DE URLs
# ========================================================
ROOT_URLCONF = 'config.urls'

# ========================================================
# TEMPLATES (para admin y emails HTML)
# ========================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ========================================================
# WSGI APPLICATION
# ========================================================
WSGI_APPLICATION = 'config.wsgi.application'

# ========================================================
# BASE DE DATOS - PostgreSQL
# ========================================================
# Por qué PostgreSQL: 
# - Integridad transaccional ACID para datos financieros críticos
# - Soporte JSONB para campos flexibles
# - Escalabilidad horizontal para crecimiento

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'erp_database'),
        'USER': os.getenv('DB_USER', 'erp_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'erp_secure_password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        # Opciones de conexión optimizadas
        'OPTIONS': {
            'connect_timeout': 10,
        },
        # Atomic requests: Cada request es una transacción
        # Por qué: Garantiza consistencia en operaciones complejas
        'ATOMIC_REQUESTS': True,
    }
}

# ========================================================
# CACHE - Redis
# ========================================================
# Por qué Redis:
# - Caché en memoria para reducir latencia de API
# - Almacenamiento de sesiones distribuido
# - Soporte para pub/sub (notificaciones en tiempo real)

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            # Compresión para optimizar memoria
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        # Prefijo para evitar colisiones si se comparte Redis
        'KEY_PREFIX': 'erp',
    }
}

# Usar Redis para sesiones
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ========================================================
# CELERY - Cola de Mensajes Asíncronos
# ========================================================
# Por qué Celery con RabbitMQ:
# - Procesamiento asíncrono de tareas pesadas (reportes, emails masivos)
# - Desacoplamiento de operaciones lentas del ciclo request/response
# - Escalabilidad horizontal de workers

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Mexico_City'

# ========================================================
# VALIDACIÓN DE CONTRASEÑAS
# ========================================================
# Por qué validación estricta: RNF3 - Seguridad
# Contraseñas deben cumplir múltiples criterios

AUTH_PASSWORD_VALIDATORS = [
    {
        # No usar contraseñas similares a datos del usuario
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        # Longitud mínima de 10 caracteres (más seguro que el default de 8)
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        }
    },
    {
        # No usar contraseñas comunes (lista de 20,000+)
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        # No usar solo números
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ========================================================
# INTERNACIONALIZACIÓN
# ========================================================
LANGUAGE_CODE = 'es-mx'  # Español de México
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# ========================================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ========================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ========================================================
# MODELO DE USUARIO PERSONALIZADO
# ========================================================
# Por qué: Necesitamos campos adicionales (rol, permisos por módulo)
AUTH_USER_MODEL = 'authentication.User'

# ========================================================
# DJANGO REST FRAMEWORK
# ========================================================
# Configuración central de la API REST

REST_FRAMEWORK = {
    # Autenticación JWT como predeterminada
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # Para admin
    ],
    
    # Permisos: Solo usuarios autenticados pueden acceder
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # Paginación por defecto
    # Por qué: RNF1 - Rendimiento, evitar cargar miles de registros
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    
    # Filtrado
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    
    # Throttling (rate limiting)
    # Por qué: Protección contra abuso de API
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',      # Usuarios no autenticados
        'user': '1000/hour',     # Usuarios autenticados
    },
    
    # Documentación OpenAPI
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
    # Formato de fechas ISO 8601
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S%z',
    'DATE_FORMAT': '%Y-%m-%d',
    
    # Manejo de excepciones personalizado
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}

# ========================================================
# SIMPLE JWT - Configuración de Tokens
# ========================================================
# RF5: Autenticación basada en JWT para PC y Móvil

SIMPLE_JWT = {
    # Tiempo de vida del access token (corto para seguridad)
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    
    # Tiempo de vida del refresh token (más largo)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    
    # Rotar refresh token en cada uso
    'ROTATE_REFRESH_TOKENS': True,
    
    # Invalidar refresh tokens antiguos
    'BLACKLIST_AFTER_ROTATION': True,
    
    # Algoritmo de firma
    'ALGORITHM': 'HS256',
    
    # Headers de autenticación
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    
    # Claims del usuario en el token
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# ========================================================
# CORS - Cross-Origin Resource Sharing
# ========================================================
# Por qué: Permitir que el frontend (React) acceda a la API

CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://localhost:19006'  # React Web y React Native
).split(',')

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ========================================================
# DRF SPECTACULAR - Documentación OpenAPI/Swagger
# ========================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'API Sistema ERP Universal',
    'DESCRIPTION': '''
    API REST del Sistema de Planificación de Recursos Empresariales (ERP) Universal.
    
    ## Módulos Disponibles:
    - **Autenticación**: Gestión de usuarios, roles y permisos
    - **Inventario**: Productos, almacenes, stock y transferencias
    - **Ventas**: Órdenes de venta, clientes y cotizaciones
    - **Finanzas**: Contabilidad, facturas y reportes financieros
    - **RRHH**: Empleados, licencias y nómina
    - **Compras**: Proveedores y órdenes de compra
    
    ## Autenticación:
    Usar Bearer Token (JWT) en el header Authorization.
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# ========================================================
# LOGGING - Registro de Eventos
# ========================================================
# Por qué: Facilitar debugging y auditoría del sistema

# Asegurar que el directorio de logs existe
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {module}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'erp.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# ========================================================
# CONFIGURACIÓN DE ID POR DEFECTO
# ========================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
