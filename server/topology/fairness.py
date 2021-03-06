#!/usr/bin/python2

"""
Fairness Topology
"""

import geni.portal as portal
import geni.rspec.pg as pg

site_name = "fairness"
mask = "255.255.255.0"

ip_count = 1


def get_ip():
    global ip_count
    # 10.10.10.1 is reserved for server
    ip = "10.10.10.{}".format(ip_count+1)
    ip_count += 1
    return ip


# Create a portal object
pc = portal.Context()
# ovs_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18OVS"
# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Switch for origin server
sw_origin = request.XenVM("sw_origin")
# sw_origin.disk_image = ovs_image

# Backbone switch
backbone_sw = []
number_of_backbone_regions = 2
for i in range(number_of_backbone_regions):
    sw = request.XenVM("sw{}".format(i + 1))
    # sw.disk_image = ovs_image
    backbone_sw.append(sw)
    link = request.Link("link-sw_origin-sw{}".format(i + 1))
    link.Site(site_name)
    link.addInterface(
        sw.addInterface("if-sw{}-sw_origin".format(i + 1), pg.IPv4Address(get_ip(), mask)))
    link.addInterface(
        sw_origin.addInterface("if-sw_origin-sw{}".format(i + 1), pg.IPv4Address(get_ip(), mask)))

# Origin server
node_server = request.RawPC('server')
node_server.routable_control_ip = True
if_sw = sw_origin.addInterface("if-sw_origin-server", pg.IPv4Address(get_ip(), mask))
if_server = node_server.addInterface('if-server', pg.IPv4Address("10.10.10.1", mask))
link = request.Link("link-sw_origin-server")
link.Site(site_name)
link.addInterface(if_sw)
link.addInterface(if_server)

# add clients and cache for each backbone region
number_of_client_each_region = 4
for i in range(number_of_backbone_regions):
    cache = request.XenVM("sw{}-cache1".format(i+1, i+1))
    link = request.Link("link-sw{}-cache1".format(i+1, i+1))
    link.Site(site_name)
    link.addInterface(backbone_sw[i].addInterface("if-sw{}-cache1".format(i+1, i+1), pg.IPv4Address(get_ip(), mask)))
    link.addInterface(cache.addInterface("if-cache1-sw{}".format(i+1, i+1), pg.IPv4Address(get_ip(), mask)))
    for j in range(number_of_client_each_region):
        client = request.XenVM("sw{}c{}".format(i + 1, j + 1))
        link = request.Link("link-sw{}c{}".format(i + 1, j + 1))
        link.Site(site_name)
        link.addInterface(
            backbone_sw[i].addInterface("if-sw{}c{}".format(i + 1, j + 1),
                                      pg.IPv4Address(get_ip(), mask))
        )
        link.addInterface(
            client.addInterface("if-c{}sw{}".format(j + 1, i + 1),
                                pg.IPv4Address(get_ip(), mask))
        )

pc.printRequestRSpec(request)
