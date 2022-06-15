import sys
import os
import ipaddress
import logging
from logging.handlers import RotatingFileHandler
import json
import requests

script_dir = os.path.dirname(__file__)

log_file_name = "ip_update.log"
log_file_path = os.path.join(script_dir, log_file_name)

logging_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logging_handler = RotatingFileHandler(log_file_path, mode="a", maxBytes=5*1024*1024, backupCount=10, encoding=None, delay=False)
logging_handler.setFormatter(logging_formatter)
logging_handler.setLevel(logging.INFO)

logger = logging.getLogger("root")
logger.setLevel(logging.INFO)
logger.addHandler(logging_handler)

logger.info('\n=============\nRun IP update\n=============')

logger.info('load config from config.json')

config_file_name = "config.json"
config_file_path = os.path.join(script_dir, config_file_name)

try:
    with open(config_file_path) as jsonfile:
        config = json.load(jsonfile)
except IOError:
    logger.error("config.json not found")
    sys.exit(1)

if config.get("zones"):
    zones = config.get("zones")
else:
    logger.error("'zones' must be defined in config.json")

if config.get("cloudflare_api_token"):
    cloudflare_dns_api_token = config.get("cloudflare_api_token")
else:
    logger.error("'cloudflare_api_token' must be defined in config.json")

logger.info('\nStarting new IP update on cloudflare DNS\n=============')
headers = {'Authorization': f'Bearer {cloudflare_dns_api_token}'}


def get_current_ip():
    logger.info('Getting current IP')
    ip_request = requests.get('https://api.ipify.org')
    return ip_request.text


current_ip = get_current_ip()
logger.info('Current IP is: ' + current_ip)

for zone in zones:
    logger.info('Getting A records of zone ' + zone["name"])
    try:
        dns_records_json = requests.get(
            f"https://api.cloudflare.com/client/v4/zones/{zone['zone_id']}/dns_records?type=A", headers=headers).json()
    except Exception:
        logger.error('Could not establish a connection to cloudflare')
    logger.info('' + str(len(dns_records_json["result"])) + ' A records found')
    for dns_record in dns_records_json["result"]:
        logger.info('Checking record ' + dns_record["name"])
        if dns_record["content"] != current_ip and not ipaddress.ip_address(dns_record["content"]).is_private:
            try:
                requests.patch(f"https://api.cloudflare.com/client/v4/zones/{zone['zone_id']}/dns_records/{dns_record['id']}", headers=headers, json={
                "type": "A", "name": dns_record["name"], "content": current_ip, "ttl": 120})
                logger.info('Updated record ' + dns_record["name"] + ' with IP ' + current_ip)
            except Exception:
                logger.error('Could not establish a connection to cloudflare')

        else:
            logger.info('No update needed for record ' + dns_record["name"] + ' , current IP ' + current_ip + ' and DNS record IP ' + dns_record["content"] + ' are the same')
