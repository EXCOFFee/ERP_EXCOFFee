# ========================================================
# SISTEMA ERP UNIVERSAL - Admin de Autenticación
# ========================================================
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, ModulePermission, UserSession


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Admin para gestión de roles.
    """
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(ModulePermission)
class ModulePermissionAdmin(admin.ModelAdmin):
    """
    Admin para permisos de módulo.
    """
    list_display = ['role', 'module', 'action']
    list_filter = ['role', 'module', 'action']
    ordering = ['role', 'module']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin personalizado para el modelo User.
    """
    list_display = [
        'email', 'first_name', 'last_name', 'role',
        'is_active', 'is_staff', 'last_login'
    ]
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'role']
    search_fields = ['email', 'first_name', 'last_name', 'employee_code']
    ordering = ['email']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'phone', 'avatar', 'employee_code')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'role')
        }),
        ('Preferencias', {
            'fields': ('language', 'timezone', 'email_notifications', 'push_notifications')
        }),
        ('Fechas', {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',
                'first_name', 'last_name', 'role'
            ),
        }),
    )
    
    readonly_fields = ['last_login', 'created_at', 'updated_at']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """
    Admin para sesiones de usuario.
    """
    list_display = [
        'user', 'device_type', 'ip_address',
        'is_active', 'created_at', 'last_activity'
    ]
    list_filter = ['device_type', 'is_active']
    search_fields = ['user__email', 'ip_address']
    readonly_fields = [
        'user', 'refresh_token_jti', 'device_type',
        'device_name', 'ip_address', 'user_agent',
        'created_at', 'last_activity', 'expires_at'
    ]
