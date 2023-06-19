# deye_collector
Python script to read different values from the Deye inverter. The script has several output options: JSON file, SQLlTE database and InfluxDB.



json_manipulator.py

This script accept multiple keys to remove from the JSON file. The --keys option supports multiple values. The remove_keys_from_json() method handles the removal of multiple keys. The keys are iterated, and if a key exists in the JSON data, it is deleted. Finally, a success message is displayed indicating which keys were removed from the JSON file.

To run the script and remove multiple keys, you can use the --keys option followed by the keys you want to remove. For example:

python script.py --file input.json --keys key1 key2 key3

This command will remove the keys "key1", "key2", and "key3" from the JSON file named "input.json".
