FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY api/requirements.txt ./api/
RUN pip install --no-cache-dir -r api/requirements.txt

# Copy all application files
COPY api/ ./api/
COPY index.html ./

# Expose the port Flask runs on
EXPOSE 5000

# Set environment variable for Python
ENV PYTHONUNBUFFERED=1

# Run the Flask application
CMD ["python", "api/server.py"]