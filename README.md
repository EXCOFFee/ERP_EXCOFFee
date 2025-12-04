# 🏢 Sistema ERP Universal

<p align="center">
  <img src="docs/images/logo.png" alt="ERP Logo" width="200"/>
</p>

<p align="center">
  <strong>Sistema de Planificación de Recursos Empresariales Completo y Modular</strong>
</p>

<p align="center">
  <a href="#características">Características</a> •
  <a href="#arquitectura">Arquitectura</a> •
  <a href="#instalación">Instalación</a> •
  <a href="#uso">Uso</a> •
  <a href="#documentación">Documentación</a>
</p>

---

## 📋 Descripción

Sistema ERP Universal es una solución empresarial completa desarrollada con tecnologías modernas que permite gestionar todos los aspectos operativos de una organización, desde inventario y ventas hasta recursos humanos y finanzas.

## ✨ Características

### 🔐 Autenticación y Seguridad
- Autenticación JWT con tokens de acceso y refresco
- Control de acceso basado en roles (RBAC)
- Autenticación de dos factores (2FA)
- Auditoría completa de acciones

### 📦 Gestión de Inventario
- Control de múltiples almacenes
- Gestión de productos y categorías
- Trazabilidad por lotes y números de serie
- Alertas de stock mínimo
- Transferencias entre almacenes

### 💰 Gestión de Ventas
- Catálogo de clientes
- Cotizaciones y pedidos
- Facturación electrónica
- Gestión de precios y descuentos
- Reportes de ventas

### 🛒 Gestión de Compras
- Catálogo de proveedores
- Requisiciones y órdenes de compra
- Recepción de mercancías
- Evaluación de proveedores
- Gestión de pagos

### 📊 Gestión Financiera
- Plan de cuentas contables
- Libro diario y mayor
- Conciliación bancaria
- Estados financieros
- Gestión de impuestos

### 👥 Recursos Humanos
- Gestión de empleados
- Control de asistencia
- Procesamiento de nómina
- Gestión de vacaciones y permisos
- Evaluaciones de desempeño

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │   React Web     │  │  React Native   │                   │
│  │   (Vite + MUI)  │  │    (Mobile)     │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
└───────────┼────────────────────┼────────────────────────────┘
            │                    │
            ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                     API GATEWAY (Nginx)                      │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│                        BACKEND                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │   Core   │ │   Auth   │ │ Inventory│ │  Sales   │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                     │
│  │Purchasing│ │ Finance  │ │    HR    │                     │
│  └──────────┘ └──────────┘ └──────────┘                     │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│                      INFRAESTRUCTURA                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                     │
│  │PostgreSQL│ │  Redis   │ │ RabbitMQ │                     │
│  └──────────┘ └──────────┘ └──────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Tecnologías

### Backend
- **Python 3.11+**
- **Django REST Framework 5.0**
- **PostgreSQL 16** - Base de datos principal
- **Redis 7** - Caché y sesiones
- **Celery** - Tareas asíncronas
- **RabbitMQ** - Message broker

### Frontend Web
- **React 18** con TypeScript
- **Vite** - Build tool
- **Material UI 5** - Componentes
- **Redux Toolkit** - Estado global
- **React Router 6** - Enrutamiento
- **React Hook Form + Zod** - Formularios y validación

### Frontend Mobile
- **React Native** con TypeScript
- **React Navigation**
- **React Native Paper** - Componentes

### DevOps
- **Docker & Docker Compose**
- **Nginx** - Servidor web/proxy
- **GitHub Actions** - CI/CD

## 📦 Instalación

### Prerrequisitos

- Docker y Docker Compose
- Node.js 20+ (para desarrollo local)
- Python 3.11+ (para desarrollo local)

### Instalación con Docker (Recomendada)

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/erp-universal.git
cd erp-universal
```

2. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Levantar los servicios**
```bash
docker-compose up -d
```

4. **Ejecutar migraciones**
```bash
docker-compose exec backend python manage.py migrate
```

5. **Crear superusuario**
```bash
docker-compose exec backend python manage.py createsuperuser
```

6. **Acceder a la aplicación**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1/
- Admin: http://localhost:8000/admin/
- RabbitMQ Management: http://localhost:15672

### Instalación para Desarrollo Local

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Frontend

```bash
cd frontend/web
npm install
npm run dev
```

## 🚀 Uso

### Endpoints API

| Módulo | Base URL |
|--------|----------|
| Core | `/api/v1/core/` |
| Auth | `/api/v1/auth/` |
| Inventario | `/api/v1/inventory/` |
| Ventas | `/api/v1/sales/` |
| Compras | `/api/v1/purchasing/` |
| Finanzas | `/api/v1/finance/` |
| RRHH | `/api/v1/hr/` |

### Documentación API

La documentación interactiva de la API está disponible en:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## 📁 Estructura del Proyecto

```
erp-universal/
├── backend/                 # Backend Django
│   ├── config/             # Configuración del proyecto
│   ├── apps/               # Aplicaciones Django
│   │   ├── core/          # Funcionalidades base
│   │   ├── authentication/# Autenticación y usuarios
│   │   ├── inventory/     # Gestión de inventario
│   │   ├── sales/         # Gestión de ventas
│   │   ├── purchasing/    # Gestión de compras
│   │   ├── finance/       # Gestión financiera
│   │   └── hr/            # Recursos humanos
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── web/               # Aplicación React
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── layouts/
│   │   │   ├── store/
│   │   │   ├── services/
│   │   │   └── types/
│   │   └── Dockerfile
│   └── mobile/            # Aplicación React Native
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🧪 Testing

### Backend
```bash
cd backend
pytest
pytest --cov=apps  # Con cobertura
```

### Frontend
```bash
cd frontend/web
npm run test
npm run test:coverage
```

## 🔒 Seguridad

- Todas las contraseñas se almacenan hasheadas con bcrypt
- Tokens JWT con tiempo de expiración configurable
- Validación y sanitización de entradas
- Protección CSRF
- Headers de seguridad configurados
- Encriptación HTTPS en producción

## 📊 Reportes

El sistema incluye reportes predefinidos para:

- **Ventas**: Ventas por período, por cliente, por producto
- **Inventario**: Valoración de inventario, movimientos, stock crítico
- **Compras**: Compras por proveedor, análisis de precios
- **Finanzas**: Balance general, estado de resultados, flujo de caja
- **RRHH**: Nómina, asistencia, rotación de personal

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Soporte

Para soporte y consultas:
- 📧 Email: soporte@erp-universal.com
- 📖 Documentación: https://docs.erp-universal.com
- 🐛 Issues: https://github.com/tu-usuario/erp-universal/issues

---

<p align="center">
  Desarrollado con ❤️ para empresas modernas
</p>
