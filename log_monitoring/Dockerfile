FROM python:3.10-slim


WORKDIR /app


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app


EXPOSE 5000
EXPOSE 8000
EXPOSE 80

COPY entrypoint.sh /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]  

