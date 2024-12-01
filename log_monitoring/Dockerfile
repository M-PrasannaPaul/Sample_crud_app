FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY ./app /app/app

# Expose necessary ports
EXPOSE 5000
EXPOSE 8000
EXPOSE 80

# Copy entrypoint script into the container
COPY ./log_monitoring/entrypoint.sh /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

# Command to run the app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
