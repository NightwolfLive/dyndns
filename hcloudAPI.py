from __future__ import annotations
from hcloud import Client
from hcloud.zones import Zone, ZoneRRSet, ZoneRecord
from requests import get
import yaml, time

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

token = ""
zone_name = ""
#The TTL is currently limited to 60 Seconds by Hetzner
time_to_live = 60
subdomain = ""

def refresh_data():
    global token, zone_name, subdomain
    token = config['api']['token']
    zone_name = config['api']['zone_name']
    subdomain = config['api']['subdomain']


def get_dns_record_ip():
    rrset = client.zones.get_rrset(zone=Zone(name=zone_name), name=subdomain, type="A")
    return rrset.records[0].value


def update_dns_record(ip):
    action = client.zones.set_rrset_records(
        rrset=ZoneRRSet(
            zone=Zone(name=zone_name),
            name=subdomain,
            type="A",
        ),
        records=[
            ZoneRecord(value=str(ip), comment="")
        ],
    )

    action.wait_until_finished()
    if action.status == "success":
        return "DNS Record update successfull!"
    else:
        return f"error: {action.status}"
    

refresh_data()
client = Client(token=token)

last_ip = get_dns_record_ip()

while True:
    try:
        ip = format(get('https://api.ipify.org').content.decode('utf8'))
    except:
        print('HTTP request failed! This may be because of an ongoing IP Address Change')

    if ip != last_ip:
        print(f'IP address change detected. Requesting DNS record update.')
        print(update_dns_record(ip))
    time.sleep(1)
    refresh_data()
    last_ip = ip