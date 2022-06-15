import sys
import os
import ipaddress
import logging
import json
import requests

script_dir = os.path.dirname(__file__)

log_file_name = "ip_update.log"
log_file_path = os.path.join(script_dir, log_file_name)

logging.basicConfig(filename=log_file_path, format='%(asctime)s %(message)s', level=logging.DEBUG)

logging.info('\n=============\nRun IP update\n=============')

logging.info('load config from config.json')

config_file_name = "config.json"
config_file_path = os.path.join(script_dir, config_file_name)

try:
    with open(config_file_path) as jsonfile:
        config = json.load(jsonfile)
except IOError:
    logging.error("config.json not found")
    sys.exit(1)

if config.get("zones"):
    zones = config.get("zones")
else:
    logging.error("'zones' must be defined in config.json")

if config.get("cloudflare_api_token"):
    cloudflare_dns_api_token = config.get("cloudflare_api_token")
else:
    logging.error("'cloudflare_api_token' must be defined in config.json")

logging.info('\nStarting new IP update on cloudflare DNS\n=============')
headers = {'Authorization': f'Bearer {cloudflare_dns_api_token}'}


def get_current_ip():
    logging.info('Getting current IP')
    ip_request = requests.get('https://api.ipify.org')
    return ip_request.text


current_ip = get_current_ip()
logging.info('Current IP is: ' + current_ip)

for zone in zones:
    logging.info('Getting A records of zone ' + zone["name"])
    try:
        dns_records_json = requests.get(
            f"https://api.cloudflare.com/client/v4/zones/{zone['zone_id']}/dns_records?type=A", headers=headers).json()
    except Exception:
        logging.error('Could not establish a connection to cloudflare')
    logging.info('' + str(len(dns_records_json["result"])) + ' A records found')
    for dns_record in dns_records_json["result"]:
        logging.info('Checking record ' + dns_record["name"])
        if dns_record["content"] != current_ip and not ipaddress.ip_address(dns_record["content"]).is_private:
            try:
                requests.patch(f"https://api.cloudflare.com/client/v4/zones/{zone['zone_id']}/dns_records/{dns_record['id']}", headers=headers, json={
                "type": "A", "name": dns_record["name"], "content": current_ip, "ttl": 120})
                logging.info('Updated record ' + dns_record["name"] + ' with IP ' + current_ip)
            except Exception:
                logging.error('Could not establish a connection to cloudflare')

        else:
            logging.info('No update needed for record ' + dns_record["name"] + ' , current IP ' + current_ip + ' and DNS record IP ' + dns_record["content"] + ' are the same')
