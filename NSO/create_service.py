#!/usr/bin/env python

import os
import urllib2
import json
import time


print("ENV=", os.environ)
NSO_HOST = os.environ['nso_host']

BASE_URL = NSO_HOST + '/restconf/data'
AUTH_HANDLER = urllib2.HTTPBasicAuthHandler()
AUTH_HANDLER.add_password(realm='restconf',
                          uri=BASE_URL,
                          user='admin',
                          passwd=os.environ['nso_password'])

OPENER = urllib2.build_opener(AUTH_HANDLER, urllib2.HTTPHandler(debuglevel=1))
urllib2.install_opener(OPENER)

TPAYLOAD = """{{
    "cloud-interconnect:cloud-interconnect": {{
        "name": "the-customer",
        "dc-esc": "escDMZ",
        "cloud-esc": "escAWS",
        "cloud-router-public-ip": "{}",
        "cloud-router-private-ip": "{}",
        "cloud-vpc-private-network": "{}",
        "dc-router-public-ip": "{}",
        "dc-router-private-ip": "{}",
        "dc-router-private-network": "{}"
    }}
}}""".format(os.environ['cloud_public_ip'],
             os.environ['cloud_router_private_ip'],
             os.environ['cloud_private_network'],
             os.environ['dc_public_ip'],
             os.environ['dc_private_ip'],
             os.environ['dc_private_network'])

PUTREQ = urllib2.Request(BASE_URL + '/cloud-interconnect=the-customer',
                         headers={'Content-Type': 'application/yang-data+json',
                                  'Accept': 'application/yang-data+json'},
                         data=TPAYLOAD)
PUTREQ.get_method = lambda: 'PUT'
OPENER.open(PUTREQ)

REQ = urllib2.Request(BASE_URL+'/cloud-interconnect=the-customer/plan/'
                      'component=self/state=ready/status',
                      headers={"Accept": "application/yang-data+json"})
while True:
    TXT = urllib2.urlopen(REQ).read()
    JDATA = json.loads(TXT)
    print(JDATA)
    status = JDATA['cloud-interconnect:status']
    if status == 'reached':
        break
    elif status == 'failed':
        raise Exception("CloudInterconnect failed")
    time.sleep(5)
