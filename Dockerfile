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

# Expose the port your MCP server listens on (adjust if needed)
EXPOSE 3000

# Start the MCP server
CMD ["npm", "start"]
