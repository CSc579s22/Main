#!/usr/bin/env bash
set -x

# setup on streaming server
cd /tmp/ || exit

# install basic dependencies
sudo apt update
curl -fsSL https://get.docker.com -o get-docker.sh
sudo bash get-docker.sh

sudo apt update && sudo apt install -y curl zsh vim screen build-essential htop
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
