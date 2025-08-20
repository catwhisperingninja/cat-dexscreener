# Smithery TypeScript server - following cookbook pattern
FROM node:22-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy all source files
COPY . .

# Build with Smithery CLI (like the cookbook)
RUN npx @smithery/cli build

# Expose port 8080
EXPOSE 8080

# Environment variables
ENV NODE_ENV=production
ENV PORT=8080

# Start the server using the built Smithery bundle
CMD ["node", ".smithery/index.cjs"]
