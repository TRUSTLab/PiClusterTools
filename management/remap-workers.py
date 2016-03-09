#!/usr/bin/python

import subprocess
import re
import random
import PiClusterTools as pct
import sqlite3 as lite

masterip = "urania.eecs.uc.edu"

print "Building a map of the network..."
subprocess.check_output('nmap -sn 192.168.0.0/24 -oG - | grep -v "^#" | cut -d " " -f 2 > all-hosts.txt', shell=True)
print "Isolating the head node..."
subprocess.check_output('grep -v \"^192.168.0.1$\" < all-hosts.txt > workers.txt', shell=True)

print "Isolating reachable hosts and removing the switch..."
subprocess.check_output('parallel-ssh -h workers.txt -t 0 -p 100 -P \'sudo ifconfig -a | grep HWaddr\' | grep HWaddr > pi-data.txt', shell=True)

inf = open('pi-data.txt', 'r')

pct.initTable()

# Parse the data on live, accessible nodes.  The data will be in the form:
# 192.168.0.12: eth0      Link encap:Ethernet  HWaddr cc:cc:cc:cc:cc:01
for line in inf:
    tokens = re.split('\s+', line)
    myip = tokens[0].replace(':', '')
    mymac = tokens[5]
    myname = pct.nameFromMac(mymac)
    myport = pct.portFromMac(mymac)

    pct.buildServices(mymac, myip, masterip)
    
print "Restarting xinetd"
subprocess.check_output("sudo /etc/init.d/xinetd restart", shell=True)
inf.close()

