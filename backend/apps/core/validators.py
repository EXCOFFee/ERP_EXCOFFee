# ========================================================
# SISTEMA ERP UNIVERSAL - Validadores Reutilizables
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Centralizar validadores de datos reutilizables.
# Cumple con el principio DRY y el requisito de validación
# en triple capa (8.2 del SRS).
#
# Uso: Estos validadores se usan en la Capa 2 (Service Layer)
# ========================================================

import re
from decimal import Decimal, InvalidOperation
from typing import Any, Optional, List
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .exceptions import (
    ValidationException,
    RequiredFieldException,
    InvalidFormatException,
)


class BaseValidator:
    """
    Clase base para todos los validadores.
    
    Propósito:
        Proporcionar una interfaz común para validadores.
    
    Por qué clase base:
        - Permite polimorfismo (Liskov Substitution)
        - Facilita testing
        - Interfaz consistente
    """
    
    def __init__(self, field_name: str, source: str = 'Validator'):
        """
        Inicializa el validador.
        
        Args:
            field_name: Nombre del campo que se valida
            source: Componente/microservicio origen
        """
        self.field_name = field_name
        self.source = source
    
    def validate(self, value: Any) -> Any:
        """
        Método principal de validación a implementar.
        
        Args:
            value: Valor a validar
        
        Returns:
            Valor validado (puede ser transformado)
        
        Raises:
            ValidationException: Si la validación falla
        """
        raise NotImplementedError("Subclases deben implementar validate()")


class RequiredValidator(BaseValidator):
    """
    Valida que un campo no esté vacío.
    
    Propósito:
        Verificar que campos obligatorios tengan valor.
    
    Uso:
        validator = RequiredValidator('nombre')
        validator.validate(valor)
    """
    
    def validate(self, value: Any) -> Any:
        """
        Valida que el valor no sea None, vacío o solo espacios.
        
        Args:
            value: Valor a validar
        
        Returns:
            Valor original si es válido
        
        Raises:
            RequiredFieldException: Si el valor está vacío
        """
        # Verificar None
        if value is None:
            raise RequiredFieldException(
                field=self.field_name,
                source=self.source
            )
        
        # Verificar strings vacíos
        if isinstance(value, str) and not value.strip():
            raise RequiredFieldException(
                field=self.field_name,
                source=self.source
            )
        
        # Verificar listas/dicts vacíos
        if isinstance(value, (list, dict)) and len(value) == 0:
            raise RequiredFieldException(
                field=self.field_name,
                source=self.source
            )
        
        return value


class EmailValidator(BaseValidator):
    """
    Valida formato de correo electrónico.
    
    Propósito:
        Asegurar que los emails tengan formato válido.
    
    Patrón utilizado:
        RFC 5322 simplificado para casos comunes.
    """
    
    # Patrón de email - Cubre la mayoría de casos válidos
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    def validate(self, value: Any) -> str:
        """
        Valida formato de email.
        
        Args:
            value: Email a validar
        
        Returns:
            Email en minúsculas (normalizado)
        
        Raises:
            InvalidFormatException: Si el formato es inválido
        """
        if value is None:
            return value
        
        email = str(value).strip().lower()
        
        if not self.EMAIL_PATTERN.match(email):
            raise InvalidFormatException(
                message=f'Formato de email inválido: {value}',
                field=self.field_name,
                source=self.source,
                solution_hint='Use el formato: usuario@dominio.com'
            )
        
        return email


class PhoneValidator(BaseValidator):
    """
    Valida formato de número telefónico.
    
    Propósito:
        Normalizar y validar números de teléfono.
    
    Formatos aceptados:
        - +52 55 1234 5678
        - 5512345678
        - (55) 1234-5678
    """
    
    # Solo dígitos después de limpiar
    PHONE_PATTERN = re.compile(r'^\d{10,15}$')
    
    def validate(self, value: Any) -> str:
        """
        Valida y normaliza número telefónico.
        
        Args:
            value: Número a validar
        
        Returns:
            Número solo con dígitos
        
        Raises:
            InvalidFormatException: Si el formato es inválido
        """
        if value is None:
            return value
        
        # Remover todo excepto dígitos
        phone = re.sub(r'[^\d]', '', str(value))
        
        if not self.PHONE_PATTERN.match(phone):
            raise InvalidFormatException(
                message=f'Formato de teléfono inválido: {value}',
                field=self.field_name,
                source=self.source,
                solution_hint='El teléfono debe tener entre 10 y 15 dígitos'
            )
        
        return phone


