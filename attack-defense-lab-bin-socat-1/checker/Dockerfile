FROM python:3.13-alpine
WORKDIR /app
COPY checker.py .
RUN mkdir /state && chown 65534:65534 /state
USER 65534:65534
CMD ["python", "checker.py"]
