import subprocess
import psutil
import signal
import sys
import time
import logging
import threading
import requests
import webbrowser

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ServerController(threading.Thread):
    def __init__(self, command, path):
        threading.Thread.__init__(self)
        self.command = command
        self.path = path
        self.process = None
        self.stop_event = threading.Event()

    def run(self):
        self.process = self.execute_command()
        if self.process:
            self.process.wait()

    def execute_command(self):
        try:
            if sys.platform == 'win32':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                process = subprocess.Popen(
                    self.command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.path,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                process = subprocess.Popen(
                    self.command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.path
                )
            logging.info(f"Started process with PID: {process.pid}")
            return process
        except subprocess.SubprocessError as e:
            logging.error(f"An error occurred while starting the process: {str(e)}")
            return None

    def stop(self):
        self.stop_event.set()
        if self.process:
            self.kill_process()

    def kill_process(self):
        if self.process:
            try:
                parent = psutil.Process(self.process.pid)
                children = parent.children(recursive=True)
                for child in children:
                    child.send_signal(signal.SIGTERM)
                parent.send_signal(signal.SIGTERM)
                self.process.terminate()
                logging.info(f"Process with PID {self.process.pid} and its children terminated successfully")
            except psutil.NoSuchProcess:
                logging.warning(f"Process with PID {self.process.pid} no longer exists")
            except Exception as e:
                logging.error(f"An error occurred while killing the process: {str(e)}")
            finally:
                self.process = None

def get_status_code(url):
    try:
        response = requests.get(url)
        return response.status_code
    except requests.RequestException as e:
        return f"An error occurred: {e}"
def delayed_get_status_code(url, delay):
    time.sleep(delay)
    status_code = get_status_code(url)
    print(f"Status code: {status_code}")
    return status_code


def main():
    # Example command - replace with your actual server start command
    command = r".\jiotv_go.exe run"
    path = r"C:\Users\havit\.jiotv_go"
    software_path = r"C:\Users\havit\kodi\kodi.exe"
    

    # Create and start the server controller

    url = "http://localhost:5001/live/144.m3u8"

    retry_count = 0
    server_controller = ServerController(command, path)
    server_controller.start()
    
    while retry_count < 3:

        if not server_controller.is_alive():
          
            server_controller = ServerController(command, path)
            server_controller.start()
        delay = 5 # Delay in seconds
        stuts_code = delayed_get_status_code(url, delay)
        if stuts_code == "200":
            logging.info("jio tv સફળતા પૂર્વક ચાલુ થયું છે")
            logging.info("software chalu kari rahya che...")
            subprocess.Popen([software_path])
            break
        else:
            logging.warning("jio tv ચાલુ  કરવામાં નિફળ")
            logging.info(f"ફરી પ્રયાસ કરવામાં આવે છે... પ્રયાસ નંબર: {retry_count + 1 }")
            server_controller.stop()
            server_controller.join()
            retry_count += 1

    if retry_count == 3:
        if not server_controller.is_alive():
            logging.info("પ્રયાસ પૂર્ણ થયું. ફરી થી login નિ પ્રક્રિયા સરુ કરવામાં આવશે")
            logout_command = r".\jiotv_go.exe l lo"
            logout_controller = ServerController(logout_command, path)
            logout_controller.start()
            logging.info("લોગિન system 3 seconds પછી ઓપન થશે")
            time.sleep(3)
            logout_controller.stop()
            logout_controller.join()

            logging.info("logout successsfuly..")
            server_controller = ServerController(command, path)
            server_controller.start()
            logging.info("લોગિન screen 2 seconds પછી ઓપન થશે")
            time.sleep(2)
            webbrowser.open("http://localhost:5001")
    

if __name__ == "__main__":
    main()