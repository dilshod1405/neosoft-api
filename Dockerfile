# Base image
FROM python:3.12-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    netcat-openbsd \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libglib2.0-0 \
    libffi8 \
    shared-mime-info \
    fonts-liberation \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*



# Copy requirements
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Expose port
EXPOSE 8000

# Entrypoint script to run migrations and collectstatic
COPY ./entrypoint.sh /app/entrypoint.sh
COPY ./wait_for_db.sh /app/wait_for_db.sh

RUN chmod +x /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh /app/wait_for_db.sh

# Run entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
