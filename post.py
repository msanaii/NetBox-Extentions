import json
import requests
import time
import ipaddress
import sys

access_token = '23aeaef183b3e35177802cadbe781660474129e5'
server = '10.104.55.39'
module = 'ipam'
section = 'ip-addresses'
request_base = 'https://' + server + '/api/' + module + '/' + section +'/'

gw = '1.1.1.1/32'

gw_obj = {
     "address": "",
     "vrf": 1,
     "status": "reserved",
     "description": "Gateway"
     }

gw_obj['address'] = gw

request = request_base
response = requests.post(request, json=gw_obj, headers={'Authorization': 'Token ' + access_token}, verify=False)

result = json.loads(response.text)

with open('answer.json', 'w') as f:
     json.dump(result, f, indent=4)