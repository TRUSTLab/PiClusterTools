#!/usr/bin/python

import subprocess
import re
import random
import sqlite3 as lite
import xkcdPasswd

def registerMac(macAddr, myip):
    myname = nameFromMac(macAddr)
    myport = portFromMac(macAddr)
    myrow = (macAddr, myip, myname, myport)

    db = lite.connect('pi-workers.db')
    with db:
        cur = db.cursor()
        cur.execute("INSERT INTO pis VALUES(?, ?, ?, ?)", myrow)

def isUserRegistered(username):
    db = lite.connect('pi-users.db')

    with db:
        db.row_factory = lite.Row
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE UserName=:username", {"username": username})
        db.commit()

        data = cur.fetchall()

    return(len(data) > 0)

def isMacRegistered(macAddr):
    db = lite.connect('pi-workers.db')

    with db:
        db.row_factory = lite.Row
        cur = db.cursor()
        cur.execute("SELECT * FROM pis WHERE MacAddr=:Mac", {"Mac": macAddr})
        db.commit()
        
        data = cur.fetchall()

    return(len(data) > 0)

def registerUserOnMin(username):
    entry = findMinMachine()
    name = str(entry["Name"])
    mac = str(entry["MacAddr"])
    users = int(entry["Users"])
    ip = str(entry["Ip"])

    passwd = xkcdPasswd.genPasswd(4)
    
    createAccount(username, name, ip, passwd)
    registerUser(name, mac, users, username)

    genUserInstructions(username, name, passwd)

def deleteUser(username):
    server = deregisterUser(username)

    db = lite.connect('pi-users.db')

    with db:
        cur = db.cursor()
        cur.execute('SELECT Ip FROM pis WHERE Name=?', (server,))
        db.commit()

        ip = cur.fetchall()[0][0]

    deleteAccount(username, ip)

    cmd = "rm user_files/instructions_" + username + ".txt"    
    subprocess.check_output(cmd, shell=True)
    
def registerUser(name, macaddr, users, username):

    db = lite.connect('pi-users.db')

    users = users + 1
    
    with db:
        cur = db.cursor()
        cur.execute('UPDATE pis SET Users=? WHERE Name=?', (users, name))
        cur.execute('INSERT INTO users VALUES(?, ?, ?)', (username, macaddr, name))

def deregisterUser(username):

    db = lite.connect('pi-users.db')

    with db:
        db.row_factory = lite.Row
        cur = db.cursor()
        cur.execute('SELECT Name FROM users WHERE UserName=?', (username,))
        db.commit()

        server = cur.fetchall()[0]["Name"]

        cur.execute('SELECT * FROM pis WHERE Name=?', (server,))
        db.commit()
        piInfo = cur.fetchall()
        users = int(piInfo[0]["Users"]) - 1
        
        cur.execute('UPDATE pis SET Users=? WHERE Name=?', (users, server))
        db.commit()

        cur.execute('DELETE FROM users WHERE UserName=?', (username,))
        db.commit()

    return(server)
        
def createAccount(username, machine, ipaddress, password):
    print "Creating new account on " + machine + " " + ipaddress
    cmd = "parallel-ssh -H " + ipaddress + " -t 0 -p 100 -P sudo mkdir /home/" + username
    subprocess.check_output(cmd, shell=True)
    cmd = "parallel-ssh -H " + ipaddress + " -t 0 -p 100 -P sudo chown " + username + " /home/" + username
    subprocess.check_output(cmd, shell=True)
    cmd = "parallel-ssh -H " + ipaddress + " -t 0 -p 100 -P sudo chgrp " + username + " /home/" + username
    subprocess.check_output(cmd, shell=True)        
    cmd = "parallel-ssh -H " + ipaddress + " -t 0 -p 100 -P sudo useradd -d /home/" + username + " " + username
    subprocess.check_output(cmd, shell=True)
    cmd = "parallel-ssh -H " + ipaddress + " -t 0 -p 100 -P \"echo -e \\\"" + username + ":" + password + "\\\" | sudo chpasswd\""
    subprocess.check_output(cmd, shell=True)
    cmd = "parallel-ssh -H " + ipaddress + " -t 0 -p 100 -P sudo chage -d 0 " + username
    subprocess.check_output(cmd, shell=True)
    cmd = "parallel-scp -H " + ipaddress + " -l pi base_dir/bash_profile ~/bash_profile"
    subprocess.check_output(cmd, shell=True)
    cmd = "parallel-ssh -H " + ipaddress + " -t 0 -p 100 -P sudo cp bash_profile ~" + username + "/.bash_profile"
    subprocess.check_output(cmd, shell=True)

