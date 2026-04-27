# syntax=docker/dockerfile:1

FROM node:20-alpine as builder

WORKDIR /build
COPY package*.json ./
RUN npm ci --omit=dev

FROM node:20-alpine

WORKDIR /app

RUN addgroup -S appgroup && adduser -S -G appgroup appuser

COPY --from=builder /build/node_modules ./node_modules
COPY . .

RUN rm -f .env .env.* && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

CMD ["node", "app.js"]
