#!/usr/bin/python

import subprocess
import time

host = "192.168.0.12"
reboot = "parallel-ssh -H " + host + " sudo shutdown -r now"
testAlive = "parallel-ssh -H " + host + " -P uptime"

try:
    subprocess.check_output(reboot, shell=True)
except:
    pass
    
maxWait = 10

for i in range(0,maxWait):
    try:
        subprocess.check_output(testAlive, shell=True)
    except subprocess.CalledProcessError as e:
        print e.output + " " + str(e.returncode)
        print "Host " + host + " unreachable... trying " + str(maxWait - i + 1) + " more times..."
        time.sleep(1)
    else:
        print "Host " + host + " rebooted successfully in " + str(i) + " cycles!"
        break
