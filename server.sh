#!/usr/bin/env bash
set -x
# setup on streaming server

cd /proj/QoESDN
git clone https://github.com/CSc579s22/SABR.git
git clone https://github.com/CSc579s22/cloudlab_SABR.git
git clone https://github.com/CSc579s22/AStream.git
git clone https://github.com/CSc579s22/SDN-OpenNetMon.git
cd SDN-OpenNetMon
git submodule update --init --recursive
mkdir -p pox/ext/opennetmon
git clone https://github.com/TUDelftNAS/SDN-OpenNetMon pox/ext/opennetmon

cd /tmp/

# install basic dependencies
sudo apt update && sudo apt install -y zsh mongodb vim screen apache2 build-essential libssl-dev libffi-dev htop
sudo systemctl enable mongodb apache2
sudo systemctl restart mongodb apache2

# install R
sudo apt update
sudo apt install -y software-properties-common dirmngr
wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | sudo tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc
sudo add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"
sudo apt install r-base -y

# install forecast package for R
# https://github.com/robjhyndman/forecast
sudo apt install -y libz-dev libssl-dev libxml2-dev libcurl4-openssl-dev gfortran libblas-dev liblapack-dev
sudo Rscript -e "install.packages('forecast', dependencies = TRUE)"

# install python3 and rpy2
sudo apt -y install python3 python3-dev python3-pip
sudo pip install rpy2\[all\] pymongo scapy scapy_http netifaces

# install python2 and pip2 for arima and opennetmon
sudo apt -y install python2 python2-dev
wget https://bootstrap.pypa.io/pip/2.7/get-pip.py
sudo python2 get-pip.py
sudo /usr/bin/python -m pip install requests pymongo numpy scipy

sudo apt install -y libreadline-dev libbz2-dev liblzma-dev libpcre2-dev
sudo pip install 'pandas<0.19' 'rpy2<2.9.0'

# Prepare mpd file for streaming
cd /var/www/html
sudo wget -r --no-parent --reject "index.html*" http://ftp.itec.aau.at/datasets/DASHDataset2014/BigBuckBunny/2sec/
sudo cp /proj/QoESDN/cloudlab_SABR/server/BigBuckBunny_2s_mod* /var/www/html/ftp.itec.aau.at/datasets/DASHDataset2014/BigBuckBunny/2sec/
for i in `seq 1 50`;
do
        sudo mkdir /var/www/html/BigBuckBunny_2s_mod$i
        sudo ln -s /var/www/html/ftp.itec.aau.at/ /var/www/html/BigBuckBunny_2s_mod$i/ftp.itec.aau.at
done

cd /proj/QoESDN/cloudlab_SABR/server
python3 create_mpdinfo.py

# start opennetmon controller
cd /proj/QoESDN/SDN-OpenNetMon/pox
sudo ./pox.py openflow.of_01 --port=1234 log --file=opennetmon.log,w opennetmon.startup

# start ARIMA forecast
cp /proj/QoESDN/SABR/controllerSABR/arima.py /proj/QoESDN/SDN-OpenNetMon/pox/ext/
cd /proj/QoESDN/SDN-OpenNetMon/pox
sudo ./pox.py openflow.of_01 --port=1235 log --file=arima.log,w arima

# start listening requests for caching
cd /proj/QoESDN/cloudlab_SABR/server
sudo python3 http_capture.py

# setup on streaming clients
cd /tmp/
sudo apt install -y python3 python3-dev python3-pip python2 python2-dev
wget https://bootstrap.pypa.io/pip/2.7/get-pip.py
sudo python2 get-pip.py
sudo /usr/bin/python -m pip install urllib3 httplib2 pymongo netifaces requests numpy sortedcontainers
