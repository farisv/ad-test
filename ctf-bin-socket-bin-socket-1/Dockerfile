FROM alpine:3.23
WORKDIR /app
COPY --chmod=755 server ./server
RUN mkdir -p /data/records && chown -R 10002:10002 /data
USER 10002:10002
EXPOSE 9002
CMD ["/app/server"]
