# PiClusterTools
Tools for Building and maintaining an educational Raspberry Pi Cluster

## History of the Project and Acknowledgements

The original idea for this project started in 2012 after reading about [a project at Boise State](http://coen.boisestate.edu/ece/raspberry-pi/) in which a PhD student named Joshua Kiepert assembled a [Raspberry Pi cluster](http://coen.boisestate.edu/ece/files/2013/05/Creating.a.Raspberry.Pi-Based.Beowulf.Cluster_v2.pdf) for his research.  A new professor at the University of Miami, I had been assigned the task of modernize the curriculum for EEN 312, their course on Microprocessors.  As both a fan of the Raspberry Pi, and out of a desire to engage the students with a real RISC architecture I built my own cluster with the help of my then graduate student, Alejandro Gutierrez.

Since the original cluster I've since begun building a set of scripts, images, and plans, to make it easier for others to replicate this work, incorporating the [hard work](https://darrenjw2.wordpress.com/2015/09/07/raspberry-pi-2-cluster-with-nat-routing/) of Professor Darren Wilinison of Newcastle University, along with my own modifications.

Thanks to Dwight Divine of the Illinois Natural History Survey, and Miguel Gavidia of the University of Miami College of Law for their help and input during this process.

## Update Jan 17, 2016

I've implemented [XKCD style passwords](http://xkcd.com/936/) for new users using a word file of 235,886 words.
For compatibility reasons, I've included this word file, as I'm finding not all systems (including Pis) have a good
source of English words.

## Update Jan 16, 2016, 8:03pm

Added automated user deployment through 'register-user.py'

## Update Jan 16, 2016

Scripts are in place to automatically scan the network, sort out the switch and head node, name the pis, and build xinetd services as well as
instructions for the students on how to login, you can run this as 'management/map-workers.py', similarly 'management/demap-workers.py' tears
all the services down and kills the instructions and config files.

### Todos
* Automated account creation, setup, and node assignment

## Update Jan 15, 2016

I'm working to get a full, standalone, build that is easy to deploy.  This is still very much a work in progress in early alpha.
