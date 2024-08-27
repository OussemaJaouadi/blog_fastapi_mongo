# Use the official Python 3.12 image based on Alpine Linux
FROM python:3.12-alpine

# Set environment variables to prevent Python from writing .pyc files and to enable unbuffered output
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port 8000 (or your application port)
EXPOSE 8000

# Command to run your application (change this as needed)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
