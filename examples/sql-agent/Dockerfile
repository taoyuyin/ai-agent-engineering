FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/examples/sql-agent

WORKDIR /app

COPY pyproject.toml framework/README.md ./
COPY framework ./framework
COPY examples/sql-agent/requirements.txt ./examples/sql-agent/requirements.txt

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -e . \
    && python -m pip install --no-cache-dir -r examples/sql-agent/requirements.txt

COPY examples/sql-agent ./examples/sql-agent

RUN mkdir -p /app/var

EXPOSE 8080

CMD ["uvicorn", "sql_agent.api:app", "--app-dir", "examples/sql-agent", "--host", "0.0.0.0", "--port", "8080"]
