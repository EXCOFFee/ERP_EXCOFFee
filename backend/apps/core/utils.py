# ========================================================
# SISTEMA ERP UNIVERSAL - Utilidades Core
# ========================================================
# Versión: 1.0
# Fecha: 4 de Diciembre de 2025
#
# Propósito: Funciones utilitarias para todo el sistema.
# ========================================================

import uuid
import hashlib
import random
import string
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List, Optional, Union

from django.utils import timezone


def generate_document_number(
    prefix: str,
    year: Optional[int] = None,
    sequence: Optional[int] = None,
    length: int = 6
) -> str:
    """
    Genera un número de documento único.
    
    Args:
        prefix: Prefijo del documento (ej: 'INV', 'PO', 'SO')
        year: Año para el documento (default: año actual)
        sequence: Número de secuencia (default: aleatorio)
        length: Longitud del número de secuencia
        
    Returns:
        Número de documento formateado (ej: 'INV-2025-000001')
    """
    if year is None:
        year = timezone.now().year
    
    if sequence is None:
        # Genera un número aleatorio único basado en timestamp y random
        timestamp = int(timezone.now().timestamp() * 1000)
        random_part = random.randint(1000, 9999)
        sequence = (timestamp % (10 ** length)) + random_part
        sequence = sequence % (10 ** length)  # Asegurar que no exceda length
    
    sequence_str = str(sequence).zfill(length)
    return f"{prefix}-{year}-{sequence_str}"


def generate_unique_code(
    prefix: str = '',
    length: int = 8,
    uppercase: bool = True
) -> str:
    """
    Genera un código único alfanumérico.
    
    Args:
        prefix: Prefijo opcional
        length: Longitud del código (sin contar prefijo)
        uppercase: Si debe ser en mayúsculas
        
    Returns:
        Código único
    """
    chars = string.ascii_uppercase + string.digits if uppercase else string.ascii_letters + string.digits
    code = ''.join(random.choices(chars, k=length))
    return f"{prefix}{code}" if prefix else code


def generate_uuid() -> str:
    """
    Genera un UUID único.
    
    Returns:
        UUID como string
    """
    return str(uuid.uuid4())


def generate_short_uuid(length: int = 8) -> str:
    """
    Genera un UUID corto.
    
    Args:
        length: Longitud deseada
        
    Returns:
        UUID corto
    """
    return str(uuid.uuid4()).replace('-', '')[:length].upper()


def format_currency(
    amount: Union[Decimal, float, int],
    currency: str = 'MXN',
    decimal_places: int = 2
) -> str:
    """
    Formatea un monto como moneda.
    
    Args:
        amount: Monto a formatear
        currency: Código de moneda
        decimal_places: Número de decimales
        
    Returns:
        Monto formateado (ej: '$1,234.56 MXN')
    """
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    
    quantize_str = '0.' + '0' * decimal_places
    amount = amount.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)
    
    # Formatear con separador de miles
    integer_part = int(amount)
    decimal_part = str(amount).split('.')[-1] if '.' in str(amount) else '00'
    
    formatted_int = '{:,}'.format(integer_part)
    
    return f"${formatted_int}.{decimal_part} {currency}"


def round_decimal(
    value: Union[Decimal, float],
    decimal_places: int = 2
) -> Decimal:
    """
    Redondea un valor decimal.
    
    Args:
        value: Valor a redondear
        decimal_places: Número de decimales
        
    Returns:
        Valor redondeado
    """
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    
    quantize_str = '0.' + '0' * decimal_places
    return value.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)


def calculate_percentage(
    value: Union[Decimal, float],
    percentage: Union[Decimal, float]
) -> Decimal:
    """
    Calcula un porcentaje de un valor.
    
    Args:
        value: Valor base
        percentage: Porcentaje a calcular
        
    Returns:
        Resultado del cálculo
    """
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    if not isinstance(percentage, Decimal):
        percentage = Decimal(str(percentage))
    
    return round_decimal(value * percentage / 100)


def calculate_tax(
    subtotal: Union[Decimal, float],
    tax_rate: Union[Decimal, float] = Decimal('16.00')
) -> Dict[str, Decimal]:
    """
    Calcula impuestos sobre un subtotal.
    
    Args:
        subtotal: Subtotal antes de impuestos
        tax_rate: Tasa de impuesto (default: 16% IVA)
        
    Returns:
        Diccionario con subtotal, impuesto y total
    """
    if not isinstance(subtotal, Decimal):
        subtotal = Decimal(str(subtotal))
    if not isinstance(tax_rate, Decimal):
        tax_rate = Decimal(str(tax_rate))
    
    tax_amount = round_decimal(subtotal * tax_rate / 100)
    total = subtotal + tax_amount
    
    return {
        'subtotal': subtotal,
        'tax_rate': tax_rate,
        'tax_amount': tax_amount,
        'total': total
    }


