#!/usr/bin/python
#
# built by gregg schudel
# - this model calls the "stackedIfMgr" top level service, which itself
#   calls two lower-levels services: myASAmgr and myCatmgr.
#
#
#    curl -X POST -u admin:admin --header "Content-Type:application/vnd.yang.data+json" \
#    http://172.26.163.113:8080/api/running/services \
#    -d '
#    {
#    "stackedIfMgr:stackedIfMgr":
#    [
#      {
#       "uid": "tix01",
#       "cat-device": "c0",
#       "asa-device": "asa0",
#       "cat-wan-ip": "10.1.1.1/30",
#       "cat-lan-ip": "172.16.16.1/24",
#       "asa-port": "80",
#       "asa-host": "172.16.16.16"
#       }
#    ]
#    }'
#
#  python create_service_cliqr.py -u tix01 -c c0 -a asa0 -w "10.1.1.1/30" -l "192.168.1.1/24" -t "172.16.16.1" -p 80
#
#
###########################################################################
# Add Devices to NCS managed devices list
###########################################################################

__author__ = 'gschudel'
import requests
from requests.auth import HTTPBasicAuth

import ncs
import sys
import getopt
import re
import csv


def create_set_value(request_id, th, path, value):
    return {'jsonrpc': '2.0', 'method': 'set_value', 'id': request_id,
            'params':
                {'th': th, 'path': path, 'value': value}
            }


def post(json, session_cookies):
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    url = 'http://172.26.163.113:8080/jsonrpc'
    return requests.post(url, json=json, auth=HTTPBasicAuth('admin', 'admin'),
                         headers=headers, cookies=session_cookies)


def createCliQrService(uid,catdev,asadev,catwanip,catlanip,asahost,asaport) :

    # print a couple things...
    print 'uid: %s' % (uid)
    print 'catdev: %s' % (catdev)
    print 'asadev: %s' % (asadev)
    print 'catwanip: %s' % (catwanip)
    print 'catlanip: %s' % (catlanip)
    print 'asahost: %s' % (asahost)
    print 'asaport: %s' % (asaport)


    try:
        addNewService(uid,catdev,asadev,catwanip,catlanip,asahost,asaport)

    finally:
        logoutCmd = {
            'jsonrpc': '2.0',
            'method': 'logout',
            'id': 1,
        }
        # Logout as admin/admin
        post(logoutCmd, session_cookies)



# add new service instance....
def addNewService(uid,catdev,asadev,catwanip,catlanip,asahost,asaport):

    print('received inputs: uid %s  catdev %s asadev %s  catwan %s catlan %s asahost %s asaport %s'
            % (uid,catdev,asadev,catwanip,catlanip,asahost,asaport))

    # Start transaction
    transRes = post(transCmd, session_cookies)
    if transRes.status_code != requests.codes.ok:
        print("error: " + str(transRes.status_code))
        exit()

    th = transRes.json()['result']['th']
    request_id = 3
    createService = {'jsonrpc': '2.0', 'method': 'create', 'id': request_id,
                    'params':
                        {'th': th, 'path': '/ncs:services/stackedIfMgr{"' + uid + '"}'}
                    }
    createRes = post(createService, session_cookies)
    print "created res: " + str(createRes.json())

    request_id = request_id + 1
    setCat1 = create_set_value(request_id, th,
                        '/ncs:services/stackedIfMgr{"' + uid + '"}/cat-device', catdev)
    request_id = request_id + 1
    setAsa1 = create_set_value(request_id, th,
                        '/ncs:services/stackedIfMgr{"' + uid + '"}/asa-device', asadev)
    request_id = request_id + 1
    setCat2 = create_set_value(request_id, th,
                        '/ncs:services/stackedIfMgr{"' + uid + '"}/cat-wan-ip', catwanip)
    request_id = request_id + 1
    setCat3 = create_set_value(request_id, th,
                        '/ncs:services/stackedIfMgr{"' + uid + '"}/cat-lan-ip', catlanip)
    request_id = request_id + 1
    setAsa2 = create_set_value(request_id, th,
                        '/ncs:services/stackedIfMgr{"' + uid + '"}/asa-host', asahost)
    request_id = request_id + 1
    setAsa3 = create_set_value(request_id, th,
                        '/ncs:services/stackedIfMgr{"' + uid + '"}/asa-port', asaport)



    # Send all sets at once
    setRes = post([setCat1, setAsa1, setCat2, setCat3, setAsa2, setAsa3], session_cookies)

    print("    set res: " + str(setRes.json()))

    request_id = request_id + 1
    validateCommit = {'jsonrpc': '2.0', 'method': 'validate_commit',
                      'id': request_id, 'params': {'th': th}}

    # Validate what we sent
    VCRes = post(validateCommit, session_cookies)
    commitData = VCRes.json()
    print("validate res: " + str(commitData))

    request_id = request_id + 1

    if 'error' in commitData:
        print str(commitData)
        clear_validate = {'jsonrpc': '2.0', 'method': 'clear_validate_lock',
                          'id': request_id, 'params': {'th': th}}
        post(clear_validate, session_cookies)
    else:
        print "commiting"
        commit = {'jsonrpc': '2.0', 'method': 'commit', 'id': request_id,
                  'params': {'th': th}}
        post(commit, session_cookies)


# main...
#...............................................................................
def main(argv):

    uid = ''
    catdev = ''
    asadev = ''
    catwanip = ''
    catlanip = ''
    asahost = ''
    asaport = ''

    try:
        opts, args = getopt.getopt(argv,"h:u:c:a:w:l:t:p:",["uid=","catdev=","asadev=","catwan=","catlan=","asahost=","asaport=", ])

    except getopt.GetoptError:
        print 'unknown errors...'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'create_service_cliqr.py -u <uid> -c <catdev> -a <asadev> -w <catwan> -l <catlan> -t <asahost> -p <asaport>'
            sys.exit()
        elif opt in ("-u", "--uid"):
            uid = arg
        elif opt in ("-c", "--catdev"):
            catdev = arg
        elif opt in ("-a", "--asadev"):
            asadev = arg
        elif opt in ("-w", "--catwan"):
            catwanip = arg
        elif opt in ("-l", "--catlan"):
            catlanip = arg
        elif opt in ("-t", "--asahost"):
            asahost = arg
        elif opt in ("-p", "--asaport"):
            asaport = arg

    createCliQrService(uid,catdev,asadev,catwanip,catlanip,asahost,asaport)



if __name__ == '__main__':

    loginCmd = {
        'jsonrpc': '2.0',
        'method': 'login',
        'id': 1,
        'params': {
            'user': 'admin',
            'passwd': 'admin'
        }
    }

    # Login as admin/admin
    #...............................................................................
    loginR = requests.post('http://172.26.163.113:8080/jsonrpc', json=loginCmd,
                           auth=HTTPBasicAuth('admin', 'admin'),
                           headers={'Content-type': 'application/json',
                                    'Accept': 'application/json'})

    # Get cookies
    #...............................................................................
    session_cookies = loginR.cookies

    transCmd = {
        'jsonrpc': '2.0',
        'method': 'new_trans',
        'id': 1,
        'params':
            {'db': 'running',
             'mode': 'read_write',
             'tag': 'create cliqr'}
    }

    main(sys.argv[1:])
