FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY services/document/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/document/app .
COPY services/protos ./protos
COPY services/document/generate_protos.sh .
RUN chmod +x generate_protos.sh
RUN ./generate_protos.sh
# Backup generated protos so entrypoint can restore them over volume mount
RUN mkdir -p /app/proto_backup && cp /app/db/*_pb2*.py /app/proto_backup/

COPY services/document/entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]