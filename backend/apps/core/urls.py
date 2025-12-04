# ========================================================
# SISTEMA ERP UNIVERSAL - URLs del Microservicio Core
# ========================================================
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Health check para monitoreo de disponibilidad
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    
    # Información del sistema
    path('system-info/', views.SystemInfoView.as_view(), name='system-info'),
]
