FROM python:3.10-slim

WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files from ./app to /app/app
COPY ./app /app/

# Expose the necessary ports
EXPOSE 5000
EXPOSE 8000
EXPOSE 80

# Copy the entrypoint script from the build context
COPY ./entrypoint.sh /app/entrypoint.sh

# Ensure the entrypoint script is executable
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command to run the application
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
