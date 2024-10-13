import subprocess
import requests
import threading
import time

def get_status_code(url):
    try:
        response = requests.get(url)
        return response.status_code
    except requests.RequestException as e:
        return f"An error occurred: {e}"

def execute_command(command, path):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=path)
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e.stderr.decode('utf-8')}"

def delayed_execute_command(command, path, delay):
    time.sleep(delay)
    output = execute_command(command, path)
    print(output)

def delayed_get_status_code(url, delay):
    time.sleep(delay)
    status_code = get_status_code(url)
    print(f"Status code: {status_code}")

command = r".\jiotv_go.exe run"
path = r"C:\Users\havit\.jiotv_go"

# Checking 
url = "http://localhost:5001/live/144.m3u8"

# Example usage
if __name__ == "__main__":
    # Run the main command in a separate thread
    jiotv = threading.Thread(target=delayed_execute_command, args=(command, path, 0)).start()
    
    # Run get_status_code after a delay
    delay = 2 # Delay in seconds
    threading.Thread(target=delayed_get_status_code, args=(url, delay)).start()
    