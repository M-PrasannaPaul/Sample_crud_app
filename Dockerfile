FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt .

# Add dependencies for cryptography package
RUN apk add --no-cache --virtual .build-deps gcc libffi-dev musl-dev openssl-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
