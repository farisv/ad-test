FROM alpine:3.23 AS build
RUN apk add --no-cache build-base
WORKDIR /src
COPY service.c .
RUN gcc -O0 -g -fno-stack-protector -no-pie -z execstack -D_FORTIFY_SOURCE=0 -o service service.c
FROM alpine:3.23
RUN apk add --no-cache socat
WORKDIR /app
COPY --from=build /src/service ./
RUN mkdir -p /data/records && chown -R 10001:10001 /data
USER 10001:10001
EXPOSE 9001
CMD ["socat", "TCP-LISTEN:9001,reuseaddr,fork", "EXEC:/app/service,stderr"]
