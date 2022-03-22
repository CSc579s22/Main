#!/usr/bin/env bash

cd /proj/QoESDN || exit
git clone https://github.com/CSc579s22/SABR.git
git clone https://github.com/CSc579s22/cloudlab_SABR.git
git clone https://github.com/CSc579s22/AStream.git
git clone https://github.com/CSc579s22/SDN-OpenNetMon.git
cd SDN-OpenNetMon || exit
git submodule update --init --recursive
mkdir -p pox/ext/opennetmon
git clone https://github.com/CSc579s22/SDN-OpenNetMon pox/ext/opennetmon
cp /proj/QoESDN/SABR/controllerSABR/arima.py /proj/QoESDN/SDN-OpenNetMon/pox/ext/

cd /var/www/html || exit
sudo wget -r --no-parent --reject "index.html*" http://ftp.itec.aau.at/datasets/DASHDataset2014/BigBuckBunny/2sec/
