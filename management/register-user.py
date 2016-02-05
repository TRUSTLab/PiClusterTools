#!/usr/bin/python

import os.path
import subprocess
import sys
from random import randint
import xkcdPasswd
import PiClusterTools as pct


username = sys.argv[1]

pct.initUserTable()

if (pct.isUserRegistered() == False):
    pct.registerUserOnMin(username)
