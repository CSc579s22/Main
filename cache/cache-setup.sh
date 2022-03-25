#!/usr/bin/env bash
set -x

# setup on cache server
sudo apt-get update && sudo apt-get install varnish -y
sudo mkdir -p /etc/systemd/system/varnish.service.d
sudo curl -fsSL https://raw.githubusercontent.com/CSc579s22/Main/master/cache/customexec.conf -o /etc/systemd/system/varnish.service.d/customexec.conf
sudo curl -fsSL https://raw.githubusercontent.com/CSc579s22/Main/master/cache/default.vcl -o /etc/varnish/default.vcl
sudo systemctl daemon-reload
sudo systemctl restart varnish
sudo varnishadm param.set default_ttl 7200
