FROM alpine:3.23 AS build
RUN apk add --no-cache build-base
WORKDIR /src
COPY server.c .
RUN gcc -O0 -g -fno-stack-protector -no-pie -D_FORTIFY_SOURCE=0 -o server server.c
FROM alpine:3.23
WORKDIR /app
COPY --from=build /src/server ./
RUN mkdir -p /data/records && chown -R 10002:10002 /data
USER 10002:10002
EXPOSE 9002
CMD ["/app/server"]
