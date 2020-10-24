import telnetlib
from datetime import datetime
import time
from auth import username, password
import json

time_start = datetime.now()
sleeptime = 0.27

with open("devices.json", 'r') as f:
    devices = json.loads(f.read())

with open("penalty.json", 'r') as f:
    penalty_dic = json.loads(f.read())

for device_name, device in devices.items():
    print("Operating {} ...".format(device_name))
    host = telnetlib.Telnet(device["IP"])
    host.read_until(b"Username:")
    host.write(username + b'\n')
    time.sleep(sleeptime)
    host.write(password + b'\n')
    time.sleep(sleeptime)
    host.read_very_eager().decode()

    for interface in device["INTERFACES"]:
        device_interface_name = device_name + '_' + interface
        cmd = ("dis int " + interface).encode('utf-8')
        host.write(b"\n" + cmd + b"\n")
        time.sleep(sleeptime)
        
        command_output = host.read_very_eager().decode()
        while command_output.endswith("---- More ----"):
            host.write(b' ')
            time.sleep(sleeptime)
            command_output += host.read_very_eager().decode()
        data = command_output.split('\r\n')
        if "device status : DOWN" in data[2] or "device status : DOWN" in data[3]:
            if not device_interface_name in penalty_dic:
                #send email operation
                penalty_dic[device_interface_name] = 43200

        if device_interface_name in penalty_dic:
            runtime = datetime.now() - time_start
            penalty_dic[device_interface_name] -= runtime
            if penalty_dic[device_interface_name] <= 0:
                penalty_dic.pop(device_interface_name)
        #print(data[2])

with open("penalty.json", 'w') as f:
    f.write(json.dumps(penalty_dic))
print("Total runtime: {}".format(datetime.now() - time_start))

