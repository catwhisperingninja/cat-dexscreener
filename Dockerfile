# Multi-stage build for Smithery with security improvements
FROM node:22-slim AS builder

WORKDIR /app

# Copy package files first for better layer caching
COPY package*.json ./

# Install all dependencies (needed for build)
RUN npm ci

# Copy source files
COPY . .

# Build TypeScript project
RUN npm run build

# Build Smithery bundle with pinned version (uses package.json module field)
RUN npx -y @smithery/cli@1.2.17 build -o .smithery/index.cjs

# Production stage with non-root user
FROM node:22-slim

# Create non-root user
RUN useradd -r -u 1001 -g root -s /bin/false mcpuser && \
    mkdir -p /app && \
    chown -R mcpuser:root /app

WORKDIR /app

# Copy built artifacts and package files
COPY --from=builder --chown=mcpuser:root /app/.smithery ./.smithery
COPY --from=builder --chown=mcpuser:root /app/package*.json ./
COPY --from=builder --chown=mcpuser:root /app/smithery.yaml ./

# Install only production dependencies and clean cache
RUN npm ci --production --ignore-scripts && \
    npm cache clean --force

# Switch to non-root user
USER mcpuser

# Expose port 8080 for Smithery HTTP transport
EXPOSE 8080

# Environment variables
ENV NODE_ENV=production
ENV PORT=8080

# Simple CMD without shell wrapper
CMD ["node", ".smithery/index.cjs"]
