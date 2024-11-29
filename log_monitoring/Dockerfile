FROM python:3.10-slim


WORKDIR /app


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app


EXPOSE 5000
EXPOSE 8000

COPY entrypoint.sh /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]


