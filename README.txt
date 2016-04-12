===========
Swarmpose
===========

Swarmpose provides an easy way to run multi-layered applications
on a Docker Swarm (much like Docker Compose)

===========
Prequisites
===========
* Docker Swarm network
* `--cluster-store` and `--cluster-advertise` needs to be set in the docker engine. (Required for the overlay network)

===========
Swarm Example
===========
#Start daemon - all
docker daemon -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock --cluster-store=consul://<consul-ip>:8500 --cluster-advertise=<node-ip>:2375

#Start consul
docker run -d -p 8500:8500 --name=consul progrium/consul -server -bootstrap

#Start swarm manager
docker run -d -p 993:993 swarm manage -H :993 --advertise <node-ip>:993 consul://<consul-ip>:8500

#Join swarm - all
docker run -d swarm join --advertise=<node-ip>:2375 consul://<consul-ip>:8500

===========
Usage
===========
usage: swarmpose [-h] -c CONFIG [-q QUIET] [-n NETWORK] {start,stop,cc} ...

a script to start an application on a distributed system

positional arguments:
  {start,stop,cc}
    start               start an application
    stop                stop an application
    cc                  clear all containers from swarm

optional arguments:
  -h, --help            show this help message and exit
  -q QUIET, --quiet QUIET
                        Supress messages from the script
  -n NETWORK, --network NETWORK
                        Name of the overlay network

required arguments:
  -c CONFIG, --config CONFIG
                        yaml file describing the application