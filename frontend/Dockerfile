# Stage 1: Node node asset compiler step
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
# Clean install dependencies using lockfile parameters for strict container reproducibility
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Production Nginx static server distribution engine
FROM nginx:stable-alpine AS runner

# Copy customized assets out of Vite's output matrix distribution folder
COPY --from=builder /app/dist /usr/share/nginx/html

# Overwrite default Nginx configs to support React Router dynamic links, 
# explicit proxy headers, and WebSockets protocol upgrades.
RUN echo 'server { \
    listen 80; \
    \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # Smooth fallback configuration to catch local developer api traffic cleanly \
    location /api/ { \
        proxy_pass http://backend-engine:8000; \
        proxy_http_version 1.1; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "upgrade"; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]