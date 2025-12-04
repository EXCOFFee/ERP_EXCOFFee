Especificación de Requisitos de Software (SRS) - Sistema ERP Universal

Título del Proyecto: Sistema de Planificación de Recursos Empresariales (ERP) Universal
Versión: 2.1 (Mejorada + Principios)
Fecha: 30 de Noviembre de 2025
Preparado para: Agente de IA Especializado en Programación

0. Meta-Instrucciones para el Agente de IA

Objetivo: Estas instrucciones definen cómo debe comportarse la IA al generar código basado en este documento.

Prioridad de Tipado: El código debe ser estrictamente tipado. No usar Any en Python ni any en TypeScript a menos que sea absolutamente inevitable.

Prevención de Alucinaciones: Solo utilizar las librerías definidas en el Stack Tecnológico. No introducir dependencias externas no aprobadas.

Manejo de Contexto: Al generar un archivo, asumir siempre que es parte de un sistema mayor. Mantener la consistencia en nombres de variables (ej. usar siempre user_id, no alternar con userId en el backend).

Defensividad: Escribir código paranoico. Asumir que toda entrada externa es maliciosa o incorrecta hasta que se valide.

1. Introducción

1.1 Qué

Este documento es la Especificación de Requisitos de Software (SRS) para un Sistema ERP integral. El sistema orquesta procesos de Finanzas, Inventario, Compras, Ventas y RRHH.

1.2 Cómo

Arquitectura de Microservicios Event-Driven. Interfaz unificada vía BFF (Backend for Frontend) pattern opcional o API Gateway directo. Clientes: Web (SPA) y Móvil (Nativa/Híbrida).

1.3 Por Qué

Centralización de la verdad operativa. Eliminación de silos de datos. Accesibilidad en tiempo real para trabajadores de escritorio y de campo (offline-first capability para móvil).

1.4 Alcance (Scope)

In-Scope: Gestión de usuarios (RBAC), Dashboard, Inventario Multi-bodega, Facturación, Asientos Contables, Nómina básica.

Out-of-Scope: E-commerce público, Gestión de flota de camiones (GPS), Inteligencia de Negocios predictiva (Fase 2).

2. Stacks Tecnológicos Detallado

Qué

Herramientas y versiones específicas.

Cómo

Capa

Tecnología

Versión Sugerida

Razón (Por Qué)

Backend

Python (FastAPI o Django Ninja)

3.11+

Mayor velocidad que DRF tradicional, soporte nativo asíncrono, validación automática con Pydantic.

DB Relacional

PostgreSQL

16.x

JSONB indexado para flexibilidad en atributos de productos.

DB Caché

Redis

7.x

Gestión de colas (Celery/Rq) y caché de sesiones.

Frontend Web

React + Vite + TypeScript

18.x

Vite para builds rápidos. TypeScript para seguridad de tipos.

State Mgmt

Zustand o Redux Toolkit

-

Manejo de estado global predecible y ligero.

Frontend Móvil

React Native + Expo

SDK 49+

Iteración rápida, acceso nativo a cámara (escaneo QR).

UI Library

Shadcn/UI (Web) / Tamagui (Mobile)

-

Componentes accesibles y personalizables.

Infraestructura

Docker Compose (Dev) / K8s (Prod)

-

Orquestación de contenedores.

3. Definición de Hecho (DoD) Reforzada

Qué

Criterios de aceptación técnica y funcional.

Cómo

Para dar una tarea por cerrada, el Agente debe verificar:

Funcionalidad: Cumple los Criterios de Aceptación (AC) de la historia.

Coverage: Tests unitarios > 85%. Tests de integración para endpoints críticos.

Linting/Formatting: El código pasa Ruff (Python) y ESLint/Prettier (JS/TS) sin advertencias.

Documentación: Docstrings en formato Google o NumPy para Python; JSDoc para TS. Debe incluir ejemplos de uso.

Manejo de Errores: No existen bloques try/except vacíos (pass). Todas las excepciones se loggean y se transforman en respuestas HTTP estandarizadas.

Tipado: Cero errores de mypy (modo estricto) o tsc.

4. Diagramas de Modelado y Arquitectura

4.1. Diagrama de Casos de Uso

Actores: Administrador, Gerente de Ventas, Operador de Almacén, Contador, Sistema de Pagos (Stripe/PayPal).

Casos Críticos: "Realizar Venta (Offline)", "Sincronizar Stock", "Cierre Contable Mensual".

4.2. Flujo de Datos (DFD) - Nivel 1 (Venta)

Cliente Móvil envía JSON OrdenVenta.

API Gateway valida token JWT.

Svc Ventas recibe orden -> Publica evento order_created en RabbitMQ.

