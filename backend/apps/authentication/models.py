# ========================================================
# SISTEMA ERP UNIVERSAL - Modelos de Autenticación
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Definir el modelo de usuario personalizado y
# el sistema de roles y permisos del ERP.
#
# Requisitos implementados:
# - RU4: Permisos específicos por rol y módulo
# - RF5: Autenticación basada en JWT
# - RNF3: Contraseñas con hashing salado (bcrypt)
# ========================================================

import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator

from apps.core.models import TimeStampedModel, SoftDeleteModel


class UserManager(BaseUserManager):
    """
    Manager personalizado para el modelo User.
    
    Propósito:
        Proporcionar métodos para crear usuarios normales y superusuarios.
    
    Por qué personalizado:
        El modelo User usa email en lugar de username como identificador
        principal, por lo que necesitamos sobrescribir los métodos de creación.
    """
    
    def create_user(
        self,
        email: str,
        password: str = None,
        **extra_fields
    ):
        """
        Crea y guarda un usuario normal.
        
        Args:
            email: Correo electrónico (requerido, único)
            password: Contraseña (será hasheada con bcrypt)
            **extra_fields: Campos adicionales (first_name, etc.)
        
        Returns:
            User: Instancia del usuario creado
        
        Raises:
            ValueError: Si no se proporciona email
        
        Por qué email obligatorio:
            - Es el identificador único del usuario
            - Facilita recuperación de contraseña
            - Estándar moderno vs username
        """
        if not email:
            raise ValueError('El email es obligatorio')
        
        # Normalizar email (minúsculas en dominio)
        email = self.normalize_email(email)
        
        # Crear instancia del usuario
        user = self.model(email=email, **extra_fields)
        
        # Establecer contraseña (hashea automáticamente)
        user.set_password(password)
        
        # Guardar en base de datos
        user.save(using=self._db)
        
        return user
    
    def create_superuser(
        self,
        email: str,
        password: str,
        **extra_fields
    ):
        """
        Crea y guarda un superusuario.
        
        Args:
            email: Correo electrónico
            password: Contraseña
            **extra_fields: Campos adicionales
        
        Returns:
            User: Instancia del superusuario
        
        Por qué:
            Los superusuarios tienen acceso total al admin de Django
            y a todos los módulos del ERP.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class Role(TimeStampedModel):
    """
    Modelo para definir roles del sistema.
    
    Propósito:
        Agrupar permisos en roles reutilizables.
        Implementa RU4 - Permisos específicos por rol.
    
    Ejemplos de roles:
        - Administrador: Acceso total
        - Gerente de Ventas: Ventas + reportes
        - Empleado de Almacén: Solo inventario
        - Contador: Solo finanzas
    
    Por qué tabla separada:
        - Permite crear roles personalizados sin cambiar código
        - Facilita auditoría de permisos
        - Separación de responsabilidades (SRP)
    """
    
    # ID único universal
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Nombre del rol (único)
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre del Rol',
        help_text='Nombre identificador del rol (ej. "Gerente de Ventas")'
    )
    
    # Código corto para programación
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código',
        help_text='Código corto para uso en código (ej. "sales_manager")'
    )
    
    # Descripción del rol
    description = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción de las responsabilidades y permisos del rol'
    )
    
    # Si el rol está activo
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Indica si el rol puede ser asignado a usuarios'
    )
    
    class Meta:
        db_table = 'auth_roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ModulePermission(models.Model):
    """
    Permisos específicos por módulo del ERP.
    
    Propósito:
        Definir qué acciones puede realizar cada rol en cada módulo.
        Granularidad: Módulo + Acción (CRUD)
    
    Por qué separado de permisos de Django:
        - Permisos de Django son por modelo
        - Necesitamos permisos por módulo/funcionalidad
        - Más fácil de entender para usuarios de negocio
    """
    
    class Module(models.TextChoices):
        """
        Módulos disponibles en el ERP.
        Corresponden a los microservicios definidos en el SRS.
        """
        DASHBOARD = 'dashboard', 'Dashboard'
        INVENTORY = 'inventory', 'Inventario'
        SALES = 'sales', 'Ventas'
        PURCHASES = 'purchases', 'Compras'
        FINANCE = 'finance', 'Finanzas'
        HR = 'hr', 'Recursos Humanos'
        REPORTS = 'reports', 'Reportes'
        SETTINGS = 'settings', 'Configuración'
        USERS = 'users', 'Usuarios'
    
    class Action(models.TextChoices):
        """
        Acciones disponibles por módulo (basado en CRUD).
        """
        VIEW = 'view', 'Ver'
        CREATE = 'create', 'Crear'
        UPDATE = 'update', 'Actualizar'
        DELETE = 'delete', 'Eliminar'
        EXPORT = 'export', 'Exportar'
        IMPORT = 'import', 'Importar'
        APPROVE = 'approve', 'Aprobar'
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Relación con el rol
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='permissions',
        verbose_name='Rol'
    )
    
    # Módulo al que aplica el permiso
    module = models.CharField(
        max_length=50,
        choices=Module.choices,
        verbose_name='Módulo'
    )
    
    # Acción permitida
    action = models.CharField(
        max_length=50,
        choices=Action.choices,
        verbose_name='Acción'
    )
    
    class Meta:
        db_table = 'auth_module_permissions'
        verbose_name = 'Permiso de Módulo'
        verbose_name_plural = 'Permisos de Módulo'
        # Un rol no puede tener el mismo permiso duplicado
        unique_together = ['role', 'module', 'action']
        ordering = ['role', 'module', 'action']
    
    def __str__(self):
        return f"{self.role.name} - {self.get_module_display()} - {self.get_action_display()}"


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel, SoftDeleteModel):
    """
    Modelo de usuario personalizado del ERP.
    
    Propósito:
        Definir el modelo de usuario con todos los campos necesarios
        para el sistema ERP, incluyendo relación con roles.
    
    Por qué personalizado:
        - Usar email en lugar de username
        - Campos adicionales específicos del negocio
        - Integración con sistema de roles propio
    
    Campos heredados de AbstractBaseUser:
        - password: Contraseña hasheada
        - last_login: Último inicio de sesión
    
    Campos heredados de PermissionsMixin:
        - is_superuser: Si tiene todos los permisos
        - groups: Grupos de Django (no usado, usamos roles propios)
        - user_permissions: Permisos individuales de Django
    
    Campos heredados de TimeStampedModel:
        - created_at: Fecha de creación
        - updated_at: Última modificación
    
    Campos heredados de SoftDeleteModel:
        - is_deleted: Borrado lógico
        - deleted_at: Fecha de eliminación
        - deleted_by: Quién eliminó
    """
    
    # ========================================================
    # IDENTIFICACIÓN
    # ========================================================
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID de Usuario'
    )
    
    email = models.EmailField(
        unique=True,
        verbose_name='Correo Electrónico',
        help_text='Email único para inicio de sesión'
    )
    
    # Código de empleado (opcional, para vincular con RRHH)
    employee_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Código de Empleado',
        help_text='Código único de empleado para vincular con módulo RRHH'
    )
    
    # ========================================================
    # INFORMACIÓN PERSONAL
    # ========================================================
    
    first_name = models.CharField(
        max_length=100,
        verbose_name='Nombre(s)',
        validators=[MinLengthValidator(2)]
    )
    
    last_name = models.CharField(
        max_length=100,
        verbose_name='Apellido(s)',
        validators=[MinLengthValidator(2)]
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono',
        help_text='Número de teléfono para contacto'
    )
    
    # Foto de perfil
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Foto de Perfil'
    )
    
    # ========================================================
    # ESTADO Y PERMISOS
    # ========================================================
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Indica si el usuario puede iniciar sesión'
    )
    
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Staff',
        help_text='Indica si puede acceder al admin de Django'
    )
    
    # Rol principal del usuario
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Rol',
        help_text='Rol que define los permisos del usuario'
    )
    
    # ========================================================
    # PREFERENCIAS
    # ========================================================
    
    # Idioma preferido
    language = models.CharField(
        max_length=10,
        default='es',
        verbose_name='Idioma',
        help_text='Código de idioma preferido (es, en, etc.)'
    )
    
    # Zona horaria
    timezone = models.CharField(
        max_length=50,
        default='America/Mexico_City',
        verbose_name='Zona Horaria'
    )
    
    # Recibir notificaciones por email
    email_notifications = models.BooleanField(
        default=True,
        verbose_name='Notificaciones Email',
        help_text='Recibir notificaciones por correo electrónico'
    )
    
    # Recibir notificaciones push
    push_notifications = models.BooleanField(
        default=True,
        verbose_name='Notificaciones Push',
        help_text='Recibir notificaciones push en móvil'
    )
    
    # ========================================================
    # SEGURIDAD
    # ========================================================
    
    # Última vez que cambió contraseña
    password_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Último Cambio de Contraseña'
    )
    
    # Intentos fallidos de login (para bloqueo)
    failed_login_attempts = models.IntegerField(
        default=0,
        verbose_name='Intentos Fallidos'
    )
    
    # Fecha de bloqueo temporal
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Bloqueado Hasta',
        help_text='Fecha hasta la cual la cuenta está temporalmente bloqueada'
    )
    
    # ========================================================
    # CONFIGURACIÓN DEL MODELO
    # ========================================================
    
    objects = UserManager()
    
    # Campo usado para autenticación
    USERNAME_FIELD = 'email'
    
    # Campos requeridos además del email y password
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'auth_users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self) -> str:
        """
        Retorna el nombre completo del usuario.
        
        Returns:
            str: Nombre y apellido concatenados
        """
        return f"{self.first_name} {self.last_name}".strip()
    
    def has_module_permission(self, module: str, action: str) -> bool:
        """
        Verifica si el usuario tiene permiso para una acción en un módulo.
        
        Args:
            module: Código del módulo (ej. 'inventory')
            action: Código de la acción (ej. 'view', 'create')
        
        Returns:
            bool: True si tiene el permiso, False si no
        
        Por qué este método:
            Centraliza la lógica de verificación de permisos.
            Usado por decoradores y vistas para control de acceso.
        
        Ejemplo:
            if user.has_module_permission('sales', 'create'):
                # Permitir crear orden de venta
        """
        # Superusuarios tienen todos los permisos
        if self.is_superuser:
            return True
        
        # Si no tiene rol, no tiene permisos
        if not self.role:
            return False
        
        # Verificar en permisos del rol
        return self.role.permissions.filter(
            module=module,
            action=action
        ).exists()
    
    def get_all_permissions_list(self) -> list:
        """
        Obtiene lista de todos los permisos del usuario.
        
        Returns:
            list: Lista de tuplas (módulo, acción)
        
        Uso:
            Para mostrar en UI qué permisos tiene el usuario.
        """
        if self.is_superuser:
            # Superuser tiene todos los permisos
            return [
                (module.value, action.value)
                for module in ModulePermission.Module
                for action in ModulePermission.Action
            ]
        
        if not self.role:
            return []
        
        return list(
            self.role.permissions.values_list('module', 'action')
        )
    
    def is_account_locked(self) -> bool:
        """
        Verifica si la cuenta está temporalmente bloqueada.
        
        Returns:
            bool: True si está bloqueada, False si no
        
        Por qué:
            Protección contra ataques de fuerza bruta.
            Después de X intentos fallidos, se bloquea temporalmente.
        """
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False
    
    def increment_failed_login(self):
        """
        Incrementa el contador de intentos fallidos y bloquea si es necesario.
        
        Lógica:
            - 5 intentos fallidos = bloqueo de 15 minutos
            - 10 intentos fallidos = bloqueo de 1 hora
            - 15+ intentos fallidos = bloqueo de 24 horas
        """
        self.failed_login_attempts += 1
        
        if self.failed_login_attempts >= 15:
            self.locked_until = timezone.now() + timezone.timedelta(hours=24)
        elif self.failed_login_attempts >= 10:
            self.locked_until = timezone.now() + timezone.timedelta(hours=1)
        elif self.failed_login_attempts >= 5:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=15)
        
        self.save(update_fields=['failed_login_attempts', 'locked_until'])
    
    def reset_failed_login(self):
        """
        Resetea el contador de intentos fallidos (llamado tras login exitoso).
        """
        if self.failed_login_attempts > 0 or self.locked_until:
            self.failed_login_attempts = 0
            self.locked_until = None
            self.save(update_fields=['failed_login_attempts', 'locked_until'])


class UserSession(models.Model):
    """
    Registro de sesiones activas del usuario.
    
    Propósito:
        Rastrear dispositivos conectados para seguridad
        y permitir cerrar sesiones remotamente.
    
    Por qué:
        - Ver dónde está logueado el usuario
        - Permitir logout de todos los dispositivos
        - Detectar actividad sospechosa
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name='Usuario'
    )
    
    # Token de refresh asociado (para invalidar)
    refresh_token_jti = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='JTI del Refresh Token',
        help_text='Identificador único del refresh token para invalidación'
    )
    
    # Información del dispositivo
    device_type = models.CharField(
        max_length=50,
        verbose_name='Tipo de Dispositivo',
        help_text='web, ios, android'
    )
    
    device_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nombre del Dispositivo'
    )
    
    # Información de ubicación (aproximada)
    ip_address = models.GenericIPAddressField(
        verbose_name='Dirección IP'
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    
    # Tiempos
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Inicio de Sesión'
    )
    
    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actividad'
    )
    
    expires_at = models.DateTimeField(
        verbose_name='Expira'
    )
    
    # Estado
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    
    class Meta:
        db_table = 'auth_user_sessions'
        verbose_name = 'Sesión de Usuario'
        verbose_name_plural = 'Sesiones de Usuario'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.email} - {self.device_type} - {self.ip_address}"
