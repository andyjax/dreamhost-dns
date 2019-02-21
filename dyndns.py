#!/usr/bin/env python

import json
import sys
import requests
import urllib3
#import uuid
import os
import os.path
import logging
import time

required_config_fields = ['accessKey', 'dreamhostUrl', 'ipUrl', 'dynamicUrl']
optional_config_fields = ['logfile']
config = {}

def read_config(config_file):
    global config
    print("Reading configuration from {}".format(config_file))
    with open(config_file, 'r') as fh:
        config = json.load(fh)

    for f in required_config_fields:
        if f not in config:
            raise LookupError("No value for {}".format(f))


def get_ip():
    response = requests.get(config['ipUrl'])
    ip = response.json()['ip']
    return ip


def send_dreamhost_command(cmd, **kwargs):
    params = "?key={}&cmd={}&format=json".format(config['accessKey'], cmd)
    for key, value in kwargs.items():
        params += "&{}={}".format(key, value)
    response = requests.get(config['dreamhostUrl'] + '/' + params)
    return response.json()


def get_dns_ip():
    dns = send_dreamhost_command('dns-list_records')
    ip = ''
    for dns_record in dns['data']:
        if dns_record['record'] == config['dynamicUrl'] and dns_record['type'] == 'A':
            ip = dns_record['value']
            logging.info('Found record for {} with IP {}'.format(config['dynamicUrl'], ip))
    return ip


def update_ip(old_ip, new_ip):
    resp = send_dreamhost_command('dns-remove_record', record=config['dynamicUrl'], type='A', value=old_ip)
    if resp['result'] == 'error':
        logging.error('Failed to remove old record. Error: {}'.format(resp['data']))
    resp = send_dreamhost_command('dns-add_record', record=config['dynamicUrl'], type='A', value=new_ip)
    if resp['result'] == 'error':
        logging.error('Failed to add record for {} with IP {}'.format(config['dynamicUrl'], new_ip))
    else:
        logging.info('Changed IP for {} from {} to {}'.format(config['dynamicUrl'], old_ip, new_ip))


def main():

    if len(sys.argv) == 2:
        config_file = sys.argv[1]
    else:
        print("Usage: python dyndns.py credential.json")
        sys.exit(2)
    read_config(config_file)

    if 'logfile' in config:
        logfile = config['logfile']
    else:
        logfile = ''

    logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO, format='%(message)s')
    logging.info('** Starting {} on {} **'.format(os.path.basename(sys.argv[0]), time.asctime()))
    logging.info('Using config file {}'.format(config_file))

    ip = get_ip()
#    print("Current IP: {}".format(ip))
    old_ip = get_dns_ip()
#    print("Current DNS: {}".format(old_ip))

    if ip == old_ip:
        logging.info("IP address has not changed. No change to DNS needed.")
    else:
#        print("Need to update DNS, IP has changed")
        update_ip(old_ip, ip)
    logging.info('** Ending {} on {} **'.format(os.path.basename(sys.argv[0]), time.asctime()))


if __name__ == "__main__":
    main()