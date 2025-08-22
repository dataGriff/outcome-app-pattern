FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements if you have a requirements.txt
COPY ../requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for delta lake
RUN pip install --no-cache-dir nats-py deltalake pandas boto3

# Copy the application code
COPY ./src/stream_nats_to_minio_delta.py ./

CMD ["python", "stream_nats_to_minio_delta.py"]
