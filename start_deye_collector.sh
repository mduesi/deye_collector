#!/bin/bash

# Set the timezone to Europe/Berlin
export TZ="Europe/Berlin"

# Set the full paths for commands and files
CURL="/usr/bin/curl"
JQ="/usr/bin/jq"
PING="/bin/ping"
PYTHON="/usr/bin/python3"
SCRIPT_PATH="/home/pi/old_main_application/shpi/core/deye.py"
LOG_FILE="/var/log/deye_collector.log"

# Get the current local time
current_time=$(/bin/date +%T)

echo "Aktuelle Zeit: $current_time"
# Get the sunrise time for Weinheim on the current date
sunrise_time=$($CURL -s "https://api.sunrise-sunset.org/json?lat=49.527220&lng=8.654260")

sunrise=$(echo "$sunrise_time" | $JQ -r '.results.sunrise')
sunset=$(echo "$sunrise_time" | $JQ -r '.results.sunset')
sunrise_local=$(/bin/date -d "$sunrise UTC" +"%H:%M:%S")
sunset_local=$(/bin/date -d "$sunset UTC" +"%H:%M:%S")
echo "Sonnenaufgang: $sunrise_local"
echo "Sonnenuntergang: $sunset_local"
# Compare the current time with the sunrise and sunset times
if [[ "$current_time" > "$sunrise_local" && "$current_time" < "$sunset_local" ]]; then
    host="192.168.178.176"
    $PING -c 1 $host > /dev/null
    if [ $? -eq 0 ]; then
        $PYTHON $SCRIPT_PATH >> $LOG_FILE 2>&1
    else
        echo "Host $host is not reachable."
    fi
elif [[ "$current_time" > "$sunset_local" ]]; then
    echo "Sonnenuntergang: $sunset_local"
else
    echo "Before sunrise. $sunrise_local"
fi
