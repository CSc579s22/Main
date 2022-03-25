# QoE Improvements For Adaptive Video Streaming Over SDN-Enabled Networks

## Install

### Provision on CloudLab

1. Create a CloudLab profile using [`multilayer.py`](./server/topology/multilayer.py)
2. Instantiate an experiment using the profile created above
3. After the experiment is ready, copy the `Manifest` from CloudLab experiment details page into [`topo.xml`](./topo.xml)
4. Run [`validate_topo.py`](./validate_topo.py) to validate topology
5. Update server login information (username, hostname, port) in [`config.py`](./config.py)
6. Run [`get_testbed_info.py`](./get_testbed_info.py), update `NodeList` in [`server/config.py`](./server/config.py) using the information printed in the last step
7. Run [`setup_testbed.py`](./setup_testbed.py) to install dependencies on nodes, update `Switch` in [`server/config.py`](./server/config.py), update `ConnectedSwitchPort` in [`server/config.py`](./server/config.py) using the output
8. Build Docker image and push to DockerHub using [`server/Dockerfile`](./server/Dockerfile), update `image` in [`server/docker-compose.yaml`](./server/docker-compose.yaml)
```bash
cd server
sudo docker build -t clarkzjw/sabrcontroller:0.1 .
```
9. SSH login to `server` node, start controller using [`docker-compose.yaml`](./server/docker-compose.yaml)
```bash
sudo docker-compose up -d
```

`cd` into the `video` directory, upload all the `*.mpd` files into `video/BigBuckBunny` directory
download corresponding videos
```bash
sudo wget -r --no-parent --reject "index.html*" http://ftp.itec.aau.at/datasets/DASHDataset2014/BigBuckBunny/2sec/
```
and move `2sec` directory below `video/BigBuckBunny` directory.

The final directory structure looks like this
```txt
$ tree -L 3 videos/
videos/
├── BigBuckBunny
│ ├── 2sec
│ │ ├── BigBuckBunny_2s_onDemand_2014_05_09.mpd
│ │ ├── BigBuckBunny_2s_simple_2014_05_09.mpd
│ │ ├── bunny_1032682bps
│ │ ├── bunny_1244778bps
│ │ ├── bunny_131087bps
│ │ ├── bunny_1546902bps
│ │ ├── bunny_178351bps
│ │ ├── bunny_2133691bps
│ │ ├── bunny_221600bps
│ │ ├── bunny_2484135bps
│ │ ├── bunny_262537bps
│ │ ├── bunny_3078587bps
│ │ ├── bunny_334349bps
│ │ ├── bunny_3526922bps
│ │ ├── bunny_3840360bps
│ │ ├── bunny_396126bps
│ │ ├── bunny_4219897bps
│ │ ├── bunny_45652bps
│ │ ├── bunny_522286bps
│ │ ├── bunny_595491bps
│ │ ├── bunny_791182bps
│ │ └── bunny_89283bps
│ ├── BigBuckBunny_2s_mod10.mpd
│ ├── BigBuckBunny_2s_mod11.mpd
│ ├── BigBuckBunny_2s_mod12.mpd
│ ├── BigBuckBunny_2s_mod13.mpd
│ ├── BigBuckBunny_2s_mod14.mpd
│ ├── BigBuckBunny_2s_mod15.mpd
│ ├── BigBuckBunny_2s_mod16.mpd
│ ├── BigBuckBunny_2s_mod17.mpd
│ ├── BigBuckBunny_2s_mod18.mpd
│ ├── BigBuckBunny_2s_mod19.mpd
│ ├── BigBuckBunny_2s_mod1.mpd
│ ├── BigBuckBunny_2s_mod20.mpd
│ ├── BigBuckBunny_2s_mod21.mpd
│ ├── BigBuckBunny_2s_mod22.mpd
│ ├── BigBuckBunny_2s_mod23.mpd
│ ├── BigBuckBunny_2s_mod24.mpd
│ ├── BigBuckBunny_2s_mod25.mpd
│ ├── BigBuckBunny_2s_mod26.mpd
│ ├── BigBuckBunny_2s_mod27.mpd
│ ├── BigBuckBunny_2s_mod28.mpd
│ ├── BigBuckBunny_2s_mod29.mpd
│ ├── BigBuckBunny_2s_mod2.mpd
│ ├── BigBuckBunny_2s_mod30.mpd
│ ├── BigBuckBunny_2s_mod31.mpd
│ ├── BigBuckBunny_2s_mod32.mpd
│ ├── BigBuckBunny_2s_mod33.mpd
│ ├── BigBuckBunny_2s_mod34.mpd
│ ├── BigBuckBunny_2s_mod35.mpd
│ ├── BigBuckBunny_2s_mod36.mpd
│ ├── BigBuckBunny_2s_mod37.mpd
│ ├── BigBuckBunny_2s_mod38.mpd
│ ├── BigBuckBunny_2s_mod39.mpd
│ ├── BigBuckBunny_2s_mod3.mpd
│ ├── BigBuckBunny_2s_mod40.mpd
│ ├── BigBuckBunny_2s_mod41.mpd
│ ├── BigBuckBunny_2s_mod42.mpd
│ ├── BigBuckBunny_2s_mod43.mpd
│ ├── BigBuckBunny_2s_mod44.mpd
│ ├── BigBuckBunny_2s_mod45.mpd
│ ├── BigBuckBunny_2s_mod46.mpd
│ ├── BigBuckBunny_2s_mod47.mpd
│ ├── BigBuckBunny_2s_mod48.mpd
│ ├── BigBuckBunny_2s_mod49.mpd
│ ├── BigBuckBunny_2s_mod4.mpd
│ ├── BigBuckBunny_2s_mod50.mpd
│ ├── BigBuckBunny_2s_mod5.mpd
│ ├── BigBuckBunny_2s_mod6.mpd
│ ├── BigBuckBunny_2s_mod7.mpd
│ ├── BigBuckBunny_2s_mod8.mpd
│ └── BigBuckBunny_2s_mod9.mpd
└── index.html

22 directories, 53 files
```

10. SSH login to switch nodes, set controller for each ovs bridge
```bash
sudo ovs-vsctl set-controller <bridge name> tcp:<server node ip>:6633
```

## Design

Steps:

+ Clients join the network by "connecting the port to OVS switch"
(manually configured on OVS switch)
+ Ryu controller monitors events from OVS switches, after it received
port_add event from switch, modify topology, save to database
+ Clients start AStream player, send a request to server, receives the
nearest cache server(by hops) and mpd file url
+ Clients start playing using the mpd file url received above
+ Ryu controller monitors ports' speed, and make predictions of ports'
bandwidth(average), save to database
+ Clients periodically requests estimated port bandwidth to benefit
local bandwidth estimation
+ Analysis logs generated by AStream player(quality switches, vmaf,
bandwidth, latency, cache hit/miss)


TODO:

- [ ] use ARIMA(or simpler estimation) to replace bandwidth estimation
- [x] dynamically dispatch servers based on SABR bandwidth
- [ ] dispatch near cache servers by latency
- [ ] set link speed and latency to simulate network congestion
- [ ] calculate fairness on Ryu controller
- [ ] set port link speed/QoS based on fairness
- [ ] AStream is not compatible with current MPD file
- [ ] Varnish cache: cache-hit/cache-miss
