import json
import requests
import time
import ipaddress
import sys

import urllib3
urllib3.disable_warnings()

access_token = '23aeaef183b3e35177802cadbe781660474129e5'
server = '10.104.55.39'
module = 'ipam'
get_section = 'prefixes'
get_base = 'https://' + server + '/api/' + module + '/' + get_section +'/'
post_section = 'ip-addresses'
post_base = 'https://' + server + '/api/' + module + '/' + post_section +'/'
request_headers = {'Authorization': 'Token ' + access_token}

get_request = get_base + '?limit=0&within=10.115.0.0%2F16'

get_response = requests.get(get_request, headers=request_headers, verify=False)

prefixes = json.loads(get_response.text)

print('OK, I got the results (' + str(len(prefixes['results'])) + '), writing it to a file just in case...')
time.sleep(1)

with open('prefixes.json', 'w') as f:
     json.dump(prefixes, f, indent=4)

print('Now, let\'s add gateways to each prefix')
time.sleep(1)

gw_obj = {
     "address": "",
     "vrf": 1,
     "status": "reserved",
     "description": "Gateway"
     }

auto_add = 0
answer = None
mask = '/27'

for prefix in prefixes['results']:
     net = ipaddress.ip_network(prefix['prefix'])
     print('The prefix is: ' + str(net) + ' and the first IP address will be: ' + str(net[1]) + '. May I add it to the IPAM? [y/n/q/a]')
     if (answer == 'a' or answer == 'A'):
          auto_add = 1
     else:
          answer = input()
     if (answer == 'y' or answer == 'Y' or answer == 'a' or answer == 'A' or auto_add == 1):
          gw_obj['address'] = str(net[1]) + mask
          post_response = requests.post(post_base, json=gw_obj, headers={'Authorization': 'Token ' + access_token}, verify=False)
          post_result = json.loads(post_response.text)
          with open('result.json', 'a') as f:
               json.dump(post_result, f, indent=4)
               f.write('\n')
     elif (answer == 'q' or answer == 'Q'):
          sys.exit()
     else:
          continue

# TODO: find if gateway exists and show a message depending on the return error
# TODO: delete if exists and add with proper attributes