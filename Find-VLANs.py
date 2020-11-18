import subprocess
# from subprocess import Popen, PIPE, DEVNULL
import json
import requests
import time
import ipaddress
import sys
from netmiko import Netmiko
from netmiko import ConnectHandler
import re
import ipcalc
# from napalm import get_network_driver

import urllib3
urllib3.disable_warnings()

# Getting prefixes parameters
access_token = '23aeaef183b3e35177802cadbe781660474129e5'
server = '10.104.55.39'
module = 'ipam'
get_section = 'prefixes'
get_base = 'https://' + server + '/api/' + module + '/' + get_section +'/'
request_headers = {'Authorization': 'Token ' + access_token}

# Getting desired prefixes for scanning
get_request = get_base + '?limit=0&within=10.114.0.0%2F16'
get_response = requests.get(get_request, headers=request_headers, verify=False)

prefixes = json.loads(get_response.text)

print('OK, I got the results (', len(prefixes['results']), '), writing it to a file just in case...')
time.sleep(1)

with open('prefixes.json', 'w') as f:
     json.dump(prefixes, f, indent=4)

answer = None

Paya_connection = Netmiko(host='10.20.118.2', port='23', username='ip_planning', password='MTC@1234', device_type='cisco_ios_telnet')

pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

for prefix in prefixes['results']:
     temp = 0
     net = ipaddress.ip_network(prefix['prefix'])
     bare_network = str(net).split('/')[0]
     output = Paya_connection.send_command('sh ip route vrf vpn_wiom ' + bare_network)
     print('-------------------------')
     print('Prefix is ' + str(net))
     output = str(output).splitlines()
     for line in output:
          if ', from' in line:
               next_hop = line.strip()
               next_hop = pattern.search(next_hop)[0]
          if str(net) in line:
               sanity_check = line
     print('Sanity: ' + sanity_check)
     print('NH (MPLS): ' + next_hop)
     if '10.20' in next_hop:
          next_hop = ipaddress.ip_address(next_hop) + 1
     elif '10.101' in next_hop:
          next_hop = ipaddress.ip_address(next_hop) + 512
     print('NH (OM): ' + str(next_hop))
     # print(str(output))
     if str(net) in sanity_check:
          print('Sanity check passed')
          vlan_id = prefix['vlan']['vid']
          print('VLAN ID should be', vlan_id)
          next_hop_router = Netmiko(host=str(next_hop), port='23', username='ip_planning', password='MTC@1234', device_type='cisco_ios_telnet')
          output = next_hop_router.send_command('sh ip route vrf vpn_wiom ' + bare_network)
          output = str(output).splitlines()
          for line in output:
               if 'directly connected' in line:
                    print('directly connected')
                    print(line)
                    if str(vlan_id) in line:
                         print('VLAN ID stored in NetBox seems correct')
                         temp = 1
                    if not temp:
                         print('VLAN ID incorrect')
                         temp = input()
               elif 'Known via ' in line:
                    print('Needs more checking')
     else:
               print('Something is wrong')
               sys.exit()
     print('-------------------------')
     time.sleep(1)


Paya_connection.disconnect()