#!/usr/bin/env bash

# install openvswitch
sudo apt update
sudo apt install -y openvswitch-switch
sudo systemctl enable openvswitch-switch
sudo systemctl restart openvswitch-switch
sudo ovs-vsctl --version

# set bridge controller
#sudo ovs-vsctl set-controller br0 tcp:<opennetmon controller ip>:6633
