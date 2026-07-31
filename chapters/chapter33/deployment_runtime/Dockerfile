FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app
COPY deployment_runtime /app/deployment_runtime

USER 65532:65532
EXPOSE 8080
CMD ["python", "-m", "deployment_runtime.server"]
