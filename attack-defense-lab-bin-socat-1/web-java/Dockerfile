FROM eclipse-temurin:25-jdk-alpine AS build
WORKDIR /src
COPY App.java .
RUN javac App.java
FROM eclipse-temurin:25-jre-alpine
WORKDIR /app
COPY --from=build /src/*.class ./
RUN mkdir /data && chown 10001:10001 /data
USER 10001:10001
CMD ["java", "App"]

