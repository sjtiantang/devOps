import telnetlib
from datetime import datetime
import time
from auth import username, password
import json

time_start = datetime.now()
sleeptime = 0.27

with open("devices.json", 'r') as f:
    devices = json.loads(f.read())

for name, device in devices.items():
    print("Operating {} ...".format(name))
    host = telnetlib.Telnet(device["IP"])
    host.read_until(b"Username:")
    host.write(username + b'\n')
    time.sleep(sleeptime)
    host.write(password + b'\n')
    time.sleep(sleeptime)
    host.read_very_eager().decode()

    for interface in device["INTERFACES"]:
        cmd = "dis int " + interface
        cmd = cmd.encode('utf-8')
        host.write(b"\n" + cmd + b"\n")
        time.sleep(sleeptime)
        
        command_output = host.read_very_eager().decode()
        while command_output.endswith("---- More ----"):
            host.write(b' ')
            time.sleep(sleeptime)
            command_output += host.read_very_eager().decode()
        data = command_output.split('\r\n')
        print(data[2])
            
print("Total runtime: {}".format(datetime.now() - time_start))

