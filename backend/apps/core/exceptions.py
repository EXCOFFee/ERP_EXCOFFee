# ========================================================
# SISTEMA ERP UNIVERSAL - Excepciones Personalizadas
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Definir excepciones personalizadas y un manejador
# de excepciones que cumple con los requisitos de validación
# y mensajes de error detallados (Sección 8.2 del SRS).
#
# Formato de error estándar:
# {
#   "error_code": "INV_001",
#   "message": "Descripción del error",
#   "source": "Microservicio-Inventario",
#   "field": "quantity",
#   "solution_hint": "Sugerencia para resolver"
# }
# ========================================================

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
import logging

# Logger para registrar excepciones
logger = logging.getLogger(__name__)


# ========================================================
# EXCEPCIONES BASE
# ========================================================

class ERPBaseException(Exception):
    """
    Excepción base para todas las excepciones del ERP.
    
    Propósito:
        Proporcionar una estructura consistente para todos los errores
        del sistema, incluyendo código, mensaje, fuente y sugerencia.
    
    Atributos:
        error_code (str): Código único del error (ej. "INV_001")
        message (str): Descripción legible del error
        source (str): Microservicio o componente donde ocurrió
        field (str): Campo específico que causó el error (opcional)
        solution_hint (str): Sugerencia para resolver el problema
        http_status (int): Código HTTP a retornar
    
    Por qué:
        Cumple con requisito 8.2 - Los errores deben indicar con precisión
        dónde ocurrió el problema y la razón para facilitar el diagnóstico.
    """
    
    error_code = 'ERP_000'
    message = 'Error interno del sistema'
    source = 'ERP-Core'
    field = None
    solution_hint = 'Contacte al administrador del sistema'
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def __init__(
        self,
        message: str = None,
        error_code: str = None,
        source: str = None,
        field: str = None,
        solution_hint: str = None,
        **kwargs
    ):
        """
        Inicializa la excepción con los parámetros proporcionados.
        
        Args:
            message: Descripción del error (sobrescribe el default de clase)
            error_code: Código único del error
            source: Componente origen del error
            field: Campo que causó el error
            solution_hint: Sugerencia de solución
            **kwargs: Argumentos adicionales para formateo del mensaje
        """
        if message:
            self.message = message
        if error_code:
            self.error_code = error_code
        if source:
            self.source = source
        if field:
            self.field = field
        if solution_hint:
            self.solution_hint = solution_hint
        
        # Permitir formateo de mensaje con kwargs
        if kwargs:
            self.message = self.message.format(**kwargs)
        
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """
        Convierte la excepción a diccionario para respuesta JSON.
        
        Returns:
            dict: Diccionario con estructura estándar de error
        """
        error_dict = {
            'error_code': self.error_code,
            'message': self.message,
            'source': self.source,
            'solution_hint': self.solution_hint,
        }
        if self.field:
            error_dict['field'] = self.field
        return error_dict


# ========================================================
# EXCEPCIONES DE VALIDACIÓN
# ========================================================

class ValidationException(ERPBaseException):
    """
    Excepción para errores de validación de datos.
    
    Propósito:
        Indicar que los datos proporcionados no cumplen con
        las reglas de validación del sistema.
    
    Uso:
        raise ValidationException(
            message="El precio no puede ser negativo",
            field="price",
            source="Microservicio-Inventario"
        )
    """
    error_code = 'VAL_001'
    message = 'Error de validación de datos'
    source = 'Validation-Layer'
    http_status = status.HTTP_400_BAD_REQUEST


class RequiredFieldException(ValidationException):
    """
    Excepción cuando falta un campo requerido.
    """
    error_code = 'VAL_002'
    message = 'El campo "{field}" es requerido'
    solution_hint = 'Proporcione un valor para el campo requerido'


class InvalidFormatException(ValidationException):
    """
    Excepción para formato de datos inválido.
    """
    error_code = 'VAL_003'
    message = 'Formato inválido para el campo "{field}"'
    solution_hint = 'Verifique el formato esperado del campo'


class DuplicateValueException(ValidationException):
    """
    Excepción cuando se intenta crear un registro duplicado.
    """
    error_code = 'VAL_004'
    message = 'Ya existe un registro con este valor para "{field}"'
    http_status = status.HTTP_409_CONFLICT
    solution_hint = 'Use un valor único o actualice el registro existente'


# ========================================================
# EXCEPCIONES DE AUTENTICACIÓN
# ========================================================

class AuthenticationException(ERPBaseException):
    """
    Excepción para errores de autenticación.
    """
    error_code = 'AUTH_001'
    message = 'Error de autenticación'
    source = 'Microservicio-Autenticacion'
    http_status = status.HTTP_401_UNAUTHORIZED
    solution_hint = 'Verifique sus credenciales o inicie sesión nuevamente'


class InvalidCredentialsException(AuthenticationException):
    """
    Excepción para credenciales inválidas.
    """
    error_code = 'AUTH_002'
    message = 'Credenciales inválidas'
    solution_hint = 'Verifique su usuario y contraseña'


