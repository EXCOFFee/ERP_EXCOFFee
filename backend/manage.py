#!/usr/bin/env python
# ========================================================
# SISTEMA ERP UNIVERSAL - Django Management Script
# ========================================================
# Versión: 1.0
#
# Propósito: Script de línea de comandos para tareas administrativas.
#
# Uso común:
#   python manage.py runserver          - Iniciar servidor de desarrollo
#   python manage.py migrate            - Aplicar migraciones de BD
#   python manage.py createsuperuser    - Crear usuario administrador
#   python manage.py test               - Ejecutar pruebas
#   python manage.py shell              - Consola interactiva
# ========================================================

import os
import sys


def main():
    """
    Función principal para ejecutar comandos administrativos de Django.
    
    Propósito: Punto de entrada para todas las operaciones de manage.py
    
    Por qué:
        Este script configura el entorno de Django y delega la ejecución
        al sistema de comandos de Django.
    
    Raises:
        ImportError: Si Django no está instalado correctamente
    """
    # Establecer el módulo de configuración por defecto
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Está instalado y disponible en PYTHONPATH? "
            "¿Olvidó activar el entorno virtual?"
        ) from exc
    
    # Ejecutar el comando proporcionado en la línea de comandos
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
