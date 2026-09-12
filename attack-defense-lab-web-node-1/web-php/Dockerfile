FROM php:8.4-cli
RUN apt-get update \
 && apt-get install -y --no-install-recommends libsqlite3-dev \
 && docker-php-ext-install pdo_sqlite \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY router.php index.html ./
RUN mkdir /data && chown www-data:www-data /data
USER www-data
CMD ["php", "-S", "0.0.0.0:8081", "router.php"]
