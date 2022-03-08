#!/usr/bin/env bash
set -x

# install openvswitch
sudo apt update
sudo apt install -y openvswitch-switch
sudo systemctl enable openvswitch-switch
sudo systemctl restart openvswitch-switch

# create ovs bridge
sudo ovs-vsctl add-br br0

# add ports to ovs bridge accordingly
sudo ovs-vsctl add-port br0 eth1

# set bridge controller to pox
sudo ovs-vsctl set-controller br0 tcp:<ip>:<port>
