FROM node:24-alpine
WORKDIR /app
COPY server.js ./
RUN mkdir /data && chown node:node /data
USER node
CMD ["node", "server.js"]

