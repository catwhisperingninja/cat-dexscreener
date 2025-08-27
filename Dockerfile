# Smithery TypeScript server
FROM node:22-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy all source files
COPY . .

# Build TypeScript
RUN npm run build

# Build Smithery bundle
RUN npx @smithery/cli@1.2.17 build

# Expose port
EXPOSE 8080

# Environment
ENV NODE_ENV=production
ENV PORT=8080

# Start the Smithery bundle
CMD ["node", ".smithery/index.cjs"]
