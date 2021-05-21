#!/usr/bin/python3

import socket
import sys

# Specify each node ID
nodes_id = {
    1: 'eucz-00101',
    2: 'eucz-00102',
    3: 'eucz-00103',
    4: 'eucz-00104',
    5: 'eucz-00105',
    6: 'eucz-00106',
    7: 'eucz-00107',
    8: 'eucz-00108',
    9: 'eucz-00109',
    10: 'eucz-00110',
    11: 'eucz-00201',
    12: 'eucz-00301',
    13: 'eucz-00302',
    14: 'eucz-00303',
    15: 'eucz-00304',
    16: 'eude-00101',
    17: 'eude-00102',
    18: 'eude-00103',
    19: 'eude-00201',
    20: 'eude-00202',
    21: 'eucz-00401',
    22: 'ocau-00101',
    23: 'ocau-00201',
    24: 'ocau-00301',
    25: 'ocau-00302',
    26: 'ocau-00303',
    27: 'eucz-00501',
    28: 'eucz-00601',
    29: 'eucz-00701',
    30: 'eucz-00801'
}

# Number of available nodes
no_nodes = len(nodes_id)

# Specify the host to check for open socket ports
remoteServer = "localhost"
remoteServerIP = socket.gethostbyname(remoteServer)

# We also put in some error handling for catching errors
try:
    for port in range(10001, 10000+no_nodes):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((remoteServerIP, port))
        if result == 0:
            print(port)
        sock.close()
except (socket.gaierror, socket.error):
    sys.exit()
