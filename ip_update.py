import sys
import os
import ipaddress
import logger
import logging
import json
import requests
import cloudflare


def get_current_ip():
    app_log = logging.getLogger("root")
    try:
        ip_request = requests.get('https://api.ipify.org')
    except requests.exceptions.HTTPError as e:
        app_log.error('Could not establish a connection to cloudflare')
        app_log.error(e)
        sys.exit(1)
    return ip_request.text


def read_config(script_dir):
    app_log = logging.getLogger("root")
    config_file_name = "config.json"
    config_file_path = os.path.join(script_dir, config_file_name)

    try:
        with open(config_file_path) as jsonfile:
            config = json.load(jsonfile)
    except IOError:
        app_log.error("config.json not found")
        sys.exit(1)

    if not config.get("zones"):
        app_log.error("'zones' must be defined in config.json")
        sys.exit(1)

    if not config.get("cloudflare_api_token"):
        app_log.error("'cloudflare_api_token' must be defined in config.json")
        sys.exit(1)

    return config


def main():
    script_dir = os.path.dirname(__file__)

    logger.init(script_dir)
    app_log = logging.getLogger("root")

    app_log.info('\n=============\nRun IP update\n=============')
    app_log.info('load config from config.json')

    config = read_config(script_dir)
    zones = config.get("zones")

    app_log.info('\nStarting new IP update on cloudflare DNS\n=============')
    cloudflare.init(config.get("cloudflare_api_token"))

    app_log.info('Getting current IP')
    current_ip = get_current_ip()
    app_log.info(f'Current IP is: {current_ip}')

    for zone in zones:
        app_log.info(f'Getting A records of zone {zone["name"]}')
        dns_records_json = cloudflare.get_dns_records(zone)
        app_log.info(f'{str(len(dns_records_json["result"]))} A records found')

        for dns_record in dns_records_json["result"]:
            app_log.info(f'Checking record {dns_record["name"]}')
            if dns_record["content"] != current_ip and not ipaddress.ip_address(dns_record["content"]).is_private:
                cloudflare.update_dns_record(zone, dns_record, current_ip)
            else:
                app_log.info(f'No update needed for record {dns_record["name"]}, current IP {current_ip} and DNS '
                             f'record IP {dns_record["content"]} are the same')


if __name__ == "__main__":
    main()
