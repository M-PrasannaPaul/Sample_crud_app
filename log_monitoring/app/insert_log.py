import mysql.connector
import json

db_config = {
    'user': 'mysqladmin',
    'password': 'Paul*1928',
    'host': 'myflaskdbserver.mysql.database.azure.com',
    'database': 'log_monitoring'
}


def create_table_if_not_exists():
    try:
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
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
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")


def insert_log(log_entry):
    try:
        with mysql.connector.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                query = '''
                    INSERT INTO nginx_logs (timestamp, client_ip, request_uri, status_code)
                    VALUES (%s, %s, %s, %s)
                '''
                cursor.execute(query, (log_entry['time'], log_entry['remote_ip'], log_entry['request'], log_entry['response']))
                connection.commit()
    except mysql.connector.Error as err:
        print(f"Error inserting log: {err}")


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


if __name__ == "__main__":
    create_table_if_not_exists()
    log_file = '/app/app/nginx_json_logs.txt'
    parse_and_store_logs(log_file)
