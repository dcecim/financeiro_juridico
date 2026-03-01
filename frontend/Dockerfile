# Estágio de Build
FROM node:22-alpine as build

WORKDIR /app

# Instala dependências de sistema necessárias para compilação (se houver módulos nativos)
RUN apk add --no-cache python3 make g++

# Copia arquivos de dependência
COPY package.json package-lock.json ./

# Instala dependências
RUN npm ci

# Copia código fonte
COPY . .

# Build da aplicação
RUN npm run build

# Estágio de Produção (Nginx)
FROM nginx:alpine

# Remove configuração padrão do Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copia configuração customizada do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia arquivos estáticos gerados no build
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
