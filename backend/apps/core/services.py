# ========================================================
# SISTEMA ERP UNIVERSAL - Servicios Base
# ========================================================
# Versión: 1.0
# Fecha: 4 de Diciembre de 2025
#
# Propósito: Clases base para servicios de negocio.
# ========================================================

from typing import Any, Dict, List, Optional, Type, TypeVar
from django.db import models, transaction
from django.core.exceptions import ValidationError


T = TypeVar('T', bound=models.Model)


class BaseService:
    """
    Clase base para servicios de negocio.
    
    Proporciona métodos comunes para operaciones CRUD y lógica de negocio.
    """
    
    model: Type[models.Model] = None
    
    @classmethod
    def get_queryset(cls) -> models.QuerySet:
        """Retorna el queryset base del modelo."""
        if cls.model is None:
            raise NotImplementedError("La clase debe definir el atributo 'model'")
        return cls.model.objects.all()
    
    @classmethod
    def get_by_id(cls, pk: Any) -> Optional[T]:
        """
        Obtiene un objeto por su ID.
        
        Args:
            pk: Primary key del objeto
            
        Returns:
            Objeto encontrado o None
        """
        try:
            return cls.get_queryset().get(pk=pk)
        except cls.model.DoesNotExist:
            return None
    
    @classmethod
    def get_all(cls, **filters) -> models.QuerySet:
        """
        Obtiene todos los objetos, opcionalmente filtrados.
        
        Args:
            **filters: Filtros a aplicar
            
        Returns:
            QuerySet filtrado
        """
        queryset = cls.get_queryset()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset
    
    @classmethod
    @transaction.atomic
    def create(cls, **data) -> T:
        """
        Crea un nuevo objeto.
        
        Args:
            **data: Datos del nuevo objeto
            
        Returns:
            Objeto creado
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        instance = cls.model(**data)
        instance.full_clean()
        instance.save()
        return instance
    
    @classmethod
    @transaction.atomic
    def update(cls, instance: T, **data) -> T:
        """
        Actualiza un objeto existente.
        
        Args:
            instance: Objeto a actualizar
            **data: Datos a actualizar
            
        Returns:
            Objeto actualizado
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        instance.full_clean()
        instance.save()
        return instance
    
    @classmethod
    @transaction.atomic
    def delete(cls, instance: T) -> bool:
        """
        Elimina un objeto.
        
        Args:
            instance: Objeto a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        instance.delete()
        return True
    
    @classmethod
    def bulk_create(cls, objects_data: List[Dict]) -> List[T]:
        """
        Crea múltiples objetos de forma eficiente.
        
        Args:
            objects_data: Lista de diccionarios con datos
            
        Returns:
            Lista de objetos creados
        """
        instances = [cls.model(**data) for data in objects_data]
        return cls.model.objects.bulk_create(instances)
    
    @classmethod
    def bulk_update(cls, instances: List[T], fields: List[str]) -> int:
        """
        Actualiza múltiples objetos de forma eficiente.
        
        Args:
            instances: Lista de objetos a actualizar
            fields: Lista de campos a actualizar
            
        Returns:
            Número de objetos actualizados
        """
        return cls.model.objects.bulk_update(instances, fields)
    
    @classmethod
    def exists(cls, **filters) -> bool:
        """
        Verifica si existe algún objeto con los filtros dados.
        
        Args:
            **filters: Filtros a aplicar
            
        Returns:
            True si existe al menos un objeto
        """
        return cls.get_queryset().filter(**filters).exists()
    
    @classmethod
    def count(cls, **filters) -> int:
        """
        Cuenta objetos que cumplen los filtros.
        
        Args:
            **filters: Filtros a aplicar
            
        Returns:
            Número de objetos
        """
        queryset = cls.get_queryset()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset.count()


class TransactionalService(BaseService):
    """
    Servicio con soporte para transacciones complejas.
    """
    
    @classmethod
    @transaction.atomic
    def execute_in_transaction(cls, func, *args, **kwargs):
        """
        Ejecuta una función dentro de una transacción.
        
        Args:
            func: Función a ejecutar
            *args: Argumentos posicionales
            **kwargs: Argumentos con nombre
            
        Returns:
            Resultado de la función
        """
        return func(*args, **kwargs)
    
    @classmethod
    def create_savepoint(cls):
        """Crea un savepoint en la transacción actual."""
        return transaction.savepoint()
    
    @classmethod
    def rollback_to_savepoint(cls, sid):
        """Hace rollback a un savepoint."""
        transaction.savepoint_rollback(sid)
    
    @classmethod
    def release_savepoint(cls, sid):
        """Libera un savepoint."""
        transaction.savepoint_commit(sid)
