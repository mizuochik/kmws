FROM node:18-slim AS builder

WORKDIR /app
COPY . .

RUN npm install \
    && npm run build

FROM node:18-slim

WORKDIR /app

COPY --from=builder /app/node_modules node_modules
COPY --from=builder /app/.next .next
COPY --from=builder /app/package.json .

ENTRYPOINT [ "npm", "run", "start" ]
