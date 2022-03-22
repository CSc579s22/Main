#!/usr/bin/env bash

# install openvswitch
#sudo apt update
#sudo apt install -y openvswitch-switch
#sudo systemctl enable openvswitch-switch
#sudo systemctl restart openvswitch-switch





# create ovs bridge
#sudo ovs-vsctl add-br br0

# add ports to ovs bridge accordingly
# sudo ifconfig eth1 0
# sudo ovs-vsctl add-port br0 eth1

# set bridge controller to pox
#sudo ovs-vsctl set-controller br0 tcp:<opennetmon controller ip>:6633