class DecimalValidator(BaseValidator):
    """
    Valida campos numéricos decimales.
    
    Propósito:
        Validar montos, precios, cantidades con decimales.
    
    Por qué Decimal y no float:
        Precisión financiera - float tiene errores de redondeo
        Ej: 0.1 + 0.2 = 0.30000000000000004 en float
    """
    
    def __init__(
        self,
        field_name: str,
        source: str = 'Validator',
        min_value: Optional[Decimal] = None,
        max_value: Optional[Decimal] = None,
        max_decimals: int = 2,
        allow_negative: bool = False
    ):
        """
        Inicializa el validador decimal.
        
        Args:
            field_name: Nombre del campo
            source: Componente origen
            min_value: Valor mínimo permitido
            max_value: Valor máximo permitido
            max_decimals: Máximo de decimales permitidos
            allow_negative: Si permite valores negativos
        """
        super().__init__(field_name, source)
        self.min_value = min_value
        self.max_value = max_value
        self.max_decimals = max_decimals
        self.allow_negative = allow_negative
    
    def validate(self, value: Any) -> Optional[Decimal]:
        """
        Valida y convierte a Decimal.
        
        Args:
            value: Valor numérico a validar
        
        Returns:
            Decimal validado
        
        Raises:
            InvalidFormatException: Si el formato o valor es inválido
        """
        if value is None:
            return None
        
        # Intentar convertir a Decimal
        try:
            decimal_value = Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise InvalidFormatException(
                message=f'"{value}" no es un número válido',
                field=self.field_name,
                source=self.source
            )
        
        # Verificar negativos
        if not self.allow_negative and decimal_value < 0:
            raise ValidationException(
                message=f'El campo "{self.field_name}" no puede ser negativo',
                field=self.field_name,
                source=self.source
            )
        
        # Verificar mínimo
        if self.min_value is not None and decimal_value < self.min_value:
            raise ValidationException(
                message=f'El valor mínimo para "{self.field_name}" es {self.min_value}',
                field=self.field_name,
                source=self.source
            )
        
        # Verificar máximo
        if self.max_value is not None and decimal_value > self.max_value:
            raise ValidationException(
                message=f'El valor máximo para "{self.field_name}" es {self.max_value}',
                field=self.field_name,
                source=self.source
            )
        
        # Verificar decimales
        decimal_places = abs(decimal_value.as_tuple().exponent)
        if decimal_places > self.max_decimals:
            raise ValidationException(
                message=f'"{self.field_name}" no puede tener más de {self.max_decimals} decimales',
                field=self.field_name,
                source=self.source
            )
        
        return decimal_value


class IntegerValidator(BaseValidator):
    """
    Valida campos numéricos enteros.
    
    Propósito:
        Validar cantidades, IDs, y otros valores enteros.
    """
    
    def __init__(
        self,
        field_name: str,
        source: str = 'Validator',
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        allow_negative: bool = False
    ):
        super().__init__(field_name, source)
        self.min_value = min_value
        self.max_value = max_value
        self.allow_negative = allow_negative
    
    def validate(self, value: Any) -> Optional[int]:
        """
        Valida y convierte a entero.
        
        Args:
            value: Valor a validar
        
        Returns:
            Entero validado
        
        Raises:
            InvalidFormatException: Si el formato es inválido
        """
        if value is None:
            return None
        
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise InvalidFormatException(
                message=f'"{value}" no es un número entero válido',
                field=self.field_name,
                source=self.source
            )
        
        if not self.allow_negative and int_value < 0:
            raise ValidationException(
                message=f'El campo "{self.field_name}" no puede ser negativo',
                field=self.field_name,
                source=self.source
            )
        
        if self.min_value is not None and int_value < self.min_value:
            raise ValidationException(
                message=f'El valor mínimo para "{self.field_name}" es {self.min_value}',
                field=self.field_name,
                source=self.source
            )
        
        if self.max_value is not None and int_value > self.max_value:
            raise ValidationException(
                message=f'El valor máximo para "{self.field_name}" es {self.max_value}',
                field=self.field_name,
                source=self.source
            )
        
        return int_value


class StringValidator(BaseValidator):
    """
    Valida campos de texto.
    
    Propósito:
        Validar longitud, caracteres permitidos y patrones de texto.
    """
    
    def __init__(
        self,
        field_name: str,
        source: str = 'Validator',
        min_length: int = 0,
        max_length: int = 255,
        pattern: Optional[str] = None,
        pattern_message: Optional[str] = None,
        strip: bool = True,
        to_upper: bool = False,
        to_lower: bool = False
    ):
        super().__init__(field_name, source)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if pattern else None
        self.pattern_message = pattern_message
        self.strip = strip
        self.to_upper = to_upper
        self.to_lower = to_lower
    
    def validate(self, value: Any) -> Optional[str]:
        """
        Valida y normaliza texto.
        
        Args:
            value: Texto a validar
        
        Returns:
            Texto validado y normalizado
        
        Raises:
            ValidationException: Si la validación falla
        """
        if value is None:
            return None
        
        text = str(value)
        
        # Aplicar transformaciones
        if self.strip:
            text = text.strip()
        if self.to_upper:
            text = text.upper()
        if self.to_lower:
            text = text.lower()
        
        # Verificar longitud mínima
        if len(text) < self.min_length:
            raise ValidationException(
                message=f'"{self.field_name}" debe tener al menos {self.min_length} caracteres',
                field=self.field_name,
                source=self.source
            )
        
        # Verificar longitud máxima
        if len(text) > self.max_length:
            raise ValidationException(
                message=f'"{self.field_name}" no puede exceder {self.max_length} caracteres',
                field=self.field_name,
                source=self.source
            )
        
        # Verificar patrón
        if self.pattern and not self.pattern.match(text):
            message = self.pattern_message or f'Formato inválido para "{self.field_name}"'
            raise InvalidFormatException(
                message=message,
                field=self.field_name,
                source=self.source
            )
        
        return text


