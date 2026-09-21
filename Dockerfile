FROM python:3.11-slim

# Install system dependencies for WeasyPrint
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose the port (Render defaults to 10000 if not specified, but 5000 is common for Flask, we'll use Render's standard approach)
# Often Render will pass PORT env variable, gunicorn will use it.
EXPOSE 10000

# Run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "120", "app:app"]
