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
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from operator import attrgetter
from pathlib import Path
from pprint import pprint
from pymongo import DESCENDING
import matplotlib.pyplot as plt
import networkx as nx
from bson import json_util
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from ryu.app import simple_switch_13
from ryu.app.wsgi import ControllerBase, WSGIApplication, route, Response
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import dpid as dpid_lib
from ryu.lib import hub
from ryu.ofproto import ofproto_v1_4
from ryu.topology import event
from tabulate import tabulate

from arima import ARIMA
from config import Interval, MongoURI, SameLink


@dataclass
class Stat:
    prev_rx_bytes_count: int = 0
    prev_tx_bytes_count: int = 0
    prev_duration_sec: int = 0
    prev_duration_nsec: int = 0


prev_stats = defaultdict(lambda: defaultdict(Stat))
rest_instance_name = "sabr_monitor"
route_name = "sabr"


class SABRMonitor(simple_switch_13.SimpleSwitch13):
    OFP_VERSIONS = [ofproto_v1_4.OFP_VERSION]
    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(SABRMonitor, self).__init__(*args, **kwargs)
        wsgi = kwargs['wsgi']
        wsgi.register(SABRController, {rest_instance_name: self})
        self.monitor_thread = hub.spawn(self._monitor)
        self.datapaths = {}
        self.topo_raw_switches = []
        self.topo_raw_links = []
        self.topo = nx.Graph()
        try:
            self.mongo_client = MongoClient(MongoURI)
            print("Connected to MongoDB")
            self.db = self.mongo_client.opencdn
            self.table_port_monitor = self.db.portmonitor
            self.table_port_info = self.db.portinfo
            self.ARIMA = ARIMA(MongoURL=MongoURI)
        except ConnectionFailure as e:
            print("MongoDB connection failed: %s" % e)
            exit(1)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %0x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %0x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(Interval)

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %0x', datapath.id)
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
        dpid = "%0x" % ev.msg.datapath.id

        table_headers = ["datapath", "port",
                         "rx-pkts", "rx-bytes", "rx-bw Mbit/sec", "rx-error", "rx-bw arima Mbit/sec",
                         "tx-pkts", "tx-bytes", "tx-bw Mbit/sec", "tx-error"]
        table = []
        for stat in sorted(body, key=attrgetter('port_no')):
            # print(vars(stat))
            if stat.port_no != 0xfffffffe:
                prev_stat = prev_stats[dpid][stat.port_no]

                delta_rx_bytes_count = stat.rx_bytes - prev_stat.prev_rx_bytes_count
                delta_tx_bytes_count = stat.tx_bytes - prev_stat.prev_tx_bytes_count
                delta_duration_sec = stat.duration_sec - prev_stat.prev_duration_sec
                delta_duration_nsec = stat.duration_nsec - prev_stat.prev_duration_nsec

                if delta_duration_sec + (delta_duration_nsec / 1000000000.0) == 0:
                    cur_rx_throughput = 0
                    cur_tx_throughput = 0
                else:
                    # Mbit/sec
                    cur_rx_throughput = delta_rx_bytes_count / (
                                delta_duration_sec + (delta_duration_nsec / 1000000000.0)) * 8.0 / 1000000
                    cur_tx_throughput = delta_tx_bytes_count / (
                                delta_duration_sec + (delta_duration_nsec / 1000000000.0)) * 8.0 / 1000000

                rx_bw_arima = self.ARIMA.predict(dpid, stat.port_no)
                post = {"date": datetime.utcnow(),
                        "dpid": "%0x" % ev.msg.datapath.id, "portno": stat.port_no,
                        "RXpackets": stat.rx_packets, "RXbytes": stat.rx_bytes,
                        "RXerrors": stat.rx_errors, "RXbandwidth": cur_rx_throughput,
                        "RXbandwidth_arima": rx_bw_arima,
                        "TXpackets": stat.tx_packets, "TXbytes": stat.tx_bytes,
                        "TXerrors": stat.tx_errors, "TXbandwidth": cur_tx_throughput}
                self.table_port_monitor.insert_one(post)
                table.append(["%0x" % ev.msg.datapath.id,
                              stat.port_no,
                              stat.rx_packets, stat.rx_bytes, cur_rx_throughput, stat.rx_errors, rx_bw_arima,
                              stat.tx_packets, stat.tx_bytes, cur_tx_throughput, stat.tx_errors
                              ])
                prev_stats[dpid][stat.port_no] = Stat(
                    stat.rx_bytes,
                    stat.tx_bytes,
                    stat.duration_sec,
                    stat.duration_nsec
                )
                hwaddr = self.get_hwaddr_from_portno(dpid, stat.port_no)

                if (not (hwaddr in SameLink.keys() or hwaddr in SameLink.values())) and hwaddr != "":
                    self.topo[dpid][hwaddr]["weight"] = cur_tx_throughput
                    self.draw_topo()
        print(tabulate(table, headers=table_headers))
        print("\n")

    def get_hwaddr_from_portno(self, dpid, port_no):
        res = self.table_port_info.find({"dpid": dpid, "portno": port_no}).limit(1)
        return res[0]["hwaddr"]

    @set_ev_cls(event.EventPortAdd)
    def _port_add(self, ev):
        print("EventPortAdd")
        post = {"dpid": "%0x" % ev.port.dpid,
                "portno": ev.port.port_no,
                "hwaddr": ev.port.hw_addr,
                "name": ev.port.name.decode("utf-8")}
        pprint(post)
        self.table_port_info.update_one({"dpid": post["dpid"], "hwaddr": post["hwaddr"]}, {"$set": post}, upsert=True)

    @set_ev_cls(event.EventPortDelete)
    def _port_delete(self, ev):
        print("EventPortDelete")
        post = {"dpid": "%0x" % ev.port.dpid,
                "portno": ev.port.port_no,
                "hwaddr": ev.port.hw_addr,
                "name": ev.port.name.decode("utf-8")}
        pprint(post)
        self.table_port_info.delete_one({"dpid": post["dpid"], "hwaddr": post["hwaddr"], "portno": post["portno"]})

    @set_ev_cls(event.EventSwitchEnter)
    def handler_switch_enter(self, ev):
        dpid = str("%0x" % ev.switch.dp.id)
        self.topo.add_node(dpid)
        for port in ev.switch.ports:
            post = {"dpid": "%0x" % port.dpid,
                    "portno": port.port_no,
                    "hwaddr": port.hw_addr,
                    "name": port.name.decode("utf-8")}

            self.table_port_info.update_one({"dpid": post["dpid"], "hwaddr": post["hwaddr"]}, {"$set": post}, upsert=True)
            self.topo.add_node(port.hw_addr)
            self.topo.add_edge(dpid, port.hw_addr)

        print("Update switch info finished, dpid: ", dpid)
        self.draw_topo()

    def draw_topo(self):
        Path("topo").mkdir(exist_ok=True)

        for k in SameLink.keys():
            if self.topo.has_node(SameLink[k]):
                nx.contracted_nodes(self.topo, k, SameLink[k], self_loops=False, copy=False)

        nodes_to_remove = [n for n in self.topo.nodes if len(list(self.topo.neighbors(n))) == 2]

        # For each of those nodes
        for node in nodes_to_remove:
            # We add an edge between neighbors (len == 2 so it is correct)
            self.topo.add_edge(*self.topo.neighbors(node))
            # And delete the node
            self.topo.remove_node(node)

        ports = self.table_port_info.find()
        dpids = [port["dpid"] for port in ports]
        fixed_pos = {}
        count = 0
        for node in self.topo.nodes:
            if node in dpids:
                fixed_pos[node] = (5, count*10)
                count += 1

        pos = nx.spring_layout(self.topo, pos=fixed_pos, fixed=fixed_pos.keys())
        nx.draw(self.topo, pos, with_labels=True)
        labels = nx.get_edge_attributes(self.topo, "weight")
        nx.draw_networkx_edge_labels(self.topo, pos, edge_labels=labels)
        # plt.show()
        plt.savefig("topo/topo-%s.png" % datetime.utcnow())
        plt.close()


