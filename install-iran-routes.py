#!/usr/bin/python3.7

# This file belongs to Behnam Yazdani, and I'm only hosting it here

import json
import requests
import time
from pprint import pprint
import pdb
# from icecream import ic
from netmiko import ConnectHandler  
import getpass

AllPrefixes = list()


#url = 'https://stat.ripe.net/data/bgp-updates/data.json?resource=46.143.32.0/19&starttime=2016-04-03T06:00&endtime=2016-04-03T12:00'
#url = 'https://stat.ripe.net/data/bgp-updates/data.json?resource=%s&starttime=%s&endtime=%s' %(prefix,Time1HAgo,TimeNow)
#url = f'https://stat.ripe.net/data/country-resource-list/data.json?resource=ir&resources=ipv4'
#url = f'https://stat.ripe.net/data/ris-prefixes/data.json?resource=43754&list_prefixes=true'

def GetLatestIPv4fromRIPESTAT() ->(list):
    url = f'https://stat.ripe.net/data/country-resource-list/data.json?resource=ir&resources=ipv4'
    data = requests.get(url).json()
    return data['data']['resources']['ipv4']

def WriteOutputToFile(FinalConfigs:set,Path:str,Filename:str):
    ItemsToWrite = set()
    for item in FinalConfigs:
        ItemsToWrite.add(f'{item}\n')
    with open(f'{Path}/{Filename}', 'w') as outfile:
        outfile.writelines(ItemsToWrite)
def UpdatePrefixes(FinalConfigs:list):
    # establish a connection to the device    
    ssh_connection = ConnectHandler(
        device_type='mikrotik_routeros',
        ip='192.168.20.1',
        port='810',
        username='admin',
        password=getpass.getpass(),
    )
    # enter enable mode
    ssh_connection.enable()
    #pdb.set_trace()
    #for ConfigItem in FinalConfigs:
    #    result = ssh_connection.send_command(ConfigItem)
    ssh_connection.send_config_set(FinalConfigs)
    ssh_connection.disconnect()

def main():
    IRANPREFIXLIST = GetLatestIPv4fromRIPESTAT()
    Config_Lines = list()
    for PREFIX in IRANPREFIXLIST:
        line = (f'/ip firewall address-list add address={PREFIX} comment=IRANPREFIXES list=IRAN-PREFIXES')
        Config_Lines.append(line)
    Path = './'
    Filename = 'configs.txt'
    WriteOutputToFile(Config_Lines,Path,Filename)
    UpdatePrefixes(Config_Lines)

def run():
    main()
if __name__ == '__main__':
    run()