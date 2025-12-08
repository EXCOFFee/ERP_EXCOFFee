# ========================================================
# SISTEMA ERP UNIVERSAL - Dockerfile Frontend
# ========================================================

# Etapa de desarrollo
FROM node:20-alpine AS development

WORKDIR /app

# Instalar pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copiar archivos de dependencias
COPY package.json pnpm-lock.yaml ./

# Instalar dependencias
RUN pnpm install --frozen-lockfile

# Copiar codigo fuente
COPY . .

# Puerto de desarrollo
EXPOSE 3000

# Comando de desarrollo
CMD ["pnpm", "run", "dev", "--", "--host", "0.0.0.0"]

# ------------------------------------------------
# Etapa de construccion
# ------------------------------------------------
FROM node:20-alpine AS build

WORKDIR /app

# Instalar pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copiar archivos de dependencias
COPY package.json pnpm-lock.yaml ./

# Instalar dependencias
RUN pnpm install --frozen-lockfile

# Copiar codigo fuente
COPY . .

# Variables de entorno para build
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Construir aplicacion
RUN pnpm run build

# ------------------------------------------------
# Etapa de produccion
# ------------------------------------------------
FROM nginx:alpine AS production

# Copiar configuracion de nginx
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Copiar archivos estaticos
COPY --from=build /app/dist /usr/share/nginx/html

# Puerto
EXPOSE 80

# Comando
CMD ["nginx", "-g", "daemon off;"]
