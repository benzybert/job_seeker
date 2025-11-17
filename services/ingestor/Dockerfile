FROM python:3.11-slim
WORKDIR /app
COPY packages/shared /app/packages/shared
COPY services/ingestor/requirements.txt .
RUN pip install -r requirements.txt
RUN pip install -e /app/packages/shared
COPY services/ingestor /app/services/ingestor
CMD ["python", "-m", "services.ingestor.app.main"]


