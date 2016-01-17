#!/usr/bin/python

import os.path
import subprocess
import sys
from random import randint

states = ["florida", "ohio", "illinois", "indiana", "michigan", "missouri", "virginia", "kentucky", "california", "texas"]
cities = ["miami", "cincinnati", "chicago", "cleveland", "columbus", "springfield", "detroit", "richmond", "urbana", "champaign"]
presidents = ["lincoln", "washington", "jefferson", "taft", "madison", "coolidge", "roosevelt", "truman", "monroe", "adams"]
nuts = ["peanut", "walnut", "almond", "macademia", "filbert", "brazil", "pistachio", "pine", "pumpkin", "sunflower"]
items = ["stapler", "pencil", "pen", "notebook", "glass", "cabinet", "fork", "spoon", "knife", "mug"]

v = randint(0, 9)
w = randint(0, 9)
x = randint(0, 9)
y = randint(0, 9)
z = randint(0, 9)

password = states[v] + cities[w] + presidents[x] + nuts[y] + items[z]

username = sys.argv[1]

if (os.path.isfile("pi-users.txt")):
    fin = open("pi-users.txt", 'r')
else:
    subprocess.check_output("cp pi-roster.txt pi-users.txt", shell=True)
    fin = open("pi-users.txt", 'r')

tenantList = {}
tenantCount = {}
ipaddress = {}
macaddress = {}
port = {}

for line in fin:
    # Line format: cc:cc:cc:cc:cc:06 wistful_silver_fox 192.168.0.16 20844
    tokens = line.split()
    tenants = len(tokens) - 4
    userlist = tokens[4:]
    tenantList[tokens[1]] = userlist
    tenantCount[tokens[1]] = tenants
    ipaddress[tokens[1]] = tokens[2]
    macaddress[tokens[1]] = tokens[0]
    port[tokens[1]] = tokens[3]
    
machine = min(tenantCount, key=tenantCount.get)
tenantList[machine].append(username)
tenantCount[machine] = tenantCount[tokens[1]] + 1

print "Creating new account on " + machine + " " + ipaddress[machine]

cmd = "parallel-ssh -H " + ipaddress[machine] + " -t 0 -p 100 -P sudo mkdir /home/" + username
print cmd
cmd = "parallel-ssh -H " + ipaddress[machine] + " -t 0 -p 100 -P sudo useradd -d /home/" + username + " " + username
print cmd
cmd = "parallel-ssh -H " + ipaddress[machine] + " -t 0 -p 100 -P \"echo -e \\\"" + username + ":" + password + "\\\" | sudo chpasswd\""
print cmd
cmd = "parallel-ssh -H " + ipaddress[machine] + " -t 0 -p 100 -P sudo chage -d 0 " + username
print cmd
cmd = "parallel-scp -H " + ipaddress[machine] + " -l pi base_dir/bash_profile /home/ ~/bash_profile"
print cmd
cmd = "parallel-ssh -H " + ipaddress[machine] + " -t 0 -p 100 -P sudo cp bash_profile ~" + username + "/.bash_profile"
print cmd

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

fout.close()

fin.close()

fout = open("pi-users.txt", 'w')
for key in tenantList:
    fout.write(macaddress[key] + " " + key + " " + ipaddress[key] + " " + port[key])
    for tenant in tenantList[key]:
        fout.write(" " + tenant)
    fout.write("\n")

fout.close()