Svc Inventario consume evento -> Reserva stock (Atomic Transaction).

Si falla: Publica stock_reservation_failed.

Si éxito: Publica stock_reserved.

Svc Finanzas consume stock_reserved -> Genera factura y asiento contable.

4.3. Arquitectura C4 (Contexto y Contenedores)

Contexto: ERP System <-> Email Service (SendGrid), Bank API, Users.

Contenedores:

WebApp (React)

MobileApp (React Native)

APIGateway (Nginx/Traefik)

AuthService (Python)

InventoryService (Python)

FinanceService (Python)

EventBus (RabbitMQ)

4.4. Diagrama ER (Entidad-Relación) - Entidades Core

User: id (UUID), email, password_hash, role_id, is_active.

Product: id (UUID), sku (Unique), name, cost_price, selling_price, current_stock (Computed), warehouse_id (FK).

Order: id (UUID), customer_id, status (Enum: PENDING, PAID, SHIPPED), total_amount, created_at.

OrderItem: id, order_id (FK), product_id (FK), quantity, unit_price_at_moment.

JournalEntry (Asiento): id, date, description, linked_document_id (Optional).

JournalLine: id, entry_id (FK), account_id (FK), debit, credit.

5. Requisitos del Sistema (Detallados)

5.1. Requisitos Funcionales (RF)

ID

Módulo

Requisito Funcional

Criterio de Aceptación (Gherkin-style)

RF1

Inventario

Bloqueo Pesimista de Stock: Al iniciar una venta, el stock debe reservarse temporalmente para evitar sobreventa.

DADO que hay 1 unidad de 'Producto A', CUANDO dos usuarios intentan comprarlo simultáneamente, ENTONCES solo uno tiene éxito y el otro recibe error "Stock Insuficiente".

RF2

Offline

Sincronización: La App Móvil debe permitir crear órdenes sin internet y sincronizar al reconectar.

DADO que el móvil no tiene red, CUANDO guardo una orden, ENTONCES se guarda en SQLite local Y se marca como 'pending_sync'.

RF3

Finanzas

Inmutabilidad: Una vez cerrado un periodo fiscal, no se pueden editar asientos de ese periodo.

DADO un asiento de fecha 'Enero', SI el periodo 'Enero' está 'CERRADO', ENTONCES cualquier intento de UPDATE retorna 403 Forbidden.

5.2. Requisitos No Funcionales (RNF)

ID

Categoría

Requisito

Métrica

RNF1

Performance

Latencia API: Endpoints críticos (Búsqueda de productos) deben responder rápido.

< 200ms (p95)

RNF2

Seguridad

Rate Limiting: Protección contra fuerza bruta en login.

Máx 5 intentos/minuto por IP.

RNF3

Código

Complejidad Ciclomática: Mantener funciones simples.

< 10 por función.

6. Estándar de API y Protocolo de Comunicación

Qué

Estándar de respuesta JSON unificado tipo JSend modificado o Envelope Pattern para garantizar consistencia, trazabilidad y facilidad de consumo por los clientes (Web/Mobile).

Cómo

El Agente debe implementar un wrapper global (Middleware en FastAPI/Django) que intercepte todas las respuestas y excepciones.

1. Estructura Base (Envelope):

Todas las respuestas HTTP (200, 400, 500) deben seguir esta estructura:

{
  "success": boolean,      // true para 2xx, false para 4xx/5xx
  "request_id": string,    // UUID único para trazar la petición en logs (Datadog/Sentry)
  "data": any | null,      // Payload principal (solo en success=true)
  "error": object | null,  // Detalle del error (solo en success=false)
  "meta": object           // Metadatos transversales (paginación, timestamp servidor)
}


2. Respuesta Exitosa (200 OK):

{
  "success": true,
  "request_id": "c9b83942-8394-4d12-8b42-1234567890ab",
  "data": {
    "id": "123",
    "name": "Laptop Dell",
    "price": 1200.50
  },
  "error": null,
  "meta": {
    "timestamp": "2025-11-30T10:00:00Z",
    "pagination": {
      "page": 1,
      "limit": 10,
      "total_items": 50,
      "total_pages": 5
    }
  }
}


3. Respuesta de Error (400 Bad Request / 500 Internal Server Error):

HTTP Status: Debe corresponder al error (ej. 400, 401, 403, 404, 500). No devolver siempre 200.

Internal Code: Código de error de negocio específico e inmutable.

