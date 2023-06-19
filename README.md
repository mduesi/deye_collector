# deye_collector
I wrote the script to read the current measurement data from the Deye inverter via the local IP and output it in different formats:

- JSON file
- SQLITE database
- InfluxDB

I have additionally created a shellscript which retrieves the sunrise and sunset times over the internet. Since the Deye inverter is only online when the sun is shining, the data retrieval is only executed when theoretical sunshine is possible. In addition, it is checked whether the Deye inverter can be reached on the network side.

I have set up a cronjob on the Raspberry that runs the shellscript every 4 minutes:

Crontab
*/4 * * * * /home/pi/scripts/start_deye_collect.sh

Required Linux packages for the shell script:

Required Python libraries for the data collector

Additionally there is a small tool to manipulate the JSON file afterwards (currently only removing key value pairs)
json_manipulator.py

This script accept multiple keys to remove from the JSON file. The --keys option supports multiple values. The remove_keys_from_json() method handles the removal of multiple keys. The keys are iterated, and if a key exists in the JSON data, it is deleted. Finally, a success message is displayed indicating which keys were removed from the JSON file.

To run the script and remove multiple keys, you can use the --keys option followed by the keys you want to remove. For example:

python script.py --file input.json --keys key1 key2 key3

This command will remove the keys "key1", "key2", and "key3" from the JSON file named "input.json".
