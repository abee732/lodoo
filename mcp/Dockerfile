FROM python:3.11-slim

WORKDIR /app
COPY ./mcp/requirements.txt .

# System deps
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python deps
COPY ./mcp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY ./mcp ./app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 3333

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3333"]