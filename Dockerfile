FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY *.py ./

# Create output and logs directories
RUN mkdir -p /app/output /app/logs

# Default command to run the main application
CMD ["python", "main.py"]