FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

COPY src /app/src
COPY README.md /app/README.md
COPY pyproject.toml /app/pyproject.toml

RUN python3 -m pip install --no-cache-dir --upgrade pip \
    && python3 -m pip install --no-cache-dir .

EXPOSE 8080

CMD ["python3", "-m", "uvicorn", "mcp_server.cloud_run_entrypoint:app", "--host", "0.0.0.0", "--port", "8080"]
