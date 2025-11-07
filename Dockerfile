# Dockerfile for n8n to Python Converter

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy application code
COPY backend/ /app/backend/
COPY samples/ /app/samples/
COPY frontend/ /app/frontend/

# Expose port
EXPOSE 8000

# Set Python path
ENV PYTHONPATH=/app

# Run the API server
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
