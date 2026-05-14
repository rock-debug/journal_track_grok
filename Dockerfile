FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (required for psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Command to run the application using Gunicorn (production server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
