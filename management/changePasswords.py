#!/usr/bin/python

import subprocess

cmd = "parallel-scp -h pi-workers.txt -l pi passfile ~/"
print subprocess.check_output(cmd, shell=True)
cmd = "parallel-ssh -i -h pi-workers.txt -t 0 -p 100 -P sudo chpasswd < passfile"
print subprocess.check_output(cmd, shell=True)
cmd = "parallel-ssh -i -h pi-workers.txt -t 0 -p 100 -P rm passfile"
print subprocess.check_output(cmd, shell=True)
