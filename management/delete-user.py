#!/usr/bin/python

import PiClusterTools as pct

username = sys.argv[1]

if (pct.isUserRegistered()):
    pct.deleteUser(username)
