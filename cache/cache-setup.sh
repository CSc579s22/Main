#!/usr/bin/env bash
set -x

# setup on cache server
sudo apt update && sudo apt upgrade -y && sudo apt install varnish -y
sudo mkdir -p /etc/systemd/system/varnish.service.d
sudo cp customexec.conf /etc/systemd/system/varnish.service.d/customexec.conf
sudo cp default.vcl /etc/varnish/default.vcl
sudo systemctl daemon-reload
sudo systemctl restart varnish
sudo varnishstat -1 | grep MAIN.cache
#MAIN.cache_hit                         6         0.04 Cache hits
#MAIN.cache_hit_grace                   0         0.00 Cache grace hits
#MAIN.cache_hitpass                     0         0.00 Cache hits for pass.
#MAIN.cache_hitmiss                     0         0.00 Cache hits for miss.
#MAIN.cache_miss                        2         0.01 Cache misses