class SABRController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(SABRController, self).__init__(req, link, data, **config)
        self.simple_switch_app = data[rest_instance_name]
        try:
            self.mongo_client = MongoClient(MongoURI)
            print("Connected to MongoDB")
            self.db = self.mongo_client.opencdn
            self.table_port_monitor = self.db.portmonitor
            self.table_port_info = self.db.portinfo
            self.ARIMA = ARIMA(MongoURL=MongoURI)
        except ConnectionFailure as e:
            print("MongoDB connection failed: %s" % e)
            exit(1)

    def response(self, text):
        return Response(content_type="application", text=text)

    @route(route_name, "/hello", methods="GET")
    def hello(self, req, **kwargs):
        return self.response("hello")

    @route(route_name, "/dpid/{dpid}/port/{portno}", methods="GET",
           requirements={"dpid": dpid_lib.DPID_PATTERN, "portno": r"\d+"})
    def get_port(self, req, **kwargs):
        dpid = "%0x" % dpid_lib.str_to_dpid(kwargs["dpid"])
        portno = int(kwargs["portno"])
        port = self.table_port_info.find({"dpid": dpid, "portno": portno}).limit(1)
        return self.response(json_util.dumps(port[0]))

    @route(route_name, "/dpid/{dpid}/portstat/{portno}", methods="GET",
           requirements={"dpid": dpid_lib.DPID_PATTERN, "portno": r"\d+"})
    def get_port_stat(self, req, **kwargs):
        dpid = "%0x" % dpid_lib.str_to_dpid(kwargs["dpid"])
        portno = int(kwargs["portno"])
        port = self.table_port_monitor.find({"dpid": dpid, "portno": portno}).sort([("_id", DESCENDING)]).limit(1)
        return self.response(json_util.dumps(port[0]))

    @route(route_name, "/mpd/{name}", methods="GET")
    def get_mpd(self, req, **kwargs):
        name = kwargs["name"]
        return self.response("mpd: " + name)

    @route(route_name, "/nearest_cache/{ip}")
    def get_nearest_cache_server(self, req, **kwargs):
        ip = kwargs["ip"]
        # TODO: verify ip
        return self.response("nearest cache server for: " + ip)
