FROM alpine:3.23
RUN apk add --no-cache socat
WORKDIR /app
COPY --chmod=755 service ./service
RUN mkdir -p /data/records && chown -R 10001:10001 /data
USER 10001:10001
EXPOSE 9001
CMD ["socat", "TCP-LISTEN:9001,reuseaddr,fork", "EXEC:/app/service,stderr"]
