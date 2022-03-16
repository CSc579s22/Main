# Copyright (C) 2016 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Modified from ryu/app/simple_monitor_13.py
# https://github.com/faucetsdn/ryu/blob/master/ryu/app/simple_monitor_13.py

from datetime import datetime
from operator import attrgetter

import networkx as nx
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.ofproto import ofproto_v1_3
from ryu.topology import event
from ryu.topology.api import get_switch, get_link
import copy
import matplotlib.pyplot as plt

from pprint import pprint

# Monitor interval in seconds
Interval = 10
MongoURL = "127.0.0.1"
# ConnectedSW = {"0000c699ecb9ea46": "0000aae305428d4a"}
# Switches = ["0000c699ecb9ea46", "0000aae305428d4a"]
SameLink = {"02:92:b4:89:d6:8f": "02:2a:41:1e:70:d0"}


class SimpleMonitor13(simple_switch_13.SimpleSwitch13):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        self.topo_raw_switches = []
        self.topo_raw_links = []
        self.topo = nx.Graph()
        try:
            self.mongo_client = MongoClient(MongoURL)
            print("Connected to MongoDB")
            self.db = self.mongo_client.opencdn
            self.table_port_monitor = self.db.portmonitor
            self.table_port_info = self.db.portinfo
        except ConnectionFailure as e:
            print("MongoDB connection failed: %s" % e)
            exit(1)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(Interval)

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    # It seems we might only need port stats to calculate throughput and bandwidth
    # So _flow_stats_reply_handler is removed
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body
        self.logger.info('datapath         port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error')
        self.logger.info('---------------- -------- '
                         '-------- -------- -------- '
                         '-------- -------- --------')
        for stat in sorted(body, key=attrgetter('port_no')):
            self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',
                             ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors)
            if stat.port_no != 0xfffffffe:
                post = {"date": datetime.utcnow(),
                        "dpid": "%016x" % ev.msg.datapath.id, "portno": stat.port_no,
                        "RXpackets": "%8d" % stat.rx_packets, "RXbytes": "%8d" % stat.rx_bytes,
                        "RXerrors": "%8d" % stat.rx_errors,
                        "TXpackets": "%8d" % stat.tx_packets, "TXbytes": "%8d" % stat.tx_bytes,
                        "TXerrors": "%8d" % stat.tx_errors}
                self.table_port_monitor.insert_one(post)

    @set_ev_cls(event.EventPortAdd)
    def _port_add(self, ev):
        print("EventPortAdd")
        post = {"dpid": "%016x" % ev.port.dpid,
                "portno": ev.port.port_no,
                "hwaddr": ev.port.hw_addr,
                "name": ev.port.name.decode("utf-8")}
        pprint(post)
        self.table_port_info.update_one({"dpid": post["dpid"], "hwaddr": post["hwaddr"]}, {"$set": post}, upsert=True)

    @set_ev_cls(event.EventPortDelete)
    def _port_delete(self, ev):
        print("EventPortDelete")
        post = {"dpid": "%016x" % ev.port.dpid,
                "portno": ev.port.port_no,
                "hwaddr": ev.port.hw_addr,
                "name": ev.port.name.decode("utf-8")}
        pprint(post)
        self.table_port_info.delete_one({"dpid": post["dpid"], "hwaddr": post["hwaddr"], "portno": post["portno"]})

    @set_ev_cls(event.EventSwitchEnter)
    def handler_switch_enter(self, ev):
        dpid = str("%016x" % ev.switch.dp.id)
        # pprint(vars(ev.switch))
        # print("handler_switch_enter, ", dpid)
        # print("current nodes: ", self.topo.nodes)
        # if self.topo.has_node(dpid):
        #     print("node already exist: ", dpid)
        #     return
        # import pdb
        # pdb.set_trace()
        self.topo.add_node(dpid)
        for port in ev.switch.ports:
            post = {"dpid": "%016x" % port.dpid,
                    "portno": port.port_no,
                    "hwaddr": port.hw_addr,
                    "name": port.name.decode("utf-8")}
            # print("current port")
            # pprint(post)
            self.table_port_info.update_one({"dpid": post["dpid"], "hwaddr": post["hwaddr"]}, {"$set": post}, upsert=True)
            # if self.topo.has_node(port.hw_addr):
            #     continue
            # import pdb
            # pdb.set_trace()
            # addr = port.hw_addr
            # if addr in SameLink.keys():
            #     addr = SameLink[addr]
            self.topo.add_node(port.hw_addr)
            # if not self.topo.has_edge(dpid, port.hw_addr):
            self.topo.add_edge(dpid, port.hw_addr)

        print("Update switch info finished, dpid: ", dpid)
        # print("keys: ", ConnectedSW.keys())
        # if dpid in ConnectedSW.keys() and self.topo.has_node(ConnectedSW[dpid]):
        #     if not self.topo.has_edge(dpid, ConnectedSW[dpid]):
        #         self.topo.add_edge(dpid, ConnectedSW[dpid])
        # print("current nodes before draw: ", self.topo.nodes)
        # print("current edges before draw: ", self.topo.edges)
        self.draw_topo()

    def draw_topo(self):
        for k in SameLink.keys():
            if self.topo.has_node(SameLink[k]):
                # edges = self.topo.edges(k)
                # for e in edges:
                #     nx.contracted_edge(self.topo, e, self_loops=False, copy=False)
                nx.contracted_nodes(self.topo, k, SameLink[k], self_loops=False, copy=False)

        nodes_to_remove = [n for n in self.topo.nodes if len(list(self.topo.neighbors(n))) == 2]

        # For each of those nodes
        for node in nodes_to_remove:
            # We add an edge between neighbors (len == 2 so it is correct)
            self.topo.add_edge(*self.topo.neighbors(node))
            # And delete the node
            self.topo.remove_node(node)

        pos = nx.spring_layout(self.topo)
        nx.draw(self.topo, pos, with_labels=True)
        labels = nx.get_edge_attributes(self.topo, "weight")
        nx.draw_networkx_edge_labels(self.topo, pos, edge_labels=labels)
        # plt.show()
        plt.savefig("topo.png")
        plt.close()
