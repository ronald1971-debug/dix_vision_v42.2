# DIX VISION v42.2 - React Dashboard Dockerfile
# Multi-stage build for development and production

FROM node:lts-alpine AS base
ENV NODE_ENV=production
WORKDIR /usr/src/app

# Development stage
FROM base AS development
ENV NODE_ENV=development
COPY ["package.json", "package-lock.json*", "npm-shrinkwrap.json*", "./"]
RUN npm install
COPY . .
EXPOSE 5173
RUN chown -R node /usr/src/app
USER node
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Production stage
FROM base AS production
ENV NODE_ENV=production
COPY ["package.json", "package-lock.json*", "npm-shrinkwrap.json*", "./"]
RUN npm ci --include=dev
COPY . .
RUN npm run build
RUN npm prune --production
EXPOSE 3000
RUN chown -R node /usr/src/app
USER node
CMD ["npm", "run", "preview"]
