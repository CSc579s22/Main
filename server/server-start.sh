#!/usr/bin/env bash

# start opennetmon controller
cd /proj/QoESDN/SDN-OpenNetMon/pox || exit
screen -d -m -S opennetmon sudo ./pox.py openflow.of_01 --port=6633 log --file=opennetmon.log,w opennetmon.startup

# start ARIMA forecast
cd /proj/QoESDN/SDN-OpenNetMon/pox || exit
screen -d -m -S arima sudo ./pox.py openflow.of_01 --port=6634 log --file=arima.log,w arima

# start listening requests for caching
cd /proj/QoESDN/cloudlab_SABR/server || exit
screen -d -m -S http_capture sudo python3 http_capture.py