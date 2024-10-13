import subprocess
import time
import v4

command = r".\jiotv_go.exe run"
path = r"C:\Users\havit\.jiotv_go"

# Assuming v4.ServerController is a custom class, you might need to adjust this part
serverc = v4.ServerController(command, path)
serverc.start()

# Capture the output of the running process
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
stdout, stderr = process.communicate()

# Print the output
print("Standard Output:\n", stdout.decode())
print("Standard Error:\n", stderr.decode())

time.sleep(2)
serverc.stop()