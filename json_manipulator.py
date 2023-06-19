import argparse
import json

#python json_manipulator.py --file input.json --keys key1 key2 key3 

class JSONManipulator:
    def __init__(self):
        self.file_path = "input.json"

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description="JSON Manipulator")
        parser.add_argument("--file", help="JSON file path")
        parser.add_argument("--keys", nargs="+", help="Keys to remove from the JSON file")
        args = parser.parse_args()

        if args.file:
            self.file_path = args.file

        if args.keys:
            self.keys_to_remove = args.keys

    def remove_keys_from_json(self, keys):
        with open(self.file_path, "r") as file:
            json_data = json.load(file)

        for key in keys:
            if key in json_data:
                del json_data[key]

        with open(self.file_path, "w") as file:
            json.dump(json_data, file, indent=4)

    def main(self):
        self.parse_arguments()

        try:
            if hasattr(self, "keys_to_remove"):
                # Remove the specified keys from the JSON file
                self.remove_keys_from_json(self.keys_to_remove)
                print(f"Keys {self.keys_to_remove} removed from {self.file_path} successfully.")
            else:
                print("No keys specified to remove.")

        except Exception as ex:
            print(f"An error occurred: {str(ex)}")


if __name__ == "__main__":
    manipulator = JSONManipulator()
    manipulator.main()