class TokenExpiredException(AuthenticationException):
    """
    Excepción cuando el token JWT ha expirado.
    """
    error_code = 'AUTH_003'
    message = 'El token de autenticación ha expirado'
    solution_hint = 'Utilice el refresh token para obtener un nuevo access token'


class InsufficientPermissionsException(ERPBaseException):
    """
    Excepción cuando el usuario no tiene permisos suficientes.
    """
    error_code = 'AUTH_004'
    message = 'No tiene permisos para realizar esta acción'
    source = 'Microservicio-Autenticacion'
    http_status = status.HTTP_403_FORBIDDEN
    solution_hint = 'Contacte al administrador para solicitar permisos'


# ========================================================
# EXCEPCIONES DE INVENTARIO
# ========================================================

class InventoryException(ERPBaseException):
    """
    Excepción base para el módulo de inventario.
    """
    error_code = 'INV_000'
    message = 'Error en el módulo de inventario'
    source = 'Microservicio-Inventario'


class InsufficientStockException(InventoryException):
    """
    Excepción cuando no hay suficiente stock disponible.
    
    Por qué es importante:
        RF1 - El sistema debe validar automáticamente la disponibilidad
        de inventario al crear órdenes de venta.
    """
    error_code = 'INV_001'
    message = 'Stock insuficiente para el producto "{product}". Cantidad solicitada: {requested}, disponible: {available}'
    http_status = status.HTTP_400_BAD_REQUEST
    solution_hint = 'Ajuste la cantidad o inicie una orden de compra'


class ProductNotFoundException(InventoryException):
    """
    Excepción cuando no se encuentra un producto.
    """
    error_code = 'INV_002'
    message = 'Producto no encontrado: {product_id}'
    http_status = status.HTTP_404_NOT_FOUND
    solution_hint = 'Verifique el código o ID del producto'


class WarehouseNotFoundException(InventoryException):
    """
    Excepción cuando no se encuentra un almacén.
    """
    error_code = 'INV_003'
    message = 'Almacén no encontrado: {warehouse_id}'
    http_status = status.HTTP_404_NOT_FOUND


class InvalidTransferException(InventoryException):
    """
    Excepción para transferencias de inventario inválidas.
    """
    error_code = 'INV_004'
    message = 'Transferencia de inventario inválida: {reason}'
    http_status = status.HTTP_400_BAD_REQUEST


# ========================================================
# EXCEPCIONES DE VENTAS
# ========================================================

class SalesException(ERPBaseException):
    """
    Excepción base para el módulo de ventas.
    """
    error_code = 'SAL_000'
    message = 'Error en el módulo de ventas'
    source = 'Microservicio-Ventas'


class OrderNotFoundException(SalesException):
    """
    Excepción cuando no se encuentra una orden.
    """
    error_code = 'SAL_001'
    message = 'Orden de venta no encontrada: {order_id}'
    http_status = status.HTTP_404_NOT_FOUND


class InvalidOrderStateException(SalesException):
    """
    Excepción para transiciones de estado inválidas.
    """
    error_code = 'SAL_002'
    message = 'No se puede cambiar el estado de "{current}" a "{target}"'
    http_status = status.HTTP_400_BAD_REQUEST
    solution_hint = 'Verifique el flujo de estados permitido'


class CustomerNotFoundException(SalesException):
    """
    Excepción cuando no se encuentra un cliente.
    """
    error_code = 'SAL_003'
    message = 'Cliente no encontrado: {customer_id}'
    http_status = status.HTTP_404_NOT_FOUND


# ========================================================
# EXCEPCIONES DE FINANZAS
# ========================================================

class FinanceException(ERPBaseException):
    """
    Excepción base para el módulo de finanzas.
    """
    error_code = 'FIN_000'
    message = 'Error en el módulo de finanzas'
    source = 'Microservicio-Finanzas'


class UnbalancedJournalEntryException(FinanceException):
    """
    Excepción cuando un asiento contable no está balanceado.
    
    Por qué:
        Principio contable fundamental: Débitos = Créditos
    """
    error_code = 'FIN_001'
    message = 'El asiento contable no está balanceado. Débitos: {debits}, Créditos: {credits}'
    http_status = status.HTTP_400_BAD_REQUEST
    solution_hint = 'Asegúrese de que la suma de débitos sea igual a la suma de créditos'


class AccountNotFoundException(FinanceException):
    """
    Excepción cuando no se encuentra una cuenta contable.
    """
    error_code = 'FIN_002'
    message = 'Cuenta contable no encontrada: {account_code}'
    http_status = status.HTTP_404_NOT_FOUND


class FiscalPeriodClosedException(FinanceException):
    """
    Excepción cuando se intenta modificar un período fiscal cerrado.
    """
    error_code = 'FIN_003'
    message = 'El período fiscal "{period}" está cerrado y no permite modificaciones'
    http_status = status.HTTP_400_BAD_REQUEST
    solution_hint = 'Contacte al contador para reabrir el período si es necesario'


