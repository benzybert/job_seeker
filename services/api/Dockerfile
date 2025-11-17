FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn pydantic
COPY services/api /app/services/api
CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]