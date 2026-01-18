FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (need devDependencies for build)
RUN npm ci

# Copy app files
COPY . .

# Build Next.js app
RUN npm run build

# Remove devDependencies after build
RUN npm prune --production

# Expose port
EXPOSE 3000

# Start app
CMD ["npm", "start"]
