# 🏢 ERP Universal - Sistema de Planificación de Recursos Empresariales

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![React](https://img.shields.io/badge/React-18.x-61DAFB)](https://reactjs.org/)
[![Django](https://img.shields.io/badge/Django-5.x-092E20)](https://www.djangoproject.com/)
[![React Native](https://img.shields.io/badge/React_Native-Expo_50-61DAFB)](https://expo.dev/)

Sistema ERP integral para la gestión de **Inventario**, **Ventas**, **Compras**, **Finanzas** y **Recursos Humanos**. Incluye aplicación web y móvil con soporte offline.

![ERP Dashboard](https://via.placeholder.com/800x400?text=ERP+Dashboard)

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Stack Tecnológico](#-stack-tecnológico)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Módulos del Sistema](#-módulos-del-sistema)
- [API Documentation](#-api-documentation)
- [Aplicación Móvil](#-aplicación-móvil)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contribución](#-contribución)
- [Licencia](#-licencia)

## ✨ Características

### Core
- 🔐 **Autenticación JWT** con refresh tokens
- 👥 **RBAC** - Control de acceso basado en roles
- 🌐 **Multi-idioma** (Español/Inglés)
- 🌙 **Tema oscuro/claro**
- 📱 **Responsive** - Web y Móvil

### Módulos de Negocio
- 📦 **Inventario**: Gestión de productos, categorías, almacenes y movimientos de stock
- 💰 **Ventas**: Clientes, pedidos, facturación
- 🛒 **Compras**: Proveedores, órdenes de compra, recepción de mercancía
- 💼 **Finanzas**: Plan de cuentas, asientos contables, bancos
- 👔 **RRHH**: Empleados, departamentos, nómina

### Características Técnicas
- 📴 **Offline-First** (App Móvil) - Sincronización automática
- 📊 **Dashboard** con métricas en tiempo real
- 📷 **Escáner de códigos de barras**
- 📄 **Generación de reportes**
- 🔔 **Notificaciones push**

## 🛠 Stack Tecnológico

### Backend
| Tecnología | Versión | Uso |
|------------|---------|-----|
| Python | 3.11+ | Lenguaje principal |
| Django | 5.x | Framework web |
| Django REST Framework | 3.14+ | API REST |
| PostgreSQL | 16.x | Base de datos |
| Redis | 7.x | Cache y colas |
| Celery | 5.6+ | Tareas asíncronas |
| RabbitMQ | 3.x | Message broker |

### Frontend Web
| Tecnología | Versión | Uso |
|------------|---------|-----|
| React | 18.x | UI Library |
| TypeScript | 5.x | Tipado estático |
| Vite | 5.x | Build tool |
| Redux Toolkit | 2.x | Estado global |
| React Query | 5.x | Server state |
| MUI | 6.x | Componentes UI |
| React Hook Form | 7.x | Formularios |

### Frontend Móvil
| Tecnología | Versión | Uso |
|------------|---------|-----|
| React Native | 0.73+ | Framework móvil |
| Expo | 50.x | Herramientas desarrollo |
| React Native Paper | 5.x | Componentes UI |
| Redux Toolkit | 2.x | Estado global |

### Infraestructura
| Tecnología | Uso |
|------------|-----|
| Docker | Containerización |
| Docker Compose | Orquestación dev |
| Nginx | Reverse proxy |

## 📋 Requisitos Previos

- **Docker** >= 24.0
- **Docker Compose** >= 2.20
- **Node.js** >= 20.x (para desarrollo móvil)
- **pnpm** >= 8.x (opcional, para desarrollo local)
- **Git**

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/EXCOFFee/ERP_EXCOFFee.git
cd ERP_EXCOFFee
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tus valores:

```env
# Database
POSTGRES_DB=erp_db
POSTGRES_USER=erp_user
POSTGRES_PASSWORD=your_secure_password

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT
JWT_SECRET_KEY=your-jwt-secret
```

### 3. Iniciar con Docker

```bash
# Construir e iniciar todos los servicios
docker compose up -d --build

# Ver logs
docker compose logs -f

# Solo backend
docker compose up -d backend

# Solo frontend
docker compose up -d frontend
```

### 4. Inicializar la base de datos

```bash
# Ejecutar migraciones
docker compose exec backend python manage.py migrate

# Crear superusuario
docker compose exec backend python manage.py createsuperuser

# Cargar datos de prueba (opcional)
docker compose exec backend python manage.py seed_data
```

### 5. Acceder a la aplicación

| Servicio | URL |
|----------|-----|
| Frontend Web | http://localhost:3000 |
| Backend API | http://localhost:8000/api/v1 |
| Django Admin | http://localhost:8000/admin |
| API Docs (Swagger) | http://localhost:8000/api/v1/docs |
| RabbitMQ Management | http://localhost:15672 |

**Credenciales por defecto:**
- Email: `admin@erp.local`
- Password: `admin123`

## 📁 Estructura del Proyecto

```
ERP/
├── backend/                    # Django Backend
│   ├── apps/
│   │   ├── users/             # Autenticación y usuarios
│   │   ├── inventory/         # Módulo de inventario
│   │   ├── sales/             # Módulo de ventas
│   │   ├── purchasing/        # Módulo de compras
│   │   ├── finance/           # Módulo de finanzas
│   │   └── hr/                # Módulo de RRHH
│   ├── core/                  # Configuración Django
│   ├── utils/                 # Utilidades compartidas
│   └── manage.py
├── frontend/
│   ├── web/                   # React Web App
│   │   ├── src/
│   │   │   ├── components/    # Componentes reutilizables
│   │   │   ├── pages/         # Páginas/Vistas
│   │   │   ├── services/      # Servicios API
│   │   │   ├── store/         # Redux store
│   │   │   ├── hooks/         # Custom hooks
│   │   │   └── utils/         # Utilidades
│   │   └── package.json
│   └── mobile/                # React Native App
│       ├── src/
│       │   ├── screens/       # Pantallas
│       │   ├── components/    # Componentes
│       │   ├── services/      # Servicios API
│       │   ├── store/         # Redux store
│       │   └── navigation/    # Navegación
│       └── package.json
├── docker/                    # Configuración Docker
├── scripts/                   # Scripts de utilidad
├── docker-compose.yml
├── .env.example
└── README.md
```

## 📦 Módulos del Sistema

### Inventario
- Gestión de productos con SKU único
- Categorías jerárquicas
- Multi-almacén
- Movimientos de stock (entrada, salida, transferencia)
- Alertas de stock bajo
- Escáner de códigos de barras

### Ventas
- Gestión de clientes
- Órdenes de venta con workflow
- Facturación
- Control de crédito
- Historial de compras por cliente

### Compras
- Gestión de proveedores
- Órdenes de compra
- Recepción de mercancía
- Evaluación de proveedores

### Finanzas
- Plan de cuentas contable
- Asientos contables
- Cuentas bancarias
- Conciliación bancaria
- Reportes financieros

### RRHH
- Gestión de empleados
- Departamentos y posiciones
- Períodos de nómina
- Control de asistencia

## 📖 API Documentation

La documentación de la API está disponible en:
- **Swagger UI**: http://localhost:8000/api/v1/docs/
- **ReDoc**: http://localhost:8000/api/v1/redoc/

### Autenticación

```bash
# Login
POST /api/v1/auth/token/
Content-Type: application/json

{
  "email": "admin@erp.local",
  "password": "admin123"
}

# Response
{
  "access": "eyJ...",
  "refresh": "eyJ..."
}

# Usar token
GET /api/v1/inventory/products/
Authorization: Bearer eyJ...
```

### Endpoints principales

```
# Autenticación
POST   /api/v1/auth/token/           # Login
POST   /api/v1/auth/token/refresh/   # Refresh token
POST   /api/v1/auth/register/        # Registro

# Inventario
GET    /api/v1/inventory/products/
POST   /api/v1/inventory/products/
GET    /api/v1/inventory/products/{id}/
PATCH  /api/v1/inventory/products/{id}/
DELETE /api/v1/inventory/products/{id}/

# Ventas
GET    /api/v1/sales/customers/
GET    /api/v1/sales/orders/
POST   /api/v1/sales/orders/
POST   /api/v1/sales/orders/{id}/confirm/

# Compras
GET    /api/v1/purchasing/suppliers/
GET    /api/v1/purchasing/purchase-orders/

# Finanzas
GET    /api/v1/finance/accounts/
GET    /api/v1/finance/journal-entries/

# RRHH
GET    /api/v1/hr/employees/
GET    /api/v1/hr/departments/
```

## 📱 Aplicación Móvil

### Desarrollo local

```bash
cd frontend/mobile

# Instalar dependencias
pnpm install

# Iniciar Expo
pnpm start

# Para Android
pnpm android

# Para iOS
pnpm ios
```

### Características móviles
- ✅ Autenticación con biométricos
- ✅ Escáner de códigos de barras
- ✅ Sincronización offline
- ✅ Notificaciones push
- ✅ Tema oscuro/claro
- ✅ Soporte multi-idioma

### Configuración API

Edita `frontend/mobile/app.json`:

```json
{
  "expo": {
    "extra": {
      "apiUrl": "http://TU_IP:8000/api/v1"
    }
  }
}
```

## 🧪 Testing

### Backend

```bash
# Ejecutar tests
docker compose exec backend pytest

# Con coverage
docker compose exec backend pytest --cov=apps

# Tests específicos
docker compose exec backend pytest apps/inventory/tests/
```

### Frontend Web

```bash
cd frontend/web

# Tests unitarios
pnpm test

# Tests E2E
pnpm test:e2e
```

### Frontend Móvil

```bash
cd frontend/mobile

# Tests
pnpm test
```

## 🚀 Deployment

### Producción con Docker

```bash
# Build para producción
docker compose -f docker-compose.prod.yml up -d --build

# Ver estado
docker compose -f docker-compose.prod.yml ps
```

### Variables de entorno producción

```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com
DATABASE_URL=postgres://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: nueva característica'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Convenciones de código

- **Backend**: PEP 8, Black formatter, isort
- **Frontend**: ESLint, Prettier
- **Commits**: [Conventional Commits](https://www.conventionalcommits.org/)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Autores

- **EXCOFFee** - *Desarrollo inicial* - [GitHub](https://github.com/EXCOFFee)

## 🙏 Agradecimientos

- [Django](https://www.djangoproject.com/)
- [React](https://reactjs.org/)
- [Expo](https://expo.dev/)
- [MUI](https://mui.com/)
- [React Native Paper](https://reactnativepaper.com/)

---

<p align="center">
  Hecho con ❤️ por EXCOFFee
</p>
