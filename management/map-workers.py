#!/usr/bin/python

import subprocess
import re
import random

colors = ["orange", "blue", "green", "gold", "silver", "purple", "red", "gray", "magenta", "cyan"]
animals = ["lion", "tiger", "bear", "eagle", "fox", "elephant", "moose", "gator", "fish", "whale"]
moods = ["happy", "grumpy", "sleepy", "bashful", "sneezy", "dopey", "smart", "lazy", "wistful", "caffeinated"]

masterip = "urania.eecs.uc.edu"

print "Building a map of the network..."
subprocess.check_output('nmap -sn 192.168.0.0/24 -oG - | grep -v "^#" | cut -d " " -f 2 > all-hosts.txt', shell=True)
print "Isolating the head node..."
subprocess.check_output('grep -v \"^192.168.0.1$\" < all-hosts.txt > workers.txt', shell=True)
subprocess.check_output('cp workers.txt ~/', shell=True)

print "Isolating reachable hosts and removing the switch..."
subprocess.check_output('parallel-ssh -h workers.txt -t 0 -p 100 -P \'sudo ifconfig -a | grep HWaddr\' | grep HWaddr > pi-data.txt', shell=True)

inf = open('pi-data.txt', 'r')
template = open('template.xinetd', 'r')
fworkers = open('pi-workers.txt', 'w')
froster = open('pi-roster.txt', 'w')

xtemplate = template.readlines()
template.close()

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
    myname = moods[mood] + "-" + colors[color] + "-" + animals[animal]
    myport = "20" + str(mood) + str(color) + str(animal)
    rline = mymac + " " + myname + " " + myip + " " + myport
    froster.write(rline + "\n")
    fworkers.write(myip + "\n")
    servicename = "pi_" + myname
    # Build the xtemplate
    myxtemplate = list(xtemplate)
    filename = "worker_files/" + servicename
    fout = open(filename, "w")
    for xline in myxtemplate:
        xline = re.sub(r"\$MASTER\$", masterip, xline)
        xline = re.sub(r"\$IP\$", myip, xline)
        xline = re.sub(r"\$PORT\$", myport, xline)
        xline = re.sub(r"\$NAME\$", servicename, xline)
        fout.write(xline.rstrip() + "\n")
    fout.close()
    print "Setting up services for " + myname + " on " + myip + " port " + myport

    filename = "worker_files/hostname." + myname
    fout = open(filename, "w")
    fout.write(myname)
    fout.close

    filename = "worker_files/hosts." + myname
    fout = open(filename, "w")
    fout.write("127.0.0.1\tlocalhost\n")
    fout.write("::1\tlocalhost ip6-localhost ip6-loopback\n")
    fout.write("ff02::1\tip6-allnodes\n")
    fout.write("ff02::2\tip6-allrouters\n\n")
    fout.write("127.0.1.1\t" + myname + "\n")
    fout.close()

    xfilename = "worker_files/" + servicename
    subprocess.check_output("sudo cp " + xfilename + " /etc/xinetd.d/", shell=True)
    subprocess.check_output("parallel-scp -H " + myip + " worker_files/hostname." + myname + " ~/", shell=True)
    subprocess.check_output("parallel-scp -H " + myip + " worker_files/hosts." + myname + " ~/", shell=True)
    subprocess.check_output("parallel-ssh -i -H " + myip + " sudo cp hostname." + myname + " /etc/hostname", shell=True)
    subprocess.check_output("parallel-ssh -i -H " + myip + " sudo cp hosts." + myname + " /etc/hosts", shell=True)
    subprocess.check_output("parallel-ssh -i -H " + myip + " sudo /etc/init.d/hostname.sh", shell=True)
    
    fout = open ("worker_files/instructions_" + myname + ".txt", "w")
    fout.write("####################################\n")
    fout.write("# CS 2011 Group Login Instructions #\n")
    fout.write("####################################\n\n")
    fout.write("Your group has been assigned the machine " + myname + "\n\n")
    fout.write("To access " + myname + " you must execute the following command:\n")
    fout.write("\tssh -p " + myport + " " + masterip + " -l USERNAME\n\n")
    fout.write("Please include both the machine name, and port number " + myport + "\n")
    fout.write("in any e-mails for support requests.\n")
    fout.close()
    
    print "Rebooting " + myname + " at " + myip
    try:
        subprocess.check_output("parallel-ssh -i -H " + myip + " sudo reboot", shell=True)
    except subprocess.CalledProcessError as e:
        if (e.returncode != 4):
            print "Unknown exception on reboot!"
            exit(0)
        else:
            print myname + " reboot in progress"
    print "Cleaning up " + myname
    subprocess.check_output("rm worker_files/hosts." + myname, shell=True)
    subprocess.check_output("rm worker_files/hostname." + myname, shell=True)
            
print "Restarting xinetd"
subprocess.check_output("sudo /etc/init.d/xinetd restart", shell=True)
            
inf.close()
fworkers.close()
froster.close()
