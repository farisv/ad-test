FROM python:3.13-alpine
WORKDIR /app
COPY app.py ./
COPY static ./static
RUN mkdir /data && chown 65534:65534 /data
USER 65534:65534
EXPOSE 8080
CMD ["python", "app.py"]

