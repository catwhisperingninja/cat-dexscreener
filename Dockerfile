# Smithery TypeScript MCP Server
FROM node:22-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY . .

# Build TypeScript
RUN npm run build

# Build with Smithery CLI
RUN npx @smithery/cli@1.2.17 build

# Run the server
EXPOSE 8080
CMD ["node", ".smithery/index.cjs"]
