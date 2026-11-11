# Mirsad web — Next.js, built once, served from the standalone bundle.
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS build
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:22-alpine AS run
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0 PORT=3000
RUN addgroup -S mirsad && adduser -S mirsad -G mirsad
COPY --from=build --chown=mirsad:mirsad /app/.next/standalone ./
COPY --from=build --chown=mirsad:mirsad /app/.next/static ./.next/static
USER mirsad
EXPOSE 3000
CMD ["node", "server.js"]