def date_range(
    start_date: date,
    end_date: date,
    include_end: bool = True
) -> List[date]:
    """
    Genera un rango de fechas.
    
    Args:
        start_date: Fecha inicial
        end_date: Fecha final
        include_end: Si incluir la fecha final
        
    Returns:
        Lista de fechas
    """
    from datetime import timedelta
    
    dates = []
    current = start_date
    end = end_date if include_end else end_date - timedelta(days=1)
    
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)
    
    return dates


def get_fiscal_year(reference_date: Optional[date] = None) -> Dict[str, date]:
    """
    Obtiene el año fiscal basado en una fecha.
    
    Args:
        reference_date: Fecha de referencia (default: hoy)
        
    Returns:
        Diccionario con inicio y fin del año fiscal
    """
    if reference_date is None:
        reference_date = timezone.now().date()
    
    # Asumiendo año fiscal = año calendario (ajustar según país)
    year = reference_date.year
    
    return {
        'start': date(year, 1, 1),
        'end': date(year, 12, 31),
        'year': year
    }


def get_quarter(reference_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Obtiene el trimestre basado en una fecha.
    
    Args:
        reference_date: Fecha de referencia (default: hoy)
        
    Returns:
        Diccionario con información del trimestre
    """
    if reference_date is None:
        reference_date = timezone.now().date()
    
    month = reference_date.month
    year = reference_date.year
    
    quarter = (month - 1) // 3 + 1
    
    quarter_starts = {1: 1, 2: 4, 3: 7, 4: 10}
    quarter_ends = {1: 3, 2: 6, 3: 9, 4: 12}
    
    start_month = quarter_starts[quarter]
    end_month = quarter_ends[quarter]
    
    # Último día del mes final del trimestre
    if end_month == 12:
        end_day = 31
    elif end_month in [4, 6, 9, 11]:
        end_day = 30
    else:
        end_day = 31
    
    return {
        'quarter': quarter,
        'year': year,
        'start': date(year, start_month, 1),
        'end': date(year, end_month, end_day),
        'label': f"Q{quarter} {year}"
    }


def slugify_text(text: str, separator: str = '-') -> str:
    """
    Convierte texto a formato slug.
    
    Args:
        text: Texto a convertir
        separator: Separador a usar
        
    Returns:
        Texto en formato slug
    """
    import re
    import unicodedata
    
    # Normalizar unicode
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Convertir a minúsculas
    text = text.lower()
    
    # Reemplazar espacios y caracteres especiales
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', separator, text)
    text = re.sub(r'-+', separator, text)
    
    return text.strip(separator)


def mask_string(
    text: str,
    visible_chars: int = 4,
    mask_char: str = '*',
    position: str = 'end'
) -> str:
    """
    Enmascara parcialmente un string.
    
    Args:
        text: Texto a enmascarar
        visible_chars: Número de caracteres visibles
        mask_char: Carácter de máscara
        position: 'start' o 'end' para posición de caracteres visibles
        
    Returns:
        Texto enmascarado
    """
    if len(text) <= visible_chars:
        return text
    
    mask_length = len(text) - visible_chars
    mask = mask_char * mask_length
    
    if position == 'start':
        return text[:visible_chars] + mask
    else:
        return mask + text[-visible_chars:]


def hash_string(text: str, algorithm: str = 'sha256') -> str:
    """
    Genera hash de un string.
    
    Args:
        text: Texto a hashear
        algorithm: Algoritmo de hash
        
    Returns:
        Hash como string hexadecimal
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode('utf-8'))
    return hash_obj.hexdigest()


def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """
    Combina dos diccionarios de forma recursiva.
    
    Args:
        dict1: Diccionario base
        dict2: Diccionario a mezclar
        
    Returns:
        Diccionario combinado
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def safe_get(data: Dict, *keys, default: Any = None) -> Any:
    """
    Obtiene un valor anidado de un diccionario de forma segura.
    
    Args:
        data: Diccionario fuente
        *keys: Secuencia de claves
        default: Valor por defecto si no existe
        
    Returns:
        Valor encontrado o default
    """
    result = data
    
    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default
    
    return result
