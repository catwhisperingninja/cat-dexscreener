# Smithery container runtime Dockerfile
FROM node:22-slim

WORKDIR /app

# Copy all project files
COPY . .

# Install dependencies (both production and dev for building)
RUN npm ci

# Build TypeScript project
RUN npm run build

# Build Smithery bundle with HTTP transport
RUN npx -y @smithery/cli@latest build -o .smithery/index.cjs

# Expose port 8080 for Smithery HTTP transport
EXPOSE 8080

# Environment variable for runtime config
ENV NODE_ENV=production
ENV PORT=8080

# Start the Smithery-built MCP server
# The built bundle handles HTTP transport automatically
CMD ["sh", "-c", "exec node .smithery/index.cjs"]
