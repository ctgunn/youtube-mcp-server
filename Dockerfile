FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

COPY src /app/src
COPY README.md /app/README.md

EXPOSE 8080

CMD ["python3", "-m", "mcp_server.cloud_run_entrypoint"]
