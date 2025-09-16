# 1. Build stage
FROM node:20-alpine AS build

WORKDIR /app

ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

# Mivel a build context a ./frontend, NEM kell előtag
COPY package*.json ./
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY public ./public
COPY src ./src
COPY index.html ./

RUN --mount=type=cache,target=/root/.npm \
	npm install
RUN --mount=type=cache,target=/root/.npm \
	npm run build

# 2. Serve stage (Nginx)
FROM nginx:alpine

WORKDIR /usr/share/nginx/html
COPY --from=build /app/dist ./

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
