# Blackboard MCP server — container for Cloud Run (Streamable HTTP).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Serves the MCP endpoint at /mcp on $PORT.
EXPOSE 8080
CMD exec uvicorn app.server:app --host 0.0.0.0 --port ${PORT}
