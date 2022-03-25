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
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from operator import attrgetter
from pprint import pprint

import networkx as nx
from bson import json_util
from networkx.readwrite import json_graph
from pymongo import DESCENDING
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from ryu.app import simple_switch_13
from ryu.app.wsgi import ControllerBase, WSGIApplication, route, Response
from ryu.controller import ofp_event
from ryu.controller.handler import DEAD_DISPATCHER
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import dpid as dpid_lib
from ryu.lib import hub
from ryu.lib.packet import ether_types
from ryu.lib.packet import ethernet
from ryu.lib.packet import packet
from ryu.ofproto import ofproto_v1_4
from ryu.topology import event
from tabulate import tabulate

from arima import ARIMA
from config import Interval, MongoURI
from config import MaxInt
from config import NodeList, AvailableMPD, get_client_list, node_name_to_ip, ip_to_node_name, EnableSABR
from config import get_cache_list, dpid_to_name, port_addr_to_node_name
from path import best_target_selection
from queue_db import put_one, db, QueueSize
import queue


@dataclass
class Stat:
    prev_rx_bytes_count: int = 0
    prev_tx_bytes_count: int = 0
    prev_duration_sec: int = 0
    prev_duration_nsec: int = 0


prev_stats = defaultdict(lambda: defaultdict(Stat))
best_cache_server_for_each_client = defaultdict()
rest_instance_name = "sabr_monitor"
route_name = "sabr"
global_topo = nx.Graph()


