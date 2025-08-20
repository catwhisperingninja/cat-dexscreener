# Smithery container runtime
FROM node:22-slim

WORKDIR /app

# Copy all project files
COPY . .

# Install dependencies and build TypeScript
RUN npm ci && \
    npm run build

# Install Smithery CLI globally
RUN npm install -g @smithery/cli@1.2.17

# Build the Smithery bundle
RUN smithery build -o .smithery/index.cjs

# Expose port 8080 for Smithery HTTP transport
EXPOSE 8080

# Environment variables
ENV NODE_ENV=production
ENV PORT=8080

# Start the built server
CMD ["node", ".smithery/index.cjs"]
