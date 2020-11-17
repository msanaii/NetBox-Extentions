import subprocess
from subprocess import Popen, PIPE, DEVNULL
import json
import requests
import time
import ipaddress
import sys
import netmiko
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

