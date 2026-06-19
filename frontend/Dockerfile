# Stage 1: Node node asset compiler step
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Production Nginx static server distribution engine
FROM nginx:stable-alpine AS runner

# Copy customized assets out of Vite's output matrix distribution folder
COPY --from=builder /app/dist /usr/share/nginx/html

# Overwrite default Nginx configs to support React Router dynamic links
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]