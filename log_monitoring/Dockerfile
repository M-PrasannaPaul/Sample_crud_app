FROM python:3.10-slim

WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files from ./app to /app/app
COPY ./app /app/app

# Expose the necessary port for the application
EXPOSE 5000

# Copy the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh

# Ensure the entrypoint script is executable
RUN chmod +x /app/entrypoint.sh

# Use entrypoint to start the application
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command to run the application
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
