import json
import requests
import ipaddress

url = f'https://stat.ripe.net/data/country-resource-list/data.json?resource=ir&resources=ipv4'
data = requests.get(url).json()

data = data['data']['resources']['ipv4']

for prefix in data:
    if str(prefix) != '91.237.254.0-91.238.0.255':
        net1 = ipaddress.ip_network(prefix)
        print(f'Checking for prefix {prefix}')
        for sub in data:
            if str(sub) != '91.237.254.0-91.238.0.255':
                net2 = ipaddress.ip_network(sub)
                if net1.supernet_of(net2) and net1 != net2:
                    data.remove(sub)
                    print(f'Removing {net2} because it\'s a subnet of {net1}')
                else:
                    print(f'Prefix {net1} is not a supernet of prefix {net2}')
print('done')