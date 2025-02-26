import csv
import json
import shutil
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests

def is_file_unlocked(file_path):
    try:
        with open(file_path, "a"):
            return True
    except IOError:
        return False

def process_file(file_path):
    # Define status messages
    status_messages = {
        'B': 'B - Being Picked', 'C': 'C - Closed', 'D': 'D - On Truck',
        'G': 'G - Truck', 'H': 'H - Credit Hold', 'I': 'I - Short Inventory',
        'K': 'K - Pick Hold', 'L': 'L - On Loading Dock', 'N': 'N - Not Scheduled',
        'O': 'O - Pick Complete-In Transit', 'P': 'P - Partial Pick',
        'S': 'S - Scheduled', 'U': 'U - Unlocked', 'X': 'X - Cancelled'
    }
    
    max_attempts = 10
    attempt = 0
    while attempt < max_attempts:
        if is_file_unlocked(file_path):
            try:
                with open(file_path, 'r', newline='') as file:
                    reader = csv.reader(file)
                    first_row = next(reader)
                    if len(first_row) >= 7:
                        delivery_id, execution_id, process_status = first_row[0], first_row[4], first_row[6]
                        process_status_int = 1 if process_status.strip() == 'N' else 0
                        #process_status_int = 1 if process_status.strip() == 'U' else 0
                        error_message = status_messages.get(process_status.strip(), 'Unknown Status')

                        payload = {
                            "executionId": execution_id.strip(),
                            "deliveryId": delivery_id.strip(),
                            "processStatus": process_status_int,
                            "errorMessage": error_message
                        }
                        print(f"Processed payload: {json.dumps(payload, indent=2)}")

                        # Save the JSON payload to a file named after the CSV
                        json_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}.json"
                        json_filepath = os.path.join(os.path.dirname(file_path), json_filename)
                        with open(json_filepath, 'w') as json_file:
                            json.dump(payload, json_file, indent=4)
                        print(f"JSON payload saved to {json_filepath}")
                        
                        
                        
                        # Send payload to API endpoint
                        # non prod api_url = "https://oicnonprod-bradfordwhiteoic.integration.ocp.oraclecloud.com/ic/api/integration/v1/flows/rest/BWC_AD_CUSTOM_ORDER_RECEIP/1.0/T3Receipt"
                        api_url = "https://oicproduction-bradfordwhiteoic.integration.ocp.oraclecloud.com:443/ic/api/integration/v1/flows/rest/BWC_AD_CUSTOM_ORDER_RECEIP/1.0/T3Receipt"
                        auth = ("AD_USER", "ADWelcome54321")
                        response = requests.post(api_url, json=payload, auth=auth)

                        print("API response:")
                        print(json.dumps(response.json(), indent=2))  # Print API response payload
                        
                           # Check API response and log the event
                        if response.status_code == 200:
                            print("API call accepted for processing.")
                        else:
                            print(f"API call failed with status code: {response.status_code}")
                        log_processing_event(folder_to_watch, os.path.basename(file_path), payload, response.status_code)

                # Move the CSV and JSON file to the 'processed' directory
                move_files(file_path, json_filepath)
                break
            except Exception as e:
                print(f"An error occurred while processing the file: {str(e)}")
                break
        else:
            print(f"Attempt {attempt + 1}: File is locked, retrying...")
            time.sleep(3)
            attempt += 1

def move_files(csv_path, json_path):
    processed_folder = os.path.join(os.path.dirname(csv_path), "processed")
    if not os.path.exists(processed_folder):
        os.makedirs(processed_folder)
    shutil.move(csv_path, os.path.join(processed_folder, os.path.basename(csv_path)))
    shutil.move(json_path, os.path.join(processed_folder, os.path.basename(json_path)))
    print(f"Moved files to: {processed_folder}")

def log_processing_event(directory, csv_filename, payload, response_code):
    log_filepath = os.path.join(directory, 'APILogs.txt')
    with open(log_filepath, 'a') as log_file:
        # Formatting the log entry with a timestamp, filename, payload, and response code
        log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')}, {csv_filename}, {json.dumps(payload)}, Response Code: {response_code}\n"
        log_file.write(log_entry)

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.csv'):
            file_path = event.src_path
            print(f"Detected new file: {file_path}")
            time.sleep(1)  # Optional: Wait a bit for the file to be fully written
            process_file(file_path)

def process_existing_files(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.lower().endswith('.csv'):
            print(f"Processing existing file: {file_path}")
            process_file(file_path)

if __name__ == "__main__":
    folder_to_watch = r'\\allen-files\edi\ASC\BRAWHI-ORDER-STATUS'
    process_existing_files(folder_to_watch)
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_to_watch, recursive=False)
    observer.start()
    print(f"Watching folder: {folder_to_watch}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
