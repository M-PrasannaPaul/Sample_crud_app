from flask import Flask, jsonify, request, Response, render_template, redirect, url_for
from prometheus_client import Counter, Gauge, Histogram, generate_latest, start_http_server
import mysql.connector
import threading
import time
import os
import random
import logging
from werkzeug.utils import secure_filename
import json

logging.basicConfig(level=logging.DEBUG)


db_config = {
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", "Paul*1928"),
    "host": os.environ.get("MYSQL_HOST", "db"),
    "database": os.environ.get("MYSQL_DATABASE", "log_monitoring"),
}

app = Flask(__name__)


UPLOAD_FOLDER = '/app/app/uploads' 
ALLOWED_EXTENSIONS = {'json'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


REQUEST_COUNT = Counter('log_requests_total', 'Total number of log requests')
SEARCH_LOGS_COUNT = Counter('search_logs_total', 'Total number of search logs')
REQUEST_LATENCY = Histogram('log_request_latency_seconds', 'Latency of log requests in seconds')
ACTIVE_REQUESTS = Gauge('active_log_requests', 'Number of active log requests')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_log():
    REQUEST_COUNT.inc()  
    with REQUEST_LATENCY.time():  
        ACTIVE_REQUESTS.inc()  
        time.sleep(random.uniform(0.1, 0.5))  
        ACTIVE_REQUESTS.dec()  


def parse_and_store_logs(log_file):
    with open(log_file, 'r') as f:
        for line in f:
            log_entry = json.loads(line)
            insert_log(log_entry)


def insert_log(log_entry):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    
    query = '''
        INSERT INTO nginx_logs (timestamp, client_ip, request_uri, status_code)
        VALUES (%s, %s, %s, %s)
    '''
    cursor.execute(query, (log_entry['time'], log_entry['remote_ip'], log_entry['request'], log_entry['response']))
    connection.commit()
    
    cursor.close()
    connection.close()


def get_logs(search_params):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM nginx_logs WHERE 1=1"


    if 'status_code' in search_params:
        query += f" AND status_code = {search_params['status_code']}"
    if 'client_ip' in search_params:
        query += f" AND client_ip = '{search_params['client_ip']}'"

    cursor.execute(query)
    logs = cursor.fetchall()
    cursor.close()
    connection.close()
    return logs

def get_all_logs():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM nginx_logs")
    logs = cursor.fetchall()
    cursor.close()
    connection.close()
    return logs

def get_common_errors():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    query = '''
        SELECT status_code, COUNT(*) AS count 
        FROM nginx_logs 
        WHERE status_code >= 200 
        GROUP BY status_code 
        ORDER BY count DESC
    '''

    cursor.execute(query)
    common_errors = cursor.fetchall()
    cursor.close()
    connection.close()
    return common_errors


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        log_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        parse_and_store_logs(log_file_path)  
        return redirect(url_for('view_logs'))  
    return "File type not allowed", 400


@app.route('/logs', methods=['GET'])
def search_logs():
    status_code = request.args.get('status_code')
    client_ip = request.args.get('client_ip')

    query = "SELECT * FROM nginx_logs WHERE 1=1"
    filters = []

    if status_code:
        query += " AND status_code = %s"
        filters.append(status_code)

    if client_ip:
        query += " AND client_ip = %s"
        filters.append(client_ip)

    try:
        # Establish database connection
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

       
        print(f"Executing query: {query}")
        print(f"With filters: {filters}")

        cursor.execute(query, filters)
        logs = cursor.fetchall()

        cursor.close()
        connection.close()

    except Exception as e:
        
        print(f"Database error: {e}")
        return "An error occurred while fetching logs.", 500

    
    return render_template('logs.html', logs=logs)



@app.route('/view_logs', methods=['GET'])
def view_logs():
    logs = get_all_logs()
    REQUEST_COUNT.inc()  
    process_log() 
    return render_template('logs.html', logs=logs)

@app.route('/common_errors', methods=['GET'])
def common_errors():
    errors = get_common_errors()
    process_log()  
    return render_template('common_errors.html', errors=errors)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain')

def start_metrics_server():
    
    start_http_server(8000)
    while True:
        process_log()
        time.sleep(1)


threading.Thread(target=start_metrics_server, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 80)))
