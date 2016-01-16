#!/usr/bin/python

import subprocess
import re
import random

colors = ["orange", "blue", "green", "gold", "silver", "purple", "red", "black", "brown", "white"]
animals = ["lion", "tiger", "bear", "eagle", "fox", "elephant", "moose", "gator", "fish", "whale"]
moods = ["happy", "grumpy", "sleepy", "bashful", "sneezy", "dopey", "smart", "lazy", "wistful", "caffinated"]

inf = open('pi-data.txt', 'r')

# Parse the data on live, accessible nodes.  The data will be in the form:
# 192.168.0.12: eth0      Link encap:Ethernet  HWaddr cc:cc:cc:cc:cc:01
for line in inf:
    tokens = re.split('\s+', line)
    myip = tokens[0].replace(':', '')
    mymac = tokens[5]
    macId = int(mymac.replace(':', ''), 16)
    random.seed(macId)
    color = random.randint(0,9)
    animal = random.randint(0,9)
    mood = random.randint(0,9)
    myname = moods[mood] + "_" + colors[color] + "_" + animals[animal]
    myport = "20" + str(mood) + str(color) + str(animal)
    rline = mymac + " " + myname + " " + myip + " " + myport
    servicename = "pi_" + myname

    # Delete the xtemplate
    print "Taking down " + servicename
    cmd = "sudo rm -f worker_files/" + servicename
    subprocess.check_output(cmd, shell=True)
    cmd = "sudo rm -f /etc/xinetd.d/" + servicename
    subprocess.check_output(cmd, shell=True)
    cmd = "sudo rm -f worker/files/instructions_" + myname + ".txt"
    subprocess.check_output(cmd, shell=True)


    
print "Restarting xinetd"
subprocess.check_output("sudo /etc/init.d/xinetd restart", shell=True)
            
inf.close()

