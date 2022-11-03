FROM public.ecr.aws/lambda/nodejs:18 AS builder

WORKDIR /build
COPY . .
RUN npm install && npm run build

FROM public.ecr.aws/lambda/nodejs:18

COPY package.json next.config.js app.js ./
COPY --from=builder /build/.next .next
COPY --from=builder /build/node_modules node_modules

CMD [ "app.handler" ]
