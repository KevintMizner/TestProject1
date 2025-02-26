import sys
import psutil
import os

def list_running_python_scripts():
    current_pid = os.getpid()
    script_name = os.path.basename(__file__)
    running_scripts = []
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if process.info['name'] == 'python.exe' or process.info['name'] == 'pythonw.exe':
            cmdline = process.info['cmdline']
            if cmdline and script_name in cmdline and process.info['pid'] != current_pid:
                print(f"Another instance of {script_name} is already running with PID: {process.info['pid']}")
                sys.exit(0)
            if process.info['pid'] == current_pid:
                continue  # Skip the current process
            running_scripts.append(process.info)
    return running_scripts

if __name__ == "__main__":
    print(f"Running with Python: {sys.executable}")
    running_scripts = list_running_python_scripts()
    for script in running_scripts:
        print(f"PID: {script['pid']}, Command Line: {script['cmdline']}")
