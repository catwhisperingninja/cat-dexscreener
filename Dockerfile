# Multi-stage build for Smithery
FROM node:22-slim AS builder

WORKDIR /app

# Copy all files
COPY . .

# Install dependencies and build
RUN npm ci --ignore-scripts && \
    npm run build

# Build Smithery bundle
RUN npx -y @smithery/cli@latest build -o .smithery/index.cjs

# Production stage
FROM node:22-slim

WORKDIR /app

# Copy built files and dependencies
COPY --from=builder /app/build ./build
COPY --from=builder /app/.smithery ./.smithery
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/smithery.yaml ./

# Install production dependencies only
RUN npm ci --production --ignore-scripts

# Expose the port for HTTP mode (required for Smithery)
EXPOSE 8080

# Start with Smithery's built bundle
CMD ["node", ".smithery/index.cjs"]