class SABRMonitor(simple_switch_13.SimpleSwitch13):
    OFP_VERSIONS = [ofproto_v1_4.OFP_VERSION]
    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(SABRMonitor, self).__init__(*args, **kwargs)
        wsgi = kwargs['wsgi']
        wsgi.register(SABRController, {rest_instance_name: self})
        self.monitor_thread = hub.spawn(self._monitor)
        self.datapaths = {}
        # self.topo_raw_switches = []
        # self.topo_raw_links = []
        self.topo = nx.Graph()
        try:
            self.mongo_client = MongoClient(MongoURI)
            print("Connected to MongoDB")
            self.db = self.mongo_client.opencdn
            # self.table_port_monitor = self.db.portmonitor
            self.table_port_info = self.db.portinfo
            self.table_topo_info = self.db.topoinfo
            self.ARIMA = ARIMA()
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

    def update_best_cache_server_for_each_client(self):
        # topo = self.table_topo_info.find_one({"id": 1})
        # data = json.loads(topo["info"])
        # self.topo = json_graph.node_link_graph(data)
        self.topo = global_topo

        cache_list = [cache["name"] for cache in get_cache_list()]
        client_list = [node["name"] for node in NodeList]

        for node in client_list:
            best_cache = best_target_selection(self.topo, node, cache_list)
            best_cache_server_for_each_client[node] = best_cache

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("======packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            self.add_flow(datapath, 1, match, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    # It seems we might only need port stats to calculate throughput and bandwidth
    # So _flow_stats_reply_handler is removed
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body
        dpid = "%016x" % ev.msg.datapath.id
        dpid_name = dpid_to_name(dpid)

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

                rx_bw_arima, tx_bw_arima = self.ARIMA.predict_avg(dpid, stat.port_no)
                post = {"date": datetime.utcnow(),
                        "dpid": "%016x" % ev.msg.datapath.id, "portno": stat.port_no,
                        "RXpackets": stat.rx_packets, "RXbytes": stat.rx_bytes,
                        "RXerrors": stat.rx_errors, "RXbandwidth": cur_rx_throughput,
                        "RXbandwidth_arima": rx_bw_arima,
                        "TXpackets": stat.tx_packets, "TXbytes": stat.tx_bytes,
                        "TXerrors": stat.tx_errors, "TXbandwidth": cur_tx_throughput}
                # self.table_port_monitor.insert_one(post)
                put_one("%016x" % ev.msg.datapath.id, stat.port_no, cur_tx_throughput, cur_rx_throughput)
                table.append(["%016x" % ev.msg.datapath.id,
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

                node_name = port_addr_to_node_name(hwaddr)
                self.topo[dpid_name][node_name]["weight"] = round(rx_bw_arima + tx_bw_arima, 3)
                self.draw_topo()
                # if (not (hwaddr in ConnectedSwitchPort.keys() or hwaddr in ConnectedSwitchPort.values())) \
                # and hwaddr != "":
                #     node_name = port_addr_to_node_name(hwaddr)
                #     self.topo[dpid_name][node_name]["weight"] = round(rx_bw_arima + tx_bw_arima, 3)
                #     self.draw_topo()
        if EnableSABR:
            self.update_best_cache_server_for_each_client()
        print(tabulate(table, headers=table_headers))
        print("\n")

    def get_hwaddr_from_portno(self, dpid, port_no):
        res = self.table_port_info.find({"dpid": dpid, "portno": port_no}).limit(1)
        return res[0]["hwaddr"]

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
        sw_name = dpid_to_name(dpid)
        self.topo.add_node(sw_name)
        for port in ev.switch.ports:
            post = {"dpid": "%016x" % port.dpid,
                    "portno": port.port_no,
                    "hwaddr": port.hw_addr,
                    "name": port.name.decode("utf-8")}
            db["%016x" % port.dpid][port.port_no]["tx"] = queue.Queue(maxsize=QueueSize)
            db["%016x" % port.dpid][port.port_no]["rx"] = queue.Queue(maxsize=QueueSize)
            self.table_port_info.update_one({"dpid": post["dpid"], "hwaddr": post["hwaddr"]}, {"$set": post}, upsert=True)
            node_name = port_addr_to_node_name(port.hw_addr)
            self.topo.add_node(node_name)
            self.topo.add_edge(sw_name, node_name, weight=0)

        print("Update switch info finished, dpid: %s, switch: %s" % (dpid, sw_name))
        self.draw_topo()
        self.init_nearest_cache_server_list()

    def save_topo(self):
        global global_topo
        global_topo = self.topo
        # post = {"id": 1, "info": json.dumps(json_graph.node_link_data(self.topo))}
        # self.table_topo_info.update_one({"id": 1}, {"$set": post}, upsert=True)

    def init_nearest_cache_server_list(self):
        print("===START initial cache server selection for each client===")
        topo = self.table_topo_info.find_one({"id": 1})
        data = json.loads(topo["info"])
        self.topo = json_graph.node_link_graph(data)

        cache_list = [cache["name"] for cache in get_cache_list()]
        client_list = [node["name"] for node in NodeList]

        for node in client_list:
            hops = MaxInt
            nearest = ""
            for cache in cache_list:
                if node not in self.topo.nodes() or cache not in self.topo.nodes():
                    continue
                path = nx.shortest_paths.shortest_path(self.topo, node, cache)
                if len(path) < hops:
                    hops = len(path)
                    nearest = cache
            best_cache_server_for_each_client[node] = nearest
        print("===END initial cache server selection for each client===")
        print(best_cache_server_for_each_client)

    def draw_topo(self):
        self.save_topo()

        # Path("topo").mkdir(exist_ok=True)
        # switch_names = [sw["name"] for sw in Switch]
        # fixed_pos = {}
        # count = 0
        # for node in self.topo.nodes:
        #     if node in switch_names:
        #         fixed_pos[node] = (5, count*10)
        #         count += 1
        #
        # pos = nx.spring_layout(self.topo, pos=fixed_pos, fixed=fixed_pos.keys())
        # nx.draw(self.topo, pos, with_labels=True)
        # labels = nx.get_edge_attributes(self.topo, "weight")
        # nx.draw_networkx_edge_labels(self.topo, pos, edge_labels=labels)
        # # plt.show()
        # plt.savefig("topo/topo-%s.png" % datetime.utcnow())
        # plt.close()


class SABRController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(SABRController, self).__init__(req, link, data, **config)
        self.simple_switch_app = data[rest_instance_name]
        try:
            self.mongo_client = MongoClient(MongoURI)
            print("Connected to MongoDB")
            self.db = self.mongo_client.opencdn
            # self.table_port_monitor = self.db.portmonitor
            self.table_port_info = self.db.portinfo
            self.table_topo_info = self.db.topoinfo
            self.ARIMA = ARIMA()
            self.topo = nx.Graph()
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
        dpid = "%016x" % dpid_lib.str_to_dpid(kwargs["dpid"])
        portno = int(kwargs["portno"])
        port = self.table_port_info.find({"dpid": dpid, "portno": portno}).limit(1)
        return self.response(json_util.dumps(port[0]))

    @route(route_name, "/dpid/{dpid}/portstat/{portno}", methods="GET",
           requirements={"dpid": dpid_lib.DPID_PATTERN, "portno": r"\d+"})
    def get_port_stat(self, req, **kwargs):
        dpid = "%016x" % dpid_lib.str_to_dpid(kwargs["dpid"])
        portno = int(kwargs["portno"])
        port = self.table_port_monitor.find({"dpid": dpid, "portno": portno}).sort([("_id", DESCENDING)]).limit(1)
        return self.response(json_util.dumps(port[0]))

    @route(route_name, "/mpd/{name}/ip/{client_ip}", methods="GET")
    def get_mpd(self, req, **kwargs):
        name = kwargs["name"]
        client_ip = kwargs["client_ip"]
        if client_ip not in get_client_list():
            return self.response(json.dumps({
                "error": "client %s is not registered in SABR" % client_ip
            }))
        if name not in AvailableMPD:
            return self.response(json.dumps({
                "error": "%s is not available" % name
            }))
        cache = self.nearest_cache_server(client_ip)
        resp = {
            "dash_mpd_url": "http://%s/%s/%s_2s_mod1.mpd" % (cache["ip"], name, name)
        }
        return self.response(json.dumps(resp))

    def nearest_cache_server(self, ip):
        port_name = ""
        for node in NodeList:
            if node["ip"] == ip:
                port_name = node["name"]
        # topo = self.table_topo_info.find_one({"id": 1})
        # data = json.loads(topo["info"])
        # self.topo = json_graph.node_link_graph(data)
        self.topo = global_topo
        hops = MaxInt
        nearest = {}

        for cache in get_cache_list():
            path = nx.shortest_paths.shortest_path(self.topo, cache["name"], port_name)
            print("current path: ", path)
            print("hops: ", len(path))
            if len(path) < hops:
                hops = len(path)
                nearest = cache
        return nearest

    @route(route_name, "/nearest_cache/{ip}")
    def get_nearest_cache_server(self, req, **kwargs):
        ip = kwargs["ip"]
        if ip not in get_client_list():
            return self.response(json.dumps({
                "error": "client %s is not registered in SABR" % ip
            }))
        # node = self.nearest_cache_server(ip)
        name = best_cache_server_for_each_client[ip_to_node_name(ip)]
        return self.response("nearest cache server for %s is [%s:%s]" % (ip, name, node_name_to_ip(name)))
