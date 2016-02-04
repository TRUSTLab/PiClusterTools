#!/usr/bin/python

import os.path
import subprocess
import sys
from random import randint
import xkcdPasswd
import PiClusterTools as pct


password = xkcdPasswd.genPasswd(4)

username = sys.argv[1]

pct.initUserTable()

entry = pct.findMinMachine()
name = str(entry["Name"])
mac = str(entry["MacAddr"])
users = int(entry["Users"])
ip = str(entry["Ip"])

tenantList[machine].append(username)
tenantCount[machine] = tenantCount[tokens[1]] + 1

print "Creating new account on " + machine + " " + ipaddress[machine]

cmd = "parallel-ssh -H " + ipaddress[machine] + " -t 0 -p 100 -P sudo mkdir /home/" + username
subprocess.check_output(cmd, shell=True)
cmd = "parallel-ssh -H " + ipaddress[machine] + " -t 0 -p 100 -P sudo useradd -d /home/" + username + " " + username
subprocess.check_output(cmd, shell=True)
cmd = "parallel-ssh -H " + ipaddress[machine] + " -t 0 -p 100 -P \"echo -e \\\"" + username + ":" + password + "\\\" | sudo chpasswd\""
subprocess.check_output(cmd, shell=True)
cmd = "parallel-ssh -H " + ipaddress[machine] + " -t 0 -p 100 -P sudo chage -d 0 " + username
subprocess.check_output(cmd, shell=True)
cmd = "parallel-scp -H " + ipaddress[machine] + " -l pi base_dir/bash_profile ~/bash_profile"
subprocess.check_output(cmd, shell=True)
cmd = "parallel-ssh -H " + ipaddress[machine] + " -t 0 -p 100 -P sudo cp bash_profile ~" + username + "/.bash_profile"
subprocess.check_output(cmd, shell=True)

fout = open("user_files/instructions_" + username + ".txt", "w")
finst = open("worker_files/instructions_" + machine + ".txt", "r")

for line in finst:
    fout.write(line)
finst.close()

fout.write("\nYour username is:\t\t" + username + "\n")
fout.write("Your temporary password is:\t" + password + "\n")
fout.write("\nYou must change this password when you first log in. Be sure to share the new\n")
fout.write("password with your fellow group mates, as it will be changed for everyone when the\n")
fout.write("first person logs in.\n")
fout.write("\nOnce you have changed your password, you will have to log back in with your new password.\n")

fout.close()

fin.close()

fout = open("pi-users.txt", 'w')
for key in tenantList:
    fout.write(macaddress[key] + " " + key + " " + ipaddress[key] + " " + port[key])
    for tenant in tenantList[key]:
        fout.write(" " + tenant)
    fout.write("\n")

fout.close()