class ChoiceValidator(BaseValidator):
    """
    Valida que el valor esté entre opciones permitidas.
    
    Propósito:
        Validar campos de selección (status, tipo, etc.)
    """
    
    def __init__(
        self,
        field_name: str,
        choices: List[Any],
        source: str = 'Validator'
    ):
        super().__init__(field_name, source)
        self.choices = choices
    
    def validate(self, value: Any) -> Any:
        """
        Valida que el valor esté en las opciones permitidas.
        
        Args:
            value: Valor a validar
        
        Returns:
            Valor validado
        
        Raises:
            ValidationException: Si el valor no está en las opciones
        """
        if value is None:
            return None
        
        if value not in self.choices:
            raise ValidationException(
                message=f'"{value}" no es una opción válida para "{self.field_name}". Opciones: {self.choices}',
                field=self.field_name,
                source=self.source,
                solution_hint=f'Use una de las siguientes opciones: {", ".join(str(c) for c in self.choices)}'
            )
        
        return value


class RFCValidator(BaseValidator):
    """
    Valida formato de RFC mexicano.
    
    Propósito:
        Validar RFC para facturas y requisitos fiscales.
    
    Formatos:
        - Persona física: 4 letras + 6 dígitos + 3 caracteres
        - Persona moral: 3 letras + 6 dígitos + 3 caracteres
    """
    
    RFC_PATTERN = re.compile(
        r'^[A-ZÑ&]{3,4}\d{6}[A-V1-9][0-9A-Z][0-9A]$'
    )
    
    def validate(self, value: Any) -> Optional[str]:
        """
        Valida formato de RFC.
        
        Args:
            value: RFC a validar
        
        Returns:
            RFC en mayúsculas
        
        Raises:
            InvalidFormatException: Si el formato es inválido
        """
        if value is None:
            return None
        
        rfc = str(value).strip().upper()
        
        if not self.RFC_PATTERN.match(rfc):
            raise InvalidFormatException(
                message=f'Formato de RFC inválido: {value}',
                field=self.field_name,
                source=self.source,
                solution_hint='RFC debe tener formato: AAAA000000XXX (persona física) o AAA000000XXX (persona moral)'
            )
        
        return rfc


class CURPValidator(BaseValidator):
    """
    Valida formato de CURP mexicana.
    
    Propósito:
        Validar CURP para identificación de empleados.
    """
    
    CURP_PATTERN = re.compile(
        r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$'
    )
    
    def validate(self, value: Any) -> Optional[str]:
        """
        Valida formato de CURP.
        
        Args:
            value: CURP a validar
        
        Returns:
            CURP en mayúsculas
        
        Raises:
            InvalidFormatException: Si el formato es inválido
        """
        if value is None:
            return None
        
        curp = str(value).strip().upper()
        
        if not self.CURP_PATTERN.match(curp):
            raise InvalidFormatException(
                message=f'Formato de CURP inválido: {value}',
                field=self.field_name,
                source=self.source,
                solution_hint='CURP debe tener 18 caracteres en formato estándar'
            )
        
        return curp


# ========================================================
# FUNCIONES DE VALIDACIÓN RÁPIDA
# ========================================================
# Para uso directo sin instanciar clases

def validate_required(value: Any, field_name: str) -> Any:
    """Valida que un campo no esté vacío."""
    return RequiredValidator(field_name).validate(value)


def validate_email(value: Any, field_name: str = 'email') -> str:
    """Valida formato de email."""
    return EmailValidator(field_name).validate(value)


def validate_phone(value: Any, field_name: str = 'telefono') -> str:
    """Valida formato de teléfono."""
    return PhoneValidator(field_name).validate(value)


def validate_positive_decimal(
    value: Any,
    field_name: str,
    max_decimals: int = 2
) -> Decimal:
    """Valida decimal positivo."""
    return DecimalValidator(
        field_name,
        min_value=Decimal('0'),
        max_decimals=max_decimals
    ).validate(value)


def validate_positive_integer(value: Any, field_name: str) -> int:
    """Valida entero positivo."""
    return IntegerValidator(field_name, min_value=0).validate(value)