# ========================================================
# EXCEPCIONES DE RRHH
# ========================================================

class HRException(ERPBaseException):
    """
    Excepción base para el módulo de recursos humanos.
    """
    error_code = 'HR_000'
    message = 'Error en el módulo de recursos humanos'
    source = 'Microservicio-RRHH'


class EmployeeNotFoundException(HRException):
    """
    Excepción cuando no se encuentra un empleado.
    """
    error_code = 'HR_001'
    message = 'Empleado no encontrado: {employee_id}'
    http_status = status.HTTP_404_NOT_FOUND


class InsufficientLeaveDaysException(HRException):
    """
    Excepción cuando no hay suficientes días de licencia.
    
    RF4: El sistema debe calcular automáticamente los días restantes.
    """
    error_code = 'HR_002'
    message = 'Días de licencia insuficientes. Solicitados: {requested}, disponibles: {available}'
    http_status = status.HTTP_400_BAD_REQUEST
    solution_hint = 'Solicite menos días o espere a que se acumulen más'


# ========================================================
# EXCEPCIONES DE COMPRAS
# ========================================================

class PurchaseException(ERPBaseException):
    """
    Excepción base para el módulo de compras.
    """
    error_code = 'PUR_000'
    message = 'Error en el módulo de compras'
    source = 'Microservicio-Compras'


class SupplierNotFoundException(PurchaseException):
    """
    Excepción cuando no se encuentra un proveedor.
    """
    error_code = 'PUR_001'
    message = 'Proveedor no encontrado: {supplier_id}'
    http_status = status.HTTP_404_NOT_FOUND


class PurchaseOrderNotFoundException(PurchaseException):
    """
    Excepción cuando no se encuentra una orden de compra.
    """
    error_code = 'PUR_002'
    message = 'Orden de compra no encontrada: {order_id}'
    http_status = status.HTTP_404_NOT_FOUND


# ========================================================
# MANEJADOR DE EXCEPCIONES PERSONALIZADO
# ========================================================

def custom_exception_handler(exc, context):
    """
    Manejador de excepciones personalizado para Django REST Framework.
    
    Propósito:
        Convertir todas las excepciones al formato estándar de error del ERP.
        Garantiza que todas las respuestas de error sean consistentes.
    
    Args:
        exc: La excepción lanzada
        context: Contexto de la vista (request, view, args, kwargs)
    
    Returns:
        Response: Respuesta HTTP con el error formateado
    
    Por qué:
        Requisito 8.2 - Mensajes de error detallados que indican dónde
        y por qué ocurrió el problema.
    """
    # Primero, obtener la respuesta estándar de DRF
    response = exception_handler(exc, context)
    
    # Obtener información del contexto para el logging
    view = context.get('view', None)
    request = context.get('request', None)
    view_name = view.__class__.__name__ if view else 'Unknown'
    
    # Si es una excepción ERP personalizada
    if isinstance(exc, ERPBaseException):
        logger.warning(
            f"ERP Exception in {view_name}: {exc.error_code} - {exc.message}",
            extra={
                'error_code': exc.error_code,
                'source': exc.source,
                'user': getattr(request, 'user', None),
            }
        )
        return Response(
            exc.to_dict(),
            status=exc.http_status
        )
    
    # Si es una ValidationError de Django
    if isinstance(exc, DjangoValidationError):
        logger.warning(f"Django ValidationError in {view_name}: {exc}")
        return Response(
            {
                'error_code': 'VAL_000',
                'message': str(exc),
                'source': view_name,
                'solution_hint': 'Verifique los datos enviados',
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Si es un 404
    if isinstance(exc, Http404):
        return Response(
            {
                'error_code': 'NOT_FOUND',
                'message': 'Recurso no encontrado',
                'source': view_name,
                'solution_hint': 'Verifique que el ID o recurso exista',
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Para otras excepciones, usar respuesta de DRF pero formatear
    if response is not None:
        # Transformar al formato estándar
        original_data = response.data
        
        # Manejar errores de campo específicos de DRF
        if isinstance(original_data, dict):
            # Si hay errores por campo
            field_errors = []
            for field, errors in original_data.items():
                if isinstance(errors, list):
                    for error in errors:
                        field_errors.append(f"{field}: {error}")
                else:
                    field_errors.append(f"{field}: {errors}")
            
            response.data = {
                'error_code': 'API_ERROR',
                'message': '; '.join(field_errors) if field_errors else str(original_data),
                'source': view_name,
                'solution_hint': 'Verifique los datos enviados',
                'details': original_data,
            }
        
        return response
    
    # Si no hay respuesta (error no manejado), crear una genérica
    logger.error(f"Unhandled exception in {view_name}: {exc}", exc_info=True)
    return Response(
        {
            'error_code': 'INTERNAL_ERROR',
            'message': 'Error interno del servidor',
            'source': view_name,
            'solution_hint': 'Contacte al administrador del sistema',
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
