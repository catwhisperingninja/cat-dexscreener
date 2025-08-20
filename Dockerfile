# Use the official Node.js LTS version as the base image
FROM node:lts

# Create and set the working directory
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Copy smithery.yaml configuration
COPY smithery.yaml ./

# Expose the port for HTTP mode (required for Smithery)
EXPOSE 8080
# SMITHERY_API_KEY must be provided at runtime via environment (compose/Kubernetes)
# Start the MCP server
CMD ["npm", "start"]
