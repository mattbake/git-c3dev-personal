#!/usr/bin/env python

import os
import urllib2


HOST = os.environ['nso_host']

BASE_URL = HOST + '/restconf/data'
AUTH_HANDLER = urllib2.HTTPBasicAuthHandler()
AUTH_HANDLER.add_password(realm='restconf',
                          uri=BASE_URL,
                          user='admin',
                          passwd=os.environ['nso_password'])

OPENER = urllib2.build_opener(AUTH_HANDLER, urllib2.HTTPHandler(debuglevel=1))
urllib2.install_opener(OPENER)


DELREQ = urllib2.Request(BASE_URL + '/cloud-interconnect=the-customer',
                         headers={'Accept': 'application/yang-data+json'})
DELREQ.get_method = lambda: 'DELETE'
try:
    OPENER.open(DELREQ)
except urllib2.HTTPError as excp:
    print("Error: ", excp.reason)
