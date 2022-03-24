#!/usr/bin/env bash
set -x

# setup on streaming server
cd /tmp/ || exit

# install basic dependencies
sudo apt update && DEBIAN_FRONTEND=noninteractive sudo apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo bash get-docker.sh

sudo apt update && sudo apt install -y curl zsh vim screen build-essential htop
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# install R
#sudo apt update
#sudo apt install -y software-properties-common dirmngr
#wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | sudo tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc
#sudo add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"
#sudo apt install r-base -y

# install forecast package for R
# https://github.com/robjhyndman/forecast
#sudo apt install -y libz-dev libssl-dev libxml2-dev libcurl4-openssl-dev gfortran libblas-dev liblapack-dev
#sudo Rscript -e "install.packages('forecast', dependencies = TRUE)"

# install python3 and rpy2
#sudo apt -y install python3 python3-dev python3-pip
#sudo /usr/bin/python3 -m pip install pymongo scapy scapy_http netifaces

# install python2 and pip2 for arima and opennetmon
#sudo apt -y install python2 python2-dev libreadline-dev libbz2-dev liblzma-dev libpcre2-dev
#wget https://bootstrap.pypa.io/pip/2.7/get-pip.py
#sudo python2 get-pip.py
#sudo /usr/bin/python -m pip install requests pymongo numpy scipy 'pandas<0.19' 'rpy2<2.9.0'
#sudo rm get-pip.py


# install ryu
#cd /proj/QoESDN/ryu || exit
#sudo apt update && sudo apt install python3 python3-dev python3-pip
#/usr/bin/python3 -m pip install .


# Prepare mpd file for streaming
#sudo mkdir -p /var/www/html/ftp.itec.aau.at/datasets/DASHDataset2014/BigBuckBunny/
#cd /proj/QoESDN/videos || exit
#sudo cp -r ftp.itec.aau.at/datasets/DASHDataset2014/BigBuckBunny/2sec/ /var/www/html/ftp.itec.aau.at/datasets/DASHDataset2014/BigBuckBunny/2sec/
#sudo cp /proj/QoESDN/cloudlab_SABR/server/mpd/BigBuckBunny_2s_mod* /var/www/html/ftp.itec.aau.at/datasets/DASHDataset2014/BigBuckBunny/2sec/
#for i in $(seq 1 50);
#do
#  sudo mkdir /var/www/html/BigBuckBunny_2s_mod"$i"
#  sudo ln -s /var/www/html/ftp.itec.aau.at/ /var/www/html/BigBuckBunny_2s_mod"$i"/ftp.itec.aau.at
#done

#cd /proj/QoESDN/cloudlab_SABR/server || exit
#sudo python create_mpdinfo.py
