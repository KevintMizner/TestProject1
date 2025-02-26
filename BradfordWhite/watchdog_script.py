import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import file_processor
import sys
import os
from file_processor import process_file, process_existing_files

def setup_logging():
    log_file = os.path.join(os.path.dirname(__file__), 'watchdog_script.log')
    sys.stdout = open(log_file, 'a')
    sys.stderr = open(log_file, 'a')

setup_logging()
print(f"Running with Python: {sys.executable}")

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.csv'):
            file_path = event.src_path
            print(f"Detected new file: {file_path}")
            time.sleep(1)  # Optional: Wait a bit for the file to be fully written
            file_processor.process_file(file_path, folder_to_watch)

if __name__ == "__main__":
    folder_to_watch = r'\\allen-files\edi\ASC\BRAWHI-ORDER-STATUS'
    file_processor.process_existing_files(folder_to_watch)
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