def deleteAccount(username, ipaddress):
    cmd = "parallel-ssh -H " + ipaddress + " -t 0 -p 100 -P sudo userdel " + username
    subprocess.check_output(cmd, shell=True)
    cmd = "parallel-ssh -H " + ipaddress + " -t 0 -p 100 -P sudo rm -rf /home/" + username
    subprocess.check_output(cmd, shell=True)
    
def findMinMachine():
    db = lite.connect('pi-users.db')

    with db:
        db.row_factory = lite.Row
        cur = db.cursor()
        cur.execute("SELECT * FROM pis")
        rows = cur.fetchall()

    return min(rows, key = lambda t: t[3])

def genUserInstructions(username, machine, password):

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

def initUserTable():

    pis = {}
    ips = {}
    
    pidb = lite.connect('pi-workers.db')
    with pidb:
        pidb.row_factory = lite.Row
        cur = pidb.cursor()

        cur.execute("SELECT * FROM pis")
        rows = cur.fetchall()

        for row in rows:
            pis[row["Name"]] = row["MacAddr"]
            ips[row["Name"]] = row["Ip"]
            
    db = lite.connect('pi-users.db')
    with db:
        db.row_factory = lite.Row
        cur = db.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users(UserName TEXT, MacAddr TEXT, Name TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS pis(MacAddr TEXT, Name TEXT, Ip TEXT, Users INTEGER)")

        for name in pis:
            mac = pis[name]
            ip = ips[name]
            users = 0
            cur.execute("SELECT count(*) FROM pis WHERE Name=:Name", {"Name": name})
            count = cur.fetchone()[0]
            if (count == 0):
                cur.execute("INSERT INTO pis VALUES(?, ?, ?, ?)", (mac, name, ip, users))
        
def initTable():
    db = lite.connect('pi-workers.db')
    with db:
        cur = db.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS pis(MacAddr TEXT, Ip TEXT, Name TEXT, Port TEXT)")

def nameFromMac(macAddr):
    colors = ["orange", "blue", "green", "gold", "silver", "purple", "red", "gray", "magenta", "cyan"]
    animals = ["lion", "tiger", "bear", "eagle", "fox", "elephant", "moose", "gator", "fish", "whale"]
    moods = ["happy", "grumpy", "sleepy", "bashful", "sneezy", "dopey", "smart", "lazy", "wistful", "caffeinated"]

    macAddr = int(macAddr.replace(':', ''), 16)
    random.seed(macAddr)
    color = random.randint(0,9)
    animal = random.randint(0,9)
    mood = random.randint(0,9)
    myname = moods[mood] + "-" + colors[color] + "-" + animals[animal]

    return myname

def portFromMac(macAddr):
    macAddr = int(macAddr.replace(':', ''), 16)
    random.seed(macAddr)
    color = random.randint(0,9)
    animal = random.randint(0,9)
    mood = random.randint(0,9)

    myport = "20" + str(mood) + str(color) + str(animal)

    return myport

def buildServices(macAddr, myip, masterip):
    myname = nameFromMac(macAddr)
    myport = portFromMac(macAddr)
    servicename = "pi_" + myname

    template = open('template.xinetd', 'r')
    xtemplate = template.readlines()
    template.close()

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
