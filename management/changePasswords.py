#!/usr/bin/python

import subprocess

newPass = raw_input('Please enter a new password for the Pis:')
cmd = "parallel-ssh -i -h pi-workers.txt -t 0 -p 100 -P sudo chpasswd pi:"+ newPass
print subprocess.check_output(cmd, shell=True)
