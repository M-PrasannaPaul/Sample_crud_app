#!/bin/bash


LOG_FILE="/home/madagalapaul/log_monitoring/logs/nginx_json_logs.txt"

trigger_alert() {
    local message=$1
    echo "ALERT: $message"
   
}


echo "Current logs in $LOG_FILE:"

echo "====================="


tail -f "$LOG_FILE" | while read -r log_line; do
    
    echo "Processing log line: $log_line"

  
    if [ -n "$log_line" ]; then
       
        response_code=$(echo "$log_line" | jq '.response' 2>/dev/null)
        request_uri=$(echo "$log_line" | jq -r '.request' 2>/dev/null)

        if [ -z "$response_code" ]; then
            echo "Warning: Could not parse log line with jq: $log_line"
            continue
        fi

        echo "Parsed response_code: $response_code, request_uri: $request_uri"

  
        if [ "$response_code" -eq 500 ]; then
            trigger_alert "500 Internal Server Error detected for request: $request_uri"
        fi

  
        if [ "$response_code" -eq 401 ]; then
            trigger_alert "401 Unauthorized (Failed Login) detected for request: $request_uri"
        fi

        if [ "$response_code" -eq 403 ]; then
            trigger_alert "403 Forbidden access detected for request: $request_uri"
        fi
    fi
done

