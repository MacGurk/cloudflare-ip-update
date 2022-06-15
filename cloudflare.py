import requests
import logging
import sys

headers = {}
app_log = {}

def init(cloudflare_dns_api_token):
    global headers, app_log
    headers = {'Authorization': f'Bearer {cloudflare_dns_api_token}'}
    app_log = logging.getLogger("root")


def get_dns_records(zone):
    try:
        dns_records_json = requests.get(
            f"https://api.cloudflare.com/client/v4/zones/{zone['zone_id']}/dns_records?type=A",
            headers=headers
        ).json()
    except requests.exceptions.HTTPError as e:
        app_log.error('Could not establish a connection to cloudflare')
        app_log.error(e)
        sys.exit(1)
    return dns_records_json


def update_dns_record(zone, dns_record, current_ip):
    try:
        requests.patch(
            f"https://api.cloudflare.com/client/v4/zones/{zone['zone_id']}/dns_records/{dns_record['id']}",
            headers=headers,
            json={
                "type": "A", "name": dns_record["name"],
                "content": current_ip,
                "ttl": 120
            }
        )
        app_log.info(f'Updated record {dns_record["name"]} with IP {current_ip}')
    except requests.exceptions.HTTPError as e:
        app_log.error('Could not establish a connection to cloudflare')
        app_log.error(e)
        sys.exit(1)