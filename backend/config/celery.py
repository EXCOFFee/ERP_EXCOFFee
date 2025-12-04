# ========================================================
# SISTEMA ERP UNIVERSAL - Configuración de Celery
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Configurar Celery para procesamiento asíncrono de tareas.
# 
# Por qué Celery:
# - RF6: Reportes financieros largos ejecutados asíncronamente
# - RU5: Notificaciones push cuando se aprueba una orden de compra
# - Mejora el rendimiento al desacoplar tareas pesadas del request
#
# Cómo funciona:
# 1. El usuario inicia una tarea (ej. generar reporte)
# 2. La API encola la tarea en RabbitMQ
# 3. Un worker de Celery procesa la tarea en background
# 4. El usuario recibe notificación cuando termina
# ========================================================

import os
from celery import Celery

# Establecer el módulo de settings de Django para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Crear instancia de la aplicación Celery
# Nombre 'erp' identifica esta app en los logs y admin
app = Celery('erp')

# Cargar configuración desde settings de Django
# namespace='CELERY' significa que todas las variables deben empezar con CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodescubrir tareas en todos los módulos 'tasks.py' de las apps instaladas
# Esto permite que cada microservicio defina sus propias tareas
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    Tarea de debugging para verificar que Celery funciona correctamente.
    
    Propósito: Prueba de conectividad y funcionamiento de Celery.
    
    Uso:
        from config.celery import debug_task
        debug_task.delay()
    
    Args:
        self: Referencia a la instancia de la tarea (bind=True)
    
    Returns:
        None (ignore_result=True para no almacenar resultado)
    """
    print(f'Request: {self.request!r}')


# ========================================================
# CONFIGURACIÓN DE COLAS DE TAREAS
# ========================================================
# Diferentes colas para diferentes prioridades y tipos de tareas
# Por qué: Permite escalar workers independientemente por tipo

app.conf.task_routes = {
    # Tareas de alta prioridad (notificaciones, alertas)
    'apps.notifications.tasks.*': {'queue': 'high_priority'},
    
    # Tareas de reportes (pueden tardar minutos)
    'apps.finance.tasks.generate_*': {'queue': 'reports'},
    
    # Tareas de sincronización de inventario
    'apps.inventory.tasks.*': {'queue': 'inventory'},
    
    # Tareas de email masivo
    'apps.notifications.tasks.send_bulk_*': {'queue': 'bulk_email'},
    
    # Por defecto: cola general
    '*': {'queue': 'default'},
}

# ========================================================
# CONFIGURACIÓN DE REINTENTOS
# ========================================================
# Por qué: Algunas tareas pueden fallar temporalmente (ej. API externa)

app.conf.task_acks_late = True  # ACK después de ejecutar (no antes)
app.conf.task_reject_on_worker_lost = True  # Reencolar si worker muere

# Configuración de reintentos por defecto
app.conf.task_default_retry_delay = 60  # 60 segundos entre reintentos
app.conf.task_max_retries = 3  # Máximo 3 reintentos

# ========================================================
# CONFIGURACIÓN DE RESULTADOS
# ========================================================
# Tiempo de expiración de resultados: 24 horas
app.conf.result_expires = 86400

# Serialización segura
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

# ========================================================
# TAREAS PROGRAMADAS (CELERY BEAT)
# ========================================================
# Por qué: Algunas tareas deben ejecutarse periódicamente

app.conf.beat_schedule = {
    # Verificar inventario bajo cada hora
    'check-low-stock-every-hour': {
        'task': 'apps.inventory.tasks.check_low_stock_alerts',
        'schedule': 3600.0,  # Cada hora
    },
    
    # Generar backup de base de datos cada noche
    'daily-database-backup': {
        'task': 'apps.core.tasks.backup_database',
        'schedule': 86400.0,  # Cada 24 horas
        'options': {'queue': 'maintenance'},
    },
    
    # Limpiar tokens expirados cada día
    'cleanup-expired-tokens': {
        'task': 'apps.authentication.tasks.cleanup_expired_tokens',
        'schedule': 86400.0,
    },
    
    # Recordatorio de licencias próximas a vencer
    'license-expiry-reminder': {
        'task': 'apps.hr.tasks.send_license_expiry_reminders',
        'schedule': 86400.0,
    },
}

app.conf.timezone = 'America/Mexico_City'
