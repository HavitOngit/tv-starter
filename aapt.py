import subprocess
import requests
import threading
import time

def execute_command(command, path, stop_event):
    try:
        # Run the command
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=path)
        if stop_event.is_set():
            return "Terminated"
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e.stderr.decode('utf-8')}"

def delayed_execute_command(command, path, delay, stop_event):
    time.sleep(delay)
    if stop_event.is_set():
        print(f"Execution of {command} stopped before starting.")
        return
    output = execute_command(command, path, stop_event)
    if stop_event.is_set():
        print("Terminated")
    else:
        print(output)

def get_status_code(url, stop_event):
    try:
        response = requests.get(url)
        if stop_event.is_set():
            return "Terminated"
        
        if not response.ok:
            stop_event.set()
            print("Stopping the execution of the command.")
        
        return response.status_code
    except requests.RequestException as e:
        return f"An error occurred: {e}"

def delayed_get_status_code(url, delay, stop_event):
    time.sleep(delay)
    if stop_event.is_set():
        print(f"Status check for {url} stopped before starting.")
        return
    status_code = get_status_code(url, stop_event)
    if stop_event.is_set():
        print("Terminated")
    else:
        print(f"Status code for {url}: {status_code}")

command = r".\jiotv_go.exe run"
path = r"C:\Users\havit\.jiotv_go"
url1 = "http://localhost:5001/live/144.m3u8"
url2 = "http://localhost:5001/live/145.m3u8"

# Create stop events for each thread
stop_event1 = threading.Event()
stop_event2 = threading.Event()
stop_event3 = threading.Event()

# Create threads with different tasks
thread1 = threading.Thread(target=delayed_execute_command, args=(command, path, 0, stop_event1))
thread2 = threading.Thread(target=delayed_get_status_code, args=(url1, 4, stop_event2))
thread3 = threading.Thread(target=delayed_get_status_code, args=(url2, 4, stop_event3))

# Start the threads
thread1.start()
thread2.start()
thread3.start()

# Stop specific threads after some time
time.sleep(5)
stop_event2.set()  # Stop the second thread
stop_event3.set()  # Stop the third thread

# Wait for threads to complete
thread1.join()
thread2.join()
thread3.join()

print("Selected threads have been terminated.")