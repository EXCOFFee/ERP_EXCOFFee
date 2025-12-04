# ========================================================
# SISTEMA ERP UNIVERSAL - Señales de Autenticación
# ========================================================
# Versión: 1.0
#
# Propósito: Definir señales (signals) que se ejecutan
# automáticamente en eventos del ciclo de vida de modelos.
# ========================================================

from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_migrate)
def create_default_roles(sender, **kwargs):
    """
    Crea roles por defecto después de migrar.
    
    Propósito:
        Asegurar que existan roles básicos en el sistema
        después de una instalación nueva.
    
    Por qué señal post_migrate:
        Se ejecuta automáticamente después de 'python manage.py migrate',
        garantizando que los roles existan antes de crear usuarios.
    
    Roles creados:
        - admin: Administrador del sistema
        - manager: Gerente con permisos de aprobación
        - employee: Empleado estándar
        - warehouse: Personal de almacén
        - accountant: Contador
    """
    # Solo ejecutar para nuestra app
    if sender.name != 'apps.authentication':
        return
    
    from apps.authentication.models import Role, ModulePermission
    
    # Definición de roles por defecto
    default_roles = [
        {
            'name': 'Administrador',
            'code': 'admin',
            'description': 'Acceso total al sistema',
            'permissions': [
                # Todos los permisos en todos los módulos
                (module, action)
                for module in ModulePermission.Module.values
                for action in ModulePermission.Action.values
            ]
        },
        {
            'name': 'Gerente de Ventas',
            'code': 'sales_manager',
            'description': 'Gestión completa de ventas y reportes',
            'permissions': [
                ('dashboard', 'view'),
                ('sales', 'view'), ('sales', 'create'), ('sales', 'update'),
                ('sales', 'delete'), ('sales', 'approve'), ('sales', 'export'),
                ('inventory', 'view'),
                ('reports', 'view'), ('reports', 'export'),
            ]
        },
        {
            'name': 'Vendedor',
            'code': 'salesperson',
            'description': 'Crear y gestionar órdenes de venta',
            'permissions': [
                ('dashboard', 'view'),
                ('sales', 'view'), ('sales', 'create'), ('sales', 'update'),
                ('inventory', 'view'),
            ]
        },
        {
            'name': 'Gerente de Almacén',
            'code': 'warehouse_manager',
            'description': 'Gestión completa de inventario',
            'permissions': [
                ('dashboard', 'view'),
                ('inventory', 'view'), ('inventory', 'create'),
                ('inventory', 'update'), ('inventory', 'delete'),
                ('inventory', 'approve'), ('inventory', 'export'),
                ('inventory', 'import'),
                ('purchases', 'view'),
            ]
        },
        {
            'name': 'Empleado de Almacén',
            'code': 'warehouse_employee',
            'description': 'Operaciones básicas de inventario',
            'permissions': [
                ('dashboard', 'view'),
                ('inventory', 'view'), ('inventory', 'create'),
                ('inventory', 'update'),
            ]
        },
        {
            'name': 'Contador',
            'code': 'accountant',
            'description': 'Gestión financiera y reportes contables',
            'permissions': [
                ('dashboard', 'view'),
                ('finance', 'view'), ('finance', 'create'),
                ('finance', 'update'), ('finance', 'export'),
                ('reports', 'view'), ('reports', 'export'),
                ('sales', 'view'),
                ('purchases', 'view'),
            ]
        },
        {
            'name': 'Gerente de RRHH',
            'code': 'hr_manager',
            'description': 'Gestión de recursos humanos',
            'permissions': [
                ('dashboard', 'view'),
                ('hr', 'view'), ('hr', 'create'), ('hr', 'update'),
                ('hr', 'delete'), ('hr', 'approve'), ('hr', 'export'),
                ('reports', 'view'), ('reports', 'export'),
            ]
        },
        {
            'name': 'Empleado',
            'code': 'employee',
            'description': 'Acceso básico a funciones de empleado',
            'permissions': [
                ('dashboard', 'view'),
                ('hr', 'view'),  # Ver sus propios datos
            ]
        },
    ]
    
    # Crear roles y permisos
    for role_data in default_roles:
        role, created = Role.objects.get_or_create(
            code=role_data['code'],
            defaults={
                'name': role_data['name'],
                'description': role_data['description'],
            }
        )
        
        if created:
            # Crear permisos para el rol
            for module, action in role_data['permissions']:
                ModulePermission.objects.get_or_create(
                    role=role,
                    module=module,
                    action=action
                )
            print(f"  Rol creado: {role.name}")


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Señal ejecutada después de guardar un usuario.
    
    Propósito:
        Realizar acciones adicionales después de crear/actualizar usuario.
    
    Acciones:
        - Enviar email de bienvenida a nuevos usuarios
        - Crear configuraciones por defecto
    """
    if created:
        # Aquí se puede agregar lógica como:
        # - Enviar email de bienvenida
        # - Crear preferencias por defecto
        # - Notificar a admins
        pass
