import flet as ft
import subprocess
import psutil
import signal
import sys
import time
import logging
import threading
import requests
import webbrowser

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

class JioTVControllerApp(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.command = r".\jiotv_go.exe run"
        self.path = r"C:\Users\havit\.jiotv_go"
        self.software_path = r"C:\Users\havit\kodi\kodi.exe"
        self.url = "http://localhost:5001/live/144.m3u8"
        self.server_controller = None
        self.status_text = ft.Text("Server Status: Initializing...", color=ft.colors.ORANGE)
        self.log_text = ft.Text("Initializing...")
        self.start_button = ft.ElevatedButton("Start Server", on_click=self.start_server, disabled=True)
        self.stop_button = ft.ElevatedButton("Stop Server", on_click=self.stop_server, disabled=True)
        self.open_kodi_button = ft.ElevatedButton("Open Kodi", on_click=self.open_kodi, disabled=True)
        self.logout_button = ft.ElevatedButton("Logout", on_click=self.logout, disabled=True)
        self.retry_count = 0
        self.max_retries = 3

    def did_mount(self):
        self.start_server_auto()

    def build(self):
        return ft.Column([
            ft.Text("JioTV Controller", size=24, weight=ft.FontWeight.BOLD),
            self.status_text,
            ft.Row([self.start_button, self.stop_button, self.open_kodi_button, self.logout_button]),
            ft.Container(
                content=self.log_text,
                width=400,
                height=200,
                border=ft.border.all(1, ft.colors.GREY_400),
                border_radius=5,
                padding=10,
            ),
        ])

    def update_log(self, message):
        self.log_text.value += f"\n{message}"
        self.update()

    def start_server_auto(self):
        self.update_log("Automatically starting server...")
        self.start_server(None)

    def start_server(self, e):
        self.server_controller = ServerController(self.command, self.path)
        self.server_controller.start()
        self.update_log("Starting server...")
        self.start_button.disabled = True
        self.stop_button.disabled = False
        self.status_text.value = "Server Status: Starting"
        self.status_text.color = ft.colors.ORANGE
        self.update()
        self.check_server_status()

    def stop_server(self, e):
        if self.server_controller:
            self.server_controller.stop()
            self.server_controller.join()
            self.update_log("Server stopped.")
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.open_kodi_button.disabled = True
        self.logout_button.disabled = True
        self.status_text.value = "Server Status: Stopped"
        self.status_text.color = ft.colors.RED
        self.update()

    def check_server_status(self):
        def check():
            time.sleep(5)
            status_code = get_status_code(self.url)
            if status_code == 200:
                self.update_log("JioTV started successfully.")
                self.status_text.value = "Server Status: Running"
                self.status_text.color = ft.colors.GREEN
                self.open_kodi_button.disabled = False
                self.logout_button.disabled = False
                self.open_kodi(None)  # Automatically open Kodi
            else:
                self.update_log(f"Failed to start JioTV. Status code: {status_code}")
                self.retry_count += 1
                if self.retry_count < self.max_retries:
                    self.update_log(f"Retrying... Attempt {self.retry_count + 1}")
                    self.stop_server(None)
                    self.start_server(None)
                else:
                    self.status_text.value = "Server Status: Error"
                    self.status_text.color = ft.colors.RED
                    self.start_button.disabled = False
                    self.update_log("Max retries reached. Please check your configuration and try again.")
                    self.logout(None)  # Automatically logout after max retries
            self.update()

        threading.Thread(target=check).start()

    def open_kodi(self, e):
        subprocess.Popen([self.software_path])
        self.update_log("Opening Kodi...")

    def logout(self, e):
        self.update_log("Logging out...")
        logout_command = r".\jiotv_go.exe l lo"
        logout_controller = ServerController(logout_command, self.path)
        logout_controller.start()
        time.sleep(3)
        logout_controller.stop()
        logout_controller.join()
        self.update_log("Logged out successfully.")
        self.status_text.value = "Server Status: Logged Out"
        self.status_text.color = ft.colors.BLUE
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.open_kodi_button.disabled = False
        self.logout_button.disabled = True
        self.retry_count = 0
        self.update()
        webbrowser.open("http://localhost:5001")

def main(page: ft.Page):
    page.title = "JioTV Controller"
    page.padding = 20
    controller = JioTVControllerApp()
    page.add(controller)

ft.app(target=main)