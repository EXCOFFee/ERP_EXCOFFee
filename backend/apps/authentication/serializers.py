# ========================================================
# SISTEMA ERP UNIVERSAL - Serializers de Autenticación
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Definir serializers para la API de autenticación.
# Manejan la validación y transformación de datos entre
# JSON (API) y objetos Python (Django).
#
# Validación de Triple Capa - Esta es la Capa 2 (API/Service Layer)
# ========================================================

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import User, Role, ModulePermission, UserSession
from apps.core.validators import (
    EmailValidator,
    PhoneValidator,
    StringValidator,
    validate_required,
)
from apps.core.exceptions import (
    ValidationException,
    InvalidCredentialsException,
    AuthenticationException,
)


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Role.
    
    Propósito:
        Serializar/deserializar roles para la API.
        Incluye los permisos asociados al rol.
    
    Uso:
        - GET /api/v1/auth/roles/
        - POST /api/v1/auth/roles/
    """
    
    # Incluir permisos en la respuesta (solo lectura)
    permissions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'code',
            'description',
            'is_active',
            'permissions_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_permissions_count(self, obj: Role) -> int:
        """
        Obtiene el número de permisos del rol.
        
        Args:
            obj: Instancia de Role
        
        Returns:
            int: Cantidad de permisos
        """
        return obj.permissions.count()


class ModulePermissionSerializer(serializers.ModelSerializer):
    """
    Serializer para ModulePermission.
    
    Propósito:
        Gestionar permisos de módulo en la API.
    """
    
    # Mostrar nombres legibles en lugar de códigos
    module_display = serializers.CharField(
        source='get_module_display',
        read_only=True
    )
    action_display = serializers.CharField(
        source='get_action_display',
        read_only=True
    )
    
    class Meta:
        model = ModulePermission
        fields = [
            'id',
            'role',
            'module',
            'module_display',
            'action',
            'action_display',
        ]
        read_only_fields = ['id']


class RoleDetailSerializer(RoleSerializer):
    """
    Serializer detallado de Role con todos los permisos.
    
    Propósito:
        Mostrar el detalle completo de un rol incluyendo
        todos sus permisos. Usado en GET /api/v1/auth/roles/{id}/
    """
    
    permissions = ModulePermissionSerializer(many=True, read_only=True)
    
    class Meta(RoleSerializer.Meta):
        fields = RoleSerializer.Meta.fields + ['permissions']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo User.
    
    Propósito:
        Serializar usuarios para listados y respuestas.
        NO incluye campos sensibles como contraseña.
    
    Uso:
        - GET /api/v1/auth/users/
        - GET /api/v1/auth/users/{id}/
    """
    
    # Nombre completo calculado
    full_name = serializers.CharField(read_only=True)
    
    # Información del rol (solo lectura)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'employee_code',
            'first_name',
            'last_name',
            'full_name',
            'phone',
            'avatar',
            'is_active',
            'is_staff',
            'role',
            'role_name',
            'language',
            'timezone',
            'email_notifications',
            'push_notifications',
            'last_login',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'last_login',
            'created_at',
            'updated_at',
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear usuarios.
    
    Propósito:
        Validar y crear nuevos usuarios con contraseña.
        Implementa validación de Capa 2 (Service Layer).
    
    Uso:
        POST /api/v1/auth/users/
    
    Validaciones:
        - Email único y formato válido
        - Contraseña cumple requisitos de seguridad
        - Confirmación de contraseña coincide
        - Nombre y apellido mínimo 2 caracteres
    """
    
    # Campos de contraseña (write_only = no se retornan)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Contraseña (mínimo 10 caracteres, mayúsculas, números)'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Confirmar contraseña'
    )
    
    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'phone',
            'role',
            'employee_code',
            'language',
            'timezone',
        ]
    
    def validate_email(self, value: str) -> str:
        """
        Valida el formato y unicidad del email.
        
        Args:
            value: Email a validar
        
        Returns:
            str: Email normalizado (minúsculas)
        
        Raises:
            serializers.ValidationError: Si formato inválido o duplicado
        """
        # Validar formato
        validator = EmailValidator('email', source='Microservicio-Autenticacion')
        try:
            email = validator.validate(value)
        except ValidationException as e:
            raise serializers.ValidationError(e.message)
        
        # Verificar unicidad
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                'Ya existe un usuario con este correo electrónico'
            )
        
        return email
    
    def validate_phone(self, value: str) -> str:
        """
        Valida y normaliza número de teléfono.
        
        Args:
            value: Teléfono a validar
        
        Returns:
            str: Teléfono normalizado (solo dígitos)
        """
        if not value:
            return value
        
        validator = PhoneValidator('phone', source='Microservicio-Autenticacion')
        try:
            return validator.validate(value)
        except ValidationException as e:
            raise serializers.ValidationError(e.message)
    
    def validate_first_name(self, value: str) -> str:
        """
        Valida el nombre.
        
        Args:
            value: Nombre a validar
        
        Returns:
            str: Nombre capitalizado
        """
        validator = StringValidator(
            'first_name',
            min_length=2,
            max_length=100,
            source='Microservicio-Autenticacion'
        )
        try:
            return validator.validate(value).title()
        except ValidationException as e:
            raise serializers.ValidationError(e.message)
    
    def validate_last_name(self, value: str) -> str:
        """
        Valida el apellido.
        
        Args:
            value: Apellido a validar
        
        Returns:
            str: Apellido capitalizado
        """
        validator = StringValidator(
            'last_name',
            min_length=2,
            max_length=100,
            source='Microservicio-Autenticacion'
        )
        try:
            return validator.validate(value).title()
        except ValidationException as e:
            raise serializers.ValidationError(e.message)
    
    def validate(self, attrs: dict) -> dict:
        """
        Validación cruzada de campos (contraseñas).
        
        Args:
            attrs: Diccionario con todos los campos
        
        Returns:
            dict: Attrs validados
        
        Raises:
            serializers.ValidationError: Si contraseñas no coinciden
        """
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        # Verificar que las contraseñas coincidan
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden'
            })
        
        # Validar fortaleza de contraseña usando validadores de Django
        try:
            validate_password(password)
        except DjangoValidationError as e:
            raise serializers.ValidationError({
                'password': list(e.messages)
            })
        
        return attrs
    
    def create(self, validated_data: dict) -> User:
        """
        Crea el usuario con la contraseña hasheada.
        
        Args:
            validated_data: Datos validados
        
        Returns:
            User: Usuario creado
        """
        # Remover password_confirm (no es campo del modelo)
        validated_data.pop('password_confirm', None)
        
        # Crear usuario usando el manager personalizado
        user = User.objects.create_user(**validated_data)
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar usuarios.
    
    Propósito:
        Permitir actualización parcial de usuarios.
        NO permite cambiar contraseña (endpoint separado).
    
    Uso:
        PATCH /api/v1/auth/users/{id}/
    """
    
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone',
            'avatar',
            'role',
            'employee_code',
            'language',
            'timezone',
            'email_notifications',
            'push_notifications',
            'is_active',
        ]
    
    def validate_phone(self, value: str) -> str:
        """Valida teléfono."""
        if not value:
            return value
        validator = PhoneValidator('phone')
        try:
            return validator.validate(value)
        except ValidationException as e:
            raise serializers.ValidationError(e.message)


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para cambio de contraseña.
    
    Propósito:
        Validar cambio de contraseña de usuario autenticado.
    
    Uso:
        POST /api/v1/auth/change-password/
    """
    
    current_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Contraseña actual'
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Nueva contraseña'
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Confirmar nueva contraseña'
    )
    
    def validate_current_password(self, value: str) -> str:
        """
        Verifica que la contraseña actual sea correcta.
        
        Args:
            value: Contraseña actual proporcionada
        
        Returns:
            str: Contraseña si es correcta
        
        Raises:
            serializers.ValidationError: Si es incorrecta
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('La contraseña actual es incorrecta')
        return value
    
    def validate(self, attrs: dict) -> dict:
        """
        Valida que las nuevas contraseñas coincidan y cumplan requisitos.
        
        Args:
            attrs: Diccionario con todos los campos
        
        Returns:
            dict: Attrs validados
        """
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'Las contraseñas no coinciden'
            })
        
        # Validar fortaleza
        try:
            validate_password(new_password, self.context['request'].user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para obtener tokens JWT.
    
    Propósito:
        Extender el token JWT con claims adicionales del usuario.
        Verificar estado de la cuenta antes de emitir token.
    
    Claims adicionales:
        - email: Correo del usuario
        - full_name: Nombre completo
        - role: ID del rol
        - role_code: Código del rol
    
    Por qué:
        Permite que el frontend conozca información básica del usuario
        sin necesidad de una llamada adicional al API.
    """
    
    def validate(self, attrs: dict) -> dict:
        """
        Valida credenciales y estado de la cuenta.
        
        Args:
            attrs: email y password
        
        Returns:
            dict: Tokens y datos del usuario
        
        Raises:
            AuthenticationException: Si la cuenta está bloqueada
            InvalidCredentialsException: Si las credenciales son inválidas
        """
        # Verificar si la cuenta existe y está bloqueada
        email = attrs.get('email', '')
        try:
            user = User.objects.get(email__iexact=email)
            if user.is_account_locked():
                raise AuthenticationException(
                    message='Cuenta temporalmente bloqueada. Intente más tarde.',
                    error_code='AUTH_005'
                )
        except User.DoesNotExist:
            pass  # Dejar que la validación normal maneje el error
        
        try:
            # Validación estándar de JWT
            data = super().validate(attrs)
        except Exception:
            # Si falla, incrementar intentos fallidos
            try:
                user = User.objects.get(email__iexact=email)
                user.increment_failed_login()
            except User.DoesNotExist:
                pass
            raise
        
        # Si llegamos aquí, el login fue exitoso
        user = self.user
        user.reset_failed_login()
        
        # Agregar datos adicionales a la respuesta
        data['user'] = {
            'id': str(user.id),
            'email': user.email,
            'full_name': user.full_name,
            'role': str(user.role.id) if user.role else None,
            'role_code': user.role.code if user.role else None,
            'is_superuser': user.is_superuser,
        }
        
        return data
    
    @classmethod
    def get_token(cls, user: User):
        """
        Genera token con claims personalizados.
        
        Args:
            user: Usuario autenticado
        
        Returns:
            Token: JWT con claims adicionales
        """
        token = super().get_token(user)
        
        # Agregar claims al token
        token['email'] = user.email
        token['full_name'] = user.full_name
        if user.role:
            token['role'] = str(user.role.id)
            token['role_code'] = user.role.code
        
        return token


class UserSessionSerializer(serializers.ModelSerializer):
    """
    Serializer para sesiones de usuario.
    
    Propósito:
        Mostrar sesiones activas del usuario.
    
    Uso:
        GET /api/v1/auth/sessions/
    """
    
    class Meta:
        model = UserSession
        fields = [
            'id',
            'device_type',
            'device_name',
            'ip_address',
            'created_at',
            'last_activity',
            'is_active',
        ]
        read_only_fields = fields


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para el perfil del usuario actual.
    
    Propósito:
        Mostrar y permitir editar el perfil propio del usuario.
    
    Uso:
        GET/PATCH /api/v1/auth/profile/
    """
    
    full_name = serializers.CharField(read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone',
            'avatar',
            'role',
            'role_name',
            'permissions',
            'language',
            'timezone',
            'email_notifications',
            'push_notifications',
            'last_login',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'email',
            'role',
            'last_login',
            'created_at',
        ]
    
    def get_permissions(self, obj: User) -> list:
        """
        Obtiene la lista de permisos del usuario.
        
        Args:
            obj: Usuario
        
        Returns:
            list: Lista de permisos [{module, action}]
        """
        permissions = obj.get_all_permissions_list()
        return [
            {'module': module, 'action': action}
            for module, action in permissions
        ]
