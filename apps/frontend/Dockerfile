# 🚀 AstraTrade Flutter Web Production Dockerfile
# Multi-stage build for optimized production deployment

# ============================================================================
# Stage 1: Build Environment
# ============================================================================
FROM ubuntu:22.04 AS build-env

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    wget \
    unzip \
    libgconf-2-4 \
    gdb \
    libstdc++6 \
    libglu1-mesa \
    fonts-droid-fallback \
    lib32stdc++6 \
    python3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Flutter
ENV FLUTTER_VERSION=3.32.5
ENV FLUTTER_HOME=/opt/flutter
ENV PATH=$FLUTTER_HOME/bin:$PATH

RUN git clone --depth 1 --branch $FLUTTER_VERSION https://github.com/flutter/flutter.git $FLUTTER_HOME \
    && flutter config --no-analytics \
    && flutter precache \
    && flutter doctor

# Set working directory
WORKDIR /app

# Copy pubspec files first for better caching
COPY pubspec.yaml pubspec.lock ./

# Get dependencies
RUN flutter pub get

# Copy source code
COPY . .

# Configure build environment
ARG WEB3AUTH_CLIENT_ID=BPPbhL4egAYdv3vHFVQDhmueoOJKUeHJZe2X8LaMvMIq9go2GN72j6OwvheQkR2ofq8WveHJQtzNKaq0_o_xKuI
ARG STARKNET_NETWORK=sepolia-alpha
ARG API_BASE_URL=https://api.astratrade.io
ARG DEMO_MODE=false

ENV WEB3AUTH_CLIENT_ID=$WEB3AUTH_CLIENT_ID
ENV STARKNET_NETWORK=$STARKNET_NETWORK
ENV API_BASE_URL=$API_BASE_URL
ENV DEMO_MODE=$DEMO_MODE

# Build web application
RUN flutter build web --release --dart-define=WEB3AUTH_CLIENT_ID=$WEB3AUTH_CLIENT_ID

# ============================================================================
# Stage 2: Production Environment
# ============================================================================
FROM nginx:alpine AS production

# Install additional tools for health checks
RUN apk add --no-cache curl

# Copy built web app from build stage
COPY --from=build-env /app/build/web /usr/share/nginx/html

# Copy custom nginx configuration
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Copy startup script
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

# Create nginx user and directories
RUN addgroup -g 1001 -S nginx && \
    adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx && \
    mkdir -p /var/log/nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx /var/cache/nginx /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# Security: Run as non-root user
USER nginx

# Expose port 80
EXPOSE 80

# Labels for container metadata
LABEL org.opencontainers.image.title="AstraTrade Flutter Web App"
LABEL org.opencontainers.image.description="Production-ready AstraTrade web application"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="AstraTrade"

# Start nginx
CMD ["/start.sh"]

# ============================================================================
# Stage 3: Development Environment (Optional)
# ============================================================================
FROM build-env AS development

# Install development tools
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up development environment
ENV FLUTTER_WEB_PORT=3000
EXPOSE 3000

# Development startup command
CMD ["flutter", "run", "-d", "web-server", "--web-hostname", "0.0.0.0", "--web-port", "3000"]