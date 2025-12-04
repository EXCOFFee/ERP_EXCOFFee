# ========================================================
# SISTEMA ERP UNIVERSAL - Dockerfile Frontend
# ========================================================

# Etapa de desarrollo
FROM node:20-alpine AS development

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY . .

# Puerto de desarrollo
EXPOSE 3000

# Comando de desarrollo
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ------------------------------------------------
# Etapa de construcción
# ------------------------------------------------
FROM node:20-alpine AS build

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY . .

# Variables de entorno para build
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Construir aplicación
RUN npm run build

# ------------------------------------------------
# Etapa de producción
# ------------------------------------------------
FROM nginx:alpine AS production

# Copiar configuración de nginx
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Copiar archivos estáticos
COPY --from=build /app/dist /usr/share/nginx/html

# Puerto
EXPOSE 80

# Comando
CMD ["nginx", "-g", "daemon off;"]
