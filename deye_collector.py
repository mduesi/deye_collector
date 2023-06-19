import argparse
import re
import requests
import base64
import sqlite3
import json
import pytz
import socket
from datetime import datetime
from sqlite3 import Error
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from influxdb import InfluxDBClient

"""
:Globale Variablen
"""
#database = "deye.db"

class Deye:
    def __init__(self):
        self.inverter_ip = "192.168.0.10"
        self.credentials = "admin:admin"
        self.database = "deye.db"
        self.sqlite_table = "deyeinverter"
        self.influxdb_ip = "192.168.0.11"
        self.influxdb_port = 8086
        self.influxdb_database = "deye"
        self.influxdb_username = "deye"
        self.influxdb_password = "deye"
        self.influxdb_measurement = "solar"
        self.output_json_filename = "deye_output.json"
        self.local_timezone = pytz.timezone('Europe/Berlin')

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description="DEYE Inverter Data Parser")
        parser.add_argument("--ip", help="DEYE Inverter IP address")
        parser.add_argument("--credentials", help="DEYE Inverter credentials in the format 'username:password'")
        args = parser.parse_args()

        if args.ip:
            self.inverter_ip = args.ip
        if args.credentials:
            self.credentials = args.credentials

    def check_host_availability(self):
        try:
            host = socket.gethostbyname(self.inverter_ip)
            socket.create_connection((host, 80), timeout=1)
            return True
        except (socket.gaierror, socket.timeout):
            return False

    def request_inverter_data(self):
        if self.check_host_availability():
            page_content = ""
            url = f"http://{self.inverter_ip}/status.html"
            username = self.credentials.split(":")[0]
            password = self.credentials.split(":")[1]

            #print ("User: ", username)
            #print ("Password: ", password)

            # Create the basic authentication credentials
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()

            # Create the headers with the Authorization field for basic authentication
            headers = {"Authorization": f"Basic {credentials}"}

            # Make the GET request to the website with basic authentication
            response = requests.get(url, headers=headers)
            
            # Get the response content and store it in a variable
            response_content = response.text

            # Print the response content or use it as needed
            #print(response_content)

            if response.status_code == 200:
                page_content = response.text
            else:
                raise Exception("ERROR: DEYE Connection failed")

            return self.extract_variable_values(page_content)
        else:
            raise Exception(f"ERROR: Host {self.inverter_ip} is not available")

    @staticmethod
    def extract_variable_values(html_code):
        variable_values = {}

        pattern = r'var\s+(\w+)\s*=\s*"?([^;]+)"?;'
        matches = re.findall(pattern, html_code)

        for match in matches:
            variable_name, variable_value = match
            if "height" not in variable_name and "nh" not in variable_name:
                if "document" not in variable_value.strip() and "window." not in variable_value.strip():
                    variable_values[variable_name] = variable_value.strip().replace('\\', '').replace('"', '')

        # Print the keys and values
        #for key, value in variable_values.items():
            #print(f"Variable '{key}' value: {value}")

        return variable_values

    def create_connection(db_file):
        """ create a database connection to the SQLite database specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return conn

    def save_values_to_sqlite(self, key, value):
        print(self.database)
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()

            create_table_query = "CREATE TABLE IF NOT EXISTS {} (Name TEXT, Value TEXT)".format(self.sqlite_table)
            cursor.execute(create_table_query)

            select_data_query = "SELECT Value FROM {} WHERE Name = ?".format(self.sqlite_table)
            cursor.execute(select_data_query, (key,))
            existing_value = cursor.fetchone()

            if existing_value:
                update_data_query = "UPDATE {} SET Value = ? WHERE Name = ?".format(self.sqlite_table)
                cursor.execute(update_data_query, (value, key))
            else:
                insert_data_query = "INSERT INTO {} (Name, Value) VALUES (?, ?)".format(self.sqlite_table)
                cursor.execute(insert_data_query, (key, value))

            connection.commit()

            #print(f"Variable '{key}' value: {value}")

    def save_values_to_json(self, data):
        with open(self.output_json_filename, "w") as f:
            json.dump(data, f, indent=4)

    def add_json_data_to_table(self, json_data, table_name):
        # Parse the JSON data
        data = json.loads(json_data)
        #print(self.database)
        #print(json.dumps(data))
        # Connect to the SQLite database
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()

            # Create the table if it doesn't exist
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} (Name TEXT, Value TEXT)"
            cursor.execute(create_table_query)

            # Iterate over the key-value pairs in the JSON data
            for key, value in data.items():
                # Check if the value already exists in the table
                select_data_query = f"SELECT Value FROM {table_name} WHERE Name = ?"
                cursor.execute(select_data_query, (key,))
                existing_value = cursor.fetchone()

                if existing_value:
                    # Update the value if it already exists
                    update_data_query = f"UPDATE {table_name} SET Value = ? WHERE Name = ?"
                    cursor.execute(update_data_query, (value.strip(), key))
                else:
                    # Insert the value if it doesn't exist
                    insert_data_query = f"INSERT INTO {table_name} (Name, Value) VALUES (?, ?)"
                    cursor.execute(insert_data_query, (key, value.strip()))

            # Commit the changes to the database
            connection.commit()

    def extend_json_with_current_time(self, file_path):
        # Read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Get the current time in the Germany/Berlin time zone
        
        current_time = datetime.now(self.local_timezone).strftime('%Y-%m-%d %H:%M:%S')
        # Add the current time as a key-value pair
        data['current_time'] = current_time
        # Remove the unused value from the json
        if "i" in data:
            del data["i"]
        # Write the updated JSON data back to the file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def save_values_to_influxdb(self, data):
        influx_client = InfluxDBClient(host=self.influxdb_ip, port=self.influxdb_port, username=self.influxdb_username, password=self.influxdb_password, database=self.influxdb_database)
        # Iterate over the key-value pairs in the data
        points = []
        for key, value in data.items():
            if value:
                point = {
                    "measurement": self.influxdb_measurement,
                    "tags": {
                        "Name": key
                    },
                    "fields": {
                        "Value": value.strip()
                    }
                }
                points.append(point)

        # Write the points to InfluxDB
        influx_client.write_points(points)

    def main(self):
        self.parse_arguments()
        print(self.getpowerconsfromdb(self.database))
        try:
            inverter_status = self.request_inverter_data()
            # Save the key-value pairs to a JSON file
            self.save_values_to_json(inverter_status)
            # Open the JSON file
            self.extend_json_with_current_time(self.output_json_filename)
            with open(self.output_json_filename, "r") as f:
                # Load the JSON data into a variable
                data = json.load(f)
            json_data = json.dumps(data)
            self.add_json_data_to_table(json_data, self.sqlite_table)
            self.save_values_to_influxdb(data)
            #for variable_name, variable_value in inverter_status.items():
            #    self.save_values_to_sqlite(variable_name, variable_value)

        except Exception as ex:
            print(f"An error occurred: {str(ex)}")

if __name__ == "__main__":
    deye = Deye()
    deye.main()
