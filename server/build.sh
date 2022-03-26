#!/usr/bin/env bash
echo "$1"
sudo docker build -t clarkzjw/sabrcontroller:"$1" .
sudo docker-compose up -d
