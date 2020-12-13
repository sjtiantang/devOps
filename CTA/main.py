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

sleeptime = 2


class Device:
    def __init__(self, item):
        self.interfaces = item["INTERFACES"]
        self.ip = item["IP"]
        if item["VENDOR"] == "HUAWEI":
            self.login = b"Username:"
            self.show = "dis int "
            self.more = "---- More ----"
            self.matchDown = ": DOWN"
            self.matchUp = "UP"
        elif item["VENDOR"] == "CISCO":
            self.login = b"Username:"
            self.show = "show int "
            self.more = "--More-- "
            # self.matchDown = "down"
            self.matchDown = "is down, line protocol is down"
            self.matchUp = "up"
        elif item["VENDOR"] == "JUNIPER":
            self.login = b"login:"
            self.show = "show interfaces "
            self.more = "---(more)---"
            self.matchDown = "is Down"
            self.matchUp = "Up"
        elif item["VENDOR"] == 'ZTE':
            self.login = b"Username:"
            self.show = "show interface "
            self.more = "--More--"
            self.matchDown = "is down,  line protocol is down"
            self.matchUp = "up"


def main():
    while True:
        time_start = datetime.now()

        # devices.json is a list of interfaces that need to be monitored, written in JSON format
        with open("devices_test.json", 'r') as f:
        # with open("devices.json", 'r') as f:
            devices = json.loads(f.read())

        # penalty.json contains a list of interfaces which are already down. When everytime the script runs and
        # detects a down interface, it will first look into the penalty list, if the down interface is already
        # in the penalty list, the script will not send email and report the outage. And when the down interface is recovered,
        # that interface will be removed from the penalty list
        with open("penalty.json", 'r') as f:
            penalty_dic = json.loads(f.read())

        # operation main body, it will run over each interface in devices.json and look for down interfaces.
        # the matching criteria ": DOWN" only match on interfaces that are in down state, but won't match on
        # interfaces in administrative down state. When calling the function "send_email", three parameters are passed - device name,
        # interface name, and description, therefore engineers will be noted of the detail of the outage
        for device_name in devices.keys():
            device = Device(devices[device_name])
            print("Operating {} ...".format(device_name))
            host = telnetlib.Telnet(device.ip)
            host.read_until(device.login)
            host.write(username + b'\n')
            time.sleep(sleeptime)
            host.write(password + b'\n')
            time.sleep(sleeptime)
            host.read_very_eager().decode()

            for interface in device.interfaces:
                device_interface_name = device_name + '_' + interface
                cmd = (device.show + interface).encode('utf-8')
                host.write(cmd + b"\n")
                time.sleep(sleeptime)

                command_output = host.read_very_eager().decode()
                while command_output.endswith(device.more):
                    host.write(b' ')
                    time.sleep(sleeptime)
                    command_output += host.read_very_eager().decode()
                data = command_output.split('\r\n')
                if device.matchDown in data[1] or device.matchDown in data[2]:
                    if device_interface_name not in penalty_dic:
                        print("Detect: " + device_interface_name + " down, processing to send email")
                        description = ""
                        for i in range(2, 5):
                            description = data[i] if "description" in data[i].lower() else ""
                        content = device_name + ": " + interface + " is down, please handle the issue ASAP!" + "\n" + description.lstrip()
                        send_email("NNI DOWN ALERT!!!!!", content)
                        penalty_dic[device_interface_name] = datetime.now()
                    else:
                        print(device_interface_name + " still in down state")
                elif device_interface_name in penalty_dic:
                    if device.matchUp in data[1]:
                        print(device_interface_name + " circuit recovered, pop out from penalty list")
                        penalty_dic.pop(device_interface_name)
                        content = device_name + ": " + interface + " recovered\nDown Time: " + penalty_dic[device_interface_name] + "\nRecover Time: {}".format(datetime.now())
                        send_email("NNI RECOVER NOTICE", content)
                else:
                    print(device_interface_name + " normal")
            host.close()

        with open("penalty.json", 'w') as f:
            f.write(json.dumps(penalty_dic))

        print("Total runtime: {}".format(datetime.now() - time_start))
        print("\n")
        time.sleep(0)


if __name__ == "__main__":
    main()
