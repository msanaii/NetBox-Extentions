import json
import requests
import time
import ipaddress

with open('prefixes.json', 'rt') as f:
    prefixes = json.load(f)
    print(type(prefixes))