import subprocess
import psutil
import signal
import sys
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def execute_command(command, path):
    try:
        if sys.platform == 'win32':
            # Windows-specific: Use CREATE_NO_WINDOW flag
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=path,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            # For non-Windows platforms
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=path
            )
        logging.info(f"Started process with PID: {process.pid}")
        return process
    except subprocess.SubprocessError as e:
        logging.error(f"An error occurred while starting the process: {str(e)}")
        return None

def kill_process(process):
    if isinstance(process, subprocess.Popen):
        try:
            parent = psutil.Process(process.pid)
            children = parent.children(recursive=True)
            for child in children:
                child.send_signal(signal.SIGTERM)
            parent.send_signal(signal.SIGTERM)
            process.terminate()
            logging.info(f"Process with PID {process.pid} and its children terminated successfully")
            return True
        except psutil.NoSuchProcess:
            logging.warning(f"Process with PID {process.pid} no longer exists")
            return False
        except Exception as e:
            logging.error(f"An error occurred while killing the process: {str(e)}")
            return False
    else:
        logging.error("Invalid process object")
        return False

def main():
    # Example command - replace with your actual server start command
    command = r".\jiotv_go.exe run"
    path = r"C:\Users\havit\.jiotv_go"

    # Start the server
    server_process = execute_command(command, path)
    if server_process is None:
        logging.error("Failed to start the server")
        return

    # Let the server run for a while
    logging.info("Server is running. Waiting for 10 seconds...")
    time.sleep(10)

    # Kill the server
    if kill_process(server_process):
        logging.info("Server has been stopped")
    else:
        logging.error("Failed to stop the server")

    # Check if the process has really been terminated
    if server_process.poll() is None:
        logging.warning("Process is still running. Forcing termination...")
        server_process.kill()
        logging.info("Process forcefully terminated")
    else:
        logging.info("Process has exited")

if __name__ == "__main__":
    main()