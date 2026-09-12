FROM golang:1.25-alpine AS build
WORKDIR /src
COPY go.mod main.go ./
RUN CGO_ENABLED=0 go build -trimpath -ldflags='-s -w' -o /service .
FROM alpine:3.23
COPY --from=build /service /service
RUN mkdir /data && chown 65534:65534 /data
USER 65534:65534
ENTRYPOINT ["/service"]
