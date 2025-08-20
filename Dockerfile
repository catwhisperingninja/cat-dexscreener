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

# Set environment variable from build arg (can be overridden at runtime)
ARG SMITHERY_API_KEY
ENV SMITHERY_API_KEY=${SMITHERY_API_KEY}

# Start the MCP server
CMD ["npm", "start"]
