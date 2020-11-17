import subprocess
from subprocess import Popen, PIPE, DEVNULL
import json
import requests
import time
import ipaddress
import sys
from netmiko import ConnectHandler
# from napalm import get_network_driver

device = {
    'device_type': 'cisco_xr',
    'host':   '10.101.3.1',
    'username': 'ip_planning',
    'password': 'MTC@1234'
}

net_connect = ConnectHandler(**device)
output = net_connect.send_command('show route vrf vpn_wiom 10.111.0.0/27')
print(output.splitlines()[2])