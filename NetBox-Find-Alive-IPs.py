# Version 1.0

import subprocess
from subprocess import Popen, PIPE, DEVNULL
import json
import requests
import time
import ipaddress
# import sys

import urllib3
urllib3.disable_warnings()

#Ping variables
ping_count = '3'
parameter = '-c'
interval = '0.2'
timeout = '1'
interface = 'ens160'
toping = {}

#List of alive IP addresses
alive_hosts = []

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

print('Now, let\'s find alive IP addresses of each prefix')
time.sleep(1)

# Pinging every IP address in each prefix to find alive IP addresses
for prefix in prefixes['results']:
    print('Total number of alive IP addresses: ', len(alive_hosts))
    print('\nGoing through prefix: ', prefix['prefix'])
    prefix = ipaddress.ip_network(prefix['prefix'])
    for i in prefix.hosts():
        i = str(i)
        toping[i] = subprocess.Popen(['ping', '-I', interface, parameter, ping_count, '-W', timeout, '-i', interval, i], stdout=DEVNULL)
    while toping:
        for i, proc in toping.items():
            if proc.poll() is not None:
                del toping[i]
                hostalive = proc.returncode
                if hostalive == 0:
                    alive_hosts.append(i)
                    print('IP address', i, 'is alive')
                else:
                    print('IP address', i, 'is not alive')
                break


# checking for presense of IP addresses in NetBox
ip_address = None
section = 'ip-addresses'
post_base = 'https://' + server + '/api/' + module + '/' + section +'/'

# Change VRF ID  and mask for each VRF
ip_obj = {
     "address": "",
     "vrf": 1,
     "status": "active",
     "description": "USED"
     }
mask = '/26'

auto_add = 0
answer = None
get_section = 'ip-addresses'
get_base = 'https://' + server + '/api/' + module + '/' + get_section +'/'

for ip in alive_hosts:
    get_request = get_base + '?address=' + str(ip)
    get_response = requests.get(get_request, headers=request_headers, verify=False)
    netbox_ip = json.loads(get_response.text)
    with open('answer.json', 'a') as f:
               json.dump(netbox_ip, f, indent=4)
               f.write('\n')
    if netbox_ip['count']:
        print('Found ', netbox_ip['results'][0]['address'])
        continue
    else:
        print('IP address ', ip, 'was not found in NetBox. May I add it to the IPAM? [y/n/q/a]')
        if (answer == 'a' or answer == 'A'):
          auto_add = 1
        else:
          answer = input()
        if (answer == 'y' or answer == 'Y' or answer == 'a' or answer == 'A' or auto_add == 1):
            ip_obj['address'] = str(ip) + mask
            post_response = requests.post(post_base, json=ip_obj, headers={'Authorization': 'Token ' + access_token}, verify=False)
            post_result = json.loads(post_response.text)
            with open('result.json', 'a') as f:
                json.dump(post_result, f, indent=4)
                f.write('\n')
        elif (answer == 'q' or answer == 'Q'):
            raise SystemExit(0)
        else:
            continue