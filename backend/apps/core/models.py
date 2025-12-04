# ========================================================
# SISTEMA ERP UNIVERSAL - Modelos Base
# ========================================================
# Versión: 1.0
# Fecha: 30 de Noviembre de 2025
#
# Propósito: Definir modelos abstractos reutilizables por todos
# los microservicios. Implementa el principio DRY al centralizar
# campos comunes como timestamps y soft delete.
#
# Principios aplicados:
# - DRY: Campos comunes definidos una sola vez
# - SRP: Cada mixin tiene una sola responsabilidad
# - OCP: Extensible sin modificar código existente
# ========================================================

import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings


class TimeStampedModel(models.Model):
    """
    Modelo abstracto que agrega campos de auditoría de tiempo.
    
    Propósito:
        Registrar automáticamente cuándo se creó y modificó cada registro.
        Esencial para auditoría y debugging.
    
    Campos:
        created_at: Fecha y hora de creación (auto)
        updated_at: Fecha y hora de última modificación (auto)
    
    Por qué es abstracto:
        No crea una tabla propia, solo proporciona campos heredables.
        Esto evita JOINs innecesarios y mejora el rendimiento.
    
    Uso:
        class MiModelo(TimeStampedModel):
            nombre = models.CharField(max_length=100)
    """
    
    # Fecha de creación - Se establece automáticamente al crear
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación',
        help_text='Fecha y hora en que se creó este registro'
    )
    
    # Fecha de última modificación - Se actualiza en cada save()
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Modificación',
        help_text='Fecha y hora de la última modificación'
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']  # Más recientes primero por defecto


class SoftDeleteManager(models.Manager):
    """
    Manager personalizado para filtrar registros eliminados (soft delete).
    
    Propósito:
        Ocultar automáticamente los registros marcados como eliminados
        en las consultas normales.
    
    Por qué Soft Delete:
        - Permite recuperar datos eliminados accidentalmente
        - Mantiene integridad referencial para reportes históricos
        - Cumple con requisitos de auditoría
    
    Uso:
        MiModelo.objects.all()          # Solo activos
        MiModelo.all_objects.all()      # Todos incluidos eliminados
    """
    
    def get_queryset(self):
        """
        Retorna QuerySet filtrando registros no eliminados.
        
        Returns:
            QuerySet: Solo registros donde is_deleted=False
        """
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    """
    Modelo abstracto que implementa soft delete (borrado lógico).
    
    Propósito:
        En lugar de eliminar físicamente un registro, se marca como eliminado.
        El registro permanece en la base de datos pero se oculta de consultas.
    
    Campos:
        is_deleted: Bandera que indica si el registro está eliminado
        deleted_at: Fecha y hora de eliminación
        deleted_by: Usuario que eliminó el registro (auditoría)
    
    Métodos:
        soft_delete(): Marcar como eliminado
        restore(): Restaurar un registro eliminado
        hard_delete(): Eliminar físicamente (usar con precaución)
    
    Por qué:
        RNF - Mantenibilidad: Permite recuperar datos y mantener historial
        Auditoría: Saber quién eliminó qué y cuándo
    """
    
    # Bandera de eliminación lógica
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='Eliminado',
        help_text='Indica si el registro ha sido eliminado lógicamente',
        db_index=True  # Índice para optimizar filtrado
    )
    
    # Fecha de eliminación
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Eliminación',
        help_text='Fecha y hora en que se eliminó el registro'
    )
    
    # Usuario que eliminó (referencia al modelo de usuario)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='%(class)s_deleted',
        verbose_name='Eliminado por',
        help_text='Usuario que realizó la eliminación'
    )
    
    # Managers
    objects = SoftDeleteManager()  # Por defecto: solo activos
    all_objects = models.Manager()  # Incluye eliminados
    
    class Meta:
        abstract = True
    
    def soft_delete(self, user=None):
        """
        Marca el registro como eliminado (soft delete).
        
        Propósito:
            Eliminar lógicamente sin perder el registro.
        
        Args:
            user: Usuario que realiza la eliminación (opcional, para auditoría)
        
        Por qué no usar delete():
            Preserva el registro para auditoría y posible recuperación.
        
        Ejemplo:
            producto.soft_delete(user=request.user)
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])
    
    def restore(self):
        """
        Restaura un registro eliminado.
        
        Propósito:
            Recuperar registros eliminados accidentalmente o por necesidad.
        
        Por qué:
            Permite corregir errores sin intervención técnica en la BD.
        
        Ejemplo:
            producto.restore()
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])
    
    def hard_delete(self):
        """
        Elimina físicamente el registro de la base de datos.
        
        ⚠️ ADVERTENCIA: Esta acción es IRREVERSIBLE.
        
        Propósito:
            Eliminación permanente cuando es absolutamente necesario
            (ej. cumplimiento GDPR, datos de prueba).
        
        Por qué está separado:
            Requiere una acción explícita para evitar eliminaciones accidentales.
        
        Ejemplo:
            # Usar con extrema precaución
            producto.hard_delete()
        """
        super().delete()


