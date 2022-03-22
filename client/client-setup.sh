#!/bin/bash
cd /tmp/ || exit
sudo apt install -y python3 python3-dev python3-pip python2 python2-dev
wget https://bootstrap.pypa.io/pip/2.7/get-pip.py
sudo python2 get-pip.py
sudo /usr/bin/python -m pip install urllib3 httplib2 pymongo netifaces requests numpy sortedcontainers


sudo python2 dist/client/dash_client.py -m http://10.10.10.11/BigBuckBunny_2s_mod1/ftp.itec.aau.at/datasets/DASHDataset2014/BigBuckBunny/2sec/BigBuckBunny_2s_mod1.mpd -p basic