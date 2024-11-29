import mysql.connector
import json


db_config = {
    'user': 'root',
    'password': 'Paul*1928',
    'host': 'db',
    'database': 'log_monitoring'
}

connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS nginx_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp VARCHAR(255),
        client_ip VARCHAR(255),
        request_uri VARCHAR(255),
        status_code INT
    )
''')
connection.commit()


def insert_log(log_entry):
    query = '''
        INSERT INTO nginx_logs (timestamp, client_ip, request_uri, status_code)
        VALUES (%s, %s, %s, %s)
    '''
    cursor.execute(query, (log_entry['time'], log_entry['remote_ip'], log_entry['request'], log_entry['response']))
    connection.commit()


def parse_and_store_logs(log_file, max_logs=500):
    count = 0  
    with open(log_file, 'r') as f:
        for line in f:
            if count >= max_logs:  
                print(f"Inserted {max_logs} logs, stopping.")
                break
            log_entry = json.loads(line)
            insert_log(log_entry)
            count += 1  

log_file = '/app/app/nginx_json_logs.txt'
parse_and_store_logs(log_file)


cursor.close()
connection.close()