{
  "success": false,
  "request_id": "c9b83942-8394-4d12-8b42-1234567890ab",
  "data": null,
  "meta": {
    "timestamp": "2025-11-30T10:05:00Z"
  },
  "error": {
    "code": "INV_STOCK_001",  // Código interno para frontend i18n
    "message": "Stock insuficiente para realizar la operación.", // Mensaje fallback
    "details": [           // Array de errores específicos (ej. validación formularios)
      {
        "field": "quantity",
        "issue": "MAX_VALUE_EXCEEDED",
        "description": "La cantidad solicitada (10) excede el disponible (5)."
      }
    ],
    "help_url": "[https://docs.erp-interno.com/errors/INV_STOCK_001](https://docs.erp-interno.com/errors/INV_STOCK_001)" // Opcional
  }
}


4. Headers Obligatorios:

Content-Type: application/json

X-Request-ID: El mismo UUID que va en el cuerpo, para correlación de logs inmediata.

7. Principios de Diseño y Calidad (SOLID, DRY, KISS)

7.1. Implementación Práctica de SOLID

S (SRP): Anti-patrón: User.save() que también envía email de bienvenida. Correcto: UserRepository.save() solo guarda. UserOnboardingService orquesta el guardado y luego llama a NotificationService.

O (OCP): Uso de Strategy Pattern para impuestos. TaxCalculator recibe una lista de estrategias (IVATStrategy, IIBBStrategy). Para agregar un impuesto nuevo, se crea una clase nueva, no se toca el calculador.

L (LSP): Si AdminUser hereda de User, AdminUser no debe lanzar una excepción si se llama a get_profile(). Debe comportarse como un User.

I (ISP): Frontend no debe recibir el objeto User completo con password_hash y audit_logs si solo necesita name y avatar. Usar DTOs (Data Transfer Objects) específicos: UserSummaryDTO.

D (DIP): Inyectar dependencias en el constructor.

# Correcto
class OrderService:
    def __init__(self, repo: IOrderRepository):
        self.repo = repo


7.2. Principio DRY (Don't Repeat Yourself)

Qué: Cada pieza de conocimiento o lógica debe tener una representación única e inequívoca dentro del sistema.

Anti-patrón (A evitar): Copiar y pegar la expresión regular de validación de email en el Frontend (React) y luego en cada microservicio del Backend. Si la regla cambia, el sistema se rompe.

Implementación Correcta:

Backend: Crear un módulo shared_kernel.validators que importen todos los servicios.

Frontend: Centralizar constantes y utilidades en src/utils/validators.ts.

Lógica de Negocio: Si calcular el IVA se hace en varios lugares, extraerlo a un TaxCalculatorService único.

7.3. Principio KISS (Keep It Simple, Stupid)

Qué: La mayoría de los sistemas funcionan mejor si se mantienen simples en lugar de complicados. Evitar la sobre-ingeniería.

Anti-patrón (A evitar): Crear una jerarquía compleja de clases abstractas o implementar un patrón "Mediator" dinámico solo para conectar dos componentes simples. Usar bibliotecas pesadas para problemas triviales (ej. importar lodash solo para usar uniq).

Implementación Correcta:

Preferir funciones puras sobre clases con estado complejo cuando sea posible.

Si un if/else es legible y hace el trabajo, no forzar un patrón de diseño innecesario.

Escribir código que un desarrollador Junior pueda entender sin leer un manual de arquitectura de 50 páginas.

7.4. Comentarios y "Self-Documenting Code"

El código debe leerse como prosa.

Nombres de Variables: days_since_last_login en vez de d.

Comentarios: Explicar el POR QUÉ de una lógica de negocio extraña ("Se suma +1 al día porque el sistema legacy cuenta desde 1, no 0"), no explicar QUÉ hace el código ("Suma 1 a la variable").

8. Estrategia de Testing

Qué

Pirámide de pruebas para asegurar estabilidad.

Cómo

Unit Tests (Backend): Usar pytest. Mocker todas las llamadas a DB y APIs externas. Probar casos borde (valores negativos, strings vacíos).

Unit Tests (Frontend): Usar Jest + React Testing Library. Probar que el componente renderiza y reacciona a eventos, no detalles de implementación CSS.

E2E (End-to-End): Usar Playwright o Cypress. Simular un flujo crítico: Login -> Crear Producto -> Vender Producto -> Verificar Stock reducido.

9. Seguridad

JWT: Access Token (15 min vida) + Refresh Token (7 días, rotativo).

CORS: Restringido estrictamente a dominios conocidos.

SQL Injection: Uso obligatorio de ORM o consultas parametrizadas. Prohibido concatenar strings en SQL.

Datos Sensibles: PII (Información Personal Identificable) debe estar encriptada en reposo si es posible.

Este documento SRS v2.1 proporciona el contexto técnico riguroso, las restricciones de arquitectura y los estándares de calidad necesarios para que una IA genere código de nivel producción, mantenible y escalable.