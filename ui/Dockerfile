## Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY ui/package*.json ./
RUN npm ci --silent
COPY ui/ ./
RUN npm run build

## Production nginx stage
FROM nginx:stable-alpine AS runtime

# Remove default nginx configs and add minimal security headers
RUN rm /etc/nginx/conf.d/default.conf
COPY ui/nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=build /app/dist /usr/share/nginx/html

# Run nginx as non-root
RUN addgroup -S app && adduser -S app -G app
USER app

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