class UUIDModel(models.Model):
    """
    Modelo abstracto que usa UUID como clave primaria.
    
    Propósito:
        Proveer identificadores únicos universales en lugar de integers.
    
    Por qué UUID:
        - No revela información sobre cantidad de registros (seguridad)
        - Permite generar IDs en cliente sin colisión
        - Facilita sincronización entre bases de datos distribuidas
        - URLs más seguras (/api/products/a1b2c3d4-... vs /api/products/1)
    
    Uso:
        class MiModelo(UUIDModel):
            nombre = models.CharField(max_length=100)
    """
    
    # UUID como clave primaria
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID',
        help_text='Identificador único universal'
    )
    
    class Meta:
        abstract = True


class AuditModel(TimeStampedModel, SoftDeleteModel):
    """
    Modelo abstracto completo con auditoría total.
    
    Propósito:
        Combina timestamps y soft delete para auditoría completa.
        Ideal para modelos de negocio críticos.
    
    Campos heredados:
        - created_at: Fecha de creación
        - updated_at: Fecha de modificación
        - is_deleted: Bandera de soft delete
        - deleted_at: Fecha de eliminación
        - deleted_by: Usuario que eliminó
    
    Campos adicionales:
        - created_by: Usuario que creó el registro
        - updated_by: Usuario que modificó por última vez
    
    Por qué:
        Requisito de auditoría financiera y cumplimiento normativo.
        Permite rastrear quién hizo qué y cuándo.
    """
    
    # Usuario que creó el registro
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='%(class)s_created',
        verbose_name='Creado por',
        help_text='Usuario que creó este registro'
    )
    
    # Usuario que modificó por última vez
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='%(class)s_updated',
        verbose_name='Modificado por',
        help_text='Usuario que realizó la última modificación'
    )
    
    class Meta:
        abstract = True


class BaseModel(UUIDModel, AuditModel):
    """
    Modelo base completo para entidades principales del ERP.
    
    Propósito:
        Proporcionar todos los campos estándar necesarios para
        cualquier entidad de negocio del ERP.
    
    Incluye:
        - UUID como clave primaria
        - Timestamps (created_at, updated_at)
        - Soft delete (is_deleted, deleted_at, deleted_by)
        - Auditoría de usuarios (created_by, updated_by)
    
    Por qué combinar todo:
        - Consistencia: Todas las entidades tienen los mismos campos base
        - DRY: Definido una vez, usado en todo el sistema
        - Mantenibilidad: Cambios en BaseModel afectan a todo el sistema
    
    Uso:
        class Producto(BaseModel):
            nombre = models.CharField(max_length=200)
            precio = models.DecimalField(...)
    """
    
    class Meta:
        abstract = True
        ordering = ['-created_at']


class StatusChoices(models.TextChoices):
    """
    Opciones de estado reutilizables para múltiples modelos.
    
    Propósito:
        Centralizar estados comunes para mantener consistencia.
    
    Por qué TextChoices:
        - Más legible en la BD que integers
        - Autodocumentado
        - Compatible con GraphQL y serialización JSON
    """
    DRAFT = 'draft', 'Borrador'
    PENDING = 'pending', 'Pendiente'
    APPROVED = 'approved', 'Aprobado'
    REJECTED = 'rejected', 'Rechazado'
    PROCESSING = 'processing', 'En Proceso'
    COMPLETED = 'completed', 'Completado'
    CANCELLED = 'cancelled', 'Cancelado'


class PriorityChoices(models.TextChoices):
    """
    Opciones de prioridad para tareas y notificaciones.
    """
    LOW = 'low', 'Baja'
    NORMAL = 'normal', 'Normal'
    HIGH = 'high', 'Alta'
    URGENT = 'urgent', 'Urgente'
