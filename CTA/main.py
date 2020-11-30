"""
the purpose of this script is to monitor the NNI interfaces listed in devices.json, it will utilize the
telnetlib library to connect to remote devices and send CLI commands like "display interface". No configuration
commands are send, therefore it is ensured that no network impact will be made by this script

telnetlib: help with connecting to remote device using Telnet, send CLI command to remote device and obtain device output
auth.py contains the authentication information for log on devices
send_email is the function for sending emails
"""
import telnetlib
from datetime import datetime
import time
from auth import username, password
import json
from send_email import send_email

sleeptime = 1

while True:
    time_start = datetime.now()

    # devices.json is a list of interfaces that need to be monitored, written in JSON format
    with open("devices_test.json", 'r') as f:
        devices = json.loads(f.read())

    # penalty.json contains a list of interfaces which are already down. When everytime the script runs and
    # detects a down interface, it will first look into the penalty list, if the down interface is already
    # in the penalty list, the script will not send email and report the outage. And when the down interface is recovered,
    # that interface will be removed from the penalty list
    with open("penalty.json", 'r') as f:
        penalty_dic = json.loads(f.read())

    # operation main body, it will run over each interface in devices.json and look for down interfaces.
    # the matching criteria ": DOWN" only match on interfaces that are in down state, but won't match on
    # interfaces in administrative down state. When calling the function "send_email", two parameters are passed - device name
    # and interface name, therefore engineers will be noted of the detail of the outage
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
            cmd = ("show int " + interface).encode('utf-8')
            host.write(b"\n" + cmd + b"\n")
            time.sleep(sleeptime)

            command_output = host.read_very_eager().decode()
            while command_output.endswith("--More-- "):
                host.write(b' ')
                time.sleep(sleeptime)
                command_output += host.read_very_eager().decode()
            data = command_output.split('\r\n')
            # if ": DOWN" in data[2] or ": DOWN" in data[3]:
            if "down" in data[2]:
                if device_interface_name not in penalty_dic:
                    send_email([device_name, interface])
                    penalty_dic[device_interface_name] = True
            elif device_interface_name in penalty_dic:
                print(device_interface_name + "当前恢复正常，从penalty list中弹出")
                penalty_dic.pop(device_interface_name)
            else:
                print(device_interface_name + "正常")
        host.close()

    with open("penalty.json", 'w') as f:
        f.write(json.dumps(penalty_dic))

    print("Total runtime: {}".format(datetime.now() - time_start))
    print("\n")

    time.sleep(1)
